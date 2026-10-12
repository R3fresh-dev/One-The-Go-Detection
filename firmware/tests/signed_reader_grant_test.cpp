#include "../nano_esp32_signed_reader/ServerGrantCore.h"
#include <openssl/evp.h>
#include <openssl/x509.h>
#include <fstream>
#include <sstream>
#include <cassert>
#include <iostream>
using namespace otgd_reader;
static std::vector<unsigned char> base64(const std::string& text){std::vector<unsigned char> out(text.size());int n=EVP_DecodeBlock(out.data(),reinterpret_cast<const unsigned char*>(text.data()),int(text.size()));assert(n>=0);if(!text.empty()&&text.back()=='=')n--;if(text.size()>1&&text[text.size()-2]=='=')n--;out.resize(size_t(n));return out;}
static bool signature(EVP_PKEY* key,const std::string& bytes,const std::string& encoded){const auto der=base64(encoded);EVP_MD_CTX* ctx=EVP_MD_CTX_new();assert(ctx);const bool valid=EVP_DigestVerifyInit(ctx,nullptr,EVP_sha256(),nullptr,key)==1&&EVP_DigestVerifyUpdate(ctx,bytes.data(),bytes.size())==1&&EVP_DigestVerifyFinal(ctx,der.data(),der.size())==1;EVP_MD_CTX_free(ctx);return valid;}
static std::string sha(const std::string& bytes){unsigned char out[32];unsigned int size=32;assert(EVP_Digest(bytes.data(),bytes.size(),out,&size,EVP_sha256(),nullptr)==1&&size==32);char text[65];for(size_t i=0;i<32;i++)snprintf(text+i*2,3,"%02x",out[i]);return text;}
int main(int argc,char**argv){
  const char* path=argc>1?argv[1]:"apps/mobile/testfixtures/backend-reader-capture-authorization.json";std::ifstream input(path);assert(input.good());std::ostringstream bytes;bytes<<input.rdbuf();
  // The offline HTTP fixture also includes participant instructions/context;
  // that wrapper is not a BLE message. Exercise the actual bounded parser on
  // the exact signed token and material which are transmitted to the reader.
  assert(bytes.str().size()<=65536);JsonDocument response;assert(!deserializeJson(response,bytes.str(),DeserializationOption::NestingLimit(16)));
  assert(response["fixture_scope"]=="FICTIONAL-SERVER-AND-READER-KEYS-FOR-PROTOCOL-TESTS-NOT-PHYSICAL-QUALIFICATION");
  JsonDocument fixture;fixture.set(response.as<JsonVariantConst>());std::string encoded;serializeJson(response["start"]["server_start"],encoded);JsonDocument token;assert(deserializeExact(token,encoded,true));fixture["start"]["server_start"].set(token.as<JsonVariantConst>());
  encoded.clear();serializeJson(response["authorization"]["configuration_material"],encoded);JsonDocument material;assert(deserializeExact(material,encoded));fixture["authorization"]["configuration_material"].set(material.as<JsonVariantConst>());
  const JsonObjectConst g=fixture["start"]["server_start"]["grant"],a=fixture["authorization"];
  JsonDocument options;for(const char* name:{"environment","owner_ref","data_generation","authorization_id","binding_id","device_id","configuration_id","configuration_hash","capture_context_sha256"})options[name].set(g[name]);options["key_id"]=g["device_key_id"];options["max_duration_ms"]=g["configuration_max_duration_ms"];
  GrantExpectations expected{g["device_id"].as<std::string>(),g["device_key_id"].as<std::string>(),g["boot_id"].as<std::string>(),g["session_id"].as<std::string>(),g["attempt_id"].as<std::string>(),"ppg",g["device_nonce"].as<std::string>(),100000,105000};
  const auto der=base64(fixture["server_public_key_spki"].as<std::string>());const unsigned char* pointer=der.data();EVP_PKEY* key=d2i_PUBKEY(nullptr,&pointer,long(der.size()));assert(key&&EVP_PKEY_base_id(key)==EVP_PKEY_EC&&EVP_PKEY_bits(key)==256&&pointer==der.data()+der.size());
  const std::string keyId=fixture["start"]["server_start"]["key_id"].as<std::string>();int verifications=0;
  auto verifier=[&](const std::string& label,const std::string& canonical,const std::string& sig){verifications++;return label==keyId&&signature(key,std::string("OTGD capture grant v1\0",22)+canonical,sig);};
  assert(verifyServerGrant(fixture["start"]["server_start"],options.as<JsonVariantConst>(),expected,verifier));assert(verifications==1);
  std::string materialBytes;assert(canonical(a["configuration_material"],materialBytes));assert(sha(materialBytes)==a["configuration_hash"].as<std::string>());
  // Real backend signature fails for altered signed channel, duration, context,
  // configuration, origin or permission; no phone key or token SPKI is trusted.
  for(const char* field:{"configuration_submitted_sha256","configuration_version","capture_context_sha256","channel","configuration_max_duration_ms","raw_recording_permission","participant_protocol_sha256","instruction_receipt_id","owner_ref","device_nonce","boot_id"}) {
    JsonDocument altered;altered.set(fixture["start"]["server_start"]);altered["grant"][field]="altered";assert(!verifyServerGrant(altered.as<JsonVariantConst>(),options.as<JsonVariantConst>(),expected,verifier));
  }
  auto expired=expected;expired.received=160000;assert(!verifyServerGrant(fixture["start"]["server_start"],options.as<JsonVariantConst>(),expired,verifier));
  auto replaced=expected;replaced.deviceNonce="replacement";assert(!verifyServerGrant(fixture["start"]["server_start"],options.as<JsonVariantConst>(),replaced,verifier));
  JsonDocument wrongDomain;wrongDomain.set(fixture["start"]["server_start"]);wrongDomain["domain"]="OTGD capture grant v1";assert(!verifyServerGrant(wrongDomain.as<JsonVariantConst>(),options.as<JsonVariantConst>(),expected,verifier));
  std::string canonical;assert(otgd_reader::canonical(g,canonical));assert(!signature(key,"OTGD capture grant v1"+canonical,fixture["start"]["server_start"]["signature"].as<std::string>()));
  EVP_PKEY_free(key);std::cout<<"Actual backend HTTP fixture: protected-SPKI P256 signature, 22-byte NUL domain, exact material SHA and scope/expiry/mutation negatives passed\n";
}
