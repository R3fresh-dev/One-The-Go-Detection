#pragma once
#include <ArduinoJson.h>
#include <string>

#include "AdcAcquisitionDriver.h"
#include "SparkFunPpgDriver.h"

/** Protected ADC and the selected SparkFun digital PPG are distinct drivers.
 * No approved material/contact means no valid measurement. Organizations
 * may link a separately approved strong driver for a documented instrument;
 * unknown saliva/alcohol vendor protocols have no fabricated implementation.
 */
bool otgdAcquisitionAvailable(const char* channel) __attribute__((weak));
bool otgdAcquisitionStart(const char* channel,JsonVariantConst authorization,
                          const char* session,const char* attempt,const char* record,
                          uint64_t startedMonotonicMs) __attribute__((weak));
void otgdAcquisitionTick() __attribute__((weak));
uint64_t otgdAcquisitionEndedMonotonicMs() __attribute__((weak));
// 0 pending, 1 actual instrument chunk, 2 terminal projection, -1 failed.
int otgdAcquisitionPoll(JsonDocument& normalized) __attribute__((weak));
void otgdAcquisitionStop() __attribute__((weak));
static otgd_reader::ProtectedAdcDriver otgdAdcDriver;
static otgd_reader::ProtectedSparkFunDriver otgdSparkFunDriver;
static uint8_t otgdAcquisitionKind=0;
bool otgdAcquisitionAvailable(const char* channel){const bool digital=otgdSparkFunDriver.available(channel);return digital||otgdAdcDriver.available(channel);}
bool otgdAcquisitionStart(const char* channel,JsonVariantConst grant,const char* session,const char* attempt,const char* record,uint64_t started){
  if(otgdSparkFunDriver.available(channel)&&otgdSparkFunDriver.matchesConfiguration(grant)){
    otgdAcquisitionKind=2;return otgdSparkFunDriver.start(channel,grant,session,attempt,record,started);
  }
  otgdAcquisitionKind=1;return otgdAdcDriver.start(channel,grant,session,attempt,record,started);
}
void otgdAcquisitionTick(){if(otgdAcquisitionKind==2)otgdSparkFunDriver.tick();else if(otgdAcquisitionKind==1)otgdAdcDriver.tick();}
uint64_t otgdAcquisitionEndedMonotonicMs(){return otgdAcquisitionKind==2?otgdSparkFunDriver.endedMs():otgdAdcDriver.endedMs();}
int otgdAcquisitionPoll(JsonDocument& normalized){return otgdAcquisitionKind==2?otgdSparkFunDriver.poll(normalized):otgdAdcDriver.poll(normalized);}
void otgdAcquisitionStop(){if(otgdAcquisitionKind==2)otgdSparkFunDriver.stop();else if(otgdAcquisitionKind==1)otgdAdcDriver.stop();}
