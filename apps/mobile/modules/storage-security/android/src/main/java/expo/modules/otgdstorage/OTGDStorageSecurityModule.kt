package expo.modules.otgdstorage

import android.content.pm.ApplicationInfo
import android.net.Uri
import android.os.Handler
import android.os.Looper
import android.view.WindowManager
import expo.modules.kotlin.functions.Queues
import expo.modules.kotlin.modules.Module
import expo.modules.kotlin.modules.ModuleDefinition
import java.io.File

class OTGDStorageSecurityModule : Module() {
  private var secureRequested = false
  private fun secure() { if (secureRequested) appContext.currentActivity?.window?.addFlags(WindowManager.LayoutParams.FLAG_SECURE) }
  override fun definition() = ModuleDefinition {
    Name("OTGDStorageSecurity")
    Function("getAvailability") { mapOf("available" to true,"platform" to "android","backupExclusion" to true,"secureWindow" to true) }
    AsyncFunction("protectDatabaseDirectoryAsync") { uri: String ->
      val context = requireNotNull(appContext.reactContext) { "REACT_CONTEXT_UNAVAILABLE" }
      require(context.applicationInfo.flags and ApplicationInfo.FLAG_ALLOW_BACKUP == 0) { "ANDROID_BACKUP_NOT_DISABLED" }
      require(uri.length <= 2048) { "DIRECTORY_URI_INVALID" }
      val parsed = Uri.parse(uri); require(parsed.scheme == null || parsed.scheme == "file") { "DIRECTORY_URI_INVALID" }
      val path = File(requireNotNull(parsed.path)).canonicalFile
      val root = File(context.applicationInfo.dataDir).canonicalFile
      require(path.path.startsWith(root.path + File.separator)) { "DIRECTORY_OUTSIDE_APP_STORAGE" }
      require(path.isDirectory) { "DIRECTORY_MISSING" }
      mapOf("excludedFromBackup" to true,"method" to "android_backup_disabled")
    }.runOnQueue(Queues.MAIN)
    AsyncFunction("enableSecureWindowAsync") {
      requireNotNull(appContext.currentActivity) { "ACTIVITY_UNAVAILABLE" }
      secureRequested = true; secure()
      mapOf("platform" to "android","secureWindow" to (appContext.currentActivity!!.window.attributes.flags and WindowManager.LayoutParams.FLAG_SECURE != 0))
    }.runOnQueue(Queues.MAIN)
    OnActivityEntersForeground { Handler(Looper.getMainLooper()).post { secure() } }
  }
}
