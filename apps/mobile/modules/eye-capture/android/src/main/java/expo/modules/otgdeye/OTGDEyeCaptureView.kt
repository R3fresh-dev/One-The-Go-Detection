package expo.modules.otgdeye

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.graphics.Color
import android.graphics.ImageFormat
import android.graphics.SurfaceTexture
import android.hardware.camera2.*
import android.media.ImageReader
import android.os.*
import android.util.Range
import android.util.Base64
import android.view.Surface
import android.view.TextureView
import android.view.View
import android.view.Choreographer
import android.widget.TextView
import androidx.core.content.ContextCompat
import expo.modules.kotlin.AppContext
import expo.modules.kotlin.views.ExpoView
import expo.modules.kotlin.viewevent.EventDispatcher
import org.json.JSONObject
import java.lang.ref.WeakReference
import java.util.UUID
import java.util.concurrent.atomic.AtomicInteger
import kotlin.math.*

object EyeViewRegistry {
  private val views=ArrayList<WeakReference<OTGDEyeCaptureView>>()
  fun add(view:OTGDEyeCaptureView){views.removeAll{it.get()==null};views.add(WeakReference(view))}
  fun stopAll(reason:String){val action={views.mapNotNull{it.get()}.forEach{it.stop(reason)}};if(Looper.myLooper()==Looper.getMainLooper())action() else Handler(Looper.getMainLooper()).post{action()}}
}
/** Process-lived executor drains late platform callbacks so originating camera handles always close. */
private object EyeCameraExecutor {val thread=HandlerThread("OTGDEyeCamera").apply{start()};val handler=Handler(thread.looper)}
private data class EyePendingFrame(val timestamp:Long,val gray:ByteArray,val segmentation:EyeCore.Segmentation)
private class EyeCameraLease(val generation:Long,val texture:SurfaceTexture){var camera:CameraDevice?=null;var session:CameraCaptureSession?=null;var reader:ImageReader?=null;var surface:Surface?=null;val matcher=EyeFrameMatcher<EyePendingFrame>();val inFlight=AtomicInteger(0)}
/** All authority/lifecycle state lives on the main looper. Camera callbacks carry a frozen generation. */
class OTGDEyeCaptureView(context:Context,private val eyeContext:AppContext):ExpoView(context,eyeContext),TextureView.SurfaceTextureListener,Choreographer.FrameCallback {
  val onProgress by EventDispatcher<Map<String,Any?>>();val onComplete by EventDispatcher<Map<String,Any?>>()
  var requestedOptions="";var requestedRunning=false
  private val main=Handler(Looper.getMainLooper());private val cameraHandler=EyeCameraExecutor.handler
  private val preview=TextureView(context);private val label=TextView(context);private val stimulusView=View(context)
  @Volatile private var cameraGeneration=0L
  private val watchdog=object:Runnable{override fun run(){if(!active)return;val c=config?:return;val last=lastFrame;if(last!=null&&SystemClock.elapsedRealtimeNanos()/1e6-last>c.gap){stop("FRAME_SILENCE");return};main.postDelayed(this,20)}}
  private var presented:Double?=null;private var originalBrightness:Float?=null;private var stimulusWindow:android.view.Window?=null;private var stimulusFinished=false
  private var generation=0L;private var active=false;private var pending=false;private var frozen="";private var run="";private var epoch="";private var authorization=""
  private val terminal=EyeTerminalCache()
  private var config:EyeCore.Config?=null;private var options:JSONObject?=null;private val seen=LinkedHashSet<String>()
  private var cameraLease:EyeCameraLease?=null
  private var startWall="";private var startClock=0.0;private var firstFrame:Double?=null;private var lastFrame:Double?=null;private var sensorOrientation:Int?=null;private var clockDomain="unknown"
  private val frames=ArrayList<Map<String,Any?>>();private val raw=ArrayList<EyeCore.RawFrame>();private val flags=LinkedHashSet<String>();private var recording=false
  private fun nativeBuild():String{val p=context.packageManager.getPackageInfo(context.packageName,0);return "${p.versionName}:${if(Build.VERSION.SDK_INT>=28)p.longVersionCode else p.versionCode.toLong()}"}
  init {setBackgroundColor(Color.rgb(10,18,30));preview.surfaceTextureListener=this;addView(preview);label.text="Reviewed eye positioning";label.setTextColor(Color.WHITE);label.setBackgroundColor(Color.rgb(10,18,30));label.contentDescription="Camera positioning; no impairment conclusion";addView(label);stimulusView.visibility=View.GONE;addView(stimulusView);EyeViewRegistry.add(this)}
  override fun onLayout(changed:Boolean,l:Int,t:Int,r:Int,b:Int){if(changed&&active)stop("LAYOUT_CHANGED");preview.layout(0,0,r-l,b-t);label.layout(0,0,r-l,min(80,b-t));stimulusView.layout(0,0,r-l,b-t);commitProps()}
  override fun onDetachedFromWindow(){stop("VIEW_DETACHED");super.onDetachedFromWindow()}
  override fun onWindowVisibilityChanged(visibility:Int){if(visibility!=View.VISIBLE)stop("VIEW_HIDDEN");super.onWindowVisibilityChanged(visibility)}
  fun commitProps(){check(Looper.myLooper()==Looper.getMainLooper());if(!active&&!pending&&frozen.isNotEmpty()&&requestedOptions!=frozen)clearIdle();if((active||pending)&&(!requestedRunning||requestedOptions!=frozen)){stop("WORKSPACE_CHANGED");return};if(!active&&!pending&&requestedRunning&&preview.isAvailable&&isAttachedToWindow&&width>0&&height>0)start()}
  private fun start(){
    var failedRun="";var failedEpoch="";var failedAuthorization=""
    try {
      require(requestedOptions.toByteArray().size<=32768);val o=JSONObject(requestedOptions);failedRun=o.optString("run_id").take(128);failedEpoch=o.optString("workspace_epoch").take(128);failedAuthorization=o.optString("authorization_id").take(128)
      require(o.keys().asSequence().toSet()==setOf("run_id","workspace_epoch","authorization_id","configuration_sha256","material_json","supported_phone_models","supported_os_versions","supported_native_builds","raw_recording_permission"))
      val id=o.getString("run_id");UUID.fromString(id);UUID.fromString(o.getString("authorization_id"));require(!seen.contains(id)&&seen.size<128)
      val e=o.getString("workspace_epoch");require(e.isNotEmpty()&&e.length<=128)
      val c=EyeCore.config(o.getString("material_json"),o.getString("configuration_sha256"))
      fun allowed(key:String,value:String){val a=o.getJSONArray(key);require(a.length() in 1..64&&(0 until a.length()).any{a.get(it)==value})}
      allowed("supported_phone_models","${Build.MANUFACTURER} ${Build.MODEL}");allowed("supported_os_versions",Build.VERSION.RELEASE);allowed("supported_native_builds",nativeBuild())
      require(ContextCompat.checkSelfPermission(context,Manifest.permission.CAMERA)==PackageManager.PERMISSION_GRANTED) {"CAMERA_PERMISSION_REQUIRED"}
      val permission=if(o.isNull("raw_recording_permission"))null else o.getJSONObject("raw_recording_permission")
      if(permission!=null){require(permission.get("record") is Boolean&&permission.get("upload") is Boolean);UUID.fromString(permission.getString("receipt_id"))}
      recording=permission?.getBoolean("record")==true
      frozen=requestedOptions;options=o;run=id;epoch=e;authorization=o.getString("authorization_id");config=c;seen.add(id);startWall="";clockDomain="unknown";generation++;cameraGeneration=generation;active=true;pending=false
      terminal.clear();frames.clear();wipeRaw();flags.clear();flags.addAll(listOf("PHYSICAL_ONSET_UNMEASURED","UNQUALIFIED_OPTICAL_EXTRACTOR","UNCALIBRATED_CAMERA_RESPONSE"));if(c.raw.getString("stimulus_mode")=="passive_ambient_no_modulation")flags.add("NO_APPROVED_STIMULUS");if(c.raw.getString("scale_basis")=="normalized")flags.add("NO_MILLIMETER_GEOMETRY");firstFrame=null;lastFrame=null;presented=null;stimulusFinished=false
      val stimulus=c.raw.optJSONObject("display_stimulus");if(stimulus!=null){val window=eyeContext.currentActivity?.window?:error("WINDOW_UNAVAILABLE");stimulusWindow=window;originalBrightness=window.attributes.screenBrightness;window.attributes=window.attributes.apply{screenBrightness=stimulus.getDouble("display_brightness_fraction").toFloat()};stimulusView.setBackgroundColor(Color.rgb(stimulus.getInt("baseline_gray_level"),stimulus.getInt("baseline_gray_level"),stimulus.getInt("baseline_gray_level")));stimulusView.visibility=View.VISIBLE}
      startWall=EyeCore.utc(System.currentTimeMillis());startClock=SystemClock.elapsedRealtimeNanos()/1e6
      val g=generation;val lease=EyeCameraLease(g,preview.surfaceTexture?:error("CAMERA_SURFACE_LOST"));cameraLease=lease;cameraHandler.post{openCamera(g,c,lease)};main.postDelayed(watchdog,20)
      main.postDelayed({if(active&&generation==g&&firstFrame==null)stop("CAMERA_START_TIMEOUT")},2000)
    } catch(e:Exception){if(active||pending){stop("CAMERA_START_FAILED");return};restoreStimulus();requestedRunning=false;onComplete(EyeCore.notStarted(failedRun,failedEpoch,failedAuthorization,"CAMERA_CONFIGURATION_UNSUPPORTED"))}
  }
  private fun openCamera(g:Long,c:EyeCore.Config,lease:EyeCameraLease){
    try {
      if(cameraGeneration!=g)return
      val manager=context.getSystemService(Context.CAMERA_SERVICE) as CameraManager;require(manager.cameraIdList.contains(c.camera))
      val chars=manager.getCameraCharacteristics(c.camera);val facing=chars.get(CameraCharacteristics.LENS_FACING)
      require(facing==if(c.lens=="front")CameraCharacteristics.LENS_FACING_FRONT else CameraCharacteristics.LENS_FACING_BACK)
      val sensor=chars.get(CameraCharacteristics.SENSOR_ORIENTATION);require(c.sensor==null||c.sensor==sensor)
      val sizes=chars.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP)?.getOutputSizes(ImageFormat.YUV_420_888)?:error("CAMERA_FORMAT_UNAVAILABLE")
      require(sizes.any{it.width==c.width&&it.height==c.height});require(c.fps==floor(c.fps))
      val rate=Range(c.fps.toInt(),c.fps.toInt());require(chars.get(CameraCharacteristics.CONTROL_AE_AVAILABLE_TARGET_FPS_RANGES)?.contains(rate)==true){"FRAME_RATE_UNSUPPORTED"}
      require(chars.get(CameraCharacteristics.CONTROL_AF_AVAILABLE_MODES)?.contains(CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_VIDEO)==true){"CONTINUOUS_FOCUS_UNSUPPORTED"}
      val clock=if(chars.get(CameraCharacteristics.SENSOR_INFO_TIMESTAMP_SOURCE)==CameraCharacteristics.SENSOR_INFO_TIMESTAMP_SOURCE_REALTIME)"elapsed_realtime_nanos" else "camera_sensor_unknown"
      require(clock=="elapsed_realtime_nanos"){"CAMERA_CLOCK_UNSUPPORTED"}
      main.post{if(active&&generation==g){sensorOrientation=sensor;clockDomain=clock}}
      val imageReader=ImageReader.newInstance(c.width,c.height,ImageFormat.YUV_420_888,3);lease.reader=imageReader
      imageReader.setOnImageAvailableListener({r ->
        if(cameraGeneration!=g)return@setOnImageAvailableListener
        val image=try{r.acquireNextImage()}catch(_:IllegalStateException){null}?:return@setOnImageAvailableListener
        if(cameraGeneration!=g){image.close();return@setOnImageAvailableListener}
        if(lease.inFlight.incrementAndGet()>3){lease.inFlight.decrementAndGet();image.close();main.post{if(active&&generation==g)stop("FRAME_QUEUE_OVERFLOW")};return@setOnImageAvailableListener}
        try {
          require(image.width==c.width&&image.height==c.height){"CAMERA_RESOLUTION_CHANGED"};val timestamp=image.timestamp;val plane=image.planes[0];val data=plane.buffer;val row=plane.rowStride;val pixel=plane.pixelStride
          val gray=EyeCore.sample(c,image.width,image.height,{x,y->data.get(y*row+x*pixel).toInt()and 255})
          val extracted=EyeCore.extract(gray,c);val matched=lease.matcher.frame(timestamp,EyePendingFrame(timestamp,gray,extracted))
          if(matched!=null)dispatchJoined(g,c,lease,matched)
          else cameraHandler.postDelayed({if(cameraGeneration==g){lease.matcher.discardFrame(timestamp)?.let{expired->expired.gray.fill(0);lease.inFlight.decrementAndGet();main.post{if(active&&generation==g)stop("FRAME_METADATA_TIMEOUT")}}}},c.gap.toLong())
        } catch(e:Exception){lease.inFlight.decrementAndGet();main.post{if(active&&generation==g)stop("FRAME_DECODE_FAILED")}} finally {image.close()}
      },cameraHandler)
      if(cameraGeneration!=g){imageReader.close();return}
      manager.openCamera(c.camera,object:CameraDevice.StateCallback(){
        override fun onOpened(device:CameraDevice){if(cameraGeneration!=g){device.close();return};lease.camera=device
          val texture=lease.texture;texture.setDefaultBufferSize(c.width,c.height);val surface=Surface(texture);lease.surface=surface
          device.createCaptureSession(listOf(surface,imageReader.surface),object:CameraCaptureSession.StateCallback(){
            override fun onConfigured(s:CameraCaptureSession){if(cameraGeneration!=g){s.close();device.close();return};lease.session=s
              try {val request=device.createCaptureRequest(CameraDevice.TEMPLATE_RECORD).apply{addTarget(surface);addTarget(imageReader.surface);set(CaptureRequest.CONTROL_AE_MODE,CaptureRequest.CONTROL_AE_MODE_ON);set(CaptureRequest.CONTROL_AE_TARGET_FPS_RANGE,rate);set(CaptureRequest.CONTROL_AF_MODE,CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_VIDEO);set(CaptureRequest.FLASH_MODE,CaptureRequest.FLASH_MODE_OFF)}.build()
                s.setRepeatingRequest(request,object:CameraCaptureSession.CaptureCallback(){override fun onCaptureCompleted(session:CameraCaptureSession,request:CaptureRequest,result:TotalCaptureResult){
                  if(cameraGeneration!=g)return
                  val stamp=result.get(CaptureResult.SENSOR_TIMESTAMP)?:return;val metadata=mapOf("exposure_duration_ms" to result.get(CaptureResult.SENSOR_EXPOSURE_TIME)?.let{it/1e6},"sensitivity_iso" to result.get(CaptureResult.SENSOR_SENSITIVITY)?.toDouble(),"autoexposure_state" to when(result.get(CaptureResult.CONTROL_AE_STATE)){CaptureResult.CONTROL_AE_STATE_INACTIVE->"inactive";CaptureResult.CONTROL_AE_STATE_SEARCHING->"searching";CaptureResult.CONTROL_AE_STATE_CONVERGED->"converged";CaptureResult.CONTROL_AE_STATE_LOCKED->"locked";CaptureResult.CONTROL_AE_STATE_FLASH_REQUIRED->"flash_required";else->"unknown"},"focus_state" to when(result.get(CaptureResult.CONTROL_AF_STATE)){CaptureResult.CONTROL_AF_STATE_PASSIVE_FOCUSED->"focused";CaptureResult.CONTROL_AF_STATE_FOCUSED_LOCKED->"focused";else->"adjusting_or_unknown"})
                  lease.matcher.metadata(stamp,metadata)?.let{dispatchJoined(g,c,lease,it)}
                }},cameraHandler)
              }catch(e:Exception){main.post{if(active&&generation==g)stop("CAMERA_SESSION_FAILED")}}
            }
            override fun onConfigureFailed(s:CameraCaptureSession){s.close();main.post{if(active&&generation==g)stop("CAMERA_FORMAT_UNSUPPORTED")}}
          },cameraHandler)
        }
        override fun onDisconnected(device:CameraDevice){device.close();main.post{if(active&&generation==g)stop("CAMERA_DISCONNECTED")}}
        override fun onError(device:CameraDevice,error:Int){device.close();main.post{if(active&&generation==g)stop("CAMERA_ERROR")}}
      },cameraHandler)
    }catch(e:Exception){main.post{if(active&&generation==g)stop(e.message?.takeIf{it.matches(Regex("[A-Z_]{1,64}"))}?:"CAMERA_UNSUPPORTED")}}
  }
  private fun dispatchJoined(g:Long,c:EyeCore.Config,lease:EyeCameraLease,matched:Pair<EyePendingFrame,Map<String,Any?>>){
    val frame=matched.first;val dispatch=SystemClock.elapsedRealtimeNanos()/1e6
    main.post{try{acceptFrame(g,c,frame.timestamp/1e6,dispatch,matched.second,frame.gray,frame.segmentation)}finally{lease.inFlight.decrementAndGet()}}
  }
  private fun acceptFrame(g:Long,c:EyeCore.Config,timestamp:Double,dispatch:Double,metadata:Map<String,Any?>?,gray:ByteArray,seg:EyeCore.Segmentation){
    if(!active||generation!=g){gray.fill(0);return}
    if(firstFrame==null){firstFrame=timestamp;if(c.raw.optJSONObject("display_stimulus")!=null)Choreographer.getInstance().postFrameCallback(this);main.postDelayed({if(active&&generation==g)finish()},c.duration.toLong())}
    val gap=lastFrame?.let{timestamp-it};if(gap!=null&&(gap<=0||gap>c.gap)){gray.fill(0);stop("FRAME_GAP");return};lastFrame=timestamp
    if(dispatch-timestamp<0||dispatch-timestamp>c.gap){gray.fill(0);stop("FRAME_DISPATCH_DELAY");return}
    if(frames.size>=c.maxFrames){gray.fill(0);finish();return}
    val exposure=metadata?.get("exposure_duration_ms") as? Double;val focus=metadata?.get("focus_state") as? String?:"unknown"
    val iso=metadata?.get("sensitivity_iso") as? Double;val ae=metadata?.get("autoexposure_state") as? String?:"unknown"
    val accepted=if(!EyeCore.cameraMetadataQualified(exposure,focus,ae))EyeCore.Segmentation("invalid","CAMERA_METADATA_UNQUALIFIED") else seg
    val index=frames.size
    frames.add(EyeCore.frame(index,timestamp,dispatch,exposure,focus,iso,ae,"capture_result_timestamp_match",EyeCore.sha(gray),accepted))
    if(recording)raw.add(EyeCore.RawFrame(timestamp,index,gray)) else gray.fill(0)
    onProgress(mapOf("run_id" to run,"workspace_epoch" to epoch,"frames" to frames.size,"maximum_frames" to c.maxFrames))
  }
  override fun doFrame(frameTimeNanos:Long){
    if(!active)return;val c=config?:return;val s=c.raw.optJSONObject("display_stimulus")?:return;val first=firstFrame?:return
    val cameraClock=frameTimeNanos/1e6+(SystemClock.elapsedRealtimeNanos()-System.nanoTime())/1e6
    if(presented==null&&cameraClock>=first+s.getInt("onset_ms")){presented=cameraClock;val level=s.getInt("step_gray_level");stimulusView.setBackgroundColor(Color.rgb(level,level,level))}
    if(presented!=null&&!stimulusFinished&&cameraClock>=presented!!+s.getInt("step_duration_ms")){stimulusFinished=true;val level=s.getInt("baseline_gray_level");stimulusView.setBackgroundColor(Color.rgb(level,level,level))}
    if(active)Choreographer.getInstance().postFrameCallback(this)
  }
  private fun restoreStimulus(){main.removeCallbacks(watchdog);Choreographer.getInstance().removeFrameCallback(this);stimulusView.visibility=View.GONE;originalBrightness?.let{brightness->stimulusWindow?.let{window->window.attributes=window.attributes.apply{screenBrightness=brightness}}};originalBrightness=null;stimulusWindow=null}
  fun destroy(){stop("VIEW_DESTROYED")}
  private fun wipeRaw(){raw.forEach{it.gray.fill(0)};raw.clear()}
  private fun releaseCamera(){val lease=cameraLease?:return;cameraLease=null;cameraHandler.post{try{lease.session?.stopRepeating()}catch(_:Exception){};lease.session?.close();lease.session=null;lease.camera?.close();lease.camera=null;lease.reader?.close();lease.reader=null;lease.surface?.release();lease.surface=null;lease.matcher.clear().forEach{it.gray.fill(0);lease.inFlight.decrementAndGet()}}}
  private fun finish(){if(!active)return;active=false;pending=true;cameraGeneration=-1;restoreStimulus();releaseCamera();val g=generation;main.post{if(pending&&generation==g){pending=false;emit(null)}}}
  private fun clearIdle(){terminal.clear();wipeRaw();frames.clear();config=null;options=null;frozen="";run="";epoch="";authorization=""}
  fun releaseRaw(runId:String,sha:String):Map<String,Any?>{require(Looper.myLooper()==Looper.getMainLooper());require(runId==run);require(terminal.get()!=null){"RUN_NOT_SETTLED"};terminal.releaseRaw(runId,sha);return mapOf("released" to true)}
  fun stop(reason:String){if(!active&&!pending){if(reason !in setOf("USER_CANCELED","USER_ENDED","END_CHECK","END_TASK","CANCEL_CAPTURE"))clearIdle();return};active=false;pending=false;generation++;cameraGeneration=-1;restoreStimulus();releaseCamera();emit(reason);if(reason !in setOf("USER_CANCELED","USER_ENDED","END_CHECK","END_TASK","CANCEL_CAPTURE")){val stoppedRun=run;main.post{if(!active&&!pending&&run==stoppedRun)clearIdle()}}}
  fun cancel(runId:String,reason:String):Map<String,Any?>{require(Looper.myLooper()==Looper.getMainLooper());require(runId==run){"RUN_MISMATCH"};stop(reason.take(64));return terminal.get()?:error("RUN_NOT_SETTLED")}
  private fun emit(reason:String?){
    val c=config?:return;if(reason!=null)flags.add(reason)
    if(frames.isEmpty()||startWall.isEmpty()||clockDomain=="unknown"){
      wipeRaw();val result=EyeCore.notStarted(run,epoch,authorization,reason?:"CAMERA_NOT_STARTED")
      terminal.put(result);onComplete(result);requestedRunning=false;return
    }
    val values=frames.mapNotNull{val s=it["segmentation"] as Map<*,*>;if(s["status"]=="valid")EyeCore.FrameDiameter(it["native_timestamp_ms"] as Double,s["diameter_normalized"] as Double) else null};val diameters=values.map{it.diameter}
    val valid=reason==null&&diameters.size>=c.minValid&&frames.isNotEmpty()&&diameters.size.toDouble()/frames.size>=c.minFraction
    if(!valid)flags.add("OPTICAL_QUALITY_INSUFFICIENT")
    val cameraInfo=mapOf("camera_id" to c.camera,"lens_facing" to c.lens,"width" to c.width,"height" to c.height,"output_width" to if(c.rotation%180==0)c.width else c.height,"output_height" to if(c.rotation%180==0)c.height else c.width,"output_rotation_degrees" to c.rotation,"sensor_orientation_degrees" to sensorOrientation,"exposure_mode" to "automatic","focus_mode" to "continuous_auto","phone_model" to "${Build.MANUFACTURER} ${Build.MODEL}","os_version" to Build.VERSION.RELEASE,"native_build" to nativeBuild())
    val stimulusInfo=mapOf("requested" to c.raw.getString("stimulus_mode"),"requested_onset_ms" to c.raw.optJSONObject("display_stimulus")?.getInt("onset_ms"),"native_presented_at_ms" to presented,"native_timestamp_method" to if(presented!=null)"choreographer_submission_elapsed_mapping" else null,"physically_measured_at_ms" to null)
    val evidence=EyeCore.evidence(run,epoch,authorization,options!!.getString("configuration_sha256"),if(valid)"valid" else "invalid",startWall,EyeCore.utc(System.currentTimeMillis()),clockDomain,cameraInfo,frames.toList(),EyeCore.features(if(valid)values else emptyList(),c,presented)+mapOf("valid_frames" to diameters.size,"total_frames" to frames.size),flags.toList(),stimulusInfo)
    var handoff:Map<String,Any?>?=null
    if(valid&&recording){val bytes=EyeCore.raw(raw,c);val chunks=ArrayList<String>();var offset=0;while(offset<bytes.size){val chunk=bytes.copyOfRange(offset,min(bytes.size,offset+196608));chunks.add(Base64.encodeToString(chunk,Base64.NO_WRAP));chunk.fill(0);offset+=196608};handoff=mapOf("format" to "OTGD-EYE-ROI-v1","media_type" to "application/octet-stream","sha256" to EyeCore.sha(bytes),"size_bytes" to bytes.size,"chunks" to chunks);bytes.fill(0)}
    wipeRaw();val result=mapOf("run_id" to run,"workspace_epoch" to epoch,"authorization_id" to authorization,"status" to if(valid)"valid" else "invalid","native_result" to evidence,"raw_recording" to handoff);terminal.put(result);onComplete(result);requestedRunning=false
    if(handoff!=null){val completedRun=run;main.postDelayed({if(!active&&!pending&&run==completedRun)terminal.releaseRaw(completedRun)},30000)}
  }
  override fun onSurfaceTextureAvailable(surface:SurfaceTexture,width:Int,height:Int){commitProps()}
  override fun onSurfaceTextureSizeChanged(surface:SurfaceTexture,width:Int,height:Int){if(active)stop("LAYOUT_CHANGED")}
  override fun onSurfaceTextureDestroyed(surface:SurfaceTexture):Boolean{stop("CAMERA_SURFACE_LOST");return true}
  override fun onSurfaceTextureUpdated(surface:SurfaceTexture){}
}
