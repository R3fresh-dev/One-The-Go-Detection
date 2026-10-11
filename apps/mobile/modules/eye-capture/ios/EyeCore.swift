import Foundation
import CoreFoundation

/// Bounded data-only extraction; anatomical identity and physical scale need independent qualification.
public enum EyeCore {
  public static let adapter = "optical_roi_v1"
  public static let extractor = "otgd-dark-component-v1"
  public static let rawCodec = "otgd_eye_roi_v1"
  public static let magic = Data("OTGD-EYE-ROI-v1\n".utf8)
  /// No observed frame means acquisition timestamps and evidence are absent.
  public static func notStarted(run:String,epoch:String,authorization:String,reason:String)->[String:Any] {
    ["run_id":run,"workspace_epoch":epoch,"authorization_id":authorization,"status":"invalid",
     "reason":String(reason.prefix(64)),"native_result":NSNull(),"raw_recording":NSNull()]
  }
  public enum Failure: Error { case configuration, frame }
  /// Keep only the originating owner alive until its finite shutdown block runs.
  public static func retainedCleanup<Owner:AnyObject>(_ owner:Owner,on queue:DispatchQueue,action:@escaping(Owner)->Void) {
    queue.async{action(owner)}
  }
  public static func cameraMetadataQualified(exposure:Double?,focus:String,ae:String)->Bool {
    guard let exposure,exposure.isFinite,exposure>0,focus=="focused" else{return false}
    return ["converged","locked","stable_at_callback"].contains(ae)
  }
  public static func frame(sequence:Int,timestamp:Double,dispatch:Double,exposure:Double?,focus:String,iso:Double?,ae:String,evidence:String,lumaSha:String,seg:Segmentation)->[String:Any] {
    ["sequence":sequence,"native_timestamp_ms":timestamp,"dispatch_ms":dispatch,"exposure_duration_ms":exposure as Any? ?? NSNull(),
     "focus_state":focus,"sensitivity_iso":iso as Any? ?? NSNull(),"autoexposure_state":ae,"exposure_evidence":evidence,"roi_luma_sha256":lumaSha,"segmentation":seg.payload]
  }
  public struct ROI { public let x0, y0, x1, y1: Double }
  public struct Config {
    public let raw: [String: Any]
    public let duration: Int, camera: String, lens: String, width: Int, height: Int, fps: Double, gap: Int, maxFrames: Int
    public let roi: ROI, sampleWidth: Int, sampleHeight: Int, threshold: Int
    public let minArea: Double, maxArea: Double, minRoundness: Double, minContrast: Int, edge: Int, minValid: Int, minFraction: Double
    public let rotation: Int, sensor: Int?
  }
  public static func config(_ json: Data) throws -> Config {
    guard json.count <= 16384, let o = try JSONSerialization.jsonObject(with: json) as? [String: Any] else { throw Failure.configuration }
    let keys: Set<String> = ["schema_version","channel","duration_ms","camera_id","stimulus_policy_id","illumination_policy_id","geometry_id","frame_rate_hz","extractor_version","lens_facing","capture_width","capture_height","maximum_frame_gap_ms","max_frames","roi","roi_sample_width","roi_sample_height","dark_threshold","min_area_fraction","max_area_fraction","min_roundness","min_contrast_delta","edge_margin_pixels","minimum_valid_frames","minimum_valid_frame_fraction","exposure_mode","focus_mode","stimulus_mode","scale_basis","expected_output_rotation_degrees","expected_sensor_orientation_degrees","raw_encoding","geometry_scale","display_stimulus","response"]
    guard Set(o.keys) == keys else { throw Failure.configuration }
    func num(_ key: String, _ low: Double, _ high: Double) throws -> Double {
      guard let n = o[key] as? NSNumber, CFGetTypeID(n) != CFBooleanGetTypeID(), n.doubleValue.isFinite, n.doubleValue >= low, n.doubleValue <= high else { throw Failure.configuration }; return n.doubleValue
    }
    func int(_ key: String, _ low: Int, _ high: Int) throws -> Int { let n = try num(key, Double(low), Double(high)); guard n == floor(n) else { throw Failure.configuration }; return Int(n) }
    func name(_ key: String) throws -> String { guard let v=o[key] as? String, v.range(of: "^[A-Za-z0-9][A-Za-z0-9_.:-]{0,255}$", options:.regularExpression) != nil else { throw Failure.configuration }; return v }
    for (key, value) in ["schema_version":"1.0.0","channel":"eyes","extractor_version":extractor,"exposure_mode":"automatic","focus_mode":"continuous_auto","raw_encoding":rawCodec] { guard o[key] as? String == value else { throw Failure.configuration } }
    func nested(_ key:String,_ keys:Set<String>) throws -> [String:Any]? {if o[key] is NSNull{return nil};guard let n=o[key] as? [String:Any],Set(n.keys)==keys else{throw Failure.configuration};return n}
    func nnum(_ n:[String:Any],_ k:String,_ low:Double,_ high:Double,_ integer:Bool=false)throws->Double{guard let v=n[k] as? NSNumber,CFGetTypeID(v) != CFBooleanGetTypeID(),v.doubleValue.isFinite,v.doubleValue>=low,v.doubleValue<=high,!integer || floor(v.doubleValue)==v.doubleValue else{throw Failure.configuration};return v.doubleValue}
    let geometry=try nested("geometry_scale",["calibration_id","calibration_sha256","pixels_to_mm","min_diameter_pixels","max_diameter_pixels","max_uncertainty_mm"]),stimulus=try nested("display_stimulus",["baseline_gray_level","step_gray_level","onset_ms","step_duration_ms","display_brightness_fraction"]),response=try nested("response",["baseline_window_ms","minimum_baseline_frames","minimum_post_frames","latency_fraction_threshold","maximum_latency_ms"])
    guard let scale=o["scale_basis"] as? String,["normalized","millimeters"].contains(scale),(scale=="millimeters") == (geometry != nil),let mode=o["stimulus_mode"] as? String,["passive_ambient_no_modulation","reviewed_display_step"].contains(mode),(mode=="reviewed_display_step") == (stimulus != nil && response != nil) else{throw Failure.configuration}
    if mode=="passive_ambient_no_modulation",stimulus != nil || response != nil{throw Failure.configuration}
    if let geometry{guard let hash=geometry["calibration_sha256"] as? String,hash.range(of:"^[a-f0-9]{64}$",options:.regularExpression) != nil,let id=geometry["calibration_id"] as? String,!id.isEmpty,id.count<=256 else{throw Failure.configuration};_ = try nnum(geometry,"pixels_to_mm",0.000000001,100);let low=try nnum(geometry,"min_diameter_pixels",0.000000001,1920);guard try nnum(geometry,"max_diameter_pixels",low,1920)>low else{throw Failure.configuration};_ = try nnum(geometry,"max_uncertainty_mm",0.000000001,100)}
    if let stimulus,let response{let baseline=try nnum(stimulus,"baseline_gray_level",0,255,true);guard try nnum(stimulus,"step_gray_level",0,255,true) != baseline else{throw Failure.configuration};let onset=try nnum(stimulus,"onset_ms",100,10000,true);guard try onset+nnum(stimulus,"step_duration_ms",100,10000,true)<=num("duration_ms",100,10000) else{throw Failure.configuration};_ = try nnum(stimulus,"display_brightness_fraction",0.000000001,1);_ = try nnum(response,"baseline_window_ms",100,onset,true);_ = try nnum(response,"minimum_baseline_frames",2,300,true);_ = try nnum(response,"minimum_post_frames",2,300,true);_ = try nnum(response,"latency_fraction_threshold",0.000000001,1);_ = try nnum(response,"maximum_latency_ms",1,10000,true)}
    for key in ["stimulus_policy_id","illumination_policy_id","geometry_id"] { _ = try name(key) }
    guard let r=o["roi"] as? [String:Any], Set(r.keys) == ["x0","y0","x1","y1"] else {throw Failure.configuration}
    func coord(_ key:String) throws -> Double { guard let n=r[key] as? NSNumber, CFGetTypeID(n) != CFBooleanGetTypeID(), n.doubleValue.isFinite, (0...1).contains(n.doubleValue) else {throw Failure.configuration}; return n.doubleValue }
    let roi=ROI(x0:try coord("x0"),y0:try coord("y0"),x1:try coord("x1"),y1:try coord("y1"))
    let sensor=o["expected_sensor_orientation_degrees"] is NSNull ? nil : try int("expected_sensor_orientation_degrees",0,270)
    let c=Config(raw:o,duration:try int("duration_ms",100,10000),camera:try name("camera_id"),lens:try name("lens_facing"),width:try int("capture_width",64,1920),height:try int("capture_height",64,1920),fps:try num("frame_rate_hz",0.001,1000),gap:try int("maximum_frame_gap_ms",1,1000),maxFrames:try int("max_frames",2,300),roi:roi,sampleWidth:try int("roi_sample_width",8,128),sampleHeight:try int("roi_sample_height",8,128),threshold:try int("dark_threshold",0,254),minArea:try num("min_area_fraction",0,1),maxArea:try num("max_area_fraction",0,1),minRoundness:try num("min_roundness",0,1),minContrast:try int("min_contrast_delta",1,255),edge:try int("edge_margin_pixels",1,16),minValid:try int("minimum_valid_frames",2,300),minFraction:try num("minimum_valid_frame_fraction",0,1),rotation:try int("expected_output_rotation_degrees",0,270),sensor:sensor)
    guard ["front","back"].contains(c.lens), c.width*c.height<=2073600, c.sampleWidth*c.sampleHeight<=16384, c.roi.x0<c.roi.x1,c.roi.y0<c.roi.y1,c.minArea>0,c.maxArea<1,c.minArea<c.maxArea,c.minFraction>0,c.minValid<=c.maxFrames,ceil(Double(c.duration)*c.fps/1000)<=Double(c.maxFrames),c.rotation%90==0,sensor==nil || sensor!%90==0 else {throw Failure.configuration}
    return c
  }
  public struct Segmentation {
    public let status: String, reason: String?, area: Int, perimeter: Int
    public let x: Double?, y: Double?, diameter: Double?, roundness: Double?, contrast: Double?
    public init(status:String,reason:String?,area:Int=0,perimeter:Int=0,x:Double?=nil,y:Double?=nil,diameter:Double?=nil,roundness:Double?=nil,contrast:Double?=nil) {self.status=status;self.reason=reason;self.area=area;self.perimeter=perimeter;self.x=x;self.y=y;self.diameter=diameter;self.roundness=roundness;self.contrast=contrast}
    public var payload: [String:Any] { ["status":status,"reason":reason as Any? ?? NSNull(),"area_pixels":area,"perimeter_pixels":perimeter,"center_x_normalized":x as Any? ?? NSNull(),"center_y_normalized":y as Any? ?? NSNull(),"diameter_normalized":diameter as Any? ?? NSNull(),"roundness":roundness as Any? ?? NSNull(),"contrast_delta":contrast as Any? ?? NSNull()] }
  }
  public static func extract(_ gray:[UInt8],_ c:Config) throws -> Segmentation {
    let w=c.sampleWidth,h=c.sampleHeight; guard gray.count==w*h else {throw Failure.frame}
    var visited=[Bool](repeating:false,count:gray.count),queue=[Int](repeating:0,count:gray.count),candidates:[Segmentation]=[]
    var rejected="NO_DARK_COMPONENT"
    let outside=gray.filter{Int($0)>c.threshold}; let outsideMean=outside.isEmpty ? 0 : Double(outside.reduce(0){$0+Int($1)})/Double(outside.count)
    for start in gray.indices {
      if visited[start] || Int(gray[start])>c.threshold {continue}
      var head=0,tail=1,area=0,perimeter=0,sx=0.0,sy=0.0,sum=0.0,edge=false;queue[0]=start;visited[start]=true
      while head<tail {
        let p=queue[head];head+=1;let x=p%w,y=p/w;area+=1;sx+=Double(x)+0.5;sy+=Double(y)+0.5;sum+=Double(gray[p])
        if x<c.edge || y<c.edge || x>=w-c.edge || y>=h-c.edge {edge=true}
        for (nx,ny) in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)] {
          if nx<0 || nx>=w || ny<0 || ny>=h || Int(gray[ny*w+nx])>c.threshold {perimeter+=1}
          else {let n=ny*w+nx;if !visited[n] {visited[n]=true;queue[tail]=n;tail+=1}}
        }
      }
      let fraction=Double(area)/Double(gray.count),roundness=4*Double.pi*Double(area)/Double(perimeter*perimeter),contrast=outside.isEmpty ? 0 : outsideMean-sum/Double(area)
      let reason: String? = edge ? "EDGE_COMPONENT" : fraction<c.minArea || fraction>c.maxArea ? "AREA_OUT_OF_RANGE" : roundness<c.minRoundness ? "ROUNDNESS_LOW" : contrast<Double(c.minContrast) ? "CONTRAST_LOW" : nil
      if let reason {rejected=reason;continue}
      candidates.append(Segmentation(status:"valid",reason:nil,area:area,perimeter:perimeter,x:sx/Double(area*w),y:sy/Double(area*h),diameter:2*sqrt(Double(area)/Double.pi)/Double(min(w,h)),roundness:roundness,contrast:contrast))
    }
    return candidates.isEmpty ? Segmentation(status:"invalid",reason:rejected) : candidates.count==1 ? candidates[0] : Segmentation(status:"invalid",reason:"AMBIGUOUS_COMPONENTS")
  }
  public static func sample(_ c:Config,width:Int,height:Int,rotation:Int=0,luminance:(Int,Int)->UInt8) throws -> [UInt8] {
    guard width>0,height>0,[0,90,180,270].contains(rotation) else {throw Failure.frame}
    return (0..<c.sampleWidth*c.sampleHeight).map {i in
      let u=c.roi.x0+(Double(i%c.sampleWidth)+0.5)/Double(c.sampleWidth)*(c.roi.x1-c.roi.x0),v=c.roi.y0+(Double(i/c.sampleWidth)+0.5)/Double(c.sampleHeight)*(c.roi.y1-c.roi.y0)
      let x:Double,y:Double
      switch rotation {case 90:x=v;y=1-u;case 180:x=1-u;y=1-v;case 270:x=1-v;y=u;default:x=u;y=v}
      return luminance(min(width-1,Int(floor(x*Double(width)))),min(height-1,Int(floor(y*Double(height)))))
    }
  }
  public static func median(_ values:[Double]) -> Double? {guard !values.isEmpty else {return nil};let a=values.sorted();return a.count%2==1 ? a[a.count/2] : (a[a.count/2-1]+a[a.count/2])/2}
  public struct FrameDiameter {public let timestamp:Double,diameter:Double;public init(timestamp:Double,diameter:Double){self.timestamp=timestamp;self.diameter=diameter}}
  public static func features(_ values:[FrameDiameter],_ c:Config,onset:Double?) -> [String:Any] {
    let overall=median(values.map{$0.diameter}),stimulus=c.raw["display_stimulus"] as? [String:Any],response=c.raw["response"] as? [String:Any],geometry=c.raw["geometry_scale"] as? [String:Any]
    var baseline=overall,constriction:Double?,latency:Double?
    if let stimulus,let response{baseline=nil;if let onset{let prior=values.filter{$0.timestamp>=onset-(response["baseline_window_ms"] as! NSNumber).doubleValue && $0.timestamp<onset}.map{$0.diameter},after=values.filter{$0.timestamp>=onset && $0.timestamp<onset+(stimulus["step_duration_ms"] as! NSNumber).doubleValue}
      if prior.count >= (response["minimum_baseline_frames"] as! NSNumber).intValue && after.count >= (response["minimum_post_frames"] as! NSNumber).intValue{baseline=median(prior);if let b=baseline,b>0{constriction=max(0,min(1,(b-after.map{$0.diameter}.min()!)/b));latency=after.first(where:{$0.timestamp-onset <= (response["maximum_latency_ms"] as! NSNumber).doubleValue && (b-$0.diameter)/b >= (response["latency_fraction_threshold"] as! NSNumber).doubleValue}).map{$0.timestamp-onset}}}
    }}
    var mm:Double?
    if let geometry,let baseline{let pixels=baseline*Double(min(c.sampleWidth,c.sampleHeight));if pixels >= (geometry["min_diameter_pixels"] as! NSNumber).doubleValue && pixels <= (geometry["max_diameter_pixels"] as! NSNumber).doubleValue{mm=pixels*(geometry["pixels_to_mm"] as! NSNumber).doubleValue}}
    return ["median_diameter_normalized":overall as Any? ?? NSNull(),"baseline_diameter_normalized":baseline as Any? ?? NSNull(),"baseline_diameter_mm":mm as Any? ?? NSNull(),"relative_constriction":constriction as Any? ?? NSNull(),"native_callback_latency_ms":latency as Any? ?? NSNull()]
  }
  public static func evidence(run:String,epoch:String,authorization:String,sha:String,status:String,started:String,ended:String,clock:String,camera:[String:Any],frames:[[String:Any]],features:[String:Any],flags:[String],stimulus:[String:Any])->[String:Any] {
    ["schema_version":"1.0.0","implementation_version":adapter,"extractor_version":extractor,"run_id":run,"workspace_epoch":epoch,"authorization_id":authorization,"configuration_sha256":sha,"status":status,"started_at":started,"ended_at":ended,"clock_domain":clock,"physical_onset_verified":false,"model_eligible":false,"stimulus":stimulus,"camera":camera,"frame_events":frames,"features":features,"quality_flags":flags]
  }
  public struct RawFrame {public let timestamp:Double,sequence:Int,gray:[UInt8];public init(timestamp:Double,sequence:Int,gray:[UInt8]){self.timestamp=timestamp;self.sequence=sequence;self.gray=gray}}
  public static func raw(_ frames:[RawFrame],_ c:Config) throws -> Data {
    guard frames.count<=c.maxFrames,frames.allSatisfy({$0.gray.count==c.sampleWidth*c.sampleHeight && $0.timestamp.isFinite}) else {throw Failure.frame}
    var data=magic
    func put<T:FixedWidthInteger>(_ n:T){var le=n.littleEndian;withUnsafeBytes(of:&le){data.append(contentsOf:$0)}}
    put(UInt16(c.sampleWidth));put(UInt16(c.sampleHeight));put(UInt32(frames.count))
    for f in frames {put(f.timestamp.bitPattern);put(UInt32(f.sequence));data.append(contentsOf:f.gray)}
    return data
  }
}

/// One originating terminal and temporary raw handoff; used by the native view on its main queue.
public final class EyeTerminalCache {
  private var result:[String:Any]?
  public init(){}
  public func put(_ value:[String:Any]){result=value}
  public func get()->[String:Any]?{result}
  public func releaseRaw(runId:String,sha:String?=nil)throws{guard var value=result else{return};guard value["run_id"] as? String==runId else{throw EyeCore.Failure.configuration};if let sha,let raw=value["raw_recording"] as? [String:Any],raw["sha256"] as? String != sha{throw EyeCore.Failure.configuration};value["raw_recording"]=NSNull();result=value}
  public func clear(){result=nil}
}
