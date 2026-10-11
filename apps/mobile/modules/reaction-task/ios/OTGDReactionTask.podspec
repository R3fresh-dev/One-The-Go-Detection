Pod::Spec.new do |s|
  s.name = 'OTGDReactionTask'
  s.version = '1.0.0'
  s.summary = 'Uncalibrated native reaction acquisition with bounded immutable evidence'
  s.description = 'Native timing and deterministic extraction; no impairment model or physical latency qualification.'
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
