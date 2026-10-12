#pragma once
#include <cassert>
#include <cstdint>
#include <deque>
#include <vector>
class TwoWire {
public:
  struct Reply {std::vector<uint8_t> bytes;uint8_t writeError=0;};
  std::deque<Reply> replies;
  std::vector<std::vector<uint8_t>> writes;
  std::vector<uint8_t> outgoing;
  Reply current;
  size_t readIndex=0;
  void beginTransmission(uint8_t address){assert(address==0x55);outgoing.clear();}
  size_t write(uint8_t value){outgoing.push_back(value);return 1;}
  uint8_t endTransmission(){assert(!replies.empty());current=replies.front();replies.pop_front();readIndex=0;writes.push_back(outgoing);return current.writeError;}
  uint8_t requestFrom(uint8_t address,uint8_t){assert(address==0x55);return uint8_t(current.bytes.size());}
  int read(){return readIndex<current.bytes.size()?current.bytes[readIndex++]:-1;}
};
inline TwoWire Wire;
