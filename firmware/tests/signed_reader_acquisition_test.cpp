#include "../nano_esp32_signed_reader/AdcAcquisitionCore.h"
#include "../nano_esp32_signed_reader/ReaderLifecycle.h"
#include "../nano_esp32_signed_reader/ReaderTime.h"
#include <cassert>
#include <condition_variable>
#include <iostream>
#include <thread>
using namespace otgd_reader;
static AdcPlan plan(){AdcPlan p;p.durationMs=5000;p.rateHz=100;p.endGuardMs=10;p.minPeakMs=250;p.maxPeakMs=2000;p.minAmplitude=100;p.threshold=2000;p.ecg=true;p.referenceMv=3300;p.gain=1000;p.offsetMv=1650;return p;}
int main(){
  uint64_t micros=0;assert(utcMicros("2026-10-11T01:02:03.123456Z",micros));assert(micros%1000000==123456);
  for(const char* text:{"2026-02-29T00:00:00Z","2026-10-11T00:00:00.1234567Z","2026-10-11T00:00:00+00:00","2026-10-11T00:00:60Z","2026-10-11T00:00:00.Z","2026-10-11T00:00:00Zjunk"})assert(!utcMicros(text,micros));
  assert(nonceWithinSignedLifetime("2026-10-11T00:00:00Z","2026-10-11T00:00:15Z",1000,15999));
  assert(!nonceWithinSignedLifetime("2026-10-11T00:00:00Z","2026-10-11T00:00:15Z",1000,16000));
  assert(!nonceWithinSignedLifetime("2026-10-11T00:00:00Z","2026-10-11T00:00:15Z",1000,16001));
  assert(!nonceWithinSignedLifetime("2026-10-11T00:00:01Z","2026-10-11T00:00:00Z",1000,1000));
  assert(!nonceWithinSignedLifetime("bad","2026-10-11T00:00:15Z",1000,1000));
  assert(!nonceWithinSignedLifetime("2026-10-11T00:00:00Z","2026-10-11T00:01:01Z",1000,1000));
  AdcAcquisition core;auto p=plan();assert(core.begin(p,1000000));int reads=0,stops=0;uint64_t observed=0;
  for(uint64_t t=1000000;t<=6000000;t+=10000){observed=t+50;core.tick(t,[&]{reads++;return uint16_t((t-1000000)%800000<10000?2500:1500);},[]{return true;},[&]{return observed;},[&]{stops++;});}
  assert(core.ended()&&!core.active()&&stops==1&&reads==499&&core.queued()==0&&core.validSignal());assert(std::fabs(core.heartRate()-75)<1e-8);assert(core.rmssd()==0);assert(core.end()==5990000);
  // No sample/read callback occurs at or beyond the bounded stop, even when
  // publication is congested. Terminal projection may wait; hardware may not.
  core.tick(10000000,[&]{reads++;return uint16_t(1500);},[]{return true;},[]{return uint64_t(10000000);},[&]{stops++;});assert(reads==499&&stops==1);
  AdcAcquisition absent;assert(absent.begin(p,1000000));absent.tick(1000000,[&]{reads++;return uint16_t(2000);},[]{return false;},[]{return uint64_t(1000000);},[&]{stops++;});assert(absent.ended()&&absent.lostContact()&&!absent.validSignal()&&reads==499);
  AdcAcquisition late;assert(late.begin(p,1000000));late.tick(1000000,[]{return uint16_t(2000);},[]{return true;},[]{return uint64_t(7000000);},[]{});assert(late.ended()&&late.overran()&&!late.validSignal());
  AdcAcquisition dropped;assert(dropped.begin(p,1000000,true));dropped.tick(1000000,[]{return uint16_t(1500);},[]{return true;},[]{return uint64_t(1000050);},[]{});dropped.tick(1030000,[]{return uint16_t(2500);},[]{return true;},[]{return uint64_t(1030050);},[]{});const auto chunk=dropped.take();assert(chunk.size()==2&&chunk[0].index==0&&chunk[1].index==3&&dropped.dropped()==2&&chunk[1].value!=2500);
  AdcAcquisition excluded;assert(excluded.begin(p,1000000));for(uint64_t t=1000000;t<=6000000;t+=10000){const auto rel=t-1000000;excluded.tick(t,[&]{return uint16_t(rel==0||rel==800000||rel==1600000||rel==4600000?2500:1500);},[]{return true;},[&]{return t+50;},[]{});}assert(excluded.ended()&&!excluded.validSignal()&&std::isnan(excluded.heartRate()));
  AdcAcquisition overflow;assert(overflow.begin(p,1000000,true));for(uint64_t t=1000000;t<4000000;t+=10000)overflow.tick(t,[]{return uint16_t(1500);},[]{return true;},[&]{return t+50;},[]{});assert(overflow.queued()==256&&overflow.queueLost()&&!overflow.validSignal());overflow.cancel(4000000,[]{});assert(overflow.queued()==0&&!overflow.active());
  for(auto bad:{0,1001}){auto invalid=p;invalid.rateHz=uint32_t(bad);AdcAcquisition a;assert(!a.begin(invalid,1000000));}
  auto invalid=p;invalid.gain=0;assert(!invalid.valid());invalid=p;invalid.referenceMv=NAN;assert(!invalid.valid());invalid=p;invalid.endGuardMs=0;assert(!invalid.valid());
  OriginGate gate;assert(gate.transition(true));const auto old=gate.epoch();int deliveries=0;std::mutex barrier;std::condition_variable changed;bool checked=false,attempting=false;
  std::thread replacing([&]{std::unique_lock<std::mutex> lock(barrier);changed.wait(lock,[&]{return checked;});attempting=true;changed.notify_all();lock.unlock();gate.transition(false);gate.transition(true);});
  assert(gate.run(old,[&]{std::unique_lock<std::mutex> lock(barrier);checked=true;changed.notify_all();changed.wait(lock,[&]{return attempting;});lock.unlock();assert(gate.current(old));deliveries++;}));replacing.join();assert(deliveries==1&&!gate.current(old));assert(!gate.run(old,[&]{deliveries++;}));assert(deliveries==1);
  assert(replayAdmission(old,gate.epoch(),true)==ReplayAdmission::ForeignOrigin);assert(replayAdmission(old,old,false)==ReplayAdmission::ConflictingContent);
  AdcAcquisition simultaneous;assert(simultaneous.begin(p,1000000,true));int concurrentStops=0;
  std::thread disconnect([&]{gate.synchronize([&]{simultaneous.cancel(1010000,[&]{concurrentStops++;});});});
  gate.synchronize([&]{simultaneous.cancel(1010000,[&]{concurrentStops++;});});disconnect.join();assert(concurrentStops==1&&!simultaneous.active()&&simultaneous.queued()==0);
  assert(connectionAdmission(false,0)&&!connectionAdmission(true,0)&&!connectionAdmission(false,3));
  const uint8_t peerA[6]={1,2,3,4,5,6},peerB[6]={6,5,4,3,2,1};AuthenticatedPeer secure;
  secure.connect(10,7,peerA);assert(!secure.current(10));
  assert(!secure.authenticate(10,peerA,true,false,true,true));assert(!secure.authenticate(10,peerA,true,true,false,true));assert(!secure.authenticate(10,peerA,true,true,true,false));assert(!secure.authenticate(10,peerB,true,true,true,true));
  assert(secure.authenticate(10,peerA,true,true,true,true));assert(secure.writes(10,7,peerA));assert(!secure.writes(10,8,peerA)&&!secure.writes(10,7,peerB));
  secure.connect(11,8,peerB);assert(!secure.current(11)&&!secure.current(10));assert(!secure.authenticate(10,peerA,true,true,true,true));assert(!secure.disconnect(7,peerA));assert(secure.authenticate(11,peerB,true,true,true,true));assert(secure.disconnect(8,peerB)&&!secure.current(11));
  // RX's identity check and insertion use the same mutex as a transition.
  gate.transition(true);const auto rxOrigin=gate.epoch();int rxQueued=0;bool rxChecked=false,transitionPending=false;
  std::thread rxReplacement([&]{std::unique_lock<std::mutex> lock(barrier);changed.wait(lock,[&]{return rxChecked;});transitionPending=true;changed.notify_all();lock.unlock();gate.transition(false);gate.transition(true);});
  gate.run(rxOrigin,[&]{std::unique_lock<std::mutex> lock(barrier);rxChecked=true;changed.notify_all();changed.wait(lock,[&]{return transitionPending;});lock.unlock();assert(gate.current(rxOrigin));rxQueued++;});rxReplacement.join();assert(rxQueued==1&&!gate.current(rxOrigin));
  assert(acquisitionDeadline(100,100)&&!acquisitionDeadline(99,100));
  std::cout<<"Actual ADC scheduler/extractor: contact, timestamps, calibration, bounds, drops, cutoff; serialized origin transition and expiry negatives passed\n";
}
