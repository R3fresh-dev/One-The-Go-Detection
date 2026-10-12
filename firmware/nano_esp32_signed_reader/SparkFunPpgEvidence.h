#pragma once
#include <ArduinoJson.h>
#include <ctime>
#include <string>
#include "SparkFunPpgCore.h"

namespace otgd_reader {
struct SparkFunHubFirmware {uint8_t major,minor,revision;};
inline std::string sparkFunUtc(uint64_t millis){time_t seconds=time_t(millis/1000);tm value{};
    if(!gmtime_r(&seconds,&value)){return {};}
  char prefix[24],text[32];
    if(!strftime(prefix,sizeof(prefix),"%Y-%m-%dT%H:%M:%S",&value)){return {};}
  snprintf(text,sizeof(text),"%s.%03uZ",prefix,unsigned(millis%1000));return text;}
/** Actual production payload factory. Only derived/vendor-quality evidence is
 * retained; raw IR/red remain RAM-only and are absent from this envelope. */
inline void sparkFunResult(JsonDocument& normalized,const SparkFunCapture& capture,const SparkFunPlan& plan,
  const std::string& configurationId,uint64_t wallStarted,bool firmwareObserved,SparkFunHubFirmware firmware,uint16_t sensorRate) {
    bool valid=capture.validSignal();auto projection=normalized["projection"].to<JsonObject>();
    projection["status"]=valid?"valid":"invalid";projection["source"]="prototype_sensor";projection["started_at"]=sparkFunUtc(wallStarted);projection["ended_at"]=sparkFunUtc(wallStarted+(capture.end()-capture.start())/1000);
    auto flags=projection["quality_flags"].to<JsonArray>();flags.add("SERVER_WALL_ANCHOR_UNQUALIFIED");flags.add("SPARKFUN_SENSOR_BPM_V1");flags.add("HOST_I2C_RECEIVE_TIMESTAMPS_UNQUALIFIED");
    if(!valid)flags.add("PPG_SIGNAL_INVALID");
    if(capture.ioError())flags.add("PPG_IO_OR_VERSION_ERROR");
    if(capture.contactLost())flags.add("CONTACT_LOST");
    if(capture.stale())flags.add("PPG_DATA_GAP");
    if(capture.overrun())flags.add("PPG_CAPTURE_OVERRUN");
    projection["acquisition_config_id"]=configurationId;projection["modality"]="ppg";projection["sample_rate_hz"]=nullptr;projection["heart_rate_bpm"]=nullptr;projection["ecg_rmssd_ms"]=nullptr;projection["raw_artifact_id"]=nullptr;projection["ecg_status"]="not_collected";
    if(valid)projection["heart_rate_bpm"]=capture.heartRate();
    auto evidence=normalized["ppg_evidence"].to<JsonObject>();evidence["schema_version"]="1.0.0";evidence["adapter_id"]="otgd_sparkfun_max32664_v1";evidence["sdk_commit"]="91575258e5e2c47f0f4b8ec97b651381671f4637";evidence["sdk_version"]="1.1";evidence["algorithm_mode"]=plan.mode;
    evidence["hub_firmware"]=nullptr;
    if(firmwareObserved){auto version=evidence["hub_firmware"].to<JsonObject>();version["major"]=firmware.major;version["minor"]=firmware.minor;version["revision"]=firmware.revision;}
    evidence["configured_sensor_rate_hz"]=nullptr;
    if(sensorRate){evidence["configured_sensor_rate_hz"]=sensorRate;}
    evidence["actual_sensor_cadence_hz"]=nullptr;evidence["host_poll_interval_ms"]=plan.pollMs;evidence["sample_timestamp_source"]="host_i2c_receive_unqualified_sensor_time";evidence["acquisition_started_monotonic_us"]=capture.start();evidence["acquisition_ended_monotonic_us"]=capture.end();evidence["observed_samples"]=capture.observed();evidence["valid_samples"]=capture.validSamples();evidence["invalid_samples"]=capture.invalidSamples();evidence["missed_poll_intervals"]=capture.missedPolls();evidence["fifo_empty_polls"]=capture.emptyPolls();evidence["fifo_backlog_peak"]=capture.backlogPeak();evidence["sensor_dropped_samples"]=nullptr;evidence["last_observation"]=nullptr;
    if(capture.observed()){const auto& last=capture.last();auto value=evidence["last_observation"].to<JsonObject>();value["sequence"]=last.sequence;value["host_received_monotonic_us"]=last.receivedUs;value["heart_rate_bpm"]=last.bpm;value["confidence_percent"]=last.confidence;value["finger_status"]=last.status;value["extended_status"]=nullptr;
    if(plan.mode==2)value["extended_status"]=last.extendedStatus;}
 }
}
