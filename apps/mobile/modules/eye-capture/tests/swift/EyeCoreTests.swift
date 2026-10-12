import XCTest
@testable import OTGDEyeCore
final class EyeCoreTests:XCTestCase {
  func testDeferredCleanupRetainsOnlyItsOriginAfterViewReleasesOwner() {
    final class Owner {var stopped=false}
    let queue=DispatchQueue(label:"fictional-eye-cleanup-test"),blocked=DispatchSemaphore(value:0),entered=DispatchSemaphore(value:0),done=expectation(description:"origin stopped after release")
    queue.async{entered.signal();blocked.wait()};XCTAssertEqual(entered.wait(timeout:.now()+2),.success)
    var owner:Owner?=Owner();weak var retained=owner
    EyeCore.retainedCleanup(owner!,on:queue){origin in origin.stopped=true;done.fulfill()}
    owner=nil;XCTAssertNotNil(retained);blocked.signal();wait(for:[done],timeout:2)
    queue.sync{};XCTAssertNil(retained)
  }

  func testFrameMetadataPreservesObservedIsoAeWithoutFrameQualification() {
    XCTAssertTrue(EyeCore.cameraMetadataQualified(exposure:10,focus:"focused",ae:"stable_at_callback"))
    for ae in ["unknown","searching","inactive","flash_required","adjusting_at_callback"]{XCTAssertFalse(EyeCore.cameraMetadataQualified(exposure:10,focus:"focused",ae:ae))}
    XCTAssertFalse(EyeCore.cameraMetadataQualified(exposure:nil,focus:"focused",ae:"stable_at_callback"))
    let frame=EyeCore.frame(sequence:0,timestamp:1000,dispatch:1001,exposure:10,focus:"focused",iso:200,ae:"stable_at_callback",evidence:"device_state_at_callback",lumaSha:String(repeating:"a",count:64),seg:EyeCore.Segmentation(status:"invalid",reason:"FICTIONAL_PIXEL"))
    XCTAssertEqual(frame["sensitivity_iso"] as? Double,200);XCTAssertEqual(frame["autoexposure_state"] as? String,"stable_at_callback");XCTAssertEqual(frame["exposure_evidence"] as? String,"device_state_at_callback")
    let unknown=EyeCore.frame(sequence:0,timestamp:1000,dispatch:1001,exposure:nil,focus:"unknown",iso:nil,ae:"unknown",evidence:"device_state_at_callback",lumaSha:String(repeating:"a",count:64),seg:EyeCore.Segmentation(status:"invalid",reason:"CAMERA_METADATA_UNQUALIFIED"))
    XCTAssertTrue(unknown["sensitivity_iso"] is NSNull)
  }

  func testNoFrameFailureHasNoInventedAcquisitionEvidence() {
    let terminal=EyeCore.notStarted(run:"origin-run",epoch:"origin-workspace",authorization:"origin-authorization",reason:"CAMERA_START_FAILED")
    XCTAssertEqual(terminal["run_id"] as? String,"origin-run");XCTAssertEqual(terminal["workspace_epoch"] as? String,"origin-workspace")
    XCTAssertEqual(terminal["status"] as? String,"invalid");XCTAssertEqual(terminal["reason"] as? String,"CAMERA_START_FAILED")
    XCTAssertTrue(terminal["native_result"] is NSNull);XCTAssertTrue(terminal["raw_recording"] is NSNull)
    XCTAssertNil(terminal["started_at"]);XCTAssertNil(terminal["clock_domain"])
    let cache=EyeTerminalCache();cache.put(terminal);XCTAssertEqual(cache.get()?["status"] as? String,"invalid");cache.clear();XCTAssertNil(cache.get())
  }

  func fixture() throws -> [String:Any] {
    let url=URL(fileURLWithPath:#filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent().appendingPathComponent("fixtures/eye-golden-v1.json")
    return try JSONSerialization.jsonObject(with:Data(contentsOf:url)) as! [String:Any]
  }
  func config(_ o:[String:Any]) throws -> EyeCore.Config {try EyeCore.config(JSONSerialization.data(withJSONObject:o,options:[.sortedKeys]))}
  func testLiteralSyntheticPixelGoldenParity() throws {
    let f=try fixture(),c=try config(f["configuration"] as! [String:Any])
    for v in f["vectors"] as! [[String:Any]] {let gray=(v["gray"] as! [Int]).map{UInt8($0)},s=try EyeCore.extract(gray,c)
      XCTAssertEqual(s.status,v["status"] as? String,v["name"] as! String);XCTAssertEqual(s.reason,v["reason"] as? String)
      if s.status=="valid" {XCTAssertEqual(s.area,(v["area"] as! NSNumber).intValue);XCTAssertEqual(s.perimeter,(v["perimeter"] as! NSNumber).intValue);XCTAssertEqual(s.x!,v["center_x"] as! Double,accuracy:1e-12);XCTAssertEqual(s.y!,v["center_y"] as! Double,accuracy:1e-12);XCTAssertEqual(s.diameter!,v["diameter"] as! Double,accuracy:1e-12);XCTAssertEqual(s.roundness!,v["roundness"] as! Double,accuracy:1e-12);XCTAssertEqual(s.contrast!,v["contrast"] as! Double,accuracy:1e-12)}
    }
  }
  func testReviewedResponseScaleAndMissingOnset() throws {
    let f=try fixture();var o=f["configuration"] as! [String:Any];let r=f["response"] as! [String:Any]
    o["scale_basis"]="millimeters";o["geometry_scale"]=["calibration_id":"FICTIONAL-GEOMETRY","calibration_sha256":String(repeating:"a",count:64),"pixels_to_mm":0.1,"min_diameter_pixels":2,"max_diameter_pixels":10,"max_uncertainty_mm":0.2]
    o["stimulus_mode"]="reviewed_display_step";o["display_stimulus"]=["baseline_gray_level":20,"step_gray_level":200,"onset_ms":200,"step_duration_ms":200,"display_brightness_fraction":0.4];o["response"]=["baseline_window_ms":200,"minimum_baseline_frames":2,"minimum_post_frames":2,"latency_fraction_threshold":0.15,"maximum_latency_ms":200]
    let c=try config(o),times=r["timestamps"] as! [Double],diameters=r["diameters"] as! [Double],values=zip(times,diameters).map{EyeCore.FrameDiameter(timestamp:$0.0,diameter:$0.1)},features=EyeCore.features(values,c,onset:r["onset"] as? Double)
    XCTAssertEqual(features["baseline_diameter_normalized"] as! Double,0.5,accuracy:1e-12);XCTAssertEqual(features["baseline_diameter_mm"] as! Double,0.8,accuracy:1e-12);XCTAssertEqual(features["relative_constriction"] as! Double,r["constriction"] as! Double,accuracy:1e-12);XCTAssertEqual(features["native_callback_latency_ms"] as! Double,r["latency"] as! Double,accuracy:1e-12)
    XCTAssertTrue(EyeCore.features(values,c,onset:nil)["native_callback_latency_ms"] is NSNull)
  }
  func testConfigurationFailClosedAndRawLittleEndian() throws {
    let f=try fixture();var o=f["configuration"] as! [String:Any];let c=try config(o)
    let gray=((f["vectors"] as! [[String:Any]])[0]["gray"] as! [Int]).map{UInt8($0)}
    let data=try EyeCore.raw([EyeCore.RawFrame(timestamp:1000,sequence:0,gray:gray),EyeCore.RawFrame(timestamp:1100,sequence:1,gray:gray)],c)
    XCTAssertEqual(data.count,f["raw_size"] as! Int);XCTAssertEqual(data.prefix(EyeCore.magic.count),EyeCore.magic);XCTAssertEqual(Array(data[16..<24]),[16,0,16,0,2,0,0,0])
    let samples=try EyeCore.sample(c,width:16,height:16,rotation:90){x,y in UInt8(y*16+x)};XCTAssertEqual(samples[0],240);XCTAssertEqual(samples[15],0)
    o["hidden"]=true;XCTAssertThrowsError(try config(o));o.removeValue(forKey:"hidden");o["scale_basis"]="millimeters";XCTAssertThrowsError(try config(o));XCTAssertThrowsError(try EyeCore.extract([1],c))
  }
  func testCompletedRawAcknowledgmentAndPrivacyClear() throws {
    let cache=EyeTerminalCache(),result:[String:Any]=["run_id":"fixture-run","status":"valid","raw_recording":["sha256":"fixture-sha","chunks":["FICTIONAL-BASE64"]]]
    cache.put(result);XCTAssertNotNil(cache.get()?["raw_recording"]);XCTAssertThrowsError(try cache.releaseRaw(runId:"other-run",sha:"fixture-sha"));XCTAssertThrowsError(try cache.releaseRaw(runId:"fixture-run",sha:"wrong-sha"))
    try cache.releaseRaw(runId:"fixture-run",sha:"fixture-sha");XCTAssertTrue(cache.get()?["raw_recording"] is NSNull);XCTAssertEqual(cache.get()?["status"] as? String,"valid")
    cache.put(result);cache.clear();XCTAssertNil(cache.get())
  }

  func testProductionPayloadFactoryMatchesActualKotlinDTOKeys() throws {
    let url=URL(fileURLWithPath:#filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent().appendingPathComponent("fixtures/native-optical-result-v1.json")
    let fixture=try JSONSerialization.jsonObject(with:Data(contentsOf:url)) as! [String:Any],native=fixture["native_result"] as! [String:Any]
    let payload=EyeCore.evidence(run:native["run_id"] as! String,epoch:native["workspace_epoch"] as! String,authorization:native["authorization_id"] as! String,sha:native["configuration_sha256"] as! String,status:native["status"] as! String,started:native["started_at"] as! String,ended:native["ended_at"] as! String,clock:native["clock_domain"] as! String,camera:native["camera"] as! [String:Any],frames:native["frame_events"] as! [[String:Any]],features:native["features"] as! [String:Any],flags:native["quality_flags"] as! [String],stimulus:native["stimulus"] as! [String:Any])
    XCTAssertTrue(NSDictionary(dictionary:payload).isEqual(to:native))
  }

}
