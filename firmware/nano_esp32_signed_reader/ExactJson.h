#pragma once
#include <ArduinoJson.h>
#include <cstdlib>
#include <string>
#include "ProtocolCore.h"

namespace otgd_reader {
/** ArduinoJson optimizes small decimal inputs into float32 even with USE_DOUBLE.
 * Restore decimal tokens as IEEE754 doubles before canonical hashing; this
 * bounded walk does not permit the parser to change signed server grant bytes.
 */
class ExactNumbers {
  const std::string& text_;size_t at_=0;
  void ws(){while(at_<text_.size() && (text_[at_]==' '||text_[at_]=='\t'||text_[at_]=='\n'||text_[at_]=='\r'))at_++;}
  std::string string(){const size_t start=at_++;bool escaped=false;while(at_<text_.size()){const char c=text_[at_++];if(!escaped&&c=='"')return text_.substr(start,at_-start);if(!escaped&&c=='\\')escaped=true;else escaped=false;}return {};}
  bool value(JsonVariant target,size_t depth){
    if(depth>16)return false;
    ws();
    if(at_>=text_.size())return false;
    const char c=text_[at_];
    if(c=='"')return !string().empty();
    if(c=='{'){
      at_++;ws();if(text_[at_]=='}'){at_++;return true;}
      for(size_t fields=0;fields<32;fields++){
        ws();JsonDocument key;if(deserializeJson(key,string()))return false;ws();if(text_[at_++]!=':')return false;
        if(!value(target[key.as<const char*>()],depth+1))return false;
        ws();
        if(text_[at_]=='}'){at_++;return true;}if(text_[at_++]!=',')return false;
      }return false;
    }
    if(c=='['){
      at_++;ws();if(text_[at_]==']'){at_++;return true;}
      for(size_t index=0;index<2048;index++){
        if(!value(target[index],depth+1))return false;
        ws();
        if(text_[at_]==']'){at_++;return true;}if(text_[at_++]!=',')return false;
      }return false;
    }
    const size_t start=at_;while(at_<text_.size()&&text_[at_]!=' '&&text_[at_]!='\t'&&text_[at_]!='\n'&&text_[at_]!='\r'&&text_[at_]!=','&&text_[at_]!=']'&&text_[at_]!='}')at_++;
    const std::string token=text_.substr(start,at_-start);
    if(token=="true" || token=="false" || token=="null") return true;
    if(token.find_first_of(".eE")!=std::string::npos){char* end=nullptr;const double number=std::strtod(token.c_str(),&end);if(end!=token.c_str()+token.size()||!std::isfinite(number))return false;target.set(number);}
    return !token.empty();
  }
public:
  explicit ExactNumbers(const std::string& text):text_(text){}
  bool repair(JsonVariant root){if(!value(root,0))return false;ws();return at_==text_.size();}
};
inline bool deserializeExact(JsonDocument& value,const std::string& text,bool domainNul=false){
  if(!otgd::StrictJson(text,domainNul).valid() || deserializeJson(value,text,DeserializationOption::NestingLimit(16)))return false;
  return ExactNumbers(text).repair(value.as<JsonVariant>());
}
}
