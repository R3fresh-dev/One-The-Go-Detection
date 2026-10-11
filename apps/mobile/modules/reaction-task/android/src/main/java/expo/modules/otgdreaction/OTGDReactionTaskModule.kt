package expo.modules.otgdreaction

import expo.modules.kotlin.modules.Module
import expo.modules.kotlin.modules.ModuleDefinition

class OTGDReactionTaskModule : Module() {
  override fun definition() = ModuleDefinition {
    Name("OTGDReactionTask")
    Function("getAvailability") {
      mapOf("available" to true, "platform" to "android", "configurationId" to ReactionConfig.ID,
        "configurationSha256" to ReactionConfig.SHA256, "modelEligible" to false, "reason" to null)
    }
    OnActivityEntersBackground { ReactionViewRegistry.stopAll("BACKGROUND") }
    OnActivityDestroys { ReactionViewRegistry.stopAll("VIEW_DETACHED") }
    View(OTGDReactionTaskView::class) {
      Events("onProgress", "onComplete")
      Prop("runId") { view: OTGDReactionTaskView, value: String -> view.requestedRunId = value }
      Prop("seed") { view: OTGDReactionTaskView, value: Double -> view.requestedSeed = value }
      Prop("running") { view: OTGDReactionTaskView, value: Boolean -> view.requestedRunning = value }
      Prop("configurationId") { view: OTGDReactionTaskView, value: String -> view.requestedConfigurationId = value }
      Prop("configurationSha256") { view: OTGDReactionTaskView, value: String -> view.requestedConfigurationHash = value }
      Prop("workspaceEpoch") { view: OTGDReactionTaskView, value: String -> view.requestedEpoch = value }
      OnViewDidUpdateProps { view: OTGDReactionTaskView -> view.commitProps() }
      AsyncFunction("cancel") { view: OTGDReactionTaskView, runId: String, reason: String -> view.cancel(runId, reason) }
      OnViewDestroys { view: OTGDReactionTaskView -> view.stop("VIEW_DETACHED") }
    }
  }
}
