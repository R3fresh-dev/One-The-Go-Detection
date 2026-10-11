#!/usr/bin/env python3
"""Build the generated iOS app with the selected Xcode. No signing or cloud credentials."""
from __future__ import annotations
import json
import pathlib
import subprocess

mobile = pathlib.Path(__file__).resolve().parents[2]
workspaces = list((mobile / "ios").glob("*.xcworkspace"))
if len(workspaces) != 1:
    raise SystemExit("Expected exactly one generated iOS workspace")
workspace = workspaces[0]
listing = subprocess.run(["xcodebuild", "-workspace", str(workspace), "-list", "-json"], check=True, text=True, capture_output=True)
data = json.loads(listing.stdout)
schemes = data.get("workspace", {}).get("schemes", [])
if workspace.stem not in schemes:
    raise SystemExit("Generated app scheme missing from Xcode workspace")
derived = mobile / "native-build" / "ios"
subprocess.run([
    "xcodebuild", "-workspace", str(workspace), "-scheme", workspace.stem,
    "-configuration", "Release", "-sdk", "iphonesimulator", "-destination", "generic/platform=iOS Simulator",
    "-derivedDataPath", str(derived), "CODE_SIGNING_ALLOWED=NO", "build",
], check=True, cwd=mobile)
apps = list((derived / "Build/Products/Release-iphonesimulator").glob("*.app"))
if len(apps) != 1 or not (apps[0] / "main.jsbundle").is_file():
    raise SystemExit("Expected one simulator app with its embedded JavaScript bundle")
subprocess.run(["ditto", "-c", "-k", "--keepParent", str(apps[0]), str(mobile / "native-build/otgd-ios-simulator.app.zip")], check=True)
print("Built an unsigned simulator app with bundled JavaScript. Physical device timing remains unqualified.")
