import ExpoModulesCore

public class OTGDReactionTaskModule: Module {
  public func definition() -> ModuleDefinition {
    Name("OTGDReactionTask")
    Function("getAvailability") {
      ["available": true, "platform": "ios", "configurationId": ReactionConfig.id,
       "configurationSha256": ReactionConfig.sha256, "modelEligible": false, "reason": NSNull()] as [String: Any]
    }
    OnAppEntersBackground { ReactionViewRegistry.stopAll("BACKGROUND") }
    View(OTGDReactionTaskView.self) {
      Events("onProgress", "onComplete")
      Prop("runId") { (view: OTGDReactionTaskView, value: String) in view.requestedRunId = value }
      Prop("seed") { (view: OTGDReactionTaskView, value: Double) in view.requestedSeed = value }
      Prop("running") { (view: OTGDReactionTaskView, value: Bool) in view.requestedRunning = value }
      Prop("configurationId") { (view: OTGDReactionTaskView, value: String) in view.requestedConfigurationId = value }
      Prop("configurationSha256") { (view: OTGDReactionTaskView, value: String) in view.requestedConfigurationHash = value }
      Prop("workspaceEpoch") { (view: OTGDReactionTaskView, value: String) in view.requestedEpoch = value }
      OnViewDidUpdateProps { (view: OTGDReactionTaskView) in view.commitProps() }
      AsyncFunction("cancel") { (view: OTGDReactionTaskView, runId: String, reason: String) -> [String: Any] in
        return try view.cancel(runId: runId, reason: reason)
      }
    }
  }
}
