#pragma once
#include <ArduinoJson.h>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include "ryu/ryu.h"
#include "ProtocolCore.h"

namespace otgd_reader {
// This version has fixed ASCII schema keys. Values retain UTF-8 JSON strings.
// Ryu supplies shortest round-trip IEEE754 digits; formatting follows the
// ECMAScript/JCS decimal exponent thresholds, with negative zero normalized.
inline bool append(std::string& out,const std::string& value,size_t limit) {
  if(out.size()>limit || value.size()>limit-out.size()) return false;
  out+=value; return true;
}
inline bool quoted(const std::string& text,std::string& out,size_t limit) {
  if(!otgd::validUtf8(text) || !append(out,"\"",limit)) return false;
  const char* hex="0123456789abcdef";
  for(uint8_t c:text) {
    std::string escaped;
    switch(c) {
      case '"':escaped="\\\"";break;case '\\':escaped="\\\\";break;
      case '\b':escaped="\\b";break;case '\t':escaped="\\t";break;
      case '\n':escaped="\\n";break;case '\f':escaped="\\f";break;case '\r':escaped="\\r";break;
      default:if(c<32) {escaped="\\u00";escaped+=hex[c>>4];escaped+=hex[c&15];}else escaped.assign(1,char(c));
    }
    if(!append(out,escaped,limit)) return false;
  }
  return append(out,"\"",limit);
}
inline bool number(double value,std::string& out,size_t limit) {
  if(!std::isfinite(value) || std::fabs(value)>9007199254740991.0) return false;
  if(value==0) return append(out,"0",limit);
  char buffer[32]; const int length=d2s_buffered_n(value,buffer);
  const std::string rendered(buffer,size_t(length));
  const size_t exponentAt=rendered.find('E'); if(exponentAt==std::string::npos) return false;
  const int exponent=std::stoi(rendered.substr(exponentAt+1));
  std::string digits=rendered.substr(rendered[0]=='-'?1:0,exponentAt-(rendered[0]=='-'?1:0));
  digits.erase(std::remove(digits.begin(),digits.end(),'.'),digits.end());
  std::string result=rendered[0]=='-'?"-":"";
  if(exponent>=21 || exponent<=-7) {
    result+=digits.substr(0,1); if(digits.size()>1) result+="."+digits.substr(1);
    result+="e"; if(exponent>=0) result+="+"; result+=std::to_string(exponent);
  } else {
    const int point=exponent+1;
    if(point<=0) result+="0."+std::string(size_t(-point),'0')+digits;
    else if(size_t(point)>=digits.size()) result+=digits+std::string(size_t(point)-digits.size(),'0');
    else result+=digits.substr(0,size_t(point))+"."+digits.substr(size_t(point));
  }
  return append(out,result,limit);
}
inline bool canonicalValue(JsonVariantConst value,std::string& out,size_t limit,size_t depth=0) {
  if(depth>16 || out.size()>limit) return false;
  if(value.isNull()) return append(out,"null",limit);
  if(value.is<bool>()) return append(out,value.as<bool>()?"true":"false",limit);
  if(value.is<const char*>()) { const JsonString text=value.as<JsonString>(); if(text.size()!=std::strlen(text.c_str())) return false; return quoted(std::string(text.c_str(),text.size()),out,limit); }
  if(value.is<JsonObjectConst>()) {
    std::vector<JsonPairConst> pairs;
    for(JsonPairConst pair:value.as<JsonObjectConst>()) {
      const char* key=pair.key().c_str(); const size_t bytes=std::strlen(key);
      if(bytes>128 || pairs.size()>=32) return false;
      for(size_t i=0;i<bytes;i++) if(uint8_t(key[i])>=128) return false;
      pairs.push_back(pair);
    }
    std::sort(pairs.begin(),pairs.end(),[](const JsonPairConst& a,const JsonPairConst& b){return std::strcmp(a.key().c_str(),b.key().c_str())<0;});
    if(!append(out,"{",limit)) return false;
    for(size_t i=0;i<pairs.size();i++) {
      if(i && !append(out,",",limit)) return false;
      if(!quoted(pairs[i].key().c_str(),out,limit) || !append(out,":",limit) || !canonicalValue(pairs[i].value(),out,limit,depth+1)) return false;
    }
    return append(out,"}",limit);
  }
  if(value.is<JsonArrayConst>()) {
    if(value.size()>2048 || !append(out,"[",limit)) return false;
    size_t index=0;
    for(JsonVariantConst item:value.as<JsonArrayConst>()) {
      if(index++ && !append(out,",",limit)) return false;
      if(!canonicalValue(item,out,limit,depth+1)) return false;
    }
    return append(out,"]",limit);
  }
  if(value.is<double>() || value.is<int64_t>() || value.is<uint64_t>()) return number(value.as<double>(),out,limit);
  return false;
}
inline bool canonical(JsonVariantConst value,std::string& out,size_t limit=8188) {
  out.clear(); return canonicalValue(value,out,limit);
}
}
