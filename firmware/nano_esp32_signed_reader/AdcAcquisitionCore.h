#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <deque>
#include <functional>
#include <vector>
namespace otgd_reader {
struct AdcPlan {
  uint32_t durationMs=0,rateHz=0,endGuardMs=0,minPeakMs=0,maxPeakMs=0,minAmplitude=0;
  uint16_t threshold=0;
  bool ecg=false;
  double referenceMv=0,gain=0,offsetMv=0;
  bool valid() const {
    return durationMs>=1000 && durationMs<=120000 && rateHz>=20 && rateHz<=1000 && endGuardMs>=10 && endGuardMs<=100 && endGuardMs<durationMs && minPeakMs>=250 && maxPeakMs<=2000 && minPeakMs<maxPeakMs && minAmplitude>=1 && minAmplitude<=4095 && threshold>=1 && threshold<=4094 && (!ecg || (std::isfinite(referenceMv)&&referenceMv>=500&&referenceMv<=5000&&std::isfinite(gain)&&gain>0&&gain<=100000&&std::isfinite(offsetMv)&&std::fabs(offsetMv)<=5000));
  }
};
struct AdcObservation {uint64_t index,monotonicUs;int32_t value;};
/** Bounded streaming extractor. It consumes only read() results, uses actual
 * observation times, records missed samples explicitly and never fills gaps.
 * No waveform fixture/default physiology is available in this core.
 */
class AdcAcquisition {
  size_t rawLimit_=256;AdcPlan plan_;bool active_=false,ended_=false,contactLost_=false,saturated_=false,queueLost_=false,peakOverflow_=false,intervalOutside_=false;
  bool retainRaw_=false;bool above_=false;uint64_t start_=0,end_=0,next_=0,lastPeak_=0,index_=0,dropped_=0;
  uint16_t low_=4095,high_=0;
  std::deque<AdcObservation> queue_;
  std::vector<double> intervals_;
  void stop(uint64_t now,const std::function<void()>& shutdown){if(active_){active_=false;ended_=true;end_=now;shutdown();}}
public:
  bool begin(const AdcPlan& plan,uint64_t now,bool retainRaw=false,size_t rawLimit=256) {
    if(rawLimit>1024||rawLimit<1||active_||!plan.valid()||now>UINT64_MAX-uint64_t(plan.durationMs)*1000)return false;
    plan_=plan;rawLimit_=rawLimit;retainRaw_=retainRaw;active_=true;ended_=false;contactLost_=false;saturated_=false;queueLost_=false;peakOverflow_=false;intervalOutside_=false;above_=false;start_=now;end_=0;next_=now;lastPeak_=0;index_=0;dropped_=0;low_=4095;high_=0;queue_.clear();intervals_.clear();intervals_.reserve(512);return true;
  }
  void tick(uint64_t now,const std::function<uint16_t()>& read,const std::function<bool()>& contact,const std::function<uint64_t()>& observedTime,const std::function<void()>& shutdown) {
    if(!active_)return;
    const uint64_t stopAt=start_+uint64_t(plan_.durationMs-plan_.endGuardMs)*1000;
    if(now<start_ || now>=stopAt){stop(now,shutdown);return;}
    if(now<next_)return;
    const uint64_t period=1000000/plan_.rateHz,missed=(now-next_)/period;
    if(missed){dropped_+=missed;index_+=missed;next_+=missed*period;}
    if(!contact()){contactLost_=true;stop(now,shutdown);return;}
    const uint16_t raw=read();const uint64_t measured=observedTime();
    // A slow ADC call cannot extend the authorized acquisition; its late result
    // is discarded and the terminal records the actual shutdown observation.
    if(measured<now || measured>=stopAt){stop(measured,shutdown);return;}
    if(raw>4095){saturated_=true;stop(measured,shutdown);return;}
    low_=std::min(low_,raw);high_=std::max(high_,raw);if(raw==0||raw==4095)saturated_=true;
    const bool crossed=raw>=plan_.threshold;
    if(crossed&&!above_ && (!lastPeak_||measured-lastPeak_>=uint64_t(plan_.minPeakMs)*1000)) {
      if(lastPeak_) {const double interval=double(measured-lastPeak_)/1000;if(interval<=plan_.maxPeakMs) {if(intervals_.size()<512)intervals_.push_back(interval);else peakOverflow_=true;}else intervalOutside_=true;}
      lastPeak_=measured;
    }
    above_=crossed;
    const double converted=plan_.ecg?((double(raw)*plan_.referenceMv/4095-plan_.offsetMv)/plan_.gain)*1000:raw;
    if(!std::isfinite(converted)||converted<INT32_MIN||converted>INT32_MAX){saturated_=true;stop(measured,shutdown);return;}
    if(!retainRaw_){}else if(queue_.size()<rawLimit_)queue_.push_back({index_,measured,int32_t(std::lround(converted))});else {queueLost_=true;dropped_++;}
    index_++;next_+=period;
  }
  void cancel(uint64_t now,const std::function<void()>& shutdown){stop(now,shutdown);queue_.clear();intervals_.clear();}
  bool active()const{return active_;}bool ended()const{return ended_;}
  uint64_t start()const{return start_;}uint64_t end()const{return end_;}uint64_t dropped()const{return dropped_;}
  bool overran()const{return ended_&&(end_<start_||end_-start_>uint64_t(plan_.durationMs)*1000);}
  bool validSignal()const{return ended_&&!overran()&&!contactLost_&&!saturated_&&!queueLost_&&!peakOverflow_&&!intervalOutside_&&dropped_==0&&uint32_t(high_-low_)>=plan_.minAmplitude&&intervals_.size()>=2;}
  bool lostContact()const{return contactLost_;}bool saturated()const{return saturated_;}bool queueLost()const{return queueLost_;}
  double heartRate()const {if(!validSignal())return NAN;double sum=0;for(double rr:intervals_)sum+=rr;return 60000*intervals_.size()/sum;}
  double rmssd()const {if(!validSignal()||intervals_.size()<2)return NAN;double sum=0;for(size_t i=1;i<intervals_.size();i++){const double diff=intervals_[i]-intervals_[i-1];sum+=diff*diff;}return std::sqrt(sum/(intervals_.size()-1));}
  std::vector<AdcObservation> take(size_t count=64,bool contiguous=false){std::vector<AdcObservation> out;while(!queue_.empty()&&out.size()<count){if(contiguous&&!out.empty()&&queue_.front().index!=out.back().index+1)break;out.push_back(queue_.front());queue_.pop_front();}return out;}
  size_t queued()const{return queue_.size();}
};
}
