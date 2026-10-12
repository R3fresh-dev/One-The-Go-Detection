#include <cassert>
#include <iostream>
#include <fstream>
#include "../nano_esp32_signed_reader/SparkFunPpgEvidence.h"
#include "../nano_esp32_signed_reader/CanonicalJson.h"
#include "../nano_esp32_signed_reader/SparkFunPpgCore.h"
#include "../nano_esp32_signed_reader/vendor/sparkfun/SparkFun_Bio_Sensor_Hub_Library.h"
using namespace otgd_reader;
static void configure(SparkFun_Bio_Sensor_Hub& hub,uint8_t mode) {
  Wire.replies={{{0}},{{0}},{{0}},{{0}},{{0,4}}};
  fakeDelayMs=0;assert(hub.configSensorBpm(mode)==0);assert(hub.otgdLastIoStatus()==0);
  assert(fakeDelayMs==96); // Four vendor commands/averaging;1000ms moved to core.
  assert(Wire.writes[Wire.writes.size()-5]==std::vector<uint8_t>({0x10,0,3}));
  assert(Wire.writes[Wire.writes.size()-4]==std::vector<uint8_t>({0x10,1,1}));
  assert(Wire.writes[Wire.writes.size()-3]==std::vector<uint8_t>({0x44,3,1}));
  assert(Wire.writes[Wire.writes.size()-2]==std::vector<uint8_t>({0x52,2,mode}));
  assert(Wire.writes.back()==std::vector<uint8_t>({0x51,0,3}));
}
static std::vector<uint8_t> record(uint8_t mode) {
  std::vector<uint8_t> bytes={0,1,0x23,0x45,0x65,0x43,0x21,0,0,0,0,0,0,0x02,0xdf,95,3,0xe8,3};
  if(mode==2)bytes.insert(bytes.end(),{0,10,0,0,0});
  return bytes;
}
int main(int argc,char**argv){
  SparkFun_Bio_Sensor_Hub hub;hub.otgdAttach(Wire,5,6);
  Wire.replies={{{0,0}}};assert(hub.otgdApplicationMode()==0&&hub.otgdLastIoStatus()==0);
  Wire.replies={{{0,10,1,0}}};auto version=hub.readSensorHubVersion();assert(version.major==10&&version.minor==1&&version.revision==0);
  for(uint8_t bits=0;bits<8;++bits){Wire.replies={{{0,uint8_t(bits<<2)}}};const uint16_t rates[8]={50,100,200,400,800,1000,1600,3200};assert(hub.readSampleRate()==rates[bits]&&hub.otgdLastIoStatus()==0);assert(Wire.writes.back()==std::vector<uint8_t>({0x41,3,0x0a}));}
  Wire.replies={{{0}}};hub.readSampleRate();assert(hub.otgdLastIoStatus()==ERR_UNKNOWN);
  for(uint8_t mode:{1,2}){
    configure(hub,mode);Wire.replies={{record(mode)}};auto data=hub.readSensorBpm();
    assert(hub.otgdLastIoStatus()==0&&data.irLed==0x12345&&data.redLed==0x654321&&data.heartRate==73&&data.confidence==95&&data.status==3);
    Wire.replies={{{0,1}}};data=hub.readSensorBpm();assert(hub.otgdLastIoStatus()==ERR_UNKNOWN&&data.heartRate==0&&data.irLed==0&&data.confidence==0&&data.status==0);
    Wire.replies={{{1}}};data=hub.readSensorBpm();assert(hub.otgdLastIoStatus()==ERR_UNKNOWN&&data.heartRate==0);
    Wire.replies={{{},4}};data=hub.readSensorBpm();assert(hub.otgdLastIoStatus()==ERR_UNKNOWN&&data.heartRate==0);
  }
  Wire.replies={{{0,0}}};assert(hub.numSamplesOutFifo()==0&&hub.otgdLastIoStatus()==0); // No fresh record; never reuse old HR.
  Wire.replies={{{0,10,1}}};version=hub.readSensorHubVersion();assert(hub.otgdLastIoStatus()==ERR_UNKNOWN&&version.major==0);
  SparkFunPlan plan;plan.durationMs=5000;plan.endGuardMs=100;plan.pollMs=50;plan.warmupMs=1000;plan.maxNoDataMs=1000;plan.minimumValid=2;plan.minimumConfidence=90;plan.minimumBpm=40;plan.maximumBpm=200;plan.mode=1;assert(plan.valid());
  SparkFunCapture capture;assert(capture.begin(plan,100));assert(!capture.stageReady(10099));assert(capture.stageReady(10100));capture.resetReleased(10100);assert(!capture.stageReady(1010099));assert(capture.stageReady(1010100));capture.configuring();capture.configured(1100100);assert(!capture.pollDue(2100099));assert(capture.pollDue(2100100));
  SparkFunObservation observation;observation.receivedUs=2100200;observation.irCount=0x12345;observation.redCount=0x654321;observation.bpm=73;observation.confidence=95;observation.status=3;capture.observe(observation,observation.receivedUs);observation.receivedUs+=50000;observation.bpm=75;capture.observe(observation,observation.receivedUs);
  capture.finish(2160100);assert(capture.validSignal()&&capture.heartRate()==75&&capture.observed()==2&&capture.validSamples()==2&&capture.last().sequence==1&&capture.last().irCount==0&&capture.last().redCount==0);
  JsonDocument payload;sparkFunResult(payload,capture,plan,"sparkfun-host-fixture",1767225600000ULL,true,{10,1,0},50);
  assert(payload["projection"]["heart_rate_bpm"]==75&&payload["projection"]["ecg_rmssd_ms"].isNull());
  assert(payload["ppg_evidence"]["configured_sensor_rate_hz"]==50&&payload["ppg_evidence"]["actual_sensor_cadence_hz"].isNull()&&payload["ppg_evidence"]["sensor_dropped_samples"].isNull());
  const JsonObject observationEvidence=payload["ppg_evidence"]["last_observation"];for(JsonPair field:observationEvidence){assert(std::strcmp(field.key().c_str(),"ir_count")!=0&&std::strcmp(field.key().c_str(),"red_count")!=0);}
  std::string output;assert(canonical(payload.as<JsonVariantConst>(),output,6000));if(argc>1){std::ofstream file(argv[1]);file<<output<<"\n";assert(file.good());}
  auto contact=capture;assert(contact.begin(plan,0));contact.resetReleased(10000);contact.configuring();contact.configured(1010000);assert(contact.pollDue(2010000));observation.receivedUs=2010001;observation.status=2;contact.observe(observation,observation.receivedUs);contact.finish(2010010);assert(!contact.validSignal()&&contact.contactLost()&&contact.invalidSamples()==1);
  auto stale=contact;assert(stale.begin(plan,0));stale.resetReleased(10000);stale.configuring();stale.configured(1010000);assert(stale.pollDue(2010000));stale.empty();assert(stale.staleAt(3010001));stale.finish(3010001);assert(!stale.validSignal()&&stale.stale()&&stale.observed()==0);
  auto late=stale;assert(late.begin(plan,0));late.resetReleased(10000);late.configuring();late.configured(1010000);assert(late.pollDue(2010000));observation.status=3;observation.receivedUs=late.stopAt();late.observe(observation,observation.receivedUs);late.finish(5000000);assert(!late.validSignal()&&late.overrun()&&late.observed()==0);
  JsonDocument invalid;sparkFunResult(invalid,stale,plan,"sparkfun-host-fixture",1767225600000ULL,false,{},0);
  assert(invalid["projection"]["status"]=="invalid"&&invalid["projection"]["heart_rate_bpm"].isNull()&&invalid["ppg_evidence"]["hub_firmware"].isNull()&&invalid["ppg_evidence"]["last_observation"].isNull());
  auto canceled=late;assert(canceled.begin(plan,0));canceled.finish(500,true);assert(!canceled.validSignal()&&!canceled.active());auto ended=canceled.end();canceled.finish(1000);assert(canceled.end()==ended);
  std::cout<<"Actual pinned SDK I2C bytes, mode1/2 decode, short/error/stale read and production-core deadlines/contact/quality/cancel checks passed\n";
}
