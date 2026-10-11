package expo.modules.otgdeye
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import java.nio.ByteBuffer
import java.nio.ByteOrder

class EyeCoreTest {
  @Test fun cameraFrameAndMetadataJoinEitherOrderAndOriginCleanupRemovesOnlyItsPendingFrames(){
    val a=EyeFrameMatcher<String>();val metadata=mapOf<String,Any?>("sensitivity_iso" to 200.0,"autoexposure_state" to "converged")
    assertNull(a.frame(1L,"origin-image"));assertEquals("origin-image" to metadata,a.metadata(1L,metadata))
    assertNull(a.metadata(2L,metadata));assertEquals("second-image" to metadata,a.frame(2L,"second-image"))
    for(i in 3L..5L)assertNull(a.frame(i,"pending-$i"))
    assertThrows(IllegalArgumentException::class.java){a.frame(6L,"overflow")}
    assertEquals("pending-3",a.discardFrame(3L));assertNull(a.discardFrame(3L))
    val b=EyeFrameMatcher<String>();assertNull(b.frame(7L,"replacement-image"))
    assertEquals(listOf("pending-4","pending-5"),a.clear());assertNull(a.discardFrame(4L))
    assertEquals("replacement-image" to metadata,b.metadata(7L,metadata))
  }

  @Test fun frameMetadataPreservesObservedIsoAeAndRejectsUnsettledExposure(){
    assertTrue(EyeCore.cameraMetadataQualified(10.0,"focused","converged"));assertTrue(EyeCore.cameraMetadataQualified(10.0,"focused","locked"));assertTrue(EyeCore.cameraMetadataQualified(10.0,"focused","stable_at_callback"))
    for(ae in listOf("unknown","searching","inactive","flash_required","adjusting_at_callback"))assertFalse(EyeCore.cameraMetadataQualified(10.0,"focused",ae))
    assertFalse(EyeCore.cameraMetadataQualified(null,"focused","converged"));assertFalse(EyeCore.cameraMetadataQualified(10.0,"unknown","converged"))
    val frame=EyeCore.frame(0,1000.0,1001.0,10.0,"focused",200.0,"converged","capture_result_timestamp_match","a".repeat(64),EyeCore.Segmentation("invalid","FICTIONAL_PIXEL"))
    assertEquals(200.0,frame["sensitivity_iso"]);assertEquals("converged",frame["autoexposure_state"])
    val unavailable=EyeCore.frame(0,1000.0,1001.0,null,"unknown",null,"unknown","capture_result_timestamp_match","a".repeat(64),EyeCore.Segmentation("invalid","CAMERA_METADATA_UNQUALIFIED"))
    assertNull(unavailable["sensitivity_iso"]);assertEquals("unknown",unavailable["autoexposure_state"])
  }

  @Test fun api24CompatibleWallTimeAndNoFrameFailureNeverInventEvidence(){
    assertEquals("1970-01-01T00:00:00.000Z",EyeCore.utc(0))
    assertEquals("2026-10-11T00:00:00.123Z",EyeCore.utc(1791676800123L))
    val terminal=EyeCore.notStarted("origin-run","origin-workspace","origin-authorization","CAMERA_START_FAILED")
    assertEquals("origin-run",terminal["run_id"]);assertEquals("origin-workspace",terminal["workspace_epoch"])
    assertEquals("invalid",terminal["status"]);assertEquals("CAMERA_START_FAILED",terminal["reason"])
    assertNull(terminal["native_result"]);assertNull(terminal["raw_recording"])
    assertFalse(terminal.containsKey("started_at"));assertFalse(terminal.containsKey("clock_domain"))
    val cache=EyeTerminalCache();cache.put(terminal);assertEquals(terminal,cache.get());cache.clear();assertNull(cache.get())
  }

  private fun fixture():JSONObject=JSONObject(javaClass.classLoader!!.getResource("eye-golden-v1.json")!!.readText())
  private fun config(o:JSONObject):EyeCore.Config {val text=o.toString();return EyeCore.config(text,EyeCore.sha(text.toByteArray()))}
  @Test fun literalSyntheticPixelGoldenParity(){
    val f=fixture();val c=config(f.getJSONObject("configuration"));val vectors=f.getJSONArray("vectors")
    for(i in 0 until vectors.length()){val v=vectors.getJSONObject(i);val a=v.getJSONArray("gray");val s=EyeCore.extract(ByteArray(a.length()){a.getInt(it).toByte()},c)
      assertEquals(v.getString("name"),v.getString("status"),s.status);assertEquals(v.optString("reason").takeUnless{v.isNull("reason")},s.reason)
      if(s.status=="valid"){assertEquals(v.getInt("area"),s.area);assertEquals(v.getInt("perimeter"),s.perimeter);assertEquals(v.getDouble("center_x"),s.x!!,1e-12);assertEquals(v.getDouble("center_y"),s.y!!,1e-12);assertEquals(v.getDouble("diameter"),s.diameter!!,1e-12);assertEquals(v.getDouble("roundness"),s.roundness!!,1e-12);assertEquals(v.getDouble("contrast"),s.contrast!!,1e-12)}
    }
  }
  @Test fun reviewedResponseAndCalibratedScaleStaySeparateFromPhysicalOnset(){
    val f=fixture();val o=f.getJSONObject("configuration");val r=f.getJSONObject("response")
    o.put("scale_basis","millimeters");o.put("geometry_scale",JSONObject().put("calibration_id","FICTIONAL-GEOMETRY").put("calibration_sha256","a".repeat(64)).put("pixels_to_mm",.1).put("min_diameter_pixels",2).put("max_diameter_pixels",10).put("max_uncertainty_mm",.2))
    o.put("stimulus_mode","reviewed_display_step");o.put("display_stimulus",JSONObject().put("baseline_gray_level",20).put("step_gray_level",200).put("onset_ms",200).put("step_duration_ms",200).put("display_brightness_fraction",.4))
    o.put("response",JSONObject().put("baseline_window_ms",200).put("minimum_baseline_frames",2).put("minimum_post_frames",2).put("latency_fraction_threshold",.15).put("maximum_latency_ms",200))
    val c=config(o);val t=r.getJSONArray("timestamps");val d=r.getJSONArray("diameters");val values=(0 until t.length()).map{EyeCore.FrameDiameter(t.getDouble(it),d.getDouble(it))}
    val features=EyeCore.features(values,c,r.getDouble("onset"))
    assertEquals(.5,features["baseline_diameter_normalized"] as Double,1e-12);assertEquals(.8,features["baseline_diameter_mm"] as Double,1e-12)
    assertEquals(r.getDouble("constriction"),features["relative_constriction"] as Double,1e-12);assertEquals(r.getDouble("latency"),features["native_callback_latency_ms"] as Double,1e-12)
    assertNull(EyeCore.features(values,c,null)["native_callback_latency_ms"]);assertNull(EyeCore.features(values,c,null)["baseline_diameter_mm"])
  }
  @Test fun configurationRejectsDigestMismatchUnknownFieldsUnsafeAndUnreviewedModes(){
    val o=fixture().getJSONObject("configuration");val text=o.toString()
    assertThrows(IllegalArgumentException::class.java){EyeCore.config(text,"0".repeat(64))}
    o.put("hidden",true);assertThrows(IllegalArgumentException::class.java){config(o)};o.remove("hidden")
    o.put("duration_ms",10001);assertThrows(IllegalArgumentException::class.java){config(o)};o.put("duration_ms",1000)
    o.put("scale_basis","millimeters");assertThrows(IllegalArgumentException::class.java){config(o)};o.put("scale_basis","normalized")
    o.put("stimulus_mode","flashing");assertThrows(IllegalArgumentException::class.java){config(o)}
  }
  @Test fun samplingRotationAndRawCodecMatchLiteralBinaryGolden(){
    val f=fixture();val c=config(f.getJSONObject("configuration"));val samples=EyeCore.sample(c,16,16,{x,y->y*16+x},90)
    assertEquals(240,samples[0].toInt()and 255);assertEquals(0,samples[15].toInt()and 255)
    val pixels=f.getJSONArray("vectors").getJSONObject(0).getJSONArray("gray");val gray=ByteArray(pixels.length()){pixels.getInt(it).toByte()}
    val raw=EyeCore.raw(listOf(EyeCore.RawFrame(1000.0,0,gray),EyeCore.RawFrame(1100.0,1,gray)),c)
    assertEquals(f.getInt("raw_size"),raw.size);assertEquals(f.getString("raw_sha256"),EyeCore.sha(raw))
    val b=ByteBuffer.wrap(raw).order(ByteOrder.LITTLE_ENDIAN);b.position(EyeCore.MAGIC.size);assertEquals(16,b.short.toInt());assertEquals(16,b.short.toInt());assertEquals(2,b.int);assertEquals(1000.0,b.double,0.0)
    assertThrows(IllegalArgumentException::class.java){EyeCore.extract(ByteArray(1),c)}
  }
  @Test fun completedRawHandoffAcknowledgmentAndPrivacyStopRemoveNativeReferences(){
    val cache=EyeTerminalCache();val raw=mapOf("sha256" to "fixture-sha","chunks" to listOf("FICTIONAL-BASE64"));val result=mapOf("run_id" to "fixture-run","status" to "valid","native_result" to mapOf("physical_onset_verified" to false),"raw_recording" to raw)
    cache.put(result);assertNotNull(cache.get()!!["raw_recording"])
    assertThrows(IllegalArgumentException::class.java){cache.releaseRaw("other-run","fixture-sha")}
    assertThrows(IllegalArgumentException::class.java){cache.releaseRaw("fixture-run","wrong-sha")}
    cache.releaseRaw("fixture-run","fixture-sha");assertNull(cache.get()!!["raw_recording"]);assertEquals("valid",cache.get()!!["status"])
    cache.put(result);cache.clear();assertNull(cache.get())
  }

  @Test fun nativeProductionPayloadFactoryEmitsInteropFixture(){
    val f=fixture();val c=EyeCore.config(f.getString("configuration_canonical_json"),f.getString("configuration_sha256"));val v=f.getJSONArray("vectors").getJSONObject(0);val a=v.getJSONArray("gray");val gray=ByteArray(a.length()){a.getInt(it).toByte()};val seg=EyeCore.extract(gray,c)
    val frames=(0 until 10).map{EyeCore.frame(it,1000.0+it*100,1001.0+it*100,10.0,"focused",200.0,"converged","capture_result_timestamp_match",EyeCore.sha(gray),seg)}
    val features=EyeCore.features(frames.map{EyeCore.FrameDiameter(it["native_timestamp_ms"] as Double,seg.diameter!!)},c,null)+mapOf("valid_frames" to 10,"total_frames" to 10)
    val flags=listOf("PHYSICAL_ONSET_UNMEASURED","UNQUALIFIED_OPTICAL_EXTRACTOR","UNCALIBRATED_CAMERA_RESPONSE","NO_APPROVED_STIMULUS","NO_MILLIMETER_GEOMETRY")
    val camera=mapOf<String,Any?>("camera_id" to c.camera,"lens_facing" to c.lens,"width" to c.width,"height" to c.height,"output_width" to c.width,"output_height" to c.height,"output_rotation_degrees" to c.rotation,"sensor_orientation_degrees" to 90,"exposure_mode" to "automatic","focus_mode" to "continuous_auto","phone_model" to "FICTIONAL-PHONE","os_version" to "FICTIONAL-OS","native_build" to "0.1.0:1")
    val native=EyeCore.evidence("11111111-1111-4111-8111-111111111111","FICTIONAL-WORKSPACE","22222222-2222-4222-8222-222222222222",f.getString("configuration_sha256"),"valid","2026-10-11T00:00:00Z","2026-10-11T00:00:01Z","elapsed_realtime_nanos",camera,frames,features,flags,mapOf("requested" to "passive_ambient_no_modulation","requested_onset_ms" to null,"native_presented_at_ms" to null,"native_timestamp_method" to null,"physically_measured_at_ms" to null))
    fun json(v:Any?):Any=when(v){null->JSONObject.NULL;is Map<*,*>->JSONObject().apply{v.forEach{(k,x)->put(k as String,json(x))}};is List<*>->org.json.JSONArray(v.map{json(it)});else->v}
    val config=mapOf("material" to c.raw,"sha256" to f.getString("configuration_sha256"),"software_adapter_id" to EyeCore.ADAPTER,"configuration_id" to "FICTIONAL-OPTICAL","supported_phone_models" to listOf("FICTIONAL-PHONE"),"supported_os_versions" to listOf("FICTIONAL-OS"),"supported_native_builds" to listOf("0.1.0:1"))
    val projection=mapOf("status" to "valid","source" to "prototype_sensor","started_at" to native["started_at"],"ended_at" to native["ended_at"],"quality_flags" to flags,"capture_config_id" to "FICTIONAL-OPTICAL","camera_id" to c.camera,"frame_rate_hz" to c.fps,"scale_basis" to "normalized","baseline_diameter_mm" to null,"relative_constriction" to null,"latency_ms" to null,"raw_artifact_id" to null)
    val result=json(mapOf("notice" to "FICTIONAL NATIVE FACTORY PIXEL FIXTURE. No camera or physical qualification.","native_result" to native,"projection" to projection,"configuration" to config)) as JSONObject
    val path=System.getProperty("otgd.eye.fixture.output") ?: error("FIXTURE_OUTPUT_REQUIRED");val file=java.io.File(path);file.parentFile.mkdirs();file.writeText(result.toString(2)+"\n")
    assertEquals(EyeCore.ADAPTER,(result.getJSONObject("native_result")).getString("implementation_version"))
    val checked=javaClass.classLoader!!.getResource("native-optical-result-v1.json")!!.readText()
    fun exactJson(left:Any,right:Any,path:String){
      when{
        left is JSONObject&&right is JSONObject->{assertEquals(path,left.keys().asSequence().toSet(),right.keys().asSequence().toSet());left.keys().asSequence().forEach{exactJson(left.get(it),right.get(it),"$path.$it")}}
        left is org.json.JSONArray&&right is org.json.JSONArray->{assertEquals(path,left.length(),right.length());for(i in 0 until left.length())exactJson(left.get(i),right.get(i),"$path[$i]")}
        left is Number&&right is Number->assertEquals(path,left.toDouble(),right.toDouble(),0.0)
        else->assertEquals(path,left,right)
      }
    }
    exactJson(result,JSONObject(checked),"native-factory")
  }

}
