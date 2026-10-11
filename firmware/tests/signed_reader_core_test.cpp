#include "../nano_esp32_signed_reader/CanonicalJson.h"
#include "../nano_esp32_signed_reader/ExactJson.h"
#include <cassert>
#include <iostream>
#include <limits>

int main() {
  using namespace otgd_reader;
  for(const auto& fixture:std::vector<std::pair<std::string,std::string>>{
    {"{\"z\":1,\"a\":true,\"nested\":{\"y\":null,\"b\":[-0.0,1e-7,1e-6,72.31]}}","{\"a\":true,\"nested\":{\"b\":[0,1e-7,0.000001,72.31],\"y\":null},\"z\":1}"},
    {"[333333333.33333329,4.50,2e-3,1e-27]","[333333333.3333333,4.5,0.002,1e-27]"},
    {"{\"text\":\"\\u20ac\\u000f\\n\\\\\\\"\"}","{\"text\":\"\xe2\x82\xac\\u000f\\n\\\\\\\"\"}"},
    {"{\"nonce\":\"abcd\",\"schema_version\":\"1.0.0\",\"data_generation\":9007199254740991}","{\"data_generation\":9007199254740991,\"nonce\":\"abcd\",\"schema_version\":\"1.0.0\"}"}}) {
    JsonDocument value;assert(deserializeExact(value,fixture.first));std::string out;
    assert(canonical(value.as<JsonVariantConst>(),out));if(out!=fixture.second){std::cerr<<out<<" != "<<fixture.second<<"\n";}assert(out==fixture.second);
  }
  JsonDocument invalid;invalid["unicode\xc3\xa9"]=1;std::string out;assert(!canonical(invalid.as<JsonVariantConst>(),out));
  invalid.clear();invalid["number"]=std::numeric_limits<double>::infinity();assert(!canonical(invalid.as<JsonVariantConst>(),out));
  invalid.clear();invalid["number"]=9007199254740992ULL;assert(!canonical(invalid.as<JsonVariantConst>(),out));
  invalid.clear();invalid["text"]="secret-value";assert(!canonical(invalid.as<JsonVariantConst>(),out,8));
  assert(!number(1.0,out,0));
  JsonDocument domain;assert(!deserializeJson(domain,"{\"domain\":\"OTGD capture grant v1\\u0000\"}"));
  assert(domain["domain"].as<JsonString>().size()==22);assert(!canonical(domain.as<JsonVariantConst>(),out));
  std::cout<<"Signed reader: exact JCS numeric/string fixtures, bounds and domain-NUL isolation passed\n";
}
