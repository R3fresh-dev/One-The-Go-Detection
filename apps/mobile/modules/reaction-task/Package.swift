// swift-tools-version: 5.9
import PackageDescription
let package = Package(
  name: "OTGDReactionCore",
  platforms: [.macOS(.v13), .iOS("16.4")],
  products: [.library(name: "OTGDReactionCore", targets: ["OTGDReactionCore"])],
  targets: [
    .target(name: "OTGDReactionCore", path: "ios", exclude: ["OTGDReactionTaskModule.swift", "OTGDReactionTaskView.swift", "OTGDReactionTask.podspec"], sources: ["ReactionCore.swift"]),
    .testTarget(name: "OTGDReactionCoreTests", dependencies: ["OTGDReactionCore"], path: "tests/swift")
  ]
)
