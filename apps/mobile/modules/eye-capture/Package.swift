// swift-tools-version: 5.9
import PackageDescription
let package = Package(name: "OTGDEyeCore", platforms: [.macOS(.v13), .iOS("16.4")], products: [.library(name: "OTGDEyeCore", targets: ["OTGDEyeCore"])], targets: [
  .target(name: "OTGDEyeCore", path: "ios", exclude: ["OTGDEyeCaptureModule.swift", "OTGDEyeCaptureView.swift", "OTGDEyeCapture.podspec"], sources: ["EyeCore.swift"]),
  .testTarget(name: "OTGDEyeCoreTests", dependencies: ["OTGDEyeCore"], path: "tests/swift")
])
