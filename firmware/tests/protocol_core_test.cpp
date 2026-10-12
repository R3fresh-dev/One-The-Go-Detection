#include "../nano_esp32_ble_simulator/ProtocolCore.h"
#include <cassert>
#include <iostream>

int main() {
  using namespace otgd;
  assert(crc32(reinterpret_cast<const uint8_t*>("123456789"),9)==0xcbf43926);
  for(const std::string text: {"{\"a\":1,\"nested\":[true,false,null,\"\\uD83D\\uDE00\"]}","{\"value\":-12.56e+4}"}) assert(StrictJson(text).valid());
  for(const std::string text: {"{\"a\":1,\"a\":2}","{\"a\":1,\"\\u0061\":2}","{\"x\":NaN}","{\"x\":1e999}","{\"x\":9007199254740992}","{\"x\":01}","{\"x\":\"\\uD800\"}","{\"x\":1,}","[] trailing"}) assert(!StrictJson(text).valid());
  const std::string deep(20,'['); const std::string invalid=deep+"0"+std::string(20,']'); assert(!StrictJson(invalid).valid());
  const std::string domain="{\"domain\":\"OTGD capture grant v1\\u0000\"}";
  assert(!StrictJson(domain).valid());
  assert(StrictJson(domain,true).valid());
  assert(!StrictJson("{\"bad\\u0000key\":1}",true).valid());
  const std::string json="{\"protocol_version\":1,\"payload\":{\"source\":\"simulated\"}}";
  auto stream=logicalStream(json); Reassembler receiver; uint8_t frame[20]; const uint16_t count=uint16_t((stream.size()+7)/8);
  size_t size=frameAt(stream,7,1,frame); assert(receiver.push(frame,size,0)==ReceiveResult::Partial); assert(receiver.push(frame,size,1)==ReceiveResult::Duplicate);
  size_t complete=0;
  for(uint16_t i=0;i<count;i++) { size=frameAt(stream,7,i,frame); if(receiver.push(frame,size,2)==ReceiveResult::Complete) complete++; }
  assert(complete==1); assert(std::string(reinterpret_cast<const char*>(receiver.jsonData()),receiver.jsonSize())==json);
  assert(receiver.push(frame,size,3)==ReceiveResult::Duplicate); frame[12]^=1; assert(receiver.push(frame,size,4)==ReceiveResult::Error);
  assert(std::string(receiver.error())=="CONFLICTING_DUPLICATE_FRAGMENT"); receiver.reset();
  size=frameAt(stream,8,0,frame); assert(receiver.push(frame,size,0)==ReceiveResult::Partial); frame[12]^=1; assert(receiver.push(frame,size,1)==ReceiveResult::Error);
  receiver.reset(); size=frameAt(stream,9,0,frame); receiver.push(frame,size,0); assert(receiver.expire(120001));
  receiver.reset(); size=frameAt(stream,10,0,frame); write16(frame+8,65535); assert(receiver.push(frame,size,0)==ReceiveResult::Error);
  receiver.reset(); stream[20]^=1;
  ReceiveResult last=ReceiveResult::Partial; for(uint16_t i=0;i<count;i++) { size=frameAt(stream,11,i,frame); last=receiver.push(frame,size,i); }
  assert(last==ReceiveResult::Error); assert(std::string(receiver.error())=="CRC_MISMATCH");
  std::cout << "Protocol core: CRC, strict JSON/Unicode/duplicates, bounds, framing, replay fragments and timeout passed\n";
}
