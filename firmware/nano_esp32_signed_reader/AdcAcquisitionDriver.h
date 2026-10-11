#pragma once
#include <Arduino.h>
#include <ArduinoJson.h>
#include <esp_timer.h>
#include <esp_secure_boot.h>
#include <esp_flash_encrypt.h>
#include <nvs.h>
#include <mbedtls/sha256.h>
#include <ctime>
#include <string>
#include "AdcAcquisitionCore.h"
#include "ExactJson.h"
#include "ServerGrantCore.h"
namespace otgd_reader {
/** An opt-in physical ADC driver, never enabled by compile-time test values.
 * All GPIO/front-end/configuration material comes from protected offline NVS.
 * ECG conversion is permitted only with the provisioned approved reference,
 * offset and amplifier gain. There is no inference from chemical/MQ inputs.
 */
class ProtectedAdcDriver {
  bool initialized_=false,ready_=false,completed_=false,recordRaw_=false;
  size_t rawLimit_=0;uint64_t rawNextIndex_=0;
  JsonDocument provision_;
  AdcPlan plan_;
  AdcAcquisition acquisition_;
  std::string channel_,configurationId_;
  int adcPin_=-1,contactPin_=-1;bool contactHigh_=false;
  uint64_t wallStarted_=0;
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
  static bool timestamp(const char* text,uint64_t& output){uint64_t micros;if(!text||!utcMicros(text,micros))return false;output=micros/1000;return true;}
  static std::string utc(uint64_t millis){time_t seconds=time_t(millis/1000);tm value{};if(!gmtime_r(&seconds,&value))return {};char prefix[24],text[32];if(!strftime(prefix,sizeof(prefix),"%Y-%m-%dT%H:%M:%S",&value))return {};snprintf(text,sizeof(text),"%s.%03uZ",prefix,unsigned(millis%1000));return text;}
  static bool gpioSafe(int gpio){return gpio==1||gpio==2||(gpio>=4&&gpio<=18)||gpio==21||(gpio>=38&&gpio<=42)||gpio==47||gpio==48;}
  void shutdown(){if(adcPin_>=0)pinMode(adcPin_,INPUT);}
public:
  bool initialize() {
    if(initialized_)return ready_;
    initialized_=true;
    if(!esp_secure_boot_enabled()||!esp_flash_encryption_enabled())return false;
    nvs_handle_t handle;if(nvs_open_from_partition("otgd_identity","reader",NVS_READONLY,&handle)!=ESP_OK)return false;
    size_t size=0;bool valid=nvs_get_str(handle,"adc_provision",nullptr,&size)==ESP_OK&&size>=2&&size<=4096;char text[4096]{};if(valid)valid=nvs_get_str(handle,"adc_provision",text,&size)==ESP_OK;nvs_close(handle);
    if(!valid||!deserializeExact(provision_,std::string(text,size-1)))return false;
    const JsonObjectConst p=provision_.as<JsonObjectConst>(),m=p["material"].as<JsonObjectConst>();
    if(!fields(p,{"schema_version","configuration_id","configuration_hash","configuration_submitted_sha256","configuration_version","calibration_id","material"})||p["schema_version"]!="1.0.0"||!p["calibration_id"].is<const char*>()||!p["configuration_id"].is<const char*>()||m.isNull())return false;
    if(!fields(m,{"schema_version","protocol_version","adapter_id","channel","modality","duration_ms","sample_rate_hz","raw_unit","extractor_version","input_gpio","contact_gpio","contact_active_high","adc_resolution_bits","attenuation_db","reference_mv","gain","offset_mv","threshold_adc","minimum_peak_interval_ms","maximum_peak_interval_ms","minimum_amplitude_adc","end_guard_ms","raw_sample_limit","raw_encoding"})||m["schema_version"]!="1.0.0"||m["protocol_version"]!=1||m["adapter_id"]!="otgd_esp32_adc_v1"||m["extractor_version"]!="adc_peak_intervals_v1"||m["adc_resolution_bits"]!=12||m["attenuation_db"]!=11||!m["contact_active_high"].is<bool>())return false;
    channel_=m["channel"].as<std::string>();if(channel_!="cardiac"&&channel_!="ecg")return false;
    plan_.ecg=channel_=="ecg";if(m["modality"]!=(plan_.ecg?"ecg":"ppg")||m["raw_unit"]!=(plan_.ecg?"mV":"counts"))return false;
    for(const char* name:{"duration_ms","sample_rate_hz","input_gpio","contact_gpio","threshold_adc","minimum_peak_interval_ms","maximum_peak_interval_ms","minimum_amplitude_adc","end_guard_ms","raw_sample_limit"})if(!m[name].is<uint32_t>())return false;
    for(const char* name:{"reference_mv","gain","offset_mv"})if(!m[name].is<double>())return false;
    plan_.durationMs=m["duration_ms"];plan_.rateHz=m["sample_rate_hz"];plan_.endGuardMs=m["end_guard_ms"];plan_.threshold=m["threshold_adc"];plan_.minPeakMs=m["minimum_peak_interval_ms"];plan_.maxPeakMs=m["maximum_peak_interval_ms"];plan_.minAmplitude=m["minimum_amplitude_adc"];plan_.referenceMv=m["reference_mv"];plan_.gain=m["gain"];plan_.offsetMv=m["offset_mv"];
    const int gpio=m["input_gpio"],contact=m["contact_gpio"];if(gpio<1||gpio>10||!gpioSafe(contact)||gpio==contact||!plan_.valid())return false;
    adcPin_=pin(gpio);contactPin_=pin(contact);if(adcPin_<0||contactPin_<0)return false;contactHigh_=m["contact_active_high"];
    std::string material;if(!canonical(m,material,4096)||sha(material)!=p["configuration_hash"].as<std::string>())return false;
    if(!m["raw_sample_limit"].is<uint32_t>()||m["raw_sample_limit"].as<uint32_t>()>1024)return false;
    rawLimit_=m["raw_sample_limit"].as<uint32_t>();
    if(rawLimit_==0){if(!m["raw_encoding"].isNull())return false;}else if(!plan_.ecg||m["raw_encoding"]!="otgd_ecg_samples_v1"||uint64_t(plan_.rateHz)*plan_.durationMs>uint64_t(rawLimit_)*1000)return false;
    ready_=true;return true;
  }
  bool available(const char* channel){return initialize()&&channel&&channel_==(std::strcmp(channel,"ppg")==0?"cardiac":channel);}
  bool start(const char* channel,JsonVariantConst grant,const char*,const char*,const char*,uint64_t) {
    if(!available(channel)||acquisition_.active()||!timestamp(grant["issued_at"],wallStarted_))return false;
    for(const char* name:{"configuration_id","configuration_hash","configuration_submitted_sha256","configuration_version"})if(grant[name]!=provision_[name])return false;
    if(grant["configuration_max_duration_ms"]!=plan_.durationMs)return false;
    recordRaw_=!grant["raw_recording_permission"].isNull();
    if(recordRaw_&&(!plan_.ecg||rawLimit_==0||uint64_t(plan_.rateHz)*plan_.durationMs>uint64_t(rawLimit_)*1000||grant["raw_recording_permission"]["record"]!=true))return false;
    rawNextIndex_=0;
    completed_=false;configurationId_=grant["configuration_id"].as<std::string>();
    pinMode(adcPin_,INPUT);pinMode(contactPin_,contactHigh_?INPUT_PULLDOWN:INPUT_PULLUP);
    analogReadResolution(12);analogSetPinAttenuation(adcPin_,ADC_11db);
    return acquisition_.begin(plan_,now(),recordRaw_,rawLimit_?rawLimit_:256);
  }
  void tick(){acquisition_.tick(now(),[&]{return analogRead(adcPin_);},[&]{return (digitalRead(contactPin_)==HIGH)==contactHigh_;},now,[&]{shutdown();});}
  uint64_t endedMs()const{return acquisition_.end()/1000;}
  int poll(JsonDocument& normalized) {
    if(!acquisition_.ended())return 0;
    if(completed_)return -1;
    if(recordRaw_&&acquisition_.queued()) {
      const auto chunk=acquisition_.take(64,true);if(chunk.empty())return -1;
      normalized["schema_version"]="1.0.0";normalized["channel"]="ecg";normalized["first_sample_index"]=chunk.front().index;normalized["sample_rate_hz"]=plan_.rateHz;normalized["units"]="uV";normalized["contact"]="good";
      normalized["acquisition_started_monotonic_us"]=acquisition_.start();normalized["acquisition_ended_monotonic_us"]=acquisition_.end();
      normalized["dropped_before"]=chunk.front().index-rawNextIndex_;JsonArray samples=normalized["samples"].to<JsonArray>();
      size_t included=0;uint64_t previous=chunk.front().index;
      // Gaps split chunks so first_sample_index+length describes actual
      // contiguous observations and dropped_before remains explicit.
      for(const auto& sample:chunk){if(included&&sample.index!=previous+1)return -1;JsonObject item=samples.add<JsonObject>();item["monotonic_us"]=sample.monotonicUs;item["value"]=sample.value;previous=sample.index;included++;}
      rawNextIndex_=chunk.back().index+1;return 1;
    }
    completed_=true;
    if(acquisition_.overran())return -1;
    const bool valid=acquisition_.validSignal();normalized["status"]=valid?"valid":"invalid";normalized["source"]="prototype_sensor";
    normalized["started_at"]=utc(wallStarted_);normalized["ended_at"]=utc(wallStarted_+(acquisition_.end()-acquisition_.start())/1000);
    JsonArray flags=normalized["quality_flags"].to<JsonArray>();flags.add("SERVER_WALL_ANCHOR_UNQUALIFIED");flags.add("ADC_PEAK_INTERVALS_V1");
    if(!valid){flags.add("ADC_SIGNAL_INVALID");if(acquisition_.lostContact())flags.add("CONTACT_LOST");if(acquisition_.saturated())flags.add("ADC_SATURATED");if(acquisition_.dropped())flags.add("ADC_SAMPLE_DROPS");if(acquisition_.queueLost())flags.add("ADC_QUEUE_OVERFLOW");}
    normalized["acquisition_config_id"]=configurationId_;normalized["modality"]=plan_.ecg?"ecg":"ppg";normalized["sample_rate_hz"]=plan_.rateHz;
    normalized["heart_rate_bpm"]=nullptr;normalized["ecg_rmssd_ms"]=nullptr;normalized["raw_artifact_id"]=nullptr;normalized["ecg_status"]=plan_.ecg?(valid?"valid":"invalid"):"not_collected";
    if(valid){normalized["heart_rate_bpm"]=acquisition_.heartRate();if(plan_.ecg)normalized["ecg_rmssd_ms"]=acquisition_.rmssd();}
    return 2;
  }
  void stop(){acquisition_.cancel(now(),[&]{shutdown();});}
};
}
