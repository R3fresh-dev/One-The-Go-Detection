#pragma once
#include <Arduino.h>
#include <esp_system.h>
#include <esp_partition.h>
#include <esp_secure_boot.h>
#include <esp_flash_encrypt.h>
#include <nvs_flash.h>
#include <nvs.h>
#include <mbedtls/base64.h>
#include <mbedtls/pk.h>
#include <mbedtls/sha256.h>
#include <mbedtls/platform_util.h>
#include <string>

namespace otgd_reader {
/** No phone key, auto-generated device key or plaintext NVS fallback. */
class ProtectedSigner {
  mbedtls_pk_context key_;
  mbedtls_pk_context server_;
  bool ready_=false;
  uint32_t passkey_=0;
  std::string device_,keyId_,hardware_,firmware_;
  std::string serverKeyId_;
  static int entropy(void*,unsigned char* out,size_t bytes) {esp_fill_random(out,bytes);return 0;}
  static bool name(nvs_handle_t handle,const char* field,std::string& output,size_t max) {
    size_t bytes=0; if(nvs_get_str(handle,field,nullptr,&bytes)!=ESP_OK || bytes<2 || bytes>max+1) return false;
    char value[129]{}; if(nvs_get_str(handle,field,value,&bytes)!=ESP_OK) return false;
    output=value; for(char c:output) if(!((c>='A'&&c<='Z')||(c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='_'||c=='-'||c=='.'||c==':')) return false;
    return true;
  }
public:
  ProtectedSigner(){mbedtls_pk_init(&key_);mbedtls_pk_init(&server_);}
  ~ProtectedSigner(){mbedtls_pk_free(&key_);mbedtls_pk_free(&server_);}
  bool begin() {
    if(ready_) return true;
    if(!esp_secure_boot_enabled() || !esp_flash_encryption_enabled()) return false;
#if defined(CONFIG_NVS_ENCRYPTION) && CONFIG_NVS_ENCRYPTION
    const esp_partition_t* partition=esp_partition_find_first(ESP_PARTITION_TYPE_DATA,ESP_PARTITION_SUBTYPE_DATA_NVS_KEYS,"otgd_nvs_keys");
    if(!partition || !partition->encrypted) return false;
    nvs_sec_cfg_t security{};
    if(nvs_flash_read_security_cfg(partition,&security)!=ESP_OK) return false;
    const esp_err_t init=nvs_flash_secure_init_partition("otgd_identity",&security);
    mbedtls_platform_zeroize(&security,sizeof(security)); if(init!=ESP_OK) return false;
    nvs_handle_t handle;
    if(nvs_open_from_partition("otgd_identity","reader",NVS_READONLY,&handle)!=ESP_OK) return false;
    size_t bytes=0; bool valid=nvs_get_blob(handle,"p256_pkcs8",nullptr,&bytes)==ESP_OK && bytes>=64 && bytes<=1024;
    unsigned char encoded[1024]{};
    if(valid) valid=nvs_get_blob(handle,"p256_pkcs8",encoded,&bytes)==ESP_OK;
    if(valid) valid=name(handle,"device_id",device_,64) && name(handle,"key_id",keyId_,128) && name(handle,"hardware_rev",hardware_,64) && name(handle,"firmware_ver",firmware_,32);
    unsigned char spki[512]{};size_t spkiBytes=sizeof(spki);
    if(valid) valid=name(handle,"server_key",serverKeyId_,128) && nvs_get_blob(handle,"server_spki",spki,&spkiBytes)==ESP_OK;
    if(valid) valid=nvs_get_u32(handle,"ble_passkey",&passkey_)==ESP_OK && passkey_>=100000 && passkey_<=999999;
    nvs_close(handle);
    if(valid) valid=mbedtls_pk_parse_key(&key_,encoded,bytes,nullptr,0)==0 && mbedtls_pk_can_do(&key_,MBEDTLS_PK_ECDSA) && mbedtls_pk_get_bitlen(&key_)==256 && mbedtls_pk_ec(key_)->grp.id==MBEDTLS_ECP_DP_SECP256R1;
    if(valid) valid=mbedtls_pk_parse_public_key(&server_,spki,spkiBytes)==0 && mbedtls_pk_can_do(&server_,MBEDTLS_PK_ECDSA) && mbedtls_pk_get_bitlen(&server_)==256 && mbedtls_pk_ec(server_)->grp.id==MBEDTLS_ECP_DP_SECP256R1;
    mbedtls_platform_zeroize(encoded,sizeof(encoded)); ready_=valid;
    return ready_;
#else
    // The stock pinned Arduino SDK has no protected NVS configuration. An
    // organization-built SDK/partition image is required; never downgrade.
    return false;
#endif
  }
  bool ready() const{return ready_;}
  uint32_t pairingPasskey() const{return ready_?passkey_:0;}
  const std::string& deviceId()const{return device_;}
  const std::string& keyId()const{return keyId_;}
  const std::string& hardware()const{return hardware_;}
  const std::string& firmware()const{return firmware_;}
  bool verifyGrant(const std::string& keyId,const std::string& canonical,const std::string& signature) {
    if(!ready_ || keyId!=serverKeyId_ || canonical.size()>6000 || signature.size()>100) return false;
    unsigned char der[72]{};size_t size=0;
    if(mbedtls_base64_decode(der,sizeof(der),&size,reinterpret_cast<const unsigned char*>(signature.data()),signature.size())!=0 || size<8 || der[0]!=0x30 || der[1]!=size-2) return false;
    size_t offset=2;
    for(size_t n=0;n<2;n++) {
      if(offset+2>size || der[offset++]!=2) return false;
      const size_t bytes=der[offset++];
      if(bytes<1 || bytes>33 || offset+bytes>size || (der[offset]&0x80) || (bytes>1 && der[offset]==0 && !(der[offset+1]&0x80))) return false;
      bool nonzero=false;for(size_t i=0;i<bytes;i++) nonzero=nonzero||der[offset+i]!=0;
      if(!nonzero) return false;
      offset+=bytes;
    }
    if(offset!=size) return false;
    std::string message("OTGD capture grant v1\0",sizeof("OTGD capture grant v1\0")-1);message+=canonical;
    unsigned char hash[32];if(mbedtls_sha256_ret(reinterpret_cast<const unsigned char*>(message.data()),message.size(),hash,0)!=0) return false;
    const bool verified=mbedtls_pk_verify(&server_,MBEDTLS_MD_SHA256,hash,32,der,size)==0;
    mbedtls_platform_zeroize(hash,sizeof(hash));return verified;
  }
  bool sign(const std::string& domain,const std::string& canonical,std::string& signature) {
    if(!ready_ || canonical.size()>8188 || (domain!="OTGD-BIND-v1\n" && domain!="OTGD-CAPTURE-v1\n")) return false;
    const std::string bytes=domain+canonical; unsigned char hash[32],der[MBEDTLS_PK_SIGNATURE_MAX_SIZE]; size_t derBytes=0;
    if(mbedtls_sha256_ret(reinterpret_cast<const unsigned char*>(bytes.data()),bytes.size(),hash,0)!=0 || mbedtls_pk_sign(&key_,MBEDTLS_MD_SHA256,hash,32,der,&derBytes,entropy,nullptr)!=0) return false;
    unsigned char encoded[256]{}; size_t encodedBytes=0;
    const bool valid=derBytes<=72 && mbedtls_base64_encode(encoded,sizeof(encoded),&encodedBytes,der,derBytes)==0;
    if(valid) signature.assign(reinterpret_cast<char*>(encoded),encodedBytes);
    mbedtls_platform_zeroize(hash,sizeof(hash));mbedtls_platform_zeroize(der,sizeof(der)); return valid;
  }
};
}
