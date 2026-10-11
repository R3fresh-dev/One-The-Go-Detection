package expo.modules.otgdeye

import android.hardware.camera2.CameraCharacteristics
import android.hardware.camera2.CameraManager
import android.graphics.ImageFormat
import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.content.ContextCompat
import expo.modules.kotlin.modules.Module
import expo.modules.kotlin.modules.ModuleDefinition

class OTGDEyeCaptureModule : Module() {
  override fun definition() = ModuleDefinition {
    Name("OTGDEyeCapture")
    Function("getAvailability") { mapOf("available" to true,"adapter_id" to EyeCore.ADAPTER,"extractor_version" to EyeCore.EXTRACTOR,"model_eligible" to false,"phone_model" to "${Build.MANUFACTURER} ${Build.MODEL}","os_version" to Build.VERSION.RELEASE) }
    Function("cameraInventory") {
      val context=appContext.reactContext ?: throw IllegalStateException("CONTEXT_UNAVAILABLE")
      val manager=context.getSystemService(android.content.Context.CAMERA_SERVICE) as CameraManager
      manager.cameraIdList.take(16).map {id ->
        val c=manager.getCameraCharacteristics(id)
        val sizes=c.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP)?.getOutputSizes(ImageFormat.YUV_420_888)?.take(64)?.map{mapOf("width" to it.width,"height" to it.height)} ?: emptyList()
        mapOf("camera_id" to id,"lens_facing" to when(c.get(CameraCharacteristics.LENS_FACING)){CameraCharacteristics.LENS_FACING_FRONT->"front";CameraCharacteristics.LENS_FACING_BACK->"back";else->"external"},"sensor_orientation_degrees" to c.get(CameraCharacteristics.SENSOR_ORIENTATION),"sizes" to sizes,"fps_ranges" to c.get(CameraCharacteristics.CONTROL_AE_AVAILABLE_TARGET_FPS_RANGES)?.take(32)?.map{listOf(it.lower,it.upper)},"timestamp_source" to if(c.get(CameraCharacteristics.SENSOR_INFO_TIMESTAMP_SOURCE)==CameraCharacteristics.SENSOR_INFO_TIMESTAMP_SOURCE_REALTIME)"elapsed_realtime_nanos" else "unknown")
      }
    }
    Function("cameraPermission") {val c=appContext.reactContext; if(c!=null && ContextCompat.checkSelfPermission(c,Manifest.permission.CAMERA)==PackageManager.PERMISSION_GRANTED)"granted" else "not_granted"}
    OnActivityEntersBackground {EyeViewRegistry.stopAll("BACKGROUND")}
    OnActivityDestroys {EyeViewRegistry.stopAll("VIEW_DETACHED")}
    View(OTGDEyeCaptureView::class) {
      Events("onProgress","onComplete")
      Prop("optionsJson") {view:OTGDEyeCaptureView,value:String -> view.requestedOptions=value}
      Prop("running") {view:OTGDEyeCaptureView,value:Boolean -> view.requestedRunning=value}
      OnViewDidUpdateProps {view:OTGDEyeCaptureView -> view.commitProps()}
      AsyncFunction("cancel") {view:OTGDEyeCaptureView,runId:String,reason:String -> view.cancel(runId,reason)}
      AsyncFunction("releaseRaw") {view:OTGDEyeCaptureView,runId:String,sha:String -> view.releaseRaw(runId,sha)}
      OnViewDestroys {view:OTGDEyeCaptureView -> view.destroy()}
    }
  }
}
