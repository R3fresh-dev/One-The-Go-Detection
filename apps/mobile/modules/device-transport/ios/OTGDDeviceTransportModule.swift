import ExpoModulesCore
import CoreBluetooth
import AVFoundation
import UIKit

public class OTGDDeviceTransportModule: Module {
  private lazy var transport = SyntheticBLECentral { [weak self] value in self?.sendEvent("onDeviceEvent", value) }
  public func definition() -> ModuleDefinition {
    Name("OTGDDeviceTransport")
    Events("onDeviceEvent")
    Function("getAvailability") { ["available": true] }
    Function("getBluetoothPermissionStatus") { () -> String in
      // Static authorization lookup does not instantiate CBCentralManager or trigger the permission alert.
      switch CBManager.authorization {
      case .allowedAlways: return "granted"
      case .denied: return "denied"
      case .restricted: return "restricted"
      case .notDetermined: return "not_requested"
      @unknown default: return "unknown"
      }
    }
    Function("getCameraPermissionStatus") { () -> String in
      switch AVCaptureDevice.authorizationStatus(for: .video) {
      case .authorized: return "granted"
      case .denied: return "denied"
      case .restricted: return "restricted"
      case .notDetermined: return "not_requested"
      @unknown default: return "unknown"
      }
    }
    Function("monotonicNow") { ProcessInfo.processInfo.systemUptime * 1000 }
    AsyncFunction("scanAsync") { (promise: Promise) in self.transport.scan(promise) }.runOnQueue(.main)
    AsyncFunction("stopScanAsync") { self.transport.stopScan() }.runOnQueue(.main)
    AsyncFunction("connectAsync") { (id: String, promise: Promise) in self.transport.connect(id, promise: promise) }.runOnQueue(.main)
    AsyncFunction("writeAsync") { (base64: String, promise: Promise) in self.transport.write(base64, promise: promise) }.runOnQueue(.main)
    AsyncFunction("disconnectAsync") { self.transport.disconnect("DISCONNECTED") }.runOnQueue(.main)
    OnAppEntersBackground { self.transport.stopScan(); self.transport.disconnect("BACKGROUND"); self.sendEvent("onDeviceEvent", ["kind": "state", "state": "background"]) }
    OnDestroy { self.transport.stopScan(); self.transport.disconnect("MODULE_DESTROYED") }
  }
}

/** The manager is created only following a user's discovery/connect action, not at application launch. */
private final class SyntheticBLECentral: NSObject, CBCentralManagerDelegate, CBPeripheralDelegate {
  private let serviceID = CBUUID(string: "680cf5d8-5656-4f41-81c4-0f48d26f1000")
  private let capabilitiesID = CBUUID(string: "680cf5d8-5656-4f41-81c4-0f48d26f1001")
  private let commandID = CBUUID(string: "680cf5d8-5656-4f41-81c4-0f48d26f1002")
  private let eventID = CBUUID(string: "680cf5d8-5656-4f41-81c4-0f48d26f1003")
  private let emit: ([String: Any]) -> Void
  private var central: CBCentralManager?
  private var discovered: [String: CBPeripheral] = [:]
  private var peripheral: CBPeripheral?
  private var command: CBCharacteristic?
  private var eventCharacteristic: CBCharacteristic?
  private var capabilities: String?
  private var ready = false
  private var scanPromise: Promise?
  private var connectPromise: Promise?
  private var writePromise: Promise?
  private var scanTimeout: DispatchWorkItem?
  private var connectTimeout: DispatchWorkItem?
  private var writeTimeout: DispatchWorkItem?
  private var scanning = false
  init(emit: @escaping ([String: Any]) -> Void) { self.emit = emit; super.init() }
  private func reject(_ promise: Promise?, _ reason: String) { promise?.reject(reason, reason) }
  private func ensureManager() {
    if central == nil { central = CBCentralManager(delegate: self, queue: .main, options: [CBCentralManagerOptionShowPowerAlertKey: false]) }
  }
  func scan(_ promise: Promise) {
    stopScan(); discovered.removeAll(); scanPromise = promise; ensureManager()
    let timeout = DispatchWorkItem { [weak self] in
      guard let self else { return }; self.reject(self.scanPromise, "DISCOVERY_TIMEOUT"); self.scanPromise = nil; self.stopScan(); self.emit(["kind": "state", "state": "idle"])
    }
    scanTimeout = timeout; DispatchQueue.main.asyncAfter(deadline: .now() + 15, execute: timeout)
    startScanIfReady()
  }
  private func startScanIfReady() {
    guard scanPromise != nil, let central else { return }
    switch central.state {
    case .poweredOn:
      scanning = true; central.scanForPeripherals(withServices: [serviceID], options: [CBCentralManagerScanOptionAllowDuplicatesKey: false]); scanPromise?.resolve(nil); scanPromise = nil
    case .unauthorized: reject(scanPromise, "BLUETOOTH_PERMISSION_BLOCKED"); scanPromise = nil; stopScan()
    case .poweredOff: reject(scanPromise, "BLUETOOTH_POWERED_OFF"); scanPromise = nil; stopScan()
    case .unsupported: reject(scanPromise, "BLUETOOTH_UNSUPPORTED"); scanPromise = nil; stopScan()
    case .unknown, .resetting: break
    @unknown default: reject(scanPromise, "BLUETOOTH_UNSUPPORTED"); scanPromise = nil; stopScan()
    }
  }
  func stopScan() {
    scanTimeout?.cancel(); scanTimeout = nil; scanning = false; central?.stopScan()
    if scanPromise != nil { reject(scanPromise, "SCAN_CANCELED"); scanPromise = nil }
  }
  func connect(_ id: String, promise: Promise) {
    guard id.count <= 128, let target = discovered[id], let central, central.state == .poweredOn else { reject(promise, "UNKNOWN_PERIPHERAL"); return }
    stopScan(); disconnect("REPLACED_CONNECTION"); peripheral = target; target.delegate = self; connectPromise = promise
    let timeout = DispatchWorkItem { [weak self] in self?.disconnect("CONNECTION_TIMEOUT") }; connectTimeout = timeout
    DispatchQueue.main.asyncAfter(deadline: .now() + 15, execute: timeout); central.connect(target, options: nil)
  }
  func write(_ encoded: String, promise: Promise) {
    guard ready, let peripheral, let command, peripheral.state == .connected else { reject(promise, "NOT_CONNECTED"); return }
    guard writePromise == nil else { reject(promise, "CONCURRENT_NATIVE_WRITE"); return }
    guard encoded.count <= 28, let data = Data(base64Encoded: encoded), data.count >= 13, data.count <= 20, data.base64EncodedString() == encoded else { reject(promise, "INVALID_FRAGMENT"); return }
    guard peripheral.maximumWriteValueLength(for: .withResponse) >= data.count else { reject(promise, "UNSUPPORTED_MTU"); return }
    writePromise = promise
    let timeout = DispatchWorkItem { [weak self] in self?.disconnect("WRITE_TIMEOUT") }; writeTimeout = timeout
    DispatchQueue.main.asyncAfter(deadline: .now() + 5, execute: timeout); peripheral.writeValue(data, for: command, type: .withResponse)
  }
  func disconnect(_ reason: String) {
    let old = peripheral; let id = old?.identifier.uuidString
    peripheral = nil; command = nil; eventCharacteristic = nil; capabilities = nil; ready = false
    connectTimeout?.cancel(); connectTimeout = nil; writeTimeout?.cancel(); writeTimeout = nil
    reject(connectPromise, reason); connectPromise = nil; reject(writePromise, reason); writePromise = nil
    if let old { old.delegate = nil; central?.cancelPeripheralConnection(old) }
    if let id { emit(["kind": "disconnected", "peripheralId": id, "reason": reason]) }
  }
  func centralManagerDidUpdateState(_ central: CBCentralManager) {
    if central.state == .poweredOn { startScanIfReady(); return }
    let reason: String
    switch central.state { case .poweredOff: reason = "powered_off"; case .unauthorized: reason = "unauthorized"; case .unsupported: reason = "unsupported"; default: reason = "resetting" }
    if central.state != .unknown && central.state != .resetting { startScanIfReady(); stopScan(); disconnect(reason.uppercased()) }
    else if peripheral != nil { disconnect("BLUETOOTH_RESET") }
    emit(["kind": "state", "state": reason])
  }
  func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral, advertisementData: [String: Any], rssi RSSI: NSNumber) {
    guard scanning else { return }; let id = peripheral.identifier.uuidString
    guard discovered[id] != nil || discovered.count < 64 else { return }
    discovered[id] = peripheral
    let alias = String(((advertisementData[CBAdvertisementDataLocalNameKey] as? String) ?? "Unnamed OTGD peripheral").prefix(64))
    emit(["kind": "discovered", "peripheralId": id, "alias": alias, "rssi": RSSI.intValue])
  }
  func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
    guard peripheral === self.peripheral else { central.cancelPeripheralConnection(peripheral); return }
    peripheral.discoverServices([serviceID])
  }
  func centralManager(_ central: CBCentralManager, didFailToConnect peripheral: CBPeripheral, error: Error?) { if peripheral === self.peripheral { disconnect("CONNECTION_FAILED") } }
  func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) { if peripheral === self.peripheral { disconnect("LINK_DISCONNECTED") } }
  func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
    guard peripheral === self.peripheral else { return }
    guard error == nil, let service = peripheral.services?.first(where: { $0.uuid == serviceID }) else { disconnect("UNSUPPORTED_DEVICE"); return }
    peripheral.discoverCharacteristics([capabilitiesID, commandID, eventID], for: service)
  }
  func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
    guard peripheral === self.peripheral, service.uuid == serviceID else { return }
    guard error == nil, let chars = service.characteristics,
      let cap = chars.first(where: { $0.uuid == capabilitiesID }), let rx = chars.first(where: { $0.uuid == commandID }), let tx = chars.first(where: { $0.uuid == eventID }),
      cap.properties.contains(.read), rx.properties.contains(.write), tx.properties.contains(.notify) else { disconnect("UNSUPPORTED_DEVICE"); return }
    command = rx; eventCharacteristic = tx; peripheral.readValue(for: cap)
  }
  func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic, error: Error?) {
    let received = ProcessInfo.processInfo.systemUptime * 1000
    guard peripheral === self.peripheral else { return }
    guard error == nil, let value = characteristic.value else { disconnect("READ_FAILED"); return }
    if characteristic.uuid == capabilitiesID {
      guard !value.isEmpty, value.count <= 1024, let text = String(data: value, encoding: .utf8), let tx = eventCharacteristic else { disconnect("CAPABILITIES_READ_FAILED"); return }
      capabilities = text; peripheral.setNotifyValue(true, for: tx)
    } else if characteristic.uuid == eventID && ready {
      guard value.count >= 13 && value.count <= 20 else { disconnect("FRAGMENT_LENGTH"); return }
      emit(["kind": "packet", "peripheralId": peripheral.identifier.uuidString, "base64": value.base64EncodedString(), "receivedAtMonotonicMs": received])
    }
  }
  func peripheral(_ peripheral: CBPeripheral, didUpdateNotificationStateFor characteristic: CBCharacteristic, error: Error?) {
    guard peripheral === self.peripheral, characteristic.uuid == eventID else { return }
    guard error == nil, characteristic.isNotifying, let capabilities else { disconnect("SUBSCRIBE_FAILED"); return }
    connectTimeout?.cancel(); connectTimeout = nil; ready = true
    let promise = connectPromise; connectPromise = nil
    // The wire adapter intentionally uses the universal 20-byte ATT payload, even when the OS supports more.
    promise?.resolve(["peripheralId": peripheral.identifier.uuidString, "mtu": 23, "capabilities": capabilities])
  }
  func peripheral(_ peripheral: CBPeripheral, didWriteValueFor characteristic: CBCharacteristic, error: Error?) {
    guard peripheral === self.peripheral, characteristic.uuid == commandID else { return }
    guard error == nil else { disconnect("WRITE_FAILED"); return }
    writeTimeout?.cancel(); writeTimeout = nil; let promise = writePromise; writePromise = nil; promise?.resolve(nil)
  }
}
