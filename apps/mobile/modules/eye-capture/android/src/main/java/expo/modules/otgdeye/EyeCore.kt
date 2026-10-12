package expo.modules.otgdeye

import org.json.JSONObject
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.security.MessageDigest
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone
import kotlin.math.*

/** Data-only reference extractor. It cannot establish a pupil identity or physical scale. */
object EyeCore {
  const val ADAPTER = "optical_roi_v1"
  const val EXTRACTOR = "otgd-dark-component-v1"
  const val RAW_CODEC = "otgd_eye_roi_v1"
  val MAGIC = "OTGD-EYE-ROI-v1\n".toByteArray(Charsets.US_ASCII)
  /** API24-compatible UTC wall clock; camera timing remains on its reported monotonic domain. */
  fun utc(milliseconds:Long):String = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'",Locale.US).apply {
    timeZone=TimeZone.getTimeZone("UTC")
  }.format(Date(milliseconds))
  /** No frame means no acquired evidence, clock identity, or raw payload may be fabricated. */
  fun notStarted(run:String,epoch:String,authorization:String,reason:String):Map<String,Any?> = mapOf(
    "run_id" to run,"workspace_epoch" to epoch,"authorization_id" to authorization,
    "status" to "invalid","reason" to reason.take(64),"native_result" to null,"raw_recording" to null)
  data class ROI(val x0: Double, val y0: Double, val x1: Double, val y1: Double)
  data class Config(val raw: JSONObject, val duration: Int, val camera: String, val lens: String,
    val width: Int, val height: Int, val fps: Double, val gap: Int, val maxFrames: Int,
    val roi: ROI, val sampleWidth: Int, val sampleHeight: Int, val threshold: Int,
    val minArea: Double, val maxArea: Double, val minRoundness: Double, val minContrast: Int,
    val edge: Int, val minValid: Int, val minFraction: Double, val rotation: Int, val sensor: Int?)
  private val KEYS = setOf("schema_version","channel","duration_ms","camera_id","stimulus_policy_id",
    "illumination_policy_id","geometry_id","frame_rate_hz","extractor_version","lens_facing","capture_width",
    "capture_height","maximum_frame_gap_ms","max_frames","roi","roi_sample_width","roi_sample_height",
    "dark_threshold","min_area_fraction","max_area_fraction","min_roundness","min_contrast_delta",
    "edge_margin_pixels","minimum_valid_frames","minimum_valid_frame_fraction","exposure_mode","focus_mode",
    "stimulus_mode","scale_basis","expected_output_rotation_degrees","expected_sensor_orientation_degrees","raw_encoding","geometry_scale","display_stimulus","response")
  fun sha(bytes: ByteArray): String = MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it.toInt() and 255) }
  fun config(json: String, expectedSha: String): Config {
    require(json.toByteArray().size <= 16384 && expectedSha.matches(Regex("[a-f0-9]{64}")) && sha(json.toByteArray()) == expectedSha) { "CONFIGURATION_SHA_MISMATCH" }
    val o = JSONObject(json)
    require(o.keys().asSequence().toSet() == KEYS) { "CONFIGURATION_FIELDS" }
    fun literal(k: String, v: String) { require(o.get(k) == v) { "CONFIGURATION_LITERAL" } }
    fun num(k: String, lo: Double, hi: Double): Double { val n=o.get(k); require(n is Number); val d=n.toDouble(); require(d.isFinite() && d>=lo && d<=hi); return d }
    fun int(k: String, lo: Int, hi: Int): Int { val d=num(k,lo.toDouble(),hi.toDouble()); require(d == floor(d)); return d.toInt() }
    fun name(k: String): String { val v=o.get(k); require(v is String && v.matches(Regex("[A-Za-z0-9][A-Za-z0-9_.:-]{0,255}"))); return v }
    literal("schema_version","1.0.0"); literal("channel","eyes"); literal("extractor_version",EXTRACTOR)
    literal("exposure_mode","automatic"); literal("focus_mode","continuous_auto"); literal("raw_encoding",RAW_CODEC)
    require(o.getString("stimulus_mode") in listOf("passive_ambient_no_modulation","reviewed_display_step"))
    require(o.getString("scale_basis") in listOf("normalized","millimeters"))
    fun nested(key:String,keys:Set<String>):JSONObject? {if(o.isNull(key))return null;val n=o.getJSONObject(key);require(n.keys().asSequence().toSet()==keys);return n}
    val geometry=nested("geometry_scale",setOf("calibration_id","calibration_sha256","pixels_to_mm","min_diameter_pixels","max_diameter_pixels","max_uncertainty_mm"))
    val stimulus=nested("display_stimulus",setOf("baseline_gray_level","step_gray_level","onset_ms","step_duration_ms","display_brightness_fraction"))
    val response=nested("response",setOf("baseline_window_ms","minimum_baseline_frames","minimum_post_frames","latency_fraction_threshold","maximum_latency_ms"))
    fun nnum(n:JSONObject,k:String,lo:Double,hi:Double,integer:Boolean=false):Double{val v=n.get(k);require(v is Number);val d=v.toDouble();require(d.isFinite()&&d>=lo&&d<=hi&&(!integer||d==floor(d)));return d}
    require((o.getString("scale_basis")=="millimeters")== (geometry!=null))
    if(geometry!=null){require(geometry.getString("calibration_sha256").matches(Regex("[a-f0-9]{64}"))&&geometry.getString("calibration_id").length in 1..256);nnum(geometry,"pixels_to_mm",0.000000001,100.0);val low=nnum(geometry,"min_diameter_pixels",0.000000001,1920.0);require(nnum(geometry,"max_diameter_pixels",low,1920.0)>low);nnum(geometry,"max_uncertainty_mm",0.000000001,100.0)}
    require((o.getString("stimulus_mode")=="reviewed_display_step")== (stimulus!=null&&response!=null))
    if(o.getString("stimulus_mode")=="passive_ambient_no_modulation")require(stimulus==null&&response==null)
    if(stimulus!=null&&response!=null){val baseline=nnum(stimulus,"baseline_gray_level",0.0,255.0,true);require(nnum(stimulus,"step_gray_level",0.0,255.0,true)!=baseline);val onset=nnum(stimulus,"onset_ms",100.0,10000.0,true);require(onset+nnum(stimulus,"step_duration_ms",100.0,10000.0,true)<=num("duration_ms",100.0,10000.0));nnum(stimulus,"display_brightness_fraction",0.000000001,1.0);nnum(response,"baseline_window_ms",100.0,onset,true);nnum(response,"minimum_baseline_frames",2.0,300.0,true);nnum(response,"minimum_post_frames",2.0,300.0,true);nnum(response,"latency_fraction_threshold",0.000000001,1.0);nnum(response,"maximum_latency_ms",1.0,10000.0,true)}
    name("stimulus_policy_id"); name("illumination_policy_id"); name("geometry_id")
    val r=o.getJSONObject("roi"); require(r.keys().asSequence().toSet() == setOf("x0","y0","x1","y1"))
    fun coord(k: String): Double { val n=r.get(k); require(n is Number); val d=n.toDouble(); require(d.isFinite()&&d in 0.0..1.0); return d }
    val roi=ROI(coord("x0"),coord("y0"),coord("x1"),coord("y1")); require(roi.x0<roi.x1&&roi.y0<roi.y1)
    val sensor=if(o.isNull("expected_sensor_orientation_degrees")) null else int("expected_sensor_orientation_degrees",0,270)
    val c=Config(o,int("duration_ms",100,10000),name("camera_id"),o.getString("lens_facing"),int("capture_width",64,1920),int("capture_height",64,1920),num("frame_rate_hz",0.001,1000.0),int("maximum_frame_gap_ms",1,1000),int("max_frames",2,300),roi,int("roi_sample_width",8,128),int("roi_sample_height",8,128),int("dark_threshold",0,254),num("min_area_fraction",0.0,1.0),num("max_area_fraction",0.0,1.0),num("min_roundness",0.0,1.0),int("min_contrast_delta",1,255),int("edge_margin_pixels",1,16),int("minimum_valid_frames",2,300),num("minimum_valid_frame_fraction",0.0,1.0),int("expected_output_rotation_degrees",0,270),sensor)
    require(c.lens in listOf("front","back") && c.width*c.height<=2073600 && c.sampleWidth*c.sampleHeight<=16384 && c.minArea>0 && c.maxArea<1 && c.minArea<c.maxArea && c.minFraction>0 && c.minValid<=c.maxFrames && ceil(c.duration*c.fps/1000)<=c.maxFrames && c.rotation%90==0 && (sensor==null || sensor%90==0)) { "CONFIGURATION_BOUNDS" }
    return c
  }
  fun cameraMetadataQualified(exposure:Double?,focus:String,ae:String):Boolean =
    exposure!=null&&exposure.isFinite()&&exposure>0&&focus=="focused"&&ae in setOf("converged","locked","stable_at_callback")
  fun frame(sequence:Int,timestamp:Double,dispatch:Double,exposure:Double?,focus:String,iso:Double?,ae:String,evidence:String,lumaSha:String,seg:Segmentation):Map<String,Any?> = mapOf(
    "sequence" to sequence,"native_timestamp_ms" to timestamp,"dispatch_ms" to dispatch,"exposure_duration_ms" to exposure,
    "focus_state" to focus,"sensitivity_iso" to iso,"autoexposure_state" to ae,"exposure_evidence" to evidence,"roi_luma_sha256" to lumaSha,"segmentation" to seg.payload())
  data class Segmentation(val status: String, val reason: String?, val area: Int=0, val perimeter: Int=0,
    val x: Double?=null, val y: Double?=null, val diameter: Double?=null, val roundness: Double?=null, val contrast: Double?=null) {
    fun payload(): Map<String, Any?> = mapOf("status" to status,"reason" to reason,"area_pixels" to area,"perimeter_pixels" to perimeter,
      "center_x_normalized" to x,"center_y_normalized" to y,"diameter_normalized" to diameter,"roundness" to roundness,"contrast_delta" to contrast)
  }
  fun extract(gray: ByteArray, c: Config): Segmentation {
    val w=c.sampleWidth; val h=c.sampleHeight; require(gray.size==w*h)
    val visited=BooleanArray(gray.size); val candidates=ArrayList<Segmentation>(); val queue=IntArray(gray.size)
    var largestRejected="NO_DARK_COMPONENT"
    for(start in gray.indices) {
      if(visited[start] || (gray[start].toInt() and 255)>c.threshold) continue
      var head=0; var tail=1; queue[0]=start; visited[start]=true
      var area=0; var perimeter=0; var sx=0.0; var sy=0.0; var sum=0.0; var edge=false
      while(head<tail) {
        val p=queue[head++]; val x=p%w; val y=p/w; area++; sx+=x+0.5; sy+=y+0.5; sum+=gray[p].toInt() and 255
        if(x<c.edge || y<c.edge || x>=w-c.edge || y>=h-c.edge) edge=true
        for((nx,ny) in arrayOf(x-1 to y,x+1 to y,x to y-1,x to y+1)) {
          if(nx !in 0 until w || ny !in 0 until h || (gray[ny*w+nx].toInt() and 255)>c.threshold) perimeter++
          else {val n=ny*w+nx; if(!visited[n]) {visited[n]=true; queue[tail++]=n}}
        }
      }
      val fraction=area.toDouble()/gray.size; val roundness=4*PI*area/(perimeter.toDouble()*perimeter)
      var outsideSum=0.0; var outsideN=0
      for(i in gray.indices) if((gray[i].toInt() and 255)>c.threshold) {outsideSum+=gray[i].toInt() and 255; outsideN++}
      val contrast=if(outsideN==0) 0.0 else outsideSum/outsideN-sum/area
      val reason=when {edge->"EDGE_COMPONENT"; fraction<c.minArea || fraction>c.maxArea->"AREA_OUT_OF_RANGE"; roundness<c.minRoundness->"ROUNDNESS_LOW"; contrast<c.minContrast->"CONTRAST_LOW"; else->null}
      if(reason!=null) {largestRejected=reason; continue}
      candidates.add(Segmentation("valid",null,area,perimeter,sx/area/w,sy/area/h,2*sqrt(area/PI)/min(w,h),roundness,contrast))
    }
    return when(candidates.size) {0->Segmentation("invalid",largestRejected); 1->candidates[0]; else->Segmentation("invalid","AMBIGUOUS_COMPONENTS")}
  }
  /** Sample approved ROI at cell centres; rotation is applied to luminance only. */
  fun sample(c: Config, width: Int, height: Int, luminance: (Int,Int)->Int, rotation: Int=c.rotation): ByteArray {
    require(width>0&&height>0)
    return ByteArray(c.sampleWidth*c.sampleHeight) {i ->
      val u=c.roi.x0+(i%c.sampleWidth+0.5)/c.sampleWidth*(c.roi.x1-c.roi.x0)
      val v=c.roi.y0+(i/c.sampleWidth+0.5)/c.sampleHeight*(c.roi.y1-c.roi.y0)
      val (x,y)=when(rotation) {0->u to v;90->v to 1-u;180->1-u to 1-v;270->1-v to u;else->error("OUTPUT_ROTATION")}
      luminance(min(width-1,floor(x*width).toInt()),min(height-1,floor(y*height).toInt())).also {require(it in 0..255)}.toByte()
    }
  }
  fun median(values: List<Double>): Double? {if(values.isEmpty())return null; val a=values.sorted(); return if(a.size%2==1)a[a.size/2] else (a[a.size/2-1]+a[a.size/2])/2}
  data class FrameDiameter(val timestamp:Double,val diameter:Double)
  fun features(values:List<FrameDiameter>,c:Config,onset:Double?):Map<String,Any?> {
    val median=median(values.map{it.diameter});val stimulus=c.raw.optJSONObject("display_stimulus");val response=c.raw.optJSONObject("response");val geometry=c.raw.optJSONObject("geometry_scale")
    var baseline:Double?=median;var constriction:Double?=null;var latency:Double?=null
    if(stimulus!=null&&response!=null){
      baseline=null
      if(onset!=null){val prior=values.filter{it.timestamp>=onset-response.getInt("baseline_window_ms")&&it.timestamp<onset}.map{it.diameter};val after=values.filter{it.timestamp>=onset&&it.timestamp<onset+stimulus.getInt("step_duration_ms")}
        if(prior.size>=response.getInt("minimum_baseline_frames")&&after.size>=response.getInt("minimum_post_frames")){baseline=median(prior);if(baseline!=null&&baseline>0){constriction=((baseline-after.minOf{it.diameter})/baseline).coerceIn(0.0,1.0);latency=after.firstOrNull{it.timestamp-onset<=response.getInt("maximum_latency_ms")&& (baseline-it.diameter)/baseline>=response.getDouble("latency_fraction_threshold")}?.let{it.timestamp-onset}}}
      }
    }
    val pixels=baseline?.times(min(c.sampleWidth,c.sampleHeight));val mm=if(geometry!=null&&pixels!=null&&pixels>=geometry.getDouble("min_diameter_pixels")&&pixels<=geometry.getDouble("max_diameter_pixels"))pixels*geometry.getDouble("pixels_to_mm") else null
    return mapOf("median_diameter_normalized" to median,"baseline_diameter_normalized" to baseline,"baseline_diameter_mm" to mm,"relative_constriction" to constriction,"native_callback_latency_ms" to latency)
  }
  fun evidence(run:String,epoch:String,authorization:String,sha:String,status:String,started:String,ended:String,clock:String,camera:Map<String,Any?>,frames:List<Map<String,Any?>>,features:Map<String,Any?>,flags:List<String>,stimulus:Map<String,Any?>):Map<String,Any?> = mapOf(
    "schema_version" to "1.0.0","implementation_version" to ADAPTER,"extractor_version" to EXTRACTOR,
    "run_id" to run,"workspace_epoch" to epoch,"authorization_id" to authorization,"configuration_sha256" to sha,
    "status" to status,"started_at" to started,"ended_at" to ended,"clock_domain" to clock,
    "physical_onset_verified" to false,"model_eligible" to false,"stimulus" to stimulus,
    "camera" to camera,"frame_events" to frames,"features" to features,"quality_flags" to flags)
  data class RawFrame(val timestamp: Double,val sequence:Int,val gray:ByteArray)
  fun raw(frames:List<RawFrame>,c:Config):ByteArray {
    require(frames.size<=c.maxFrames && frames.all {it.gray.size==c.sampleWidth*c.sampleHeight && it.timestamp.isFinite()})
    val b=ByteBuffer.allocate(MAGIC.size+8+frames.size*(12+c.sampleWidth*c.sampleHeight)).order(ByteOrder.LITTLE_ENDIAN)
    b.put(MAGIC).putShort(c.sampleWidth.toShort()).putShort(c.sampleHeight.toShort()).putInt(frames.size)
    frames.forEach {b.putDouble(it.timestamp).putInt(it.sequence).put(it.gray)}
    return b.array()
  }
}

/** One originating terminal and temporary raw handoff. Privacy transitions remove both references. */
class EyeTerminalCache {
  private var result:Map<String,Any?>?=null
  fun put(value:Map<String,Any?>){result=value}
  fun get():Map<String,Any?>?=result
  fun releaseRaw(runId:String,sha:String?=null){val r=result?:return;require(r["run_id"]==runId);val raw=r["raw_recording"] as? Map<*,*>;if(raw!=null&&sha!=null)require(raw["sha256"]==sha);result=r+mapOf("raw_recording" to null)}
  fun clear(){result=null}
}


/** Camera2 image and TotalCaptureResult may arrive in either order on one executor. */
class EyeFrameMatcher<Frame:Any> {
  private val frames=LinkedHashMap<Long,Frame>()
  private val metadata=LinkedHashMap<Long,Map<String,Any?>>()
  fun frame(timestamp:Long,value:Frame):Pair<Frame,Map<String,Any?>>? {
    require(!frames.containsKey(timestamp)) {"DUPLICATE_CAMERA_FRAME"}
    val matched=metadata.remove(timestamp)
    if(matched!=null)return value to matched
    require(frames.size<3) {"FRAME_METADATA_QUEUE_OVERFLOW"}
    frames[timestamp]=value;return null
  }
  fun metadata(timestamp:Long,value:Map<String,Any?>):Pair<Frame,Map<String,Any?>>? {
    val matched=frames.remove(timestamp)
    if(matched!=null)return matched to value
    metadata[timestamp]=value
    while(metadata.size>16)metadata.remove(metadata.keys.first())
    return null
  }
  fun discardFrame(timestamp:Long):Frame?=frames.remove(timestamp)
  fun clear():List<Frame>{val abandoned=frames.values.toList();frames.clear();metadata.clear();return abandoned}
}
