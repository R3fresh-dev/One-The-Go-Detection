import AVFoundation
import UIKit
import QuartzCore
import CryptoKit
import ExpoModulesCore

final class EyeViewRegistry {
  static let views=NSHashTable<OTGDEyeCaptureView>.weakObjects()
  static func stopAll(_ reason:String){if Thread.isMainThread{views.allObjects.forEach{$0.stop(reason)}}else{DispatchQueue.main.async{views.allObjects.forEach{$0.stop(reason)}}}}
}
private final class EyeCancellation {
  private let lock=NSLock();private var enabled=true;private var pendingFrames=0
  func cancel(){lock.lock();enabled=false;lock.unlock()}
  func reserve()->Bool{lock.lock();defer{lock.unlock()};guard enabled,pendingFrames<3 else{return false};pendingFrames+=1;return true}
  func release(){lock.lock();pendingFrames=max(0,pendingFrames-1);lock.unlock()}
  func current()->Bool{lock.lock();defer{lock.unlock()};return enabled}
}
private final class EyeCameraWorker:NSObject,AVCaptureVideoDataOutputSampleBufferDelegate {
  let session=AVCaptureSession(),queue=DispatchQueue(label:"OTGDEyeCamera",qos:.userInitiated)
  let token=EyeCancellation();let config:EyeCore.Config
  private var device:AVCaptureDevice?
  var onFrame:((Double,Double,Double?,String,Double?,String,[UInt8],EyeCore.Segmentation)->Void)?
  var onFailure:((String)->Void)?
  init(_ c:EyeCore.Config){config=c;super.init()}
  func start(){queue.async{[weak self] in
    guard let self,self.token.current() else{return}
    do {
      guard self.config.sensor==nil else{throw EyeCore.Failure.configuration}
      let devices=AVCaptureDevice.DiscoverySession(deviceTypes:[.builtInWideAngleCamera],mediaType:.video,position:.unspecified).devices
      guard let d=devices.first(where:{$0.uniqueID==self.config.camera}),d.position==(self.config.lens=="front" ? .front:.back),d.isExposureModeSupported(.continuousAutoExposure),d.isFocusModeSupported(.continuousAutoFocus) else{throw EyeCore.Failure.configuration}
      guard let format=d.formats.first(where:{f in let size=CMVideoFormatDescriptionGetDimensions(f.formatDescription);return size.width==self.config.width && size.height==self.config.height && f.videoSupportedFrameRateRanges.contains(where:{$0.minFrameRate<=self.config.fps && $0.maxFrameRate>=self.config.fps})}) else{throw EyeCore.Failure.configuration}
      try d.lockForConfiguration();guard self.token.current() else{d.unlockForConfiguration();return};d.activeFormat=format;d.activeVideoMinFrameDuration=CMTime(seconds:1/self.config.fps,preferredTimescale:1_000_000_000);d.activeVideoMaxFrameDuration=d.activeVideoMinFrameDuration;d.exposureMode = .continuousAutoExposure;d.focusMode = .continuousAutoFocus;if d.hasTorch{d.torchMode = .off};d.unlockForConfiguration();self.device=d
      self.session.beginConfiguration();defer{self.session.commitConfiguration()};self.session.sessionPreset = .inputPriority
      let input=try AVCaptureDeviceInput(device:d);guard self.session.canAddInput(input) else{throw EyeCore.Failure.configuration};self.session.addInput(input)
      let output=AVCaptureVideoDataOutput();output.alwaysDiscardsLateVideoFrames=true;output.videoSettings=[kCVPixelBufferPixelFormatTypeKey as String:kCVPixelFormatType_420YpCbCr8BiPlanarFullRange];output.setSampleBufferDelegate(self,queue:self.queue)
      guard self.session.canAddOutput(output) else{throw EyeCore.Failure.configuration};self.session.addOutput(output)
      guard let connection=output.connection(with:.video) else{throw EyeCore.Failure.configuration}
      if #available(iOS 17.0,*){guard connection.isVideoRotationAngleSupported(CGFloat(self.config.rotation)) else{throw EyeCore.Failure.configuration};connection.videoRotationAngle=CGFloat(self.config.rotation)}
      else{guard connection.isVideoOrientationSupported else{throw EyeCore.Failure.configuration};connection.videoOrientation=[0:AVCaptureVideoOrientation.landscapeRight,90:.portrait,180:.landscapeLeft,270:.portraitUpsideDown][self.config.rotation]!}
      connection.automaticallyAdjustsVideoMirroring=false;connection.isVideoMirrored=false
      // Start only after commitConfiguration and one last authority check.
      self.queue.async{[weak self] in guard let self,self.token.current() else{return};self.session.startRunning()}
    }catch{self.onFailure?("CAMERA_CONFIGURATION_UNSUPPORTED")}
  }}
  func stop(){token.cancel();EyeCore.retainedCleanup(self,on:queue){owner in owner.session.stopRunning();owner.session.outputs.forEach{owner.session.removeOutput($0)};owner.session.inputs.forEach{owner.session.removeInput($0)};owner.device=nil}}
  func captureOutput(_ output:AVCaptureOutput,didDrop sampleBuffer:CMSampleBuffer,from connection:AVCaptureConnection){if token.current(){onFailure?("FRAME_DROPPED")}}
  func captureOutput(_ output:AVCaptureOutput,didOutput sampleBuffer:CMSampleBuffer,from connection:AVCaptureConnection){
    guard token.current(),let buffer=CMSampleBufferGetImageBuffer(sampleBuffer),CVPixelBufferGetPixelFormatType(buffer)==kCVPixelFormatType_420YpCbCr8BiPlanarFullRange else{return}
    let timestamp=CMSampleBufferGetPresentationTimeStamp(sampleBuffer).seconds*1000,dispatch=CACurrentMediaTime()*1000
    guard timestamp.isFinite,timestamp>=0,CVPixelBufferLockBaseAddress(buffer,.readOnly)==kCVReturnSuccess else{onFailure?("FRAME_CLOCK_UNAVAILABLE");return};defer{CVPixelBufferUnlockBaseAddress(buffer,.readOnly)}
    guard let base=CVPixelBufferGetBaseAddressOfPlane(buffer,0) else{onFailure?("FRAME_DECODE_FAILED");return}
    let width=CVPixelBufferGetWidthOfPlane(buffer,0),height=CVPixelBufferGetHeightOfPlane(buffer,0)
    guard width==(config.rotation%180==0 ? config.width:config.height),height==(config.rotation%180==0 ? config.height:config.width) else{onFailure?("CAMERA_RESOLUTION_CHANGED");return}
    let stride=CVPixelBufferGetBytesPerRowOfPlane(buffer,0),pixels=base.assumingMemoryBound(to:UInt8.self)
    do{
      let gray=try EyeCore.sample(config,width:width,height:height,rotation:0){x,y in pixels[y*stride+x]}
      let segmentation=try EyeCore.extract(gray,config),exposure=device.map{$0.exposureDuration.seconds*1000},focus=device?.isAdjustingFocus==false ? "focused":"adjusting_or_unknown"
      let iso=device.map{Double($0.iso)},ae=device.map{$0.isAdjustingExposure ? "adjusting_at_callback":"stable_at_callback"} ?? "unknown"
      if token.current(){guard token.reserve() else{token.cancel();onFailure?("FRAME_QUEUE_OVERFLOW");return};onFrame?(timestamp,dispatch,exposure,focus,iso,ae,gray,segmentation)}
    }catch{onFailure?("FRAME_DECODE_FAILED")}
  }
}
final class OTGDEyeCaptureView:ExpoView {
  let onProgress=EventDispatcher(),onComplete=EventDispatcher()
  var requestedOptions="",requestedRunning=false
  private var generation=0,active=false,pending=false,frozen="",run="",epoch="",authorization="",sha=""
  private let terminal=EyeTerminalCache()
  private var config:EyeCore.Config?,worker:EyeCameraWorker?,preview:AVCaptureVideoPreviewLayer?
  private var frames:[[String:Any]]=[],raw:[EyeCore.RawFrame]=[],flags=Set<String>(),seen=Set<String>(),recording=false
  private var watchdog:DispatchSourceTimer?
  private var presented:Double?,originalBrightness:CGFloat?,displayLink:CADisplayLink?,stimulusFinished=false
  private let stimulusView=UIView()
  private var firstFrame:Double?,lastFrame:Double?,startWall="",frozenBounds=CGRect.zero,observers:[NSObjectProtocol]=[]
  required init(appContext:AppContext?=nil){super.init(appContext:appContext);backgroundColor=UIColor(red:0.04,green:0.07,blue:0.12,alpha:1);clipsToBounds=true;stimulusView.isHidden=true;addSubview(stimulusView);EyeViewRegistry.views.add(self)
    for name in [UIApplication.willResignActiveNotification,UIApplication.didEnterBackgroundNotification,AVCaptureSession.wasInterruptedNotification,AVCaptureSession.runtimeErrorNotification]{observers.append(NotificationCenter.default.addObserver(forName:name,object:nil,queue:.main){[weak self] note in guard let self else{return};if name==AVCaptureSession.wasInterruptedNotification || name==AVCaptureSession.runtimeErrorNotification{guard let origin=note.object as? AVCaptureSession,origin === self.worker?.session else{return}};self.stop("CAMERA_INTERRUPTED")})}
  }
  deinit{worker?.stop();observers.forEach{NotificationCenter.default.removeObserver($0)}}
  override func layoutSubviews(){super.layoutSubviews();if active && bounds != frozenBounds{stop("LAYOUT_CHANGED")};preview?.frame=bounds;stimulusView.frame=bounds;commitProps()}
  override var isHidden:Bool{didSet{if isHidden{stop("VIEW_HIDDEN")}}}
  override func willMove(toWindow newWindow:UIWindow?){if newWindow==nil{stop("VIEW_DETACHED")};super.willMove(toWindow:newWindow)}
  override func didMoveToWindow(){super.didMoveToWindow();commitProps()}
  func commitProps(){dispatchPrecondition(condition:.onQueue(.main));if !active && !pending && !frozen.isEmpty && requestedOptions != frozen{clearIdle()};if (active||pending)&&(!requestedRunning||requestedOptions != frozen){stop("WORKSPACE_CHANGED");return};if !active && !pending && requestedRunning && window != nil && bounds.width>0 && bounds.height>0{start()}}
  private func start(){
    var failedRun="",failedEpoch="",failedAuthorization=""
    do{
      guard let initialData=requestedOptions.data(using:.utf8),initialData.count<=32768,let initial=try JSONSerialization.jsonObject(with:initialData) as? [String:Any] else{throw EyeCore.Failure.configuration}
      failedRun=String((initial["run_id"] as? String ?? "").prefix(128));failedEpoch=String((initial["workspace_epoch"] as? String ?? "").prefix(128));failedAuthorization=String((initial["authorization_id"] as? String ?? "").prefix(128))
      guard requestedOptions.utf8.count<=32768,let data=requestedOptions.data(using:.utf8),let o=try JSONSerialization.jsonObject(with:data) as? [String:Any],Set(o.keys)==["run_id","workspace_epoch","authorization_id","configuration_sha256","material_json","supported_phone_models","supported_os_versions","supported_native_builds","raw_recording_permission"],let id=o["run_id"] as? String,UUID(uuidString:id) != nil,!seen.contains(id),seen.count<128,let e=o["workspace_epoch"] as? String,!e.isEmpty,e.utf8.count<=128,let auth=o["authorization_id"] as? String,UUID(uuidString:auth) != nil,let hash=o["configuration_sha256"] as? String,let material=o["material_json"] as? String,let materialData=material.data(using:.utf8),hash==SHA256.hash(data:materialData).map({String(format:"%02x",$0)}).joined(),let phones=o["supported_phone_models"] as? [String],(1...64).contains(phones.count),phones.contains(eyePhoneModel()),let os=o["supported_os_versions"] as? [String],(1...64).contains(os.count),os.contains(UIDevice.current.systemVersion),let builds=o["supported_native_builds"] as? [String],(1...64).contains(builds.count),builds.contains(eyeNativeBuild()),AVCaptureDevice.authorizationStatus(for: .video) == .authorized else{throw EyeCore.Failure.configuration}
      let c=try EyeCore.config(materialData);guard c.sensor==nil else{throw EyeCore.Failure.configuration}
      let permission=o["raw_recording_permission"] as? [String:Any];if let permission{guard permission["record"] is Bool,permission["upload"] is Bool,let receipt=permission["receipt_id"] as? String,UUID(uuidString:receipt) != nil else{throw EyeCore.Failure.configuration}}
      frozen=requestedOptions;run=id;epoch=e;authorization=auth;sha=hash;config=c;recording=permission?["record"] as? Bool==true
      startWall="";generation+=1;active=true;pending=false;seen.insert(id);terminal.clear();frames=[];raw=[];flags=["PHYSICAL_ONSET_UNMEASURED","UNQUALIFIED_OPTICAL_EXTRACTOR","UNCALIBRATED_CAMERA_RESPONSE","EXPOSURE_NOT_FRAME_MATCHED"];if c.raw["stimulus_mode"] as? String=="passive_ambient_no_modulation"{flags.insert("NO_APPROVED_STIMULUS")};if c.raw["scale_basis"] as? String=="normalized"{flags.insert("NO_MILLIMETER_GEOMETRY")};firstFrame=nil;lastFrame=nil;presented=nil;stimulusFinished=false;frozenBounds=bounds
      if let stimulus=c.raw["display_stimulus"] as? [String:Any]{originalBrightness=UIScreen.main.brightness;UIScreen.main.brightness=CGFloat((stimulus["display_brightness_fraction"] as! NSNumber).doubleValue);let level=CGFloat((stimulus["baseline_gray_level"] as! NSNumber).doubleValue/255);stimulusView.backgroundColor=UIColor(white:level,alpha:1);stimulusView.isHidden=false};startWall=ISO8601DateFormatter().string(from:Date())
      let g=generation,w=EyeCameraWorker(c);worker=w;let layer=AVCaptureVideoPreviewLayer(session:w.session);layer.videoGravity = .resizeAspect;layer.frame=bounds;self.layer.insertSublayer(layer,at:0);preview=layer
      w.onFailure={[weak self] reason in DispatchQueue.main.async{guard let self,self.active,self.generation==g else{return};self.stop(reason)}}
      w.onFrame={[weak self,weak w] timestamp,dispatch,exposure,focus,iso,ae,gray,seg in DispatchQueue.main.async{defer{w?.token.release()};guard let self else{return};self.acceptFrame(g,c,timestamp,dispatch,exposure,focus,iso,ae,gray,seg)}}
      w.start();let timer=DispatchSource.makeTimerSource(queue:.main);timer.schedule(deadline: .now() + .milliseconds(20),repeating:.milliseconds(20));timer.setEventHandler{[weak self] in guard let self,self.active,self.generation==g,let last=self.lastFrame else{return};if CACurrentMediaTime()*1000-last>Double(c.gap){self.stop("FRAME_SILENCE")}};watchdog=timer;timer.resume();DispatchQueue.main.asyncAfter(deadline:.now()+2){[weak self] in guard let self,self.active,self.generation==g,self.firstFrame==nil else{return};self.stop("CAMERA_START_TIMEOUT")}
    }catch{if active||pending{stop("CAMERA_START_FAILED");return};restoreStimulus();requestedRunning=false;onComplete(EyeCore.notStarted(run:failedRun,epoch:failedEpoch,authorization:failedAuthorization,reason:"CAMERA_CONFIGURATION_UNSUPPORTED"))}
  }
  private func acceptFrame(_ g:Int,_ c:EyeCore.Config,_ timestamp:Double,_ dispatch:Double,_ exposure:Double?,_ focus:String,_ iso:Double?,_ ae:String,_ gray:[UInt8],_ seg:EyeCore.Segmentation){
    guard active,generation==g else{return}
    if firstFrame==nil{firstFrame=timestamp;if c.raw["display_stimulus"] is [String:Any]{displayLink=CADisplayLink(target:self,selector:#selector(displayFrame(_:)));displayLink?.add(to:.main,forMode:.common)};DispatchQueue.main.asyncAfter(deadline:.now()+Double(c.duration)/1000){[weak self] in guard let self,self.active,self.generation==g else{return};self.finish()}}
    if let lastFrame,timestamp<=lastFrame || timestamp-lastFrame>Double(c.gap){stop("FRAME_GAP");return};lastFrame=timestamp
    guard dispatch>=timestamp,dispatch-timestamp<=Double(c.gap) else{stop("FRAME_DISPATCH_DELAY");return}
    guard frames.count<c.maxFrames else{finish();return}
    let accepted=EyeCore.cameraMetadataQualified(exposure:exposure,focus:focus,ae:ae) ? seg:EyeCore.Segmentation(status:"invalid",reason:"CAMERA_METADATA_UNQUALIFIED"),index=frames.count
    frames.append(EyeCore.frame(sequence:index,timestamp:timestamp,dispatch:dispatch,exposure:exposure,focus:focus,iso:iso,ae:ae,evidence:"device_state_at_callback",lumaSha:SHA256.hash(data:Data(gray)).map{String(format:"%02x",$0)}.joined(),seg:accepted))
    if recording{raw.append(EyeCore.RawFrame(timestamp:timestamp,sequence:index,gray:gray))}
    onProgress(["run_id":run,"workspace_epoch":epoch,"frames":frames.count,"maximum_frames":c.maxFrames])
  }
  @objc private func displayFrame(_ link:CADisplayLink){guard active,let c=config,let first=firstFrame,let stimulus=c.raw["display_stimulus"] as? [String:Any] else{return};let stamp=link.targetTimestamp*1000
    if presented==nil,stamp>=first+(stimulus["onset_ms"] as! NSNumber).doubleValue{presented=stamp;stimulusView.backgroundColor=UIColor(white:CGFloat((stimulus["step_gray_level"] as! NSNumber).doubleValue/255),alpha:1)}
    if let presented,!stimulusFinished,stamp>=presented+(stimulus["step_duration_ms"] as! NSNumber).doubleValue{stimulusFinished=true;stimulusView.backgroundColor=UIColor(white:CGFloat((stimulus["baseline_gray_level"] as! NSNumber).doubleValue/255),alpha:1)}
  }
  private func restoreStimulus(){watchdog?.cancel();watchdog=nil;displayLink?.invalidate();displayLink=nil;stimulusView.isHidden=true;if let originalBrightness{UIScreen.main.brightness=originalBrightness};originalBrightness=nil}
  private func finish(){guard active else{return};active=false;pending=true;restoreStimulus();worker?.stop();let g=generation;DispatchQueue.main.async{[weak self] in guard let self,self.pending,self.generation==g else{return};self.pending=false;self.emit(nil)}}
  private func clearIdle(){terminal.clear();raw=[];frames=[];config=nil;frozen="";run="";epoch="";authorization="";sha=""}
  func releaseRaw(runId:String,sha:String)throws->[String:Any]{dispatchPrecondition(condition:.onQueue(.main));guard runId==run,terminal.get() != nil else{throw EyeCore.Failure.configuration};try terminal.releaseRaw(runId:runId,sha:sha);return ["released":true]}
  func stop(_ reason:String){guard active||pending else{if !["USER_CANCELED","USER_ENDED","END_CHECK","END_TASK","CANCEL_CAPTURE"].contains(reason){clearIdle()};return};active=false;pending=false;generation+=1;restoreStimulus();worker?.stop();emit(reason);if !["USER_CANCELED","USER_ENDED","END_CHECK","END_TASK","CANCEL_CAPTURE"].contains(reason){let stoppedRun=run;DispatchQueue.main.async{[weak self] in guard let self,!self.active,!self.pending,self.run==stoppedRun else{return};self.clearIdle()}}}
  func cancel(runId:String,reason:String)throws->[String:Any]{dispatchPrecondition(condition:.onQueue(.main));guard runId==run else{throw EyeCore.Failure.configuration};stop(String(reason.prefix(64)));guard let result=terminal.get() else{throw EyeCore.Failure.configuration};return result}
  private func emit(_ reason:String?){
    guard let c=config else{return};if let reason{flags.insert(reason)}
    guard !frames.isEmpty,!startWall.isEmpty else{
      raw=[];worker=nil;preview?.removeFromSuperlayer();preview=nil
      let result=EyeCore.notStarted(run:run,epoch:epoch,authorization:authorization,reason:reason ?? "CAMERA_NOT_STARTED")
      terminal.put(result);onComplete(result);requestedRunning=false;return
    }
    let values=frames.compactMap{f -> EyeCore.FrameDiameter? in guard let s=f["segmentation"] as? [String:Any],s["status"] as? String=="valid",let d=s["diameter_normalized"] as? Double,let t=f["native_timestamp_ms"] as? Double else{return nil};return EyeCore.FrameDiameter(timestamp:t,diameter:d)};let diameters=values.map{$0.diameter}
    let valid=reason==nil && diameters.count>=c.minValid && !frames.isEmpty && Double(diameters.count)/Double(frames.count)>=c.minFraction;if !valid{flags.insert("OPTICAL_QUALITY_INSUFFICIENT")}
    let camera:[String:Any]=["camera_id":c.camera,"lens_facing":c.lens,"width":c.width,"height":c.height,"output_width":c.rotation%180==0 ? c.width:c.height,"output_height":c.rotation%180==0 ? c.height:c.width,"output_rotation_degrees":c.rotation,"sensor_orientation_degrees":NSNull(),"exposure_mode":"automatic","focus_mode":"continuous_auto","phone_model":eyePhoneModel(),"os_version":UIDevice.current.systemVersion,"native_build":eyeNativeBuild()]
    let stimulusInfo:[String:Any]=["requested":c.raw["stimulus_mode"]!,"requested_onset_ms":(c.raw["display_stimulus"] as? [String:Any])?["onset_ms"] ?? NSNull(),"native_presented_at_ms":presented as Any? ?? NSNull(),"native_timestamp_method":presented != nil ? "cadisplaylink_target_timestamp" as Any:NSNull(),"physically_measured_at_ms":NSNull()]
    let evidence=EyeCore.evidence(run:run,epoch:epoch,authorization:authorization,sha:sha,status:valid ? "valid":"invalid",started:startWall,ended:ISO8601DateFormatter().string(from:Date()),clock:"avfoundation_host_clock_seconds",camera:camera,frames:frames,features:EyeCore.features(valid ? values:[],c,onset:presented).merging(["valid_frames":diameters.count,"total_frames":frames.count]){_,new in new},flags:flags.sorted(),stimulus:stimulusInfo)
    var handoff:Any=NSNull()
    if valid,recording,let bytes=try? EyeCore.raw(raw,c){var chunks:[String]=[];for offset in stride(from:0,to:bytes.count,by:196608){chunks.append(bytes.subdata(in:offset..<min(bytes.count,offset+196608)).base64EncodedString())};handoff=["format":"OTGD-EYE-ROI-v1","media_type":"application/octet-stream","sha256":SHA256.hash(data:bytes).map{String(format:"%02x",$0)}.joined(),"size_bytes":bytes.count,"chunks":chunks]}
    raw.removeAll(keepingCapacity:false);worker=nil;preview?.removeFromSuperlayer();preview=nil
    let result:[String:Any]=["run_id":run,"workspace_epoch":epoch,"authorization_id":authorization,"status":valid ? "valid":"invalid","native_result":evidence,"raw_recording":handoff];terminal.put(result);onComplete(result);requestedRunning=false
    if handoff is [String:Any]{let completedRun=run;DispatchQueue.main.asyncAfter(deadline:.now()+30){[weak self] in guard let self,!self.active,!self.pending,self.run==completedRun else{return};try? self.terminal.releaseRaw(runId:completedRun)}}
  }
}
