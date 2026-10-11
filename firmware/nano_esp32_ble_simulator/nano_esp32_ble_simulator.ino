/*
 * OTGD synthetic BLE bench peripheral, protocol 1 / firmware 1.0.0.
 * Board: Arduino Nano ESP32, arduino:esp32:nano_nora.
 * This program never reads a biological sensor, electrode, pupil or chemical assay.
 * All reported values are fixed fictional fixtures. CRC and replay hashes are NOT authentication.
 */
#include <Arduino.h>
#include <ArduinoJson.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <esp_system.h>
#include <esp_timer.h>
#include <mbedtls/sha256.h>
#include <atomic>
#include <deque>
#include "ProtocolCore.h"

using namespace otgd;
static const char* SERVICE="680cf5d8-5656-4f41-81c4-0f48d26f1000";
static const char* CAPABILITIES="680cf5d8-5656-4f41-81c4-0f48d26f1001";
static const char* COMMAND_UUID="680cf5d8-5656-4f41-81c4-0f48d26f1002";
static const char* EVENT_UUID="680cf5d8-5656-4f41-81c4-0f48d26f1003";
static const size_t JOURNAL_LIMIT=128, RESPONSE_CACHE_LIMIT=65536, TX_QUEUE_LIMIT=8, TX_BYTES_LIMIT=32768;
static BLEServer* server=nullptr;
static BLECharacteristic* tx=nullptr;
static std::atomic<bool> connected(false), linkChanged(false), rxOverflow(false);
static std::atomic<uint32_t> linkEpoch(0);
static uint32_t handlingEpoch=0, transferSequence=0;
static uint64_t deviceSequence=0;
static std::string deviceId,bootId,currentSession;
static Reassembler receiver;
struct RxFrame { uint32_t epoch; uint8_t size; uint8_t bytes[20]; };
static QueueHandle_t rxQueue=nullptr;
struct PendingMessage {
  std::string id,json; std::vector<uint8_t> stream; uint32_t transfer;
  uint16_t index=0; uint8_t retries=0; bool needsAck=false,waiting=false,acked=false;
  uint64_t lastFragment=0,ackDeadline=0;
};
struct JournalEntry { std::string id,hash; std::vector<std::string> responses; };
struct SessionSequence { std::string id; uint64_t sequence; };
static std::deque<PendingMessage> outgoing;
static std::vector<JournalEntry> journal;
static std::vector<SessionSequence> sessions;
static std::vector<std::string> sentIds;
static size_t cachedBytes=0,queuedBytes=0;
struct Capture { bool active=false; std::string command,session,attempt,capture,epoch,channel; uint64_t started=0,due=0; };
static Capture capture;
static uint64_t clockMs() { return uint64_t(esp_timer_get_time()/1000); }
static std::string randomUuid() {
  uint8_t bytes[16]; esp_fill_random(bytes,sizeof(bytes)); bytes[6]=(bytes[6]&15)|0x40; bytes[8]=(bytes[8]&63)|0x80;
  char out[37]; snprintf(out,sizeof(out),"%02x%02x%02x%02x-%02x%02x-%02x%02x-%02x%02x-%02x%02x%02x%02x%02x%02x",bytes[0],bytes[1],bytes[2],bytes[3],bytes[4],bytes[5],bytes[6],bytes[7],bytes[8],bytes[9],bytes[10],bytes[11],bytes[12],bytes[13],bytes[14],bytes[15]); return out;
}
static bool uuid(const char* value) {
  if(!value || strlen(value)!=36) return false;
  for(size_t i=0;i<36;i++) { const char c=value[i]; if(i==8 || i==13 || i==18 || i==23) { if(c!='-') return false; } else if(!((c>='0' && c<='9') || (c>='a' && c<='f') || (c>='A' && c<='F'))) return false; }
  return true;
}
static std::string hash(const std::string& value) {
  uint8_t bytes[32]; mbedtls_sha256_ret(reinterpret_cast<const uint8_t*>(value.data()),value.size(),bytes,0);
  char output[65]; for(size_t i=0;i<32;i++) snprintf(output+i*2,3,"%02x",bytes[i]); return output;
}
static void abortLink(const char* reason) {
  Serial.print("Protocol stopped: "); Serial.println(reason); capture.active=false; connected.store(false);
  if(server) server->disconnect(server->getConnId());
  linkChanged.store(true);
}
static JournalEntry* entry(const std::string& id) { for(auto& e:journal) if(e.id==id) return &e; return nullptr; }
static bool keys(JsonObjectConst object,std::initializer_list<const char*> allowed) {
  for(JsonPairConst pair:object) { bool found=false; for(const char* key:allowed) if(strcmp(pair.key().c_str(),key)==0) { found=true; break; } if(!found) return false; }
  return true;
}
static bool boundedString(JsonVariantConst value,size_t minimum,size_t maximum) {
  if(!value.is<const char*>()) return false; const char* text=value.as<const char*>(); const size_t size=strlen(text);
  return size>=minimum && size<=maximum;
}
static void queueRaw(const std::string& json) {
  if(!connected.load()) return;
  if(json.size()+4>kLogicalLimit || outgoing.size()>=TX_QUEUE_LIMIT || queuedBytes+json.size()>TX_BYTES_LIMIT || transferSequence==UINT32_MAX) { abortLink("TX_QUEUE_OVERFLOW"); return; }
  JsonDocument parsed;
  if(deserializeJson(parsed,json) || !parsed["message_id"].is<const char*>()) { abortLink("INTERNAL_ENVELOPE_ERROR"); return; }
  PendingMessage m; m.id=parsed["message_id"].as<std::string>(); m.json=json; m.stream=logicalStream(json); m.transfer=transferSequence++;
  m.needsAck=strcmp(parsed["type"].as<const char*>(),"ack")!=0;
  if(m.needsAck && std::find(sentIds.begin(),sentIds.end(),m.id)==sentIds.end()) {
    if(sentIds.size()>=256) { abortLink("SENT_JOURNAL_FULL"); return; } sentIds.push_back(m.id);
  }
  queuedBytes+=json.size(); outgoing.push_back(std::move(m));
}
static void reply(const std::string& request,const std::string& session,const char* type,JsonDocument& payload,bool retain=true) {
  JsonDocument message;
  message["protocol_version"]=1; message["message_id"]=randomUuid(); message["device_id"]=deviceId; message["boot_id"]=bootId;
  message["session_id"]=session; message["sequence"]=deviceSequence++; message["monotonic_ms"]=clockMs(); message["type"]=type;
  message["payload"].set(payload.as<JsonVariantConst>());
  std::string json; serializeJson(message,json);
  if(retain) {
    JournalEntry* e=entry(request);
    if(!e || cachedBytes+json.size()>RESPONSE_CACHE_LIMIT || e->responses.size()>=3) { abortLink("REPLAY_JOURNAL_FULL"); return; }
    e->responses.push_back(json); cachedBytes+=json.size();
  }
  queueRaw(json);
}
static void errorReply(const std::string& request,const std::string& session,const char* reason) {
  capture.active=false; JsonDocument p; p["request_message_id"]=request; p["code"]=reason; reply(request,session,"error",p,false);
}
static void acknowledge(const std::string& request,const std::string& session) {
  JsonDocument p; p["ack_message_id"]=request; p["status"]="accepted"; reply(request,session,"ack",p);
}
static void process(const std::string& json,uint64_t assemblyStart) {
  const uint64_t received=clockMs();
  if(!StrictJson(json).valid()) { abortLink("INVALID_JSON"); return; }
  JsonDocument doc; const auto parseError=deserializeJson(doc,json,DeserializationOption::NestingLimit(16));
  if(parseError || !doc.is<JsonObject>() || !keys(doc.as<JsonObjectConst>(),{"protocol_version","message_id","device_id","boot_id","session_id","sequence","monotonic_ms","type","payload"}) || !doc["protocol_version"].is<uint32_t>() || doc["protocol_version"].as<uint32_t>()!=1 || !uuid(doc["message_id"]) || !uuid(doc["boot_id"]) || !uuid(doc["session_id"]) || !doc["sequence"].is<uint64_t>() || !doc["monotonic_ms"].is<double>() || doc["monotonic_ms"].as<double>()<0 || !doc["payload"].is<JsonObject>() || !boundedString(doc["type"],1,32)) { abortLink("INVALID_ENVELOPE"); return; }
  if(doc["device_id"]!=deviceId.c_str() || doc["boot_id"]!=bootId.c_str()) { abortLink("IDENTITY_MISMATCH"); return; }
  const std::string id=doc["message_id"].as<std::string>(),session=doc["session_id"].as<std::string>(),type=doc["type"].as<std::string>(),fingerprint=hash(json);
  if(JournalEntry* previous=entry(id)) {
    if(previous->hash!=fingerprint) { errorReply(id,session,"MESSAGE_ID_CONFLICT"); return; }
    for(const auto& response:previous->responses) queueRaw(response);
    return;
  }
  if(journal.size()>=JOURNAL_LIMIT) { errorReply(id,session,"REPLAY_JOURNAL_FULL"); return; }
  const uint64_t sequence=doc["sequence"].as<uint64_t>();
  SessionSequence* seq=nullptr; for(auto& s:sessions) if(s.id==session) { seq=&s; break; }
  if(seq && sequence<=seq->sequence) { errorReply(id,session,"SEQUENCE_REPLAY"); return; }
  if(!seq) {
    if(type!="hello" || sessions.size()>=32) { errorReply(id,session,"SESSION_NOT_INITIALIZED"); return; }
    sessions.push_back({session,sequence});
  } else seq->sequence=sequence;
  journal.push_back({id,fingerprint,{}});
  JsonObjectConst p=doc["payload"].as<JsonObjectConst>();
  if(type=="ack") {
    if(!keys(p,{"ack_message_id","status"}) || !uuid(p["ack_message_id"]) || p["status"]!="accepted") { errorReply(id,session,"INVALID_ACK"); return; }
    const std::string ack=p["ack_message_id"].as<std::string>();
    if(std::find(sentIds.begin(),sentIds.end(),ack)==sentIds.end()) { errorReply(id,session,"UNEXPECTED_ACK"); return; }
    if(!outgoing.empty() && outgoing.front().id==ack) outgoing.front().acked=true;
    return;
  }
  if(!p["deadline_after_ms"].is<uint32_t>() || p["deadline_after_ms"].as<uint32_t>()==0 || p["deadline_after_ms"].as<uint32_t>()>120000 || received<assemblyStart || received-assemblyStart>p["deadline_after_ms"].as<uint32_t>()) { errorReply(id,session,"COMMAND_DEADLINE"); return; }
  if(type=="hello") {
    if(!keys(p,{"deadline_after_ms"}) || (capture.active && capture.session!=session)) { errorReply(id,session,"DEVICE_BUSY"); return; }
    currentSession=session; acknowledge(id,session); JsonDocument response; response["request_message_id"]=id; response["source"]="simulated"; response["configuration_id"]="synthetic_bench_v1"; reply(id,session,"hello",response);
  } else if(session!=currentSession) errorReply(id,session,"SESSION_MISMATCH");
  else if(type=="clock_sync") {
    if(!keys(p,{"deadline_after_ms","phone_send_ms"}) || !p["phone_send_ms"].is<double>() || p["phone_send_ms"].as<double>()<0) { errorReply(id,session,"CLOCK_REQUEST"); return; }
    acknowledge(id,session); JsonDocument response; response["request_message_id"]=id; response["phone_send_ms"]=p["phone_send_ms"];
    response["device_receive_ms"]=received; response["device_send_ms"]=clockMs(); reply(id,session,"clock_sync",response);
  } else if(type=="start_capture") {
    if(!keys(p,{"deadline_after_ms","deadline_device_ms","attempt_id","capture_id","workspace_epoch","channel","source"}) || !uuid(p["attempt_id"]) || !uuid(p["capture_id"]) || !boundedString(p["workspace_epoch"],1,128) || !boundedString(p["channel"],3,6) || p["source"]!="simulated" || !p["deadline_device_ms"].is<double>()) { errorReply(id,session,"INVALID_CAPTURE_REQUEST"); return; }
    const double deadline=p["deadline_device_ms"].as<double>(); const std::string channel=p["channel"].as<std::string>();
    if(capture.active || deadline<double(received) || deadline>double(received)+120000 || (channel!="ppg" && channel!="ecg" && channel!="saliva")) { errorReply(id,session,"CAPTURE_REFUSED"); return; }
    capture.active=true; capture.command=id; capture.session=session; capture.attempt=p["attempt_id"].as<std::string>(); capture.capture=p["capture_id"].as<std::string>(); capture.epoch=p["workspace_epoch"].as<std::string>(); capture.channel=channel;
    capture.started=received; capture.due=received+(channel=="ppg" ? 3000 : channel=="ecg" ? 4000 : 2000); acknowledge(id,session);
  } else if(type=="cancel_capture") {
    if(!keys(p,{"deadline_after_ms","attempt_id","capture_id","workspace_epoch"}) || !uuid(p["attempt_id"]) || !uuid(p["capture_id"]) || !boundedString(p["workspace_epoch"],1,128) || (capture.active && (capture.attempt!=p["attempt_id"].as<std::string>() || capture.capture!=p["capture_id"].as<std::string>() || capture.epoch!=p["workspace_epoch"].as<std::string>()))) { errorReply(id,session,"CANCEL_IDENTITY"); return; }
    capture.active=false; acknowledge(id,session);
  } else errorReply(id,session,"UNSUPPORTED_COMMAND");
}
static void finishCapture() {
  if(!capture.active || clockMs()<capture.due) return;
  capture.active=false; JsonDocument p;
  p["source"]="simulated"; p["channel"]=capture.channel; p["attempt_id"]=capture.attempt; p["capture_id"]=capture.capture; p["workspace_epoch"]=capture.epoch;
  p["started_monotonic_ms"]=capture.started; p["ended_monotonic_ms"]=clockMs(); p["fixture_id"]="synthetic_bench_v1";
  JsonObject values=p["values"].to<JsonObject>();
  if(capture.channel=="ppg" || capture.channel=="ecg") {
    values["heart_rate_bpm"]=72; values["duration_seconds"]=capture.channel=="ppg" ? 3 : 4; values["method"]=capture.channel;
    if(capture.channel=="ecg") {
      values["sample_rate_hz"]=50; values["lead_count"]=1; values["units"]="arbitrary_counts"; JsonArray samples=values["samples"].to<JsonArray>();
      for(int i=0;i<200;i++) { const int phase=i%42; const int sample=phase==10 ? 800 : phase==11 ? -250 : phase>=20 && phase<=25 ? (phase<=22 ? phase-19 : 26-phase)*25 : phase>=4 && phase<=6 ? 30 : 0; samples.add(sample); }
    }
  } else {
    values["specimen"]="oral_fluid"; values["assay_id"]="synthetic_assay_v1"; JsonArray analytes=values["analytes"].to<JsonArray>();
    const char* names[]={"delta9_thc","11_hydroxy_thc","thc_cooh"};
    for(int i=0;i<3;i++) { JsonObject a=analytes.add<JsonObject>(); a["analyte"]=names[i]; a["qualifier"]=i==0 ? "quantified" : "not_detected"; if(i==0) a["value"]=12; else a["value"]=nullptr; a["unit"]="ng/mL"; a["lod"]=1; a["loq"]=2; a["uloq"]=100; }
  }
  reply(capture.command,capture.session,"capture_complete",p);
}
static void drainTx() {
  if(!connected.load() || outgoing.empty()) return;
  PendingMessage& message=outgoing.front(); const uint64_t now=clockMs();
  if(message.acked) { queuedBytes-=message.json.size(); outgoing.pop_front(); return; }
  if(message.waiting) {
    if(now<message.ackDeadline) return;
    if(message.retries>=3) { abortLink("ACK_TIMEOUT"); return; }
    message.retries++; message.waiting=false; message.index=0; message.transfer=transferSequence++;
  }
  if(now-message.lastFragment<10) return;
  uint8_t frame[20]; const size_t count=frameAt(message.stream,message.transfer,message.index,frame);
  if(count==0) { abortLink("INTERNAL_FRAGMENT_ERROR"); return; }
  tx->setValue(frame,count); tx->notify(); message.lastFragment=now; message.index++;
  if(size_t(message.index)*kCapacity>=message.stream.size()) {
    if(message.needsAck) { message.waiting=true; message.ackDeadline=now+2000; }
    else { queuedBytes-=message.json.size(); outgoing.pop_front(); }
  }
}
class ServerCallbacks final:public BLEServerCallbacks {
  void onConnect(BLEServer*) override { linkEpoch.fetch_add(1); connected.store(true); linkChanged.store(true); }
  void onDisconnect(BLEServer*) override { connected.store(false); linkChanged.store(true); }
};
class RxCallbacks final:public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic* characteristic) override {
    const std::string value=characteristic->getValue();
    if(!connected.load()) return;
    if(value.size()<13 || value.size()>20) { rxOverflow.store(true); return; }
    RxFrame frame{}; frame.epoch=linkEpoch.load(); frame.size=uint8_t(value.size()); memcpy(frame.bytes,value.data(),value.size());
    if(xQueueSend(rxQueue,&frame,0)!=pdTRUE) rxOverflow.store(true);
  }
};
void setup() {
  Serial.begin(115200); // Do not wait for USB: the BLE peripheral also works from a bench power supply.
  bootId=randomUuid(); char id[32]; snprintf(id,sizeof(id),"SIM-NANO-%012llX",static_cast<unsigned long long>(ESP.getEfuseMac())); deviceId=id;
  journal.reserve(JOURNAL_LIMIT); sessions.reserve(32); sentIds.reserve(256);
  rxQueue=xQueueCreate(64,sizeof(RxFrame)); if(!rxQueue) { Serial.println("RX_QUEUE_ALLOCATION_FAILED"); return; }
  BLEDevice::init("OTGD Synthetic"); BLEDevice::setMTU(23);
  server=BLEDevice::createServer(); server->setCallbacks(new ServerCallbacks()); BLEService* service=server->createService(SERVICE);
  BLECharacteristic* cap=service->createCharacteristic(CAPABILITIES,BLECharacteristic::PROPERTY_READ);
  BLECharacteristic* rx=service->createCharacteristic(COMMAND_UUID,BLECharacteristic::PROPERTY_WRITE); rx->setCallbacks(new RxCallbacks());
  tx=service->createCharacteristic(EVENT_UUID,BLECharacteristic::PROPERTY_NOTIFY); tx->addDescriptor(new BLE2902());
  JsonDocument capabilities;
  capabilities["protocol_version"]=1; capabilities["encodings"].to<JsonArray>().add(1); capabilities["max_logical_bytes"]=8192; capabilities["max_att_bytes"]=20;
  capabilities["source"]="simulated"; capabilities["device_id"]=deviceId; capabilities["boot_id"]=bootId; capabilities["hardware_revision"]="nano_esp32_bench_1"; capabilities["firmware_version"]="1.0.0";
  JsonArray channels=capabilities["channels"].to<JsonArray>(); channels.add("ppg"); channels.add("ecg"); channels.add("saliva");
  capabilities["configuration_id"]="synthetic_bench_v1"; capabilities["calibration_status"]="not_applicable"; capabilities["timestamp_resolution_ms"]=1;
  std::string json; serializeJson(capabilities,json); if(json.size()>512) { Serial.println("CAPABILITIES_TOO_LARGE"); return; } cap->setValue(json);
  service->start(); BLEAdvertising* advertising=BLEDevice::getAdvertising(); advertising->addServiceUUID(SERVICE); advertising->setScanResponse(true); advertising->start();
  Serial.println("OTGD synthetic simulator ready. No human sensing. Fixed fictional fixtures only.");
}
void loop() {
  if(!rxQueue || !server || !tx) { delay(20); return; }
  if(linkChanged.exchange(false)) {
    capture.active=false; receiver.reset(); outgoing.clear(); queuedBytes=0; handlingEpoch=linkEpoch.load(); currentSession.clear(); sessions.clear();
    if(!connected.load()) BLEDevice::startAdvertising();
    // Replay journal and physical boot ID survive reconnect. Restart the board on journal exhaustion.
  }
  if(rxOverflow.exchange(false)) abortLink("RX_QUEUE_OVERFLOW");
  RxFrame frame{}; int drained=0;
  while(drained++<64 && xQueueReceive(rxQueue,&frame,0)==pdTRUE) {
    if(!connected.load() || frame.epoch!=handlingEpoch) continue;
    const ReceiveResult result=receiver.push(frame.bytes,frame.size,clockMs());
    if(result==ReceiveResult::Error) { abortLink(receiver.error()); break; }
    if(result==ReceiveResult::Complete) process(std::string(reinterpret_cast<const char*>(receiver.jsonData()),receiver.jsonSize()),receiver.startedAt());
  }
  if(connected.load()) { if(receiver.expire(clockMs())) abortLink(receiver.error()); else { finishCapture(); drainTx(); } }
  delay(1);
}
