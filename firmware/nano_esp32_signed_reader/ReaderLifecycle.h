#pragma once
#include <cstdint>
#include <atomic>
#include <mutex>
#include <limits>
#include <array>
#include <algorithm>
namespace otgd_reader {
inline bool connectionAdmission(bool alreadyConnected,uint8_t pairingFailures){return !alreadyConnected&&pairingFailures<3;}
inline bool sameOrigin(bool connected,uint32_t current,uint32_t origin) {
  return connected && origin!=0 && current==origin;
}
class OriginGate {
  std::atomic<bool> connected_{false};
  std::atomic<uint32_t> epoch_{0};
public:
  std::recursive_mutex mutex;
  bool connected() const{return connected_.load();}
  uint32_t epoch() const{return epoch_.load();}
  bool current(uint32_t origin) const{return sameOrigin(connected(),epoch(),origin);}
  bool transition(bool connect) {
    std::lock_guard<std::recursive_mutex> lock(mutex);
    if(epoch()==std::numeric_limits<uint32_t>::max()){connected_.store(false);return false;}
    epoch_.fetch_add(1);connected_.store(connect);return true;
  }
  template<class Action> void synchronize(Action action) {std::lock_guard<std::recursive_mutex> lock(mutex);action();}
  template<class Action> bool run(uint32_t origin,Action action) {
    std::lock_guard<std::recursive_mutex> lock(mutex);
    if(!current(origin))return false;
    action();return true;
  }
};
// Protected peer state is only mutated/read while OriginGate.mutex is held.
// Authentication never carries across a connection transition or peer address.
class AuthenticatedPeer {
  std::array<uint8_t,6> address_{};
  uint32_t epoch_=0;
  uint16_t connection_=0;
  bool authenticated_=false;
public:
  void connect(uint32_t epoch,uint16_t connection,const uint8_t* address) {
    epoch_=epoch;connection_=connection;std::copy(address,address+6,address_.begin());authenticated_=false;
  }
  bool matches(uint32_t epoch,const uint8_t* address) const {
    return epoch!=0&&epoch_==epoch&&std::equal(address_.begin(),address_.end(),address);
  }
  bool authenticate(uint32_t epoch,const uint8_t* address,bool success,bool secureConnections,bool mitm,bool bonded) {
    if(!matches(epoch,address))return false;
    authenticated_=success&&secureConnections&&mitm&&bonded;return authenticated_;
  }
  bool current(uint32_t epoch) const{return epoch!=0&&epoch_==epoch&&authenticated_;}
  uint16_t connection()const{return connection_;}
  bool writes(uint32_t epoch,uint16_t connection,const uint8_t* address) const {return current(epoch)&&connection_==connection&&matches(epoch,address);}
  bool disconnect(uint16_t connection,const uint8_t* address) {
    if(connection_!=connection||!std::equal(address_.begin(),address_.end(),address))return false;
    authenticated_=false;epoch_=0;return true;
  }
};
enum class ReplayAdmission { Admit, ForeignOrigin, ConflictingContent };
inline ReplayAdmission replayAdmission(uint32_t entryOrigin,uint32_t origin,bool sameContent) {
  if(entryOrigin!=origin)return ReplayAdmission::ForeignOrigin;
  return sameContent?ReplayAdmission::Admit:ReplayAdmission::ConflictingContent;
}
// This decision is independent of transport queue occupancy. Call the driver's
// stop before deferring any terminal response due to TX backpressure.
inline bool acquisitionDeadline(uint64_t now,uint64_t due) {return now>=due;}
}
