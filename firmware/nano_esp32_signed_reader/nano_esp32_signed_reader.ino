/*
 * OTGD signed research reader transport, protocol 1 / firmware 1.0.0.
 * Board: Arduino Nano ESP32, arduino:esp32:nano_nora.
 * Acquisition is unavailable until an approved actual hardware driver is linked.
 * Protected identity and server grant signing keys are provisioned offline.
 * No synthetic measurements, phone signatures or plaintext key fallback exist.
 */
#include <Arduino.h>
#include <ArduinoJson.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <BLESecurity.h>
#include <esp_system.h>
#include <esp_timer.h>
#include <mbedtls/sha256.h>
#include <atomic>
#include <deque>
#include <mutex>
#include "ProtocolCore.h"
#include "CanonicalJson.h"
#include "ServerGrantCore.h"
#include "ReaderLifecycle.h"
#include "ProtectedSigner.h"
#include "AcquisitionDriver.h"

using namespace otgd;
static const char* SERVICE="680cf5d8-5656-4f41-81c4-0f48d26f1000";
static const char* CAPABILITIES="680cf5d8-5656-4f41-81c4-0f48d26f1001";
static const char* COMMAND_UUID="680cf5d8-5656-4f41-81c4-0f48d26f1002";
static const char* EVENT_UUID="680cf5d8-5656-4f41-81c4-0f48d26f1003";
static const size_t JOURNAL_LIMIT=128, RESPONSE_CACHE_LIMIT=65536, TX_QUEUE_LIMIT=8, TX_BYTES_LIMIT=32768;
static BLEServer* server=nullptr;
static BLECharacteristic* tx=nullptr;
static BLE2902* notificationConfiguration=nullptr;
static esp_gatt_if_t admittedGattsInterface=ESP_GATT_IF_NONE;
static std::atomic<bool> linkChanged(false), rxOverflow(false);
// BLE connection transitions and sensitive hardware/sign/notify operations
// share this short gate. Parsing and TX waits run outside it.
static otgd_reader::OriginGate connectionGate;
static otgd_reader::AuthenticatedPeer authenticatedPeer;
static uint8_t pairingFailures=0;
static uint32_t handlingEpoch=0, transferSequence=0;
static uint64_t deviceSequence=0;
static std::string deviceId,bootId,currentSession;
static Reassembler receiver;
static otgd_reader::ProtectedSigner signer;
static JsonDocument captureAuthorization;
static std::string startNonce;
static uint64_t nonceCreated=0;
static size_t sampleChunks=0;
struct RxFrame { uint32_t epoch; uint8_t size; uint8_t bytes[20]; };
static QueueHandle_t rxQueue=nullptr;
struct PendingMessage {
  std::string id,json; std::vector<uint8_t> stream; uint32_t transfer;
  uint32_t origin=0;
  uint16_t index=0; uint8_t retries=0; bool needsAck=false,waiting=false,acked=false;
  uint64_t lastFragment=0,ackDeadline=0;
};
struct JournalEntry { std::string id,hash; std::vector<std::string> responses; uint32_t epoch; };
struct SessionSequence { std::string id; uint64_t sequence; };
static std::deque<PendingMessage> outgoing;
static std::vector<JournalEntry> journal;
static std::vector<SessionSequence> sessions;
static std::vector<std::string> sentIds;
static size_t cachedBytes=0,queuedBytes=0;
struct Capture { bool active=false; std::string command,session,attempt,capture,epoch,channel; uint64_t started=0,due=0,ended=0; uint32_t origin=0; };
static Capture capture;
static bool currentOrigin(uint32_t origin) {std::lock_guard<std::recursive_mutex> lock(connectionGate.mutex);return connectionGate.current(origin)&&authenticatedPeer.current(origin);}
static uint64_t clockMs() { return uint64_t(esp_timer_get_time()/1000); }
static void stopAcquisition(){connectionGate.synchronize([]{otgdAcquisitionStop();});}
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
  Serial.print("Protocol stopped: "); Serial.println(reason); capture.active=false; stopAcquisition(); connectionGate.transition(false);
  if(server) server->disconnect(server->getConnId());
  linkChanged.store(true);
}
static JournalEntry* entry(const std::string& id) { for(auto& e:journal) if(e.id==id) return &e; return nullptr; }
static bool keys(JsonObjectConst object,std::initializer_list<const char*> allowed) {
  for(JsonPairConst pair:object) { bool found=false; for(const char* key:allowed) if(strcmp(pair.key().c_str(),key)==0) { found=true; break; } if(!found) return false; }
  return true;
}
static bool boundedString(JsonVariantConst value,size_t minimum,size_t maximum) {
  if(!value.is<const char*>()) return false;
  const char* text=value.as<const char*>(); const size_t size=strlen(text);
  return size>=minimum && size<=maximum;
}
static void queueRaw(const std::string& json) {
  if(!currentOrigin(handlingEpoch)) return;
  if(json.size()+4>kLogicalLimit || outgoing.size()>=TX_QUEUE_LIMIT || queuedBytes+json.size()>TX_BYTES_LIMIT || transferSequence==UINT32_MAX) { abortLink("TX_QUEUE_OVERFLOW"); return; }
  JsonDocument parsed;
  if(deserializeJson(parsed,json) || !parsed["message_id"].is<const char*>()) { abortLink("INTERNAL_ENVELOPE_ERROR"); return; }
  PendingMessage m; m.origin=handlingEpoch; m.id=parsed["message_id"].as<std::string>(); m.json=json; m.stream=logicalStream(json); m.transfer=transferSequence++;
  m.needsAck=strcmp(parsed["type"].as<const char*>(),"ack")!=0;
  if(m.needsAck && std::find(sentIds.begin(),sentIds.end(),m.id)==sentIds.end()) {
    if(sentIds.size()>=256) { abortLink("SENT_JOURNAL_FULL"); return; } sentIds.push_back(m.id);
  }
  queuedBytes+=json.size(); outgoing.push_back(std::move(m));
}
static void reply(const std::string& request,const std::string& session,const char* type,JsonDocument& payload,bool retain=true) {
  if(!currentOrigin(handlingEpoch)) return;
  JsonDocument message;
  message["protocol_version"]=1; message["message_id"]=randomUuid(); message["device_id"]=deviceId; message["boot_id"]=bootId;
  message["session_id"]=session; message["sequence"]=deviceSequence++; message["monotonic_ms"]=clockMs(); message["type"]=type;
  message["payload"].set(payload.as<JsonVariantConst>());
  std::string json; if(!otgd_reader::canonical(message.as<JsonVariantConst>(),json)) {abortLink("NONCANONICAL_REPLY");return;}
  if(!currentOrigin(handlingEpoch)) return;
  if(retain) {
    JournalEntry* e=entry(request);
    if(!e || cachedBytes+json.size()>RESPONSE_CACHE_LIMIT || e->responses.size()>=3) { abortLink("REPLAY_JOURNAL_FULL"); return; }
    e->responses.push_back(json); cachedBytes+=json.size();
  }
  queueRaw(json);
}
static void errorReply(const std::string& request,const std::string& session,const char* reason) {
  capture.active=false; stopAcquisition(); JsonDocument p; p["request_message_id"]=request; p["code"]=reason; reply(request,session,"error",p,false);
}
static void acknowledge(const std::string& request,const std::string& session) {
  JsonDocument p; p["ack_message_id"]=request; p["status"]="accepted"; reply(request,session,"ack",p);
}
static void process(const std::string& json,uint64_t assemblyStart) {
  const uint64_t received=clockMs();
  if(!currentOrigin(handlingEpoch)) return;
  if(!StrictJson(json).valid()) { abortLink("INVALID_JSON"); return; }
  JsonDocument doc; const auto parseError=deserializeJson(doc,json,DeserializationOption::NestingLimit(16));
  if(parseError || !doc.is<JsonObject>() || !keys(doc.as<JsonObjectConst>(),{"protocol_version","message_id","device_id","boot_id","session_id","sequence","monotonic_ms","type","payload"}) || !doc["protocol_version"].is<uint32_t>() || doc["protocol_version"].as<uint32_t>()!=1 || !uuid(doc["message_id"]) || !uuid(doc["boot_id"]) || !uuid(doc["session_id"]) || !doc["sequence"].is<uint64_t>() || !doc["monotonic_ms"].is<double>() || doc["monotonic_ms"].as<double>()<0 || !doc["payload"].is<JsonObject>() || !boundedString(doc["type"],1,32)) { abortLink("INVALID_ENVELOPE"); return; }
  if(doc["device_id"]!=deviceId.c_str() || doc["boot_id"]!=bootId.c_str()) { abortLink("IDENTITY_MISMATCH"); return; }
  const std::string id=doc["message_id"].as<std::string>(),session=doc["session_id"].as<std::string>(),type=doc["type"].as<std::string>(),fingerprint=hash(json);
  if(JournalEntry* previous=entry(id)) {
    if(otgd_reader::replayAdmission(previous->epoch,handlingEpoch,previous->hash==fingerprint)==otgd_reader::ReplayAdmission::ForeignOrigin) {errorReply(id,session,"FOREIGN_CONNECTION_REPLAY");return;}
    if(otgd_reader::replayAdmission(previous->epoch,handlingEpoch,previous->hash==fingerprint)==otgd_reader::ReplayAdmission::ConflictingContent) { errorReply(id,session,"MESSAGE_ID_CONFLICT"); return; }
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
  journal.push_back({id,fingerprint,{},handlingEpoch});
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
    if(!keys(p,{"deadline_after_ms","protocol_id","binding_transcript","request_start_nonce"}) || capture.active) {errorReply(id,session,"DEVICE_BUSY");return;}
    currentSession=session;JsonDocument response;response["request_message_id"]=id;response["source"]="prototype_sensor";
    response["protocol_id"]="otgd_signed_reader_v1";response["key_id"]=signer.keyId();
    if(p["binding_transcript"].is<JsonObjectConst>()) {
      JsonObjectConst t=p["binding_transcript"].as<JsonObjectConst>();
      if(!keys(t,{"schema_version","challenge_id","environment","owner_ref","data_generation","device_id","key_id","nonce","expires_at","hardware_revision","firmware_version"}) || t.size()!=11 || t["schema_version"]!="1.0.0" || !uuid(t["challenge_id"]) || !uuid(t["owner_ref"]) || !t["data_generation"].is<uint64_t>() || t["data_generation"].as<uint64_t>()<1 || t["data_generation"].as<uint64_t>()>9007199254740991ULL || t["device_id"]!=deviceId || t["key_id"]!=signer.keyId() || t["hardware_revision"]!=signer.hardware() || t["firmware_version"]!=signer.firmware() || !boundedString(t["nonce"],43,43) || !boundedString(t["expires_at"],20,40)) {errorReply(id,session,"BINDING_TRANSCRIPT_REFUSED");return;}
      std::string canonical,signature;
      std::lock_guard<std::recursive_mutex> originLock(connectionGate.mutex);
      if(!currentOrigin(handlingEpoch) || !otgd_reader::canonical(t,canonical) || !signer.sign("OTGD-BIND-v1\n",canonical,signature)) {errorReply(id,session,"SIGNER_UNAVAILABLE");return;}
      response["challenge_id"]=t["challenge_id"];response["signature"]=signature;
    } else if(p["request_start_nonce"]==true) {
      unsigned char bytes[32];esp_fill_random(bytes,sizeof(bytes));unsigned char encoded[45]{};size_t length=0;
      if(mbedtls_base64_encode(encoded,sizeof(encoded),&length,bytes,sizeof(bytes))!=0 || length!=44) {errorReply(id,session,"NONCE_GENERATION_FAILED");return;}
      startNonce.assign(reinterpret_cast<char*>(encoded),43);for(char& c:startNonce) {if(c=='+')c='-';else if(c=='/')c='_';}
      nonceCreated=received;response["device_nonce"]=startNonce;
    }
    acknowledge(id,session);reply(id,session,"hello",response);
  } else if(session!=currentSession) errorReply(id,session,"SESSION_MISMATCH");
  else if(type=="clock_sync") {
    if(!keys(p,{"deadline_after_ms","phone_send_ms"}) || !p["phone_send_ms"].is<double>() || p["phone_send_ms"].as<double>()<0) { errorReply(id,session,"CLOCK_REQUEST"); return; }
    acknowledge(id,session); JsonDocument response; response["request_message_id"]=id; response["phone_send_ms"]=p["phone_send_ms"];
    response["device_receive_ms"]=received; response["device_send_ms"]=clockMs(); reply(id,session,"clock_sync",response);
  } else if(type=="start_capture") {
    if(!keys(p,{"deadline_after_ms","protocol_id","attempt_id","capture_id","workspace_epoch","channel","source","authorization"}) || p.size()!=8 || p["protocol_id"]!="otgd_signed_reader_v1" || p["source"]!="prototype_sensor" || !uuid(p["attempt_id"]) || !uuid(p["capture_id"]) || !boundedString(p["workspace_epoch"],1,128) || !boundedString(p["channel"],3,7)) {errorReply(id,session,"INVALID_CAPTURE_REQUEST");return;}
    JsonObjectConst authorization=p["authorization"].as<JsonObjectConst>();
    if(!boundedString(authorization["server_start_base64"],8,6000)) {errorReply(id,session,"SERVER_GRANT_REQUIRED");return;}
    const std::string encoded=authorization["server_start_base64"].as<std::string>();unsigned char decoded[4501]{};size_t decodedSize=0;
    if(mbedtls_base64_decode(decoded,4500,&decodedSize,reinterpret_cast<const unsigned char*>(encoded.data()),encoded.size())!=0) {errorReply(id,session,"SERVER_GRANT_ENCODING");return;}
    const std::string tokenBytes(reinterpret_cast<char*>(decoded),decodedSize);
    if(!StrictJson(tokenBytes,true).valid()) {errorReply(id,session,"SERVER_GRANT_ENCODING");return;}
    JsonDocument tokenDocument;
    if(!otgd_reader::deserializeExact(tokenDocument,tokenBytes,true)) {errorReply(id,session,"SERVER_GRANT_ENCODING");return;}
    JsonObjectConst token=tokenDocument.as<JsonObjectConst>(),grant=token["grant"].as<JsonObjectConst>();
    const JsonString domain=token["domain"].as<JsonString>();
    if(domain.size()!=sizeof("OTGD capture grant v1\0")-1 || memcmp(domain.c_str(),"OTGD capture grant v1\0",sizeof("OTGD capture grant v1\0")-1)!=0) {errorReply(id,session,"SERVER_GRANT_DOMAIN");return;}
    if(!keys(authorization,{"environment","owner_ref","data_generation","authorization_id","binding_id","device_id","key_id","configuration_id","configuration_hash","max_duration_ms","capture_context_sha256","server_start_base64"}) || authorization.size()!=12 || !keys(token,{"grant","signature","key_id","domain"}) || token.size()!=4 || !keys(grant,{"schema_version","environment","owner_ref","data_generation","session_id","attempt_id","authorization_id","binding_id","device_id","device_key_id","boot_id","configuration_id","configuration_hash","configuration_submitted_sha256","configuration_version","capture_context_sha256","channel","configuration_max_duration_ms","raw_recording_permission","expires_at","issued_at","device_nonce","nonce"}) || grant.size()!=23) {errorReply(id,session,"SERVER_GRANT_REQUIRED");return;}
    const std::string channel=p["channel"].as<std::string>();
    if(capture.active || !otgdAcquisitionAvailable(channel.c_str())) {errorReply(id,session,"ACQUISITION_DRIVER_UNAVAILABLE");return;}
    if(startNonce.empty() || grant["device_nonce"]!=startNonce || received<nonceCreated || received-nonceCreated>60000 || grant["boot_id"]!=bootId || grant["device_id"]!=deviceId || grant["device_key_id"]!=signer.keyId() || grant["session_id"]!=session || grant["attempt_id"]!=p["attempt_id"] || grant["schema_version"]!="1.0.0" || !uuid(grant["authorization_id"]) || !uuid(grant["binding_id"]) || !uuid(grant["owner_ref"]) || !uuid(grant["nonce"])) {errorReply(id,session,"SERVER_GRANT_SCOPE");return;}
    for(const char* field:{"environment","owner_ref","data_generation","authorization_id","binding_id","device_id","configuration_id","configuration_hash","capture_context_sha256"}) if(authorization[field]!=grant[field]) {errorReply(id,session,"SERVER_GRANT_SCOPE");return;}
    if(authorization["key_id"]!=signer.keyId() || !authorization["max_duration_ms"].is<uint32_t>() || authorization["max_duration_ms"].as<uint32_t>()==0 || authorization["max_duration_ms"].as<uint32_t>()>120000) {errorReply(id,session,"SERVER_GRANT_SCOPE");return;}
    if(grant["channel"]!=(channel=="ppg"?"cardiac":channel.c_str()) || authorization["max_duration_ms"]!=grant["configuration_max_duration_ms"]) {errorReply(id,session,"SERVER_GRANT_SCOPE");return;}
    const otgd_reader::GrantExpectations expected{deviceId,signer.keyId(),bootId,session,p["attempt_id"].as<std::string>(),channel,startNonce,nonceCreated,received};
    if(!otgd_reader::verifyServerGrant(token,authorization,expected,[](const std::string& label,const std::string& canonical,const std::string& signature){return signer.verifyGrant(label,canonical,signature);})) {errorReply(id,session,"SERVER_GRANT_SIGNATURE");return;}
    if(!currentOrigin(handlingEpoch)) return;
    startNonce.clear();captureAuthorization.set(authorization);sampleChunks=0;
    capture.command=id;capture.session=session;capture.attempt=p["attempt_id"].as<std::string>();capture.capture=p["capture_id"].as<std::string>();capture.epoch=p["workspace_epoch"].as<std::string>();capture.channel=channel;
    capture.origin=handlingEpoch;capture.ended=0;capture.started=clockMs();capture.due=capture.started+authorization["max_duration_ms"].as<uint32_t>();
    std::lock_guard<std::recursive_mutex> originLock(connectionGate.mutex);
    if(!currentOrigin(capture.origin)) return;
    if(!otgdAcquisitionStart(channel.c_str(),grant,capture.session.c_str(),capture.attempt.c_str(),capture.capture.c_str(),capture.started)) {errorReply(id,session,"ACQUISITION_DRIVER_UNAVAILABLE");return;}
    if(!currentOrigin(capture.origin)) {stopAcquisition();return;}
    capture.active=true;acknowledge(id,session);
  } else if(type=="cancel_capture") {
    if(!keys(p,{"deadline_after_ms","attempt_id","capture_id","workspace_epoch"}) || !uuid(p["attempt_id"]) || !uuid(p["capture_id"]) || !boundedString(p["workspace_epoch"],1,128) || (capture.active && (capture.attempt!=p["attempt_id"].as<std::string>() || capture.capture!=p["capture_id"].as<std::string>() || capture.epoch!=p["workspace_epoch"].as<std::string>()))) { errorReply(id,session,"CANCEL_IDENTITY"); return; }
    capture.active=false; stopAcquisition(); acknowledge(id,session);
  } else errorReply(id,session,"UNSUPPORTED_COMMAND");
}
static bool signedEvidence(JsonDocument& normalized,JsonDocument& payload) {
  std::lock_guard<std::recursive_mutex> originLock(connectionGate.mutex);
  if(!currentOrigin(capture.origin)) return false;
  std::string canonical; if(!otgd_reader::canonical(normalized.as<JsonVariantConst>(),canonical,6000)) return false;
  JsonObject e=payload["envelope"].to<JsonObject>();
  e["schema_version"]="1.0.0";
  for(const char* field:{"environment","owner_ref","data_generation","authorization_id","binding_id","device_id","key_id","configuration_hash"}) e[field].set(captureAuthorization[field]);
  e["session_id"]=capture.session; e["attempt_id"]=capture.attempt; e["boot_id"]=bootId;
  e["sequence"]=deviceSequence; e["payload_sha256"]=hash(canonical);
  std::string envelope,signature;
  if(!currentOrigin(capture.origin) || !otgd_reader::canonical(e,envelope) || !signer.sign("OTGD-CAPTURE-v1\n",envelope,signature)) return false;
  if(!currentOrigin(capture.origin)) return false;
  payload["signature"]=signature; payload["normalized_payload"].set(normalized.as<JsonVariantConst>()); return true;
}
static void finishCapture() {
  std::lock_guard<std::recursive_mutex> originLock(connectionGate.mutex);
  if(!capture.active) return;
  if(!currentOrigin(capture.origin)) {capture.active=false;stopAcquisition();return;}
  // Acquisition advances/stops regardless of queued notifications. Sampling
  // must never wait on network backpressure or an acknowledgment.
  otgdAcquisitionTick();
  const uint64_t observedEnd=otgdAcquisitionEndedMonotonicMs();
  if(observedEnd)capture.ended=observedEnd;
  if((capture.ended && (capture.ended<capture.started||capture.ended>capture.due)) || (!capture.ended&&otgd_reader::acquisitionDeadline(clockMs(),capture.due))) {errorReply(capture.command,capture.session,"ACQUISITION_TIMEOUT");return;}
  if(outgoing.size()>=4) return;
  JsonDocument normalized; const int status=otgdAcquisitionPoll(normalized);
  if(status==0) return;
  if(status<0 || status>2) {errorReply(capture.command,capture.session,"ACQUISITION_DRIVER_FAILED");return;}
  if(status==1 && ++sampleChunks>64) {errorReply(capture.command,capture.session,"SAMPLE_LEDGER_FULL");return;}
  JsonDocument payload;
  if(!signedEvidence(normalized,payload)) {errorReply(capture.command,capture.session,"SIGNER_UNAVAILABLE");return;}
  if(status==1) {reply(capture.command,capture.session,"capture_chunk",payload,false);return;}
  capture.active=false; stopAcquisition();
  payload["source"]="prototype_sensor";payload["protocol_id"]="otgd_signed_reader_v1";payload["channel"]=capture.channel;
  payload["attempt_id"]=capture.attempt;payload["capture_id"]=capture.capture;payload["workspace_epoch"]=capture.epoch;
  payload["started_monotonic_ms"]=capture.started;payload["ended_monotonic_ms"]=capture.ended?capture.ended:clockMs();payload["attestation_id"]=randomUuid();
  reply(capture.command,capture.session,"capture_complete",payload);
}
static void drainTx() {
  if(outgoing.empty()) return;
  if(!currentOrigin(outgoing.front().origin)) {queuedBytes-=outgoing.front().json.size();outgoing.pop_front();return;}
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
  std::lock_guard<std::recursive_mutex> originLock(connectionGate.mutex);
  if(!currentOrigin(message.origin)) return;
  // Bind the stack send to the immutable admitted connection. BLECharacteristic
  // notify() broadcasts to every peer in its map, including a rejected pending
  // connection; it must not carry participant frames here.
  if(admittedGattsInterface==ESP_GATT_IF_NONE||!notificationConfiguration||!notificationConfiguration->getNotifications()){abortLink("NOTIFICATIONS_NOT_ADMITTED");return;}
  if(esp_ble_gatts_send_indicate(admittedGattsInterface,authenticatedPeer.connection(),tx->getHandle(),uint16_t(count),frame,false)!=ESP_OK){abortLink("NOTIFICATION_FAILED");return;}
  message.lastFragment=now; message.index++;
  if(size_t(message.index)*kCapacity>=message.stream.size()) {
    if(message.needsAck) { message.waiting=true; message.ackDeadline=now+2000; }
    else { queuedBytes-=message.json.size(); outgoing.pop_front(); }
  }
}
class ServerCallbacks final:public BLEServerCallbacks {
  void onConnect(BLEServer* p,esp_ble_gatts_cb_param_t* param) override {
    std::lock_guard<std::recursive_mutex> originLock(connectionGate.mutex);
    if(!otgd_reader::connectionAdmission(connectionGate.connected(),pairingFailures) || !connectionGate.transition(true)) {p->disconnect(param->connect.conn_id);return;}
    authenticatedPeer.connect(connectionGate.epoch(),param->connect.conn_id,param->connect.remote_bda);
    linkChanged.store(true);
    esp_ble_set_encryption(param->connect.remote_bda,ESP_BLE_SEC_ENCRYPT_MITM);
  }
  void onDisconnect(BLEServer*,esp_ble_gatts_cb_param_t* param) override {
    std::lock_guard<std::recursive_mutex> originLock(connectionGate.mutex);
    if(!authenticatedPeer.disconnect(param->disconnect.conn_id,param->disconnect.remote_bda))return;
    connectionGate.transition(false);stopAcquisition();if(notificationConfiguration)notificationConfiguration->setNotifications(false);linkChanged.store(true);
  }
};
class SecurityCallbacks final:public BLESecurityCallbacks {
  uint32_t onPassKeyRequest() override {return signer.pairingPasskey();}
  void onPassKeyNotify(uint32_t) override {} // The offline per-device label is the display; never log a passkey.
  bool onConfirmPIN(uint32_t) override {return false;} // No unattended numeric/Just Works confirmation.
  bool onSecurityRequest() override {
    std::lock_guard<std::recursive_mutex> lock(connectionGate.mutex);
    return connectionGate.connected()&&pairingFailures<3&&signer.ready();
  }
  void onAuthenticationComplete(esp_ble_auth_cmpl_t result) override {
    std::lock_guard<std::recursive_mutex> lock(connectionGate.mutex);
    const uint32_t epoch=connectionGate.epoch();
    if(!authenticatedPeer.matches(epoch,result.bd_addr))return;
    const auto mode=result.auth_mode;
    if(authenticatedPeer.authenticate(epoch,result.bd_addr,result.success,(mode&ESP_LE_AUTH_REQ_SC_ONLY)!=0,(mode&ESP_LE_AUTH_REQ_MITM)!=0,(mode&ESP_LE_AUTH_BOND)!=0))return;
    if(pairingFailures<3)pairingFailures++;
    connectionGate.transition(false);stopAcquisition();linkChanged.store(true);
    if(server)server->disconnect(server->getConnId());
  }
};
class RxCallbacks final:public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic*,esp_ble_gatts_cb_param_t* param) override {
    std::lock_guard<std::recursive_mutex> lock(connectionGate.mutex);
    if(!currentOrigin(connectionGate.epoch())||!authenticatedPeer.writes(connectionGate.epoch(),param->write.conn_id,param->write.bda)) return;
    const std::string value(reinterpret_cast<const char*>(param->write.value),param->write.len);
    if(value.size()<13 || value.size()>20) { rxOverflow.store(true); return; }
    RxFrame frame{}; frame.epoch=connectionGate.epoch(); frame.size=uint8_t(value.size()); memcpy(frame.bytes,value.data(),value.size());
    if(xQueueSend(rxQueue,&frame,0)!=pdTRUE) rxOverflow.store(true);
  }
};
void setup() {
  Serial.begin(115200); // Do not wait for USB: the BLE peripheral also works from a bench power supply.
  bootId=randomUuid();
  if(!signer.begin() || signer.firmware()!="1.0.0") {Serial.println("PROTECTED_SIGNER_UNAVAILABLE");return;}
  deviceId=signer.deviceId();
  bool anyDriver=false;for(const char* channel:{"ppg","ecg","saliva","alcohol"}) anyDriver=anyDriver||otgdAcquisitionAvailable(channel);
  if(!anyDriver) {Serial.println("ACQUISITION_DRIVER_UNAVAILABLE");return;}
  journal.reserve(JOURNAL_LIMIT); sessions.reserve(32); sentIds.reserve(256);
  rxQueue=xQueueCreate(64,sizeof(RxFrame)); if(!rxQueue) { Serial.println("RX_QUEUE_ALLOCATION_FAILED"); return; }
  BLEDevice::init("OTGD Research Reader"); BLEDevice::setMTU(23);
  BLEDevice::setEncryptionLevel(ESP_BLE_SEC_ENCRYPT_MITM);
  BLEDevice::setSecurityCallbacks(new SecurityCallbacks());
  BLESecurity* security=new BLESecurity();
  security->setStaticPIN(signer.pairingPasskey());
  security->setAuthenticationMode(ESP_LE_AUTH_REQ_SC_MITM_BOND);
  security->setCapability(ESP_IO_CAP_OUT);security->setKeySize(16);
  security->setInitEncryptionKey(ESP_BLE_ENC_KEY_MASK|ESP_BLE_ID_KEY_MASK);
  security->setRespEncryptionKey(ESP_BLE_ENC_KEY_MASK|ESP_BLE_ID_KEY_MASK);
  uint8_t minimumKeySize=16;
  if(esp_ble_gap_set_security_param(ESP_BLE_SM_MIN_KEY_SIZE,&minimumKeySize,sizeof(minimumKeySize))!=ESP_OK){Serial.println("BLE_KEY_SIZE_POLICY_UNAVAILABLE");return;}
  uint8_t strictAuth=ESP_BLE_ONLY_ACCEPT_SPECIFIED_AUTH_ENABLE;
  if(esp_ble_gap_set_security_param(ESP_BLE_SM_ONLY_ACCEPT_SPECIFIED_SEC_AUTH,&strictAuth,sizeof(strictAuth))!=ESP_OK){Serial.println("BLE_AUTH_POLICY_UNAVAILABLE");return;}
  BLEDevice::setCustomGattsHandler([](esp_gatts_cb_event_t event,esp_gatt_if_t interface,esp_ble_gatts_cb_param_t* param){
    if(event==ESP_GATTS_REG_EVT&&param->reg.status==ESP_GATT_OK){std::lock_guard<std::recursive_mutex> lock(connectionGate.mutex);if(admittedGattsInterface==ESP_GATT_IF_NONE)admittedGattsInterface=interface;}
  });
  server=BLEDevice::createServer(); server->setCallbacks(new ServerCallbacks()); BLEService* service=server->createService(SERVICE);
  BLECharacteristic* cap=service->createCharacteristic(CAPABILITIES,BLECharacteristic::PROPERTY_READ);
  cap->setAccessPermissions(ESP_GATT_PERM_READ_ENC_MITM);
  BLECharacteristic* rx=service->createCharacteristic(COMMAND_UUID,BLECharacteristic::PROPERTY_WRITE); rx->setCallbacks(new RxCallbacks());
  rx->setAccessPermissions(ESP_GATT_PERM_WRITE_ENC_MITM);
  tx=service->createCharacteristic(EVENT_UUID,BLECharacteristic::PROPERTY_NOTIFY); tx->setAccessPermissions(ESP_GATT_PERM_READ_ENC_MITM);
  notificationConfiguration=new BLE2902();notificationConfiguration->setAccessPermissions(ESP_GATT_PERM_READ_ENC_MITM|ESP_GATT_PERM_WRITE_ENC_MITM);tx->addDescriptor(notificationConfiguration);
  JsonDocument capabilities;
  capabilities["protocol_version"]=1; capabilities["encodings"].to<JsonArray>().add(1); capabilities["max_logical_bytes"]=8192; capabilities["max_att_bytes"]=20;
  capabilities["source"]="prototype_sensor";capabilities["protocol_id"]="otgd_signed_reader_v1";
  capabilities["device_id"]=deviceId;capabilities["boot_id"]=bootId;capabilities["key_id"]=signer.keyId();
  capabilities["hardware_revision"]=signer.hardware();capabilities["firmware_version"]=signer.firmware();
  JsonArray channels=capabilities["channels"].to<JsonArray>();for(const char* channel:{"ppg","ecg","saliva","alcohol"}) if(otgdAcquisitionAvailable(channel)) channels.add(channel);
  capabilities["timestamp_resolution_ms"]=1;
  std::string json; serializeJson(capabilities,json); if(json.size()>512) { Serial.println("CAPABILITIES_TOO_LARGE"); return; } cap->setValue(json);
  service->start(); BLEAdvertising* advertising=BLEDevice::getAdvertising(); advertising->addServiceUUID(SERVICE); advertising->setScanResponse(true); advertising->start();
  Serial.println("OTGD research reader ready. Device trust and actual sensing qualification remain independent.");
}
void loop() {
  if(!rxQueue || !server || !tx) { delay(20); return; }
  if(linkChanged.exchange(false)) {
    capture.active=false; stopAcquisition(); startNonce.clear(); receiver.reset();
    for(auto& old:journal) {old.responses.clear();}cachedBytes=0; outgoing.clear(); queuedBytes=0; handlingEpoch=connectionGate.epoch(); currentSession.clear(); sessions.clear();
    if(!connectionGate.connected()) BLEDevice::startAdvertising();
    // Replay journal and physical boot ID survive reconnect. Restart the board on journal exhaustion.
  }
  if(rxOverflow.exchange(false)) abortLink("RX_QUEUE_OVERFLOW");
  RxFrame frame{}; int drained=0;
  while(drained++<64 && xQueueReceive(rxQueue,&frame,0)==pdTRUE) {
    if(!connectionGate.connected() || frame.epoch!=handlingEpoch) continue;
    const ReceiveResult result=receiver.push(frame.bytes,frame.size,clockMs());
    if(result==ReceiveResult::Error) { abortLink(receiver.error()); break; }
    if(result==ReceiveResult::Complete) process(std::string(reinterpret_cast<const char*>(receiver.jsonData()),receiver.jsonSize()),receiver.startedAt());
  }
  if(connectionGate.connected()) { if(receiver.expire(clockMs())) abortLink(receiver.error()); else { finishCapture(); drainTx(); } }
  delay(1);
}
