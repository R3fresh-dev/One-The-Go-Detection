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
static SparkFunCapture sampling(const SparkFunPlan& plan) {
  SparkFunCapture capture;assert(capture.begin(plan,0));capture.resetReleased(10000);
  capture.configuring();capture.configured(1010000);assert(capture.pollDue(2010000));return capture;
}
static SparkFunObservation received(const bioData& data,uint64_t when) {
  SparkFunObservation value;value.receivedUs=when;value.irCount=data.irLed;value.redCount=data.redLed;
  value.bpm=data.heartRate;value.confidence=data.confidence;value.status=data.status;value.extendedStatus=data.extStatus;return value;
}
static void freshFifoAcceptance(SparkFun_Bio_Sensor_Hub& hub,SparkFunPlan plan) {
  for(uint8_t mode:{1,2}) {
    plan.mode=mode;configure(hub,mode);auto identical=sampling(plan);
    Wire.replies={{{0,2}},{record(mode)},{record(mode)}};
    assert(hub.numSamplesOutFifo()==2&&hub.otgdLastIoStatus()==0);identical.backlog(2);
    const auto first=hub.readSensorBpm();assert(hub.otgdLastIoStatus()==0);
    const auto second=hub.readSensorBpm();assert(hub.otgdLastIoStatus()==0&&Wire.replies.empty());
    assert(first.heartRate==73&&second.heartRate==73&&first.confidence==95&&second.confidence==95&&first.status==3&&second.status==3);
    identical.observe(received(first,2010001),2010001);identical.observe(received(second,2010002),2010002);
    identical.finish(2010010);assert(identical.validSignal()&&identical.observed()==2&&identical.validSamples()==2&&identical.invalidSamples()==0);
    JsonDocument same;sparkFunResult(same,identical,plan,"fictional-identical-fifo",1767225600000ULL,true,{10,1,0},50);
    assert(same["projection"]["heart_rate_bpm"]==73&&same["ppg_evidence"]["last_observation"]["sequence"]==1);
    assert(same["ppg_evidence"]["last_observation"]["host_received_monotonic_us"]==2010002);
    assert(same["ppg_evidence"]["sample_timestamp_source"]=="host_i2c_receive_unqualified_sensor_time");
    assert(same["ppg_evidence"]["actual_sensor_cadence_hz"].isNull()&&same["ppg_evidence"]["sensor_dropped_samples"].isNull());

    auto mixed=sampling(plan);auto poor=record(mode);poor[13]=0x04;poor[14]=0xb0;poor[18]=2; //120 bpm, poor contact.
    Wire.replies={{{0,3}},{record(mode)},{record(mode)},{poor}};assert(hub.numSamplesOutFifo()==3&&hub.otgdLastIoStatus()==0);
    const auto good=hub.readSensorBpm();assert(hub.otgdLastIoStatus()==0);mixed.observe(received(good,2010001),2010001);
    const auto alsoGood=hub.readSensorBpm();assert(hub.otgdLastIoStatus()==0);mixed.observe(received(alsoGood,2010002),2010002);
    const auto bad=hub.readSensorBpm();assert(hub.otgdLastIoStatus()==0&&bad.heartRate==120&&bad.status==2);mixed.observe(received(bad,2010003),2010003);
    mixed.finish(2010010);assert(mixed.observed()==3&&mixed.validSamples()==2&&mixed.invalidSamples()==1&&mixed.observed()==mixed.validSamples()+mixed.invalidSamples());
    JsonDocument quality;sparkFunResult(quality,mixed,plan,"fictional-mixed-fifo",1767225600000ULL,true,{10,1,0},50);
    assert(!mixed.validSignal()&&mixed.contactLost()&&quality["projection"]["status"]=="invalid"&&quality["projection"]["heart_rate_bpm"].isNull());
    assert(quality["ppg_evidence"]["observed_samples"]==3&&quality["ppg_evidence"]["valid_samples"]==2&&quality["ppg_evidence"]["invalid_samples"]==1);
    assert(quality["ppg_evidence"]["last_observation"]["heart_rate_bpm"]==120); //Truthful rejected evidence, never a valid summary.

    auto empty=sampling(plan);Wire.replies={{record(mode)}};const auto prior=hub.readSensorBpm();assert(hub.otgdLastIoStatus()==0);
    empty.observe(received(prior,2010001),2010001);Wire.replies={{{0,0}}};assert(hub.numSamplesOutFifo()==0&&hub.otgdLastIoStatus()==0);empty.empty();
    assert(empty.observed()==1&&empty.validSamples()==1&&empty.invalidSamples()==0&&empty.emptyPolls()==1&&empty.last().sequence==0&&empty.last().receivedUs==2010001);
    auto insufficient=empty;insufficient.finish(2060000);JsonDocument shortRun;sparkFunResult(shortRun,insufficient,plan,"fictional-empty-fifo",1767225600000ULL,true,{10,1,0},50);
    assert(!insufficient.validSignal()&&!insufficient.stale()&&shortRun["projection"]["heart_rate_bpm"].isNull());
    // A second genuinely fresh record reaches the valid-count threshold; the
    // following empty interval must still invalidate on the exact stale bound.
    Wire.replies={{record(mode)}};const auto later=hub.readSensorBpm();assert(hub.otgdLastIoStatus()==0);empty.observe(received(later,2060001),2060001);
    Wire.replies={{{0,0}}};assert(hub.numSamplesOutFifo()==0&&hub.otgdLastIoStatus()==0);empty.empty();
    assert(empty.observed()==2&&empty.validSamples()==2&&empty.emptyPolls()==2&&!empty.staleAt(3060001)&&empty.staleAt(3060002));empty.finish(3060002);
    JsonDocument gap;sparkFunResult(gap,empty,plan,"fictional-stale-fifo",1767225600000ULL,true,{10,1,0},50);
    assert(empty.stale()&&empty.observed()==2&&empty.validSamples()==2&&gap["projection"]["heart_rate_bpm"].isNull());
    assert(gap["ppg_evidence"]["last_observation"]["host_received_monotonic_us"]==2060001&&gap["ppg_evidence"]["fifo_empty_polls"]==2);

    auto truncated=sampling(plan);Wire.replies={{record(mode)}};const auto beforeFailure=hub.readSensorBpm();assert(hub.otgdLastIoStatus()==0);
    truncated.observe(received(beforeFailure,2010001),2010001);Wire.replies={{record(mode)}};const auto enough=hub.readSensorBpm();assert(hub.otgdLastIoStatus()==0);truncated.observe(received(enough,2010002),2010002);
    Wire.replies={{{0,1}}};const auto failed=hub.readSensorBpm();
    assert(hub.otgdLastIoStatus()==ERR_UNKNOWN&&failed.heartRate==0&&failed.confidence==0&&failed.status==0&&failed.irLed==0&&failed.redLed==0);
    truncated.ioFailure();truncated.finish(2060000);JsonDocument failure;sparkFunResult(failure,truncated,plan,"fictional-truncated-fifo",1767225600000ULL,true,{10,1,0},50);
    assert(truncated.ioError()&&!truncated.validSignal()&&truncated.observed()==2&&truncated.validSamples()==2&&truncated.invalidSamples()==0);
    assert(failure["projection"]["status"]=="invalid"&&failure["projection"]["heart_rate_bpm"].isNull()&&failure["ppg_evidence"]["last_observation"]["sequence"]==1);
    assert(Wire.replies.empty());
  }
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
  freshFifoAcceptance(hub,plan);
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
