#pragma once
#include <algorithm>
#include <cstdint>

namespace otgd_reader {
struct SparkFunPlan {
  uint32_t durationMs=0,endGuardMs=0,pollMs=0,warmupMs=0,maxNoDataMs=0;
  uint16_t minimumValid=0,minimumBpm=0,maximumBpm=0;
  uint8_t minimumConfidence=0,mode=0;
  bool valid()const {
    return durationMs>=3000&&durationMs<=60000&&endGuardMs>=100&&endGuardMs<=500&&
      pollMs>=50&&pollMs<=1000&&warmupMs>=1000&&warmupMs<=10000&&
      maxNoDataMs>=pollMs&&maxNoDataMs<=5000&&minimumValid>=1&&minimumValid<=256&&
      minimumConfidence<=100&&(mode==1||mode==2)&&minimumBpm>=1&&maximumBpm<=300&&minimumBpm<maximumBpm&&
      durationMs>10+1000+warmupMs+endGuardMs+250;
  }
};
struct SparkFunObservation {
  uint64_t sequence=0,receivedUs=0;
  uint32_t irCount=0,redCount=0;
  uint16_t bpm=0;
  uint8_t confidence=0,status=0;
  int8_t extendedStatus=0;
};
enum class SparkFunStage {Idle,ResetLow,Boot,Configure,Warmup,Sampling,Ended};
/** Actual-used bounded aggregate. No waveform or substituted previous sample is
 * retained: only the last actual FIFO observation and explicit counters remain.
 * Times are host receive observations, never asserted sensor sample onsets.
 */
class SparkFunCapture {
  SparkFunPlan plan_{};
  SparkFunStage stage_=SparkFunStage::Idle;
  uint64_t start_=0,end_=0,stageDue_=0,nextPoll_=0,lastData_=0;
  uint32_t observed_=0,valid_=0,invalid_=0,missedPolls_=0,emptyPolls_=0;
  uint8_t backlogPeak_=0;
  bool ioError_=false,contactLost_=false,stale_=false,overrun_=false,canceled_=false;
  SparkFunObservation last_{};
public:
  bool begin(const SparkFunPlan& plan,uint64_t now) {
    if(active()||!plan.valid())return false;
    *this=SparkFunCapture{};plan_=plan;start_=now;stage_=SparkFunStage::ResetLow;stageDue_=now+10000;
    return true;
  }
  bool active()const{return stage_!=SparkFunStage::Idle&&stage_!=SparkFunStage::Ended;}
  SparkFunStage stage()const{return stage_;}
  uint64_t start()const{return start_;} uint64_t end()const{return end_;}
  uint64_t stopAt()const{return start_+uint64_t(plan_.durationMs-plan_.endGuardMs)*1000;}
  bool canIo(uint64_t now,uint64_t worstUs)const{return active()&&now<stopAt()&&worstUs<stopAt()-now;}
  bool stageReady(uint64_t now)const{return active()&&now>=stageDue_;}
  void resetReleased(uint64_t now){if(stage_==SparkFunStage::ResetLow){stage_=SparkFunStage::Boot;stageDue_=now+1000000;}}
  void configuring(){if(stage_==SparkFunStage::Boot)stage_=SparkFunStage::Configure;}
  void configured(uint64_t now){if(stage_==SparkFunStage::Configure){stage_=SparkFunStage::Warmup;stageDue_=now+uint64_t(plan_.warmupMs)*1000;}}
  bool pollDue(uint64_t now) {
    if(stage_==SparkFunStage::Warmup&&now>=stageDue_){stage_=SparkFunStage::Sampling;nextPoll_=now;lastData_=now;}
    if(stage_!=SparkFunStage::Sampling||now<nextPoll_)return false;
    const uint64_t period=uint64_t(plan_.pollMs)*1000;
    const uint64_t missed=(now-nextPoll_)/period;
    missedPolls_+=uint32_t(missed);nextPoll_+=(missed+1)*period;
    if(missed)stale_=true;
    return true;
  }
  void empty(){++emptyPolls_;}
  void backlog(uint8_t count){backlogPeak_=std::max(backlogPeak_,count);}
  void observe(SparkFunObservation value,uint64_t afterIo) {
    if(stage_!=SparkFunStage::Sampling)return;
    if(afterIo>=start_+uint64_t(plan_.durationMs)*1000||value.receivedUs>=stopAt()||value.receivedUs<lastData_){overrun_=true;return;}
    value.sequence=observed_++;last_=value;lastData_=value.receivedUs;
    bool accepted=value.status==3&&value.confidence>=plan_.minimumConfidence&&value.confidence<=100&&
      value.bpm>=plan_.minimumBpm&&value.bpm<=plan_.maximumBpm&&value.irCount<=0xffffff&&value.redCount<=0xffffff;
    if(accepted){++valid_;}else{++invalid_;contactLost_|=value.status!=3;}
  }
  bool staleAt(uint64_t now)const{return stage_==SparkFunStage::Sampling&&now>=lastData_&&now-lastData_>uint64_t(plan_.maxNoDataMs)*1000;}
  void ioFailure(){ioError_=true;}
  void markStale(){stale_=true;}
  void finish(uint64_t now,bool canceled=false) {
    if(!active())return;
    overrun_|=now>=start_+uint64_t(plan_.durationMs)*1000;
    stale_|=staleAt(now);canceled_|=canceled;end_=now;stage_=SparkFunStage::Ended;last_.irCount=0;last_.redCount=0;
  }
  bool validSignal()const{return stage_==SparkFunStage::Ended&&!ioError_&&!contactLost_&&!stale_&&!overrun_&&!canceled_&&invalid_==0&&valid_>=plan_.minimumValid;}
  double heartRate()const{return valid_?last_.bpm:0;}
  uint32_t observed()const{return observed_;}uint32_t validSamples()const{return valid_;}uint32_t invalidSamples()const{return invalid_;}
  uint32_t missedPolls()const{return missedPolls_;}uint32_t emptyPolls()const{return emptyPolls_;}uint8_t backlogPeak()const{return backlogPeak_;}
  bool ioError()const{return ioError_;}bool contactLost()const{return contactLost_;}bool stale()const{return stale_;}bool overrun()const{return overrun_;}
  const SparkFunObservation& last()const{return last_;}
};
}
