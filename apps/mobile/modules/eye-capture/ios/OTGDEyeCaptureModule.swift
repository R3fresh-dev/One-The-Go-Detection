import ExpoModulesCore
import AVFoundation
import UIKit
import Darwin

func eyePhoneModel() -> String {
  var system = utsname(); uname(&system)
  let capacity=MemoryLayout.size(ofValue:system.machine)
  return withUnsafePointer(to: &system.machine) {pointer in pointer.withMemoryRebound(to:CChar.self,capacity:capacity){String(cString:$0)}}
}
func eyeNativeBuild()->String{"\(Bundle.main.object(forInfoDictionaryKey:"CFBundleShortVersionString") as? String ?? "unknown"):\(Bundle.main.object(forInfoDictionaryKey:"CFBundleVersion") as? String ?? "unknown")"}
public class OTGDEyeCaptureModule: Module {
  public func definition() -> ModuleDefinition {
    Name("OTGDEyeCapture")
    Function("getAvailability") { ["available":true,"adapter_id":EyeCore.adapter,"extractor_version":EyeCore.extractor,"model_eligible":false,"phone_model":eyePhoneModel(),"os_version":UIDevice.current.systemVersion] as [String:Any] }
    Function("cameraPermission") { AVCaptureDevice.authorizationStatus(for:.video) == .authorized ? "granted" : "not_granted" }
    Function("cameraInventory") {
      let devices=AVCaptureDevice.DiscoverySession(deviceTypes:[.builtInWideAngleCamera],mediaType:.video,position:.unspecified).devices
      return devices.prefix(16).map {device -> [String:Any] in
        ["camera_id":device.uniqueID,"lens_facing":device.position == .front ? "front":"back","sensor_orientation_degrees":NSNull(),"formats":device.formats.prefix(128).map{format -> [String:Any] in let d=CMVideoFormatDescriptionGetDimensions(format.formatDescription);return ["width":d.width,"height":d.height,"fps_ranges":format.videoSupportedFrameRateRanges.map{[$0.minFrameRate,$0.maxFrameRate]}]}]
      }
    }
    OnAppEntersBackground { EyeViewRegistry.stopAll("BACKGROUND") }
    View(OTGDEyeCaptureView.self) {
      Events("onProgress","onComplete")
      Prop("optionsJson") { (view:OTGDEyeCaptureView,value:String) in view.requestedOptions=value }
      Prop("running") { (view:OTGDEyeCaptureView,value:Bool) in view.requestedRunning=value }
      OnViewDidUpdateProps { (view:OTGDEyeCaptureView) in view.commitProps() }
      AsyncFunction("cancel") { (view:OTGDEyeCaptureView,runId:String,reason:String) -> [String:Any] in try view.cancel(runId:runId,reason:reason) }
      AsyncFunction("releaseRaw") { (view:OTGDEyeCaptureView,runId:String,sha:String) -> [String:Any] in try view.releaseRaw(runId:runId,sha:sha) }
    }
  }
}
