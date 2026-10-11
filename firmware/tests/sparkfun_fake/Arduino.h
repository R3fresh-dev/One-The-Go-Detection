#pragma once
#include <cstddef>
#include <cstdint>
#define HIGH 1
#define LOW 0
#define OUTPUT 1
#define INPUT_PULLUP 2
inline uint64_t fakeDelayMs=0;
inline void pinMode(int,int){}
inline void digitalWrite(int,int){}
inline void delay(uint32_t value){fakeDelayMs+=value;}
