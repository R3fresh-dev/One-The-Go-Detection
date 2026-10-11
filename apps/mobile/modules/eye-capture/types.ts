import type { NativeSyntheticEvent, ViewProps } from 'react-native';
export const EYE_ADAPTER_ID = 'optical_roi_v1';
export const EYE_EXTRACTOR_VERSION = 'otgd-dark-component-v1';
export interface EyeAvailability { available:boolean;adapter_id:string;extractor_version:string;model_eligible:false;phone_model?:string;os_version?:string;reason?:string; }
export interface EyeRawHandoff {format:'OTGD-EYE-ROI-v1';media_type:'application/octet-stream';sha256:string;size_bytes:number;chunks:string[];}
export interface EyeCaptureComplete {run_id:string;workspace_epoch:string;authorization_id?:string;status:'valid'|'invalid';reason?:string;native_result:Record<string,unknown>|null;raw_recording:EyeRawHandoff|null;}
export interface EyeOptions {
  run_id:string;workspace_epoch:string;authorization_id:string;configuration_sha256:string;
  /** Exact RFC8785 canonical bytes of the server's approved inline scientific material. */
  material_json:string;supported_phone_models:string[];supported_os_versions:string[];supported_native_builds:string[];
  raw_recording_permission:null|{record:boolean;upload:boolean;receipt_id:string;policy_id:string;policy_version:string;policy_sha256:string;raw_notice_version:string;raw_notice_sha256:string;};
}
export interface EyeCaptureViewProps extends ViewProps {optionsJson:string;running:boolean;onProgress?:(event:NativeSyntheticEvent<{run_id:string;workspace_epoch:string;frames:number;maximum_frames:number}>)=>void;onComplete?:(event:NativeSyntheticEvent<EyeCaptureComplete>)=>void;}
export interface EyeCaptureViewRef {cancel(runId:string,reason:string):Promise<EyeCaptureComplete>;releaseRaw(runId:string,sha:string):Promise<{released:boolean}>;}
