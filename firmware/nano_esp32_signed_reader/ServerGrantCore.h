#pragma once
#include <ArduinoJson.h>
#include <functional>
#include <string>
#include "CanonicalJson.h"
#include "ExactJson.h"
#include "ReaderTime.h"

namespace otgd_reader {
struct GrantExpectations {
  std::string deviceId,keyId,bootId,sessionId,attemptId,channel,deviceNonce;
  uint64_t nonceCreated,received;
};
inline bool fields(JsonObjectConst value,std::initializer_list<const char*> names) {
  if(value.size()!=names.size()) return false;
  for(JsonPairConst item:value) {bool found=false;for(const char* name:names)found=found||std::strcmp(item.key().c_str(),name)==0;if(!found)return false;}
  return true;
}
inline bool verifyServerGrant(JsonVariantConst tokenValue,JsonVariantConst optionsValue,const GrantExpectations& expected,
  const std::function<bool(const std::string&,const std::string&,const std::string&)>& verify) {
  if(!tokenValue.is<JsonObjectConst>()||!optionsValue.is<JsonObjectConst>())return false;
  const JsonObjectConst token=tokenValue.as<JsonObjectConst>(),options=optionsValue.as<JsonObjectConst>(),g=token["grant"].as<JsonObjectConst>();
  if(!fields(token,{"grant","signature","key_id","domain"}) || !fields(g,{"schema_version","environment","owner_ref","data_generation","session_id","attempt_id","authorization_id","binding_id","device_id","device_key_id","boot_id","configuration_id","configuration_hash","configuration_submitted_sha256","configuration_version","capture_context_sha256","channel","configuration_max_duration_ms","raw_recording_permission","participant_protocol_sha256","instruction_receipt_id","expires_at","issued_at","device_nonce","nonce"}))return false;
  const JsonString domain=token["domain"].as<JsonString>();
  if(domain.size()!=sizeof("OTGD capture grant v1\0")-1 || std::memcmp(domain.c_str(),"OTGD capture grant v1\0",sizeof("OTGD capture grant v1\0")-1)!=0)return false;
  if(!nonceWithinSignedLifetime(g["issued_at"],g["expires_at"],expected.nonceCreated,expected.received))return false;
  if(expected.deviceNonce.empty()||expected.received<expected.nonceCreated||expected.received-expected.nonceCreated>60000 || g["schema_version"]!="1.0.0" || g["device_nonce"]!=expected.deviceNonce || g["boot_id"]!=expected.bootId || g["device_id"]!=expected.deviceId || g["device_key_id"]!=expected.keyId || g["session_id"]!=expected.sessionId || g["attempt_id"]!=expected.attemptId || g["channel"]!=(expected.channel=="ppg"?"cardiac":expected.channel.c_str()))return false;
  for(const char* name:{"environment","owner_ref","data_generation","authorization_id","binding_id","device_id","configuration_id","configuration_hash","capture_context_sha256"})if(options[name]!=g[name])return false;
  if(options["key_id"]!=expected.keyId || !g["configuration_max_duration_ms"].is<uint32_t>() || g["configuration_max_duration_ms"].as<uint32_t>()<1 || g["configuration_max_duration_ms"].as<uint32_t>()>120000 || options["max_duration_ms"]!=g["configuration_max_duration_ms"])return false;
  // The exact signed participant instruction receipt is required for reader
  // acquisition. It is a reported acknowledgment, never hardware qualification.
  if(!g["participant_protocol_sha256"].is<const char*>()||!g["instruction_receipt_id"].is<const char*>())return false;
  const std::string protocol=g["participant_protocol_sha256"],receipt=g["instruction_receipt_id"];
  if(protocol.size()!=64||receipt.size()!=36)return false;
  for(char c:protocol)if(!((c>='0'&&c<='9')||(c>='a'&&c<='f')))return false;
  for(size_t i=0;i<receipt.size();++i){const char c=receipt[i];if(i==8||i==13||i==18||i==23){if(c!='-')return false;}else if(!((c>='0'&&c<='9')||(c>='a'&&c<='f')))return false;}
  if(!g["raw_recording_permission"].isNull()) {
    const JsonObjectConst permission=g["raw_recording_permission"].as<JsonObjectConst>();
    if(expected.channel!="ecg"||!fields(permission,{"record","upload","receipt_id","policy_id","policy_version","policy_sha256","raw_notice_version","raw_notice_sha256"})||permission["record"]!=true||!permission["upload"].is<bool>())return false;
    for(const char* name:{"receipt_id","policy_id","policy_version","policy_sha256","raw_notice_version","raw_notice_sha256"})if(!permission[name].is<const char*>()||permission[name].as<std::string>().empty()||permission[name].as<std::string>().size()>256)return false;
    for(const char* name:{"policy_sha256","raw_notice_sha256"}){const std::string value=permission[name];if(value.size()!=64)return false;for(char c:value)if(!((c>='0'&&c<='9')||(c>='a'&&c<='f')))return false;}
  }
  if(!token["key_id"].is<const char*>()||!token["signature"].is<const char*>())return false;
  const std::string label=token["key_id"].as<std::string>(),signature=token["signature"].as<std::string>();if(label.empty()||label.size()>128||signature.empty()||signature.size()>100)return false;
  std::string bytes;if(!canonical(g,bytes,6000))return false;
  return verify(label,bytes,signature);
}
}
