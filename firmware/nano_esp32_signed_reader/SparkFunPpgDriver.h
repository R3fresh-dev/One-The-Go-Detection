#pragma once
#include <Arduino.h>
#include <Wire.h>
#include <ArduinoJson.h>
#include <esp_timer.h>
#include <esp_secure_boot.h>
#include <esp_flash_encrypt.h>
#include <nvs.h>
#include <mbedtls/sha256.h>
#include <ctime>
#include "ExactJson.h"
#include "ServerGrantCore.h"
#include "SparkFunPpgCore.h"
#include "SparkFunPpgEvidence.h"
#include "vendor/sparkfun/SparkFun_Bio_Sensor_Hub_Library.h"

namespace otgd_reader {
class ProtectedSparkFunDriver {
  bool initialized_=false,ready_=false,completed_=false,firmwareObserved_=false;
  JsonDocument provision_;
  SparkFunPlan plan_;
  SparkFunCapture capture_;
  SparkFun_Bio_Sensor_Hub hub_;
  version firmware_{};
  int sda_=-1,scl_=-1,reset_=-1,mfio_=-1;
  uint16_t ioTimeoutMs_=0,sensorRate_=0;
  uint64_t wallStarted_=0;
  std::string configurationId_;
  static uint64_t now(){return uint64_t(esp_timer_get_time());}
  static std::string sha(const std::string& bytes){unsigned char value[32];if(mbedtls_sha256_ret(reinterpret_cast<const unsigned char*>(bytes.data()),bytes.size(),value,0)!=0)return {};char out[65];for(size_t i=0;i<32;i++)snprintf(out+i*2,3,"%02x",value[i]);return out;}
  static int pin(int gpio) {
#if defined(BOARD_HAS_PIN_REMAP) && !defined(BOARD_USES_HW_GPIO_NUMBERS)
    for(int d=0;d<NUM_DIGITAL_PINS;d++)if(digitalPinToGPIONumber(d)==gpio)return d;
    return -1;
#else
    return gpio;
#endif
  }

  void shutdown(bool canceled=false){if(reset_>=0){pinMode(reset_,OUTPUT);digitalWrite(reset_,LOW);}capture_.finish(now(),canceled);}
  bool ioAllowed(uint64_t worstUs){if(capture_.canIo(now(),worstUs))return true;shutdown();return false;}
  bool versionMatches()const {
    const auto m=provision_["material"].as<JsonObjectConst>();
    return firmware_.major==m["hub_firmware_major"].as<uint8_t>()&&firmware_.minor==m["hub_firmware_minor"].as<uint8_t>()&&firmware_.revision==m["hub_firmware_revision"].as<uint8_t>();
  }
public:
  bool initialize() {
    if(initialized_)return ready_;
    initialized_=true;
    if(!esp_secure_boot_enabled()||!esp_flash_encryption_enabled())return false;
    nvs_handle_t handle;if(nvs_open_from_partition("otgd_identity","reader",NVS_READONLY,&handle)!=ESP_OK)return false;
    size_t size=0;bool valid=nvs_get_str(handle,"ppg_provision",nullptr,&size)==ESP_OK&&size>=2&&size<=4096;char text[4096]{};if(valid)valid=nvs_get_str(handle,"ppg_provision",text,&size)==ESP_OK;nvs_close(handle);
    if(!valid||!deserializeExact(provision_,std::string(text,size-1)))return false;
    const auto p=provision_.as<JsonObjectConst>(),m=p["material"].as<JsonObjectConst>();
    if(!fields(p,{"schema_version","configuration_id","configuration_hash","configuration_submitted_sha256","configuration_version","calibration_id","material"})||p["schema_version"]!="1.0.0"||!p["configuration_id"].is<const char*>()||!p["calibration_id"].is<const char*>()||m.isNull())return false;
    if(!fields(m,{"schema_version","channel","modality","adapter_id","protocol_version","duration_ms","end_guard_ms","poll_interval_ms","i2c_timeout_ms","i2c_address","bus_frequency_hz","sda_gpio","scl_gpio","reset_gpio","mfio_gpio","algorithm_mode","sdk_commit","sdk_version","extractor_version","minimum_valid_samples","minimum_confidence","minimum_heart_rate_bpm","maximum_heart_rate_bpm","hub_firmware_major","hub_firmware_minor","hub_firmware_revision","warmup_ms","max_no_data_ms"})||m["schema_version"]!="1.0.0"||m["channel"]!="cardiac"||m["modality"]!="ppg"||m["adapter_id"]!="otgd_sparkfun_max32664_v1"||m["protocol_version"]!=1||m["sdk_commit"]!="91575258e5e2c47f0f4b8ec97b651381671f4637"||m["sdk_version"]!="1.1"||m["extractor_version"]!="sparkfun_sensor_bpm_v1")return false;
    for(const char* name:{"duration_ms","end_guard_ms","poll_interval_ms","i2c_timeout_ms","i2c_address","bus_frequency_hz","sda_gpio","scl_gpio","reset_gpio","mfio_gpio","algorithm_mode","minimum_valid_samples","minimum_confidence","minimum_heart_rate_bpm","maximum_heart_rate_bpm","hub_firmware_major","hub_firmware_minor","hub_firmware_revision","warmup_ms","max_no_data_ms"})if(!m[name].is<uint32_t>())return false;
    if(m["i2c_address"]!=85||m["bus_frequency_hz"]!=100000||m["sda_gpio"]!=11||m["scl_gpio"]!=12||m["reset_gpio"]!=5||m["mfio_gpio"]!=6||m["i2c_timeout_ms"].as<uint32_t>()<1||m["i2c_timeout_ms"].as<uint32_t>()>20)return false;
    for(const char* name:{"hub_firmware_major","hub_firmware_minor","hub_firmware_revision"})if(m[name].as<uint32_t>()>255)return false;
    if(m["minimum_valid_samples"].as<uint32_t>()>256||m["minimum_confidence"].as<uint32_t>()>100||m["minimum_heart_rate_bpm"].as<uint32_t>()>300||m["maximum_heart_rate_bpm"].as<uint32_t>()>300||m["algorithm_mode"].as<uint32_t>()>2)return false;
    plan_.durationMs=m["duration_ms"];plan_.endGuardMs=m["end_guard_ms"];plan_.pollMs=m["poll_interval_ms"];plan_.warmupMs=m["warmup_ms"];plan_.maxNoDataMs=m["max_no_data_ms"];plan_.mode=m["algorithm_mode"];plan_.minimumValid=m["minimum_valid_samples"];plan_.minimumConfidence=m["minimum_confidence"];plan_.minimumBpm=m["minimum_heart_rate_bpm"];plan_.maximumBpm=m["maximum_heart_rate_bpm"];
    if(!plan_.valid())return false;
    std::string bytes;if(!canonical(m,bytes,4096)||sha(bytes)!=p["configuration_hash"].as<std::string>())return false;
    sda_=pin(11);scl_=pin(12);reset_=pin(5);mfio_=pin(6);if(sda_<0||scl_<0||reset_<0||mfio_<0)return false;
    ioTimeoutMs_=m["i2c_timeout_ms"];ready_=true;return true;
  }
  bool available(const char* channel){return initialize()&&channel&&(std::strcmp(channel,"ppg")==0||std::strcmp(channel,"cardiac")==0);}
  bool matchesConfiguration(JsonVariantConst grant)const {
    for(const char* name:{"configuration_id","configuration_hash","configuration_submitted_sha256","configuration_version"})if(grant[name]!=provision_[name])return false;
    return ready_;
  }
  bool start(const char* channel,JsonVariantConst grant,const char*,const char*,const char*,uint64_t) {
    uint64_t wall;if(!available(channel)||capture_.active()||!grant["raw_recording_permission"].isNull()||!utcMicros(grant["issued_at"],wall))return false;
    for(const char* name:{"configuration_id","configuration_hash","configuration_submitted_sha256","configuration_version"})if(grant[name]!=provision_[name])return false;
    if(grant["configuration_max_duration_ms"]!=plan_.durationMs||grant["channel"]!="cardiac")return false;
    if(!Wire.begin(sda_,scl_,100000)){return false;}
    Wire.setTimeOut(ioTimeoutMs_);
    hub_.otgdAttach(Wire,reset_,mfio_);pinMode(reset_,OUTPUT);pinMode(mfio_,OUTPUT);digitalWrite(mfio_,HIGH);digitalWrite(reset_,LOW);
    completed_=false;firmwareObserved_=false;sensorRate_=0;firmware_={};wallStarted_=wall/1000;configurationId_=grant["configuration_id"].as<std::string>();
    return capture_.begin(plan_,now());
  }
  void tick() {
    if(!capture_.active())return;
    uint64_t entered=now();if(entered>=capture_.stopAt()){shutdown();return;}
    if(capture_.stage()==SparkFunStage::ResetLow&&capture_.stageReady(entered)){digitalWrite(reset_,HIGH);pinMode(mfio_,INPUT_PULLUP);capture_.resetReleased(now());return;}
    if(capture_.stage()==SparkFunStage::Boot&&capture_.stageReady(entered)){
      if(!ioAllowed(uint64_t(ioTimeoutMs_)*4000+4000))return;
      if(hub_.otgdApplicationMode()!=APP_MODE||hub_.otgdLastIoStatus()!=SFE_BIO_SUCCESS){capture_.ioFailure();shutdown();return;}
      firmware_=hub_.readSensorHubVersion();firmwareObserved_=hub_.otgdLastIoStatus()==SFE_BIO_SUCCESS;if(!firmwareObserved_||!versionMatches()){capture_.ioFailure();shutdown();return;}
      capture_.configuring();return;
    }
    if(capture_.stage()==SparkFunStage::Configure){
      // Official config command sequence: four bounded writes, two45ms enable
      // waits and read averaging. The1000ms warmup runs in the state machine.
      if(!ioAllowed(uint64_t(ioTimeoutMs_)*12000+110000))return;
      if(hub_.configSensorBpm(plan_.mode)!=SFE_BIO_SUCCESS||hub_.otgdLastIoStatus()!=SFE_BIO_SUCCESS){capture_.ioFailure();shutdown();return;}
      sensorRate_=hub_.readSampleRate();if(hub_.otgdLastIoStatus()!=SFE_BIO_SUCCESS||sensorRate_<50||sensorRate_>3200){capture_.ioFailure();shutdown();return;}
      capture_.configured(now());return;
    }
    if(!capture_.pollDue(entered)){if(capture_.staleAt(entered)){capture_.markStale();shutdown();}return;}
    if(!ioAllowed(uint64_t(ioTimeoutMs_)*2000+2000))return;
    const uint8_t queued=hub_.numSamplesOutFifo();if(hub_.otgdLastIoStatus()!=SFE_BIO_SUCCESS){capture_.ioFailure();shutdown();return;}
    capture_.backlog(queued);if(queued==0){capture_.empty();if(capture_.staleAt(now())){capture_.markStale();shutdown();}return;}
    for(uint8_t index=0;index<std::min<uint8_t>(queued,8);++index){
      if(!ioAllowed(uint64_t(ioTimeoutMs_)*2000+2000))return;
      bioData data=hub_.readSensorBpm();uint64_t received=now();
      if(hub_.otgdLastIoStatus()!=SFE_BIO_SUCCESS){capture_.ioFailure();shutdown();return;}
      SparkFunObservation value{};value.receivedUs=received;value.irCount=data.irLed;value.redCount=data.redLed;value.bpm=data.heartRate;value.confidence=data.confidence;value.status=data.status;value.extendedStatus=data.extStatus;
      volatile unsigned char* transient=reinterpret_cast<volatile unsigned char*>(&data);for(size_t b=0;b<sizeof(data);++b)transient[b]=0;
      capture_.observe(value,received);value.irCount=0;value.redCount=0;if(capture_.overrun()||capture_.contactLost()){shutdown();return;}
    }
  }
  uint64_t endedMs()const{return capture_.end()/1000;}
  int poll(JsonDocument& normalized) {
    if(capture_.active()||capture_.stage()==SparkFunStage::Idle)return 0;
    if(completed_){return -1;}
    completed_=true;
    sparkFunResult(normalized,capture_,plan_,configurationId_,wallStarted_,firmwareObserved_,{firmware_.major,firmware_.minor,firmware_.revision},sensorRate_);
    return 2;
  }
  void stop(){shutdown(true);}
};
}
