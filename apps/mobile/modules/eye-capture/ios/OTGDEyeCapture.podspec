Pod::Spec.new do |s|
  s.name = 'OTGDEyeCapture'
  s.version = '1.0.0'
  s.summary = 'Bounded reviewed passive optical ROI acquisition'
  s.description = 'Normalized descriptive optical extraction; no stimulus or physical qualification claim.'
  s.license = { :type => 'MIT' }
  s.author = 'One-The-Go Detection'
  s.homepage = 'https://github.com/R3fresh-dev/One-The-Go-Detection'
  s.platforms = { :ios => '16.4' }
  s.source = { :git => 'https://github.com/R3fresh-dev/One-The-Go-Detection.git' }
  s.static_framework = true
  s.dependency 'ExpoModulesCore'
  s.source_files = '**/*.{h,m,mm,swift}'
  s.swift_version = '5.9'
  s.pod_target_xcconfig = { 'DEFINES_MODULE' => 'YES' }
end
