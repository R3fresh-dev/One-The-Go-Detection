#pragma once
#include <ArduinoJson.h>
#include <string>

#include "AdcAcquisitionDriver.h"

/** The shipped default is a protected, opt-in actual ADC driver for cardiac
 * PPG/ECG. No material or no contact means no valid measurement. Organizations
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
bool otgdAcquisitionAvailable(const char* channel){return otgdAdcDriver.available(channel);}
bool otgdAcquisitionStart(const char* channel,JsonVariantConst grant,const char* session,const char* attempt,const char* record,uint64_t started){return otgdAdcDriver.start(channel,grant,session,attempt,record,started);}
void otgdAcquisitionTick(){otgdAdcDriver.tick();}
uint64_t otgdAcquisitionEndedMonotonicMs(){return otgdAdcDriver.endedMs();}
int otgdAcquisitionPoll(JsonDocument& normalized){return otgdAdcDriver.poll(normalized);}
void otgdAcquisitionStop(){otgdAdcDriver.stop();}
