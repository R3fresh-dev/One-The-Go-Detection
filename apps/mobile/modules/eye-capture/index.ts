import React from 'react';
import { requireOptionalNativeModule, requireNativeViewManager } from 'expo-modules-core';
import type { EyeAvailability, EyeCaptureViewProps, EyeCaptureViewRef } from './types';
import { EYE_ADAPTER_ID, EYE_EXTRACTOR_VERSION } from './types';
export * from './types';
const native=requireOptionalNativeModule<{getAvailability():EyeAvailability;cameraInventory():Record<string,unknown>[];cameraPermission():string}>('OTGDEyeCapture');
export function getEyeCaptureAvailability():EyeAvailability{return native?.getAvailability()??{available:false,adapter_id:EYE_ADAPTER_ID,extractor_version:EYE_EXTRACTOR_VERSION,model_eligible:false,reason:'NATIVE_CAMERA_MODULE_UNAVAILABLE'};}
export function eyeCameraInventory():Record<string,unknown>[] {return native?.cameraInventory()??[];}
export function eyeCameraPermission():string{return native?.cameraPermission()??'unavailable';}
const NativeView=native?requireNativeViewManager<EyeCaptureViewProps>('OTGDEyeCapture'):null;
export const EyeCaptureView=React.forwardRef<EyeCaptureViewRef,EyeCaptureViewProps>((props,ref)=>{
  if(props.optionsJson.length>32768)throw new Error('EYE_CONFIGURATION_LIMIT');
  if(!NativeView)throw new Error('NATIVE_CAMERA_MODULE_UNAVAILABLE');
  return React.createElement(NativeView,{...props,ref} as EyeCaptureViewProps & {ref:React.ForwardedRef<EyeCaptureViewRef>});
});
EyeCaptureView.displayName='EyeCaptureView';
