#pragma once
#include <algorithm>
#include <array>
#include <bitset>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

namespace otgd {
constexpr size_t kHeader = 12;
constexpr size_t kAttBytes = 20;
constexpr size_t kCapacity = kAttBytes - kHeader;
constexpr size_t kLogicalLimit = 8192;
constexpr uint64_t kReassemblyMs = 120000;
inline uint16_t read16(const uint8_t* p) { return uint16_t(p[0]) | uint16_t(p[1]) << 8; }
inline uint32_t read32(const uint8_t* p) { return uint32_t(p[0]) | uint32_t(p[1]) << 8 | uint32_t(p[2]) << 16 | uint32_t(p[3]) << 24; }
inline void write16(uint8_t* p, uint16_t v) { p[0] = uint8_t(v); p[1] = uint8_t(v >> 8); }
inline void write32(uint8_t* p, uint32_t v) { for (int i=0;i<4;i++) p[i] = uint8_t(v >> (i*8)); }
inline uint32_t crc32(const uint8_t* data, size_t size) {
  uint32_t crc = 0xffffffff;
  for (size_t i=0;i<size;i++) { crc ^= data[i]; for (int bit=0;bit<8;bit++) crc = (crc >> 1) ^ ((crc & 1) ? 0xedb88320 : 0); }
  return crc ^ 0xffffffff;
}
inline bool validUtf8(const std::string& s) {
  for (size_t i=0;i<s.size();) {
    const uint8_t a = uint8_t(s[i++]); if (a < 128) continue;
    uint32_t cp, minimum; size_t count;
    if (a>=0xc2 && a<=0xdf) { cp=a&31; minimum=128; count=1; }
    else if (a>=0xe0 && a<=0xef) { cp=a&15; minimum=2048; count=2; }
    else if (a>=0xf0 && a<=0xf4) { cp=a&7; minimum=65536; count=3; }
    else return false;
    if (i+count>s.size()) return false;
    for (size_t n=0;n<count;n++) { const uint8_t b=uint8_t(s[i++]); if ((b&0xc0)!=0x80) return false; cp=(cp<<6)|(b&63); }
    if (cp<minimum || cp>0x10ffff || (cp>=0xd800 && cp<=0xdfff)) return false;
  }
  return true;
}

/** Lexical validation before ArduinoJson can discard duplicate keys. No unbounded recursion or key tables. */
class StrictJson {
  const std::string& text_; size_t pos_=0;
  void ws() { while (pos_<text_.size() && (text_[pos_]==' ' || text_[pos_]=='\t' || text_[pos_]=='\r' || text_[pos_]=='\n')) pos_++; }
  bool consume(char c) { ws(); if (pos_>=text_.size() || text_[pos_]!=c) return false; pos_++; return true; }
  bool hex4(uint32_t& out) {
    out=0; if (pos_+4>text_.size()) return false;
    for (int n=0;n<4;n++) { char c=text_[pos_++]; unsigned v; if (c>='0' && c<='9') v=c-'0'; else if(c>='a' && c<='f') v=c-'a'+10; else if(c>='A' && c<='F') v=c-'A'+10; else return false; out=(out<<4)|v; }
    return true;
  }
  void appendCodepoint(std::string& out,uint32_t cp) {
    if(cp<128) out.push_back(char(cp));
    else if(cp<2048) { out.push_back(char(0xc0|(cp>>6))); out.push_back(char(0x80|(cp&63))); }
    else if(cp<65536) { out.push_back(char(0xe0|(cp>>12))); out.push_back(char(0x80|((cp>>6)&63))); out.push_back(char(0x80|(cp&63))); }
    else { out.push_back(char(0xf0|(cp>>18))); out.push_back(char(0x80|((cp>>12)&63))); out.push_back(char(0x80|((cp>>6)&63))); out.push_back(char(0x80|(cp&63))); }
  }
  bool string(std::string& decoded) {
    if (!consume('"')) return false;
    while (pos_<text_.size()) {
      const uint8_t c=uint8_t(text_[pos_++]);
      if(c=='"') return validUtf8(decoded) && decoded.find('\0')==std::string::npos;
      if(c<32) return false;
      if(c!='\\') { decoded.push_back(char(c)); continue; }
      if(pos_==text_.size()) return false;
      switch(text_[pos_++]) {
        case '"': decoded.push_back('"'); break; case '\\': decoded.push_back('\\'); break; case '/': decoded.push_back('/'); break;
        case 'b': decoded.push_back('\b'); break; case 'f': decoded.push_back('\f'); break; case 'n': decoded.push_back('\n'); break; case 'r': decoded.push_back('\r'); break; case 't': decoded.push_back('\t'); break;
        case 'u': { uint32_t cp; if(!hex4(cp)) return false;
          if(cp>=0xd800 && cp<=0xdbff) { if(pos_+2>text_.size() || text_[pos_]!='\\' || text_[pos_+1]!='u') return false; pos_+=2; uint32_t low; if(!hex4(low) || low<0xdc00 || low>0xdfff) return false; cp=0x10000+((cp-0xd800)<<10)+(low-0xdc00); }
          else if(cp>=0xdc00 && cp<=0xdfff) return false;
          appendCodepoint(decoded,cp); break; }
        default: return false;
      }
    }
    return false;
  }
  bool number() {
    const size_t start=pos_; if(pos_<text_.size() && text_[pos_]=='-') pos_++;
    if(pos_>=text_.size()) return false;
    if(text_[pos_]=='0') pos_++;
    else if(text_[pos_]>='1' && text_[pos_]<='9') { while(pos_<text_.size() && text_[pos_]>='0' && text_[pos_]<='9') pos_++; }
    else return false;
    if(pos_<text_.size() && text_[pos_]=='.') { pos_++; const size_t digit=pos_; while(pos_<text_.size() && text_[pos_]>='0' && text_[pos_]<='9') pos_++; if(digit==pos_) return false; }
    if(pos_<text_.size() && (text_[pos_]=='e' || text_[pos_]=='E')) { pos_++; if(pos_<text_.size() && (text_[pos_]=='+' || text_[pos_]=='-')) pos_++; const size_t digit=pos_; while(pos_<text_.size() && text_[pos_]>='0' && text_[pos_]<='9') pos_++; if(digit==pos_) return false; }
    const std::string token=text_.substr(start,pos_-start); const double n=std::strtod(token.c_str(),nullptr);
    return std::isfinite(n) && std::fabs(n)<=9007199254740991.0;
  }
  bool value(size_t depth) {
    if(depth>16) return false;
    ws(); if(pos_>=text_.size()) return false;
    const char c=text_[pos_];
    if(c=='"') { std::string decoded; return string(decoded); }
    if(c=='{') {
      pos_++; ws(); if(pos_<text_.size() && text_[pos_]=='}') { pos_++; return true; }
      std::vector<std::string> keys;
      while(pos_<text_.size()) {
        std::string key; if(!string(key) || key.size()>128 || keys.size()>=32 || std::find(keys.begin(),keys.end(),key)!=keys.end()) return false;
        keys.push_back(key); if(!consume(':') || !value(depth+1)) return false; ws(); if(pos_<text_.size() && text_[pos_]=='}') { pos_++; return true; } if(!consume(',')) return false;
      }
      return false;
    }
    if(c=='[') { pos_++; ws(); if(pos_<text_.size() && text_[pos_]==']') { pos_++; return true; } size_t count=0;
      while(pos_<text_.size()) { if(++count>2048 || !value(depth+1)) return false; ws(); if(pos_<text_.size() && text_[pos_]==']') { pos_++; return true; } if(!consume(',')) return false; } return false; }
    for(const char* literal: {"true","false","null"}) { const size_t len=std::strlen(literal); if(text_.compare(pos_,len,literal)==0) { pos_+=len; return true; } }
    return number();
  }
public:
  explicit StrictJson(const std::string& text):text_(text) {}
  bool valid() { if(text_.size()>kLogicalLimit-4 || !validUtf8(text_)) return false; if(!value(0)) return false; ws(); return pos_==text_.size(); }
};

enum class ReceiveResult { Partial, Complete, Duplicate, Error };
class Reassembler {
  std::array<uint8_t,kLogicalLimit> bytes_{};
  std::array<uint8_t,kLogicalLimit> completedBytes_{};
  std::array<uint16_t,1024> sizes_{};
  std::bitset<1024> received_;
  bool active_=false,haveCompleted_=false; uint32_t id_=0,completedId_=0;
  uint16_t count_=0,completedCount_=0; size_t receivedCount_=0,total_=0,lastSize_=0,completedTotal_=0;
  uint64_t started_=0;
  const char* error_=nullptr;
  ReceiveResult fail(const char* reason) { active_=false; received_.reset(); error_=reason; return ReceiveResult::Error; }
public:
  const char* error() const { return error_ ? error_ : "NONE"; }
  const uint8_t* jsonData() const { return bytes_.data(); }
  size_t jsonSize() const { return total_>=4 ? total_-4 : 0; }
  uint64_t startedAt() const { return started_; }
  void reset() { active_=false; haveCompleted_=false; received_.reset(); error_=nullptr; }
  bool expire(uint64_t now) { if(active_ && (now<started_ || now-started_>kReassemblyMs)) { fail("REASSEMBLY_TIMEOUT"); return true; } return false; }
  ReceiveResult push(const uint8_t* frame,size_t size,uint64_t now) {
    if(expire(now)) return ReceiveResult::Error;
    if(size<kHeader+1 || size>kAttBytes) return fail("FRAGMENT_LENGTH");
    if(frame[0]!=1 || frame[1]!=1) return fail("FRAGMENT_VERSION");
    const uint32_t id=read32(frame+2); const uint16_t index=read16(frame+6),count=read16(frame+8),payload=read16(frame+10);
    if(count==0 || count>1024 || index>=count || payload!=size-kHeader || payload>kCapacity || (index!=count-1 && payload!=kCapacity) || (size_t(count)-1)*kCapacity+1>kLogicalLimit) return fail("FRAGMENT_BOUNDS");
    const size_t offset=size_t(index)*kCapacity;
    if(haveCompleted_ && id==completedId_) {
      const size_t expected=index==completedCount_-1 ? completedTotal_-offset : kCapacity;
      if(count!=completedCount_ || expected!=payload || offset+payload>completedTotal_ || std::memcmp(completedBytes_.data()+offset,frame+kHeader,payload)!=0) return fail("CONFLICTING_DUPLICATE_FRAGMENT");
      return ReceiveResult::Duplicate;
    }
    if(!active_) { active_=true; id_=id; count_=count; receivedCount_=0; total_=0; lastSize_=0; started_=now; received_.reset(); }
    if(id!=id_) return fail("CONCURRENT_TRANSFER");
    if(count!=count_) return fail("FRAGMENT_SEQUENCE");
    if(received_.test(index)) {
      if(sizes_[index]!=payload || std::memcmp(bytes_.data()+offset,frame+kHeader,payload)!=0) return fail("CONFLICTING_DUPLICATE_FRAGMENT");
      return ReceiveResult::Duplicate;
    }
    if(offset+payload>kLogicalLimit || total_+payload>kLogicalLimit) return fail("MESSAGE_TOO_LARGE");
    std::memcpy(bytes_.data()+offset,frame+kHeader,payload); received_.set(index); sizes_[index]=payload; total_+=payload; receivedCount_++;
    if(index==count-1) lastSize_=payload;
    if(receivedCount_!=count) return ReceiveResult::Partial;
    if(total_<6 || total_!=(size_t(count)-1)*kCapacity+lastSize_) return fail("MESSAGE_LENGTH");
    if(crc32(bytes_.data(),total_-4)!=read32(bytes_.data()+total_-4)) return fail("CRC_MISMATCH");
    completedId_=id_; completedCount_=count_; completedTotal_=total_; std::copy_n(bytes_.begin(),total_,completedBytes_.begin());
    haveCompleted_=true; active_=false; return ReceiveResult::Complete;
  }
};
inline std::vector<uint8_t> logicalStream(const std::string& json) {
  if(json.size()+4>kLogicalLimit) return {};
  std::vector<uint8_t> stream(json.begin(),json.end()); stream.resize(json.size()+4); write32(stream.data()+json.size(),crc32(stream.data(),json.size())); return stream;
}
inline size_t frameAt(const std::vector<uint8_t>& stream,uint32_t transfer,uint16_t index,uint8_t* output) {
  if(stream.empty() || stream.size()>kLogicalLimit) return 0;
  const uint16_t count=uint16_t((stream.size()+kCapacity-1)/kCapacity); if(index>=count) return 0;
  const size_t offset=size_t(index)*kCapacity,payload=std::min(kCapacity,stream.size()-offset);
  output[0]=1; output[1]=1; write32(output+2,transfer); write16(output+6,index); write16(output+8,count); write16(output+10,uint16_t(payload));
  std::copy_n(stream.begin()+offset,payload,output+kHeader); return kHeader+payload;
}
}
