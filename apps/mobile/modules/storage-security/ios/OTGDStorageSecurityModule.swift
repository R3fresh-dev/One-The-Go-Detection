import ExpoModulesCore
import Foundation

public class OTGDStorageSecurityModule: Module {
  public func definition() -> ModuleDefinition {
    Name("OTGDStorageSecurity")
    Function("getAvailability") { ["available":true,"platform":"ios","backupExclusion":true,"secureWindow":false] as [String:Any] }
    AsyncFunction("protectDatabaseDirectoryAsync") { (uri: String) throws -> [String:Any] in
      func fail(_ reason: String) throws -> Never { throw NSError(domain:"OTGDStorageSecurity",code:1,userInfo:[NSLocalizedDescriptionKey:reason]) }
      guard uri.count <= 2048, let supplied = URL(string:uri), supplied.isFileURL else { try fail("DIRECTORY_URI_INVALID") }
      var url = supplied.standardizedFileURL.resolvingSymlinksInPath()
      let manager = FileManager.default
      let roots = [manager.urls(for:.documentDirectory,in:.userDomainMask).first, manager.urls(for:.libraryDirectory,in:.userDomainMask).first].compactMap { $0?.standardizedFileURL.resolvingSymlinksInPath().path }
      guard roots.contains(where: { url.path.hasPrefix($0+"/") }) else { try fail("DIRECTORY_OUTSIDE_APP_STORAGE") }
      var directory: ObjCBool = false
      guard manager.fileExists(atPath:url.path,isDirectory:&directory), directory.boolValue else { try fail("DIRECTORY_MISSING") }
      var values = URLResourceValues(); values.isExcludedFromBackup = true
      try url.setResourceValues(values)
      let readback = try url.resourceValues(forKeys:[.isExcludedFromBackupKey])
      guard readback.isExcludedFromBackup == true else { try fail("BACKUP_EXCLUSION_NOT_CONFIRMED") }
      return ["excludedFromBackup":true,"method":"ios_resource_value"]
    }.runOnQueue(.main)
    AsyncFunction("enableSecureWindowAsync") { ["platform":"ios","secureWindow":false] as [String:Any] }
  }
}
