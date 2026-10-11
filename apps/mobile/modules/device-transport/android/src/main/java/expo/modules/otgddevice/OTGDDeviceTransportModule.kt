package expo.modules.otgddevice

import android.Manifest
import android.bluetooth.*
import android.bluetooth.le.*
import android.content.*
import android.content.pm.PackageManager
import android.os.*
import android.util.Base64
import expo.modules.kotlin.Promise
import expo.modules.kotlin.functions.Queues
import expo.modules.kotlin.modules.Module
import expo.modules.kotlin.modules.ModuleDefinition
import java.util.UUID

/** Radio transport only. No device credential, physiological authority or source upgrading exists here. */
class OTGDDeviceTransportModule : Module() {
  private val main = Handler(Looper.getMainLooper())
  private val serviceId = UUID.fromString("680cf5d8-5656-4f41-81c4-0f48d26f1000")
  private val capId = UUID.fromString("680cf5d8-5656-4f41-81c4-0f48d26f1001")
  private val rxId = UUID.fromString("680cf5d8-5656-4f41-81c4-0f48d26f1002")
  private val txId = UUID.fromString("680cf5d8-5656-4f41-81c4-0f48d26f1003")
  private val cccdId = UUID.fromString("00002902-0000-1000-8000-00805f9b34fb")
  private val discovered = LinkedHashMap<String, BluetoothDevice>()
  private var scanning = false
  private var gatt: BluetoothGatt? = null
  private var peripheralId: String? = null
  private var rx: BluetoothGattCharacteristic? = null
  private var capabilities: String? = null
  private var ready = false
  private var connectPromise: Promise? = null
  private var writePromise: Promise? = null
  private var registered = false
  private val scanTimeout = Runnable { stopScan(); event(mapOf("kind" to "state", "state" to "idle")) }
  private val connectTimeout = Runnable { close("CONNECTION_TIMEOUT") }
  private val writeTimeout = Runnable { close("WRITE_TIMEOUT") }
  private val context: Context get() = requireNotNull(appContext.reactContext) { "REACT_CONTEXT_UNAVAILABLE" }
  private val adapter: BluetoothAdapter? get() = (context.getSystemService(Context.BLUETOOTH_SERVICE) as BluetoothManager).adapter
  private fun now() = System.nanoTime() / 1_000_000.0
  private fun event(value: Map<String, Any?>) { sendEvent("onDeviceEvent", value) }
  private fun reject(promise: Promise, reason: String) { promise.reject(reason, reason, null) }
  private fun permitted(scan: Boolean): Boolean = if (Build.VERSION.SDK_INT >= 31) {
    context.checkSelfPermission(Manifest.permission.BLUETOOTH_CONNECT) == PackageManager.PERMISSION_GRANTED && (!scan || context.checkSelfPermission(Manifest.permission.BLUETOOTH_SCAN) == PackageManager.PERMISSION_GRANTED)
  } else !scan || context.checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
  private fun radio(promise: Promise, scan: Boolean): Boolean {
    if (!permitted(scan)) { reject(promise, "BLUETOOTH_PERMISSION_DENIED"); return false }
    if (adapter == null) { reject(promise, "BLUETOOTH_UNSUPPORTED"); return false }
    if (adapter?.isEnabled != true) { reject(promise, "BLUETOOTH_POWERED_OFF"); return false }
    ensureReceiver(); return true
  }
  override fun definition() = ModuleDefinition {
    Name("OTGDDeviceTransport")
    Events("onDeviceEvent")
    Function("getAvailability") { mapOf("available" to context.packageManager.hasSystemFeature(PackageManager.FEATURE_BLUETOOTH_LE)) }
    Function("monotonicNow") { now() }
    AsyncFunction("scanAsync") { promise: Promise ->
      if (radio(promise, true)) {
        try {
          stopScan(); discovered.clear()
          val scanner = adapter?.bluetoothLeScanner
          if (scanner == null) reject(promise, "BLUETOOTH_POWERED_OFF") else {
            val filter = ScanFilter.Builder().setServiceUuid(ParcelUuid(serviceId)).build()
            scanning = true
            scanner.startScan(listOf(filter), ScanSettings.Builder().setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY).build(), scanCallback)
            main.postDelayed(scanTimeout, 15_000); promise.resolve(null)
          }
        } catch (_: SecurityException) { scanning = false; reject(promise, "BLUETOOTH_PERMISSION_DENIED") }
      }
    }.runOnQueue(Queues.MAIN)
    AsyncFunction("stopScanAsync") { stopScan() }.runOnQueue(Queues.MAIN)
    AsyncFunction("connectAsync") { id: String, promise: Promise ->
      if (radio(promise, false)) {
        val device = discovered[id]
        if (id.length > 128 || device == null) reject(promise, "UNKNOWN_PERIPHERAL") else {
          stopScan(); close("REPLACED_CONNECTION"); peripheralId = id; connectPromise = promise
          try { gatt = device.connectGatt(context, false, callback, BluetoothDevice.TRANSPORT_LE); main.postDelayed(connectTimeout, 15_000) }
          catch (_: SecurityException) { close("BLUETOOTH_PERMISSION_DENIED") }
        }
      }
    }.runOnQueue(Queues.MAIN)
    AsyncFunction("writeAsync") { encoded: String, promise: Promise ->
      val connection = gatt; val characteristic = rx
      if (!ready || connection == null || characteristic == null) reject(promise, "NOT_CONNECTED")
      else if (writePromise != null) reject(promise, "CONCURRENT_NATIVE_WRITE")
      else if (!permitted(false)) { reject(promise, "BLUETOOTH_PERMISSION_DENIED"); close("BLUETOOTH_PERMISSION_DENIED") }
      else {
        try {
          require(encoded.length <= 28) { "FRAGMENT_TOO_LARGE" }
          val bytes = Base64.decode(encoded, Base64.NO_WRAP)
          require(bytes.size in 13..20 && Base64.encodeToString(bytes, Base64.NO_WRAP) == encoded) { "INVALID_FRAGMENT" }
          writePromise = promise
          val accepted = if (Build.VERSION.SDK_INT >= 33) connection.writeCharacteristic(characteristic, bytes, BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT) == BluetoothStatusCodes.SUCCESS
          else { @Suppress("DEPRECATION") characteristic.setValue(bytes); characteristic.writeType = BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT; @Suppress("DEPRECATION") connection.writeCharacteristic(characteristic) }
          if (!accepted) close("WRITE_REFUSED") else main.postDelayed(writeTimeout, 5000)
        } catch (_: SecurityException) { reject(promise, "BLUETOOTH_PERMISSION_DENIED"); close("BLUETOOTH_PERMISSION_DENIED") }
        catch (_: IllegalArgumentException) { reject(promise, "INVALID_FRAGMENT") }
      }
    }.runOnQueue(Queues.MAIN)
    AsyncFunction("disconnectAsync") { close("DISCONNECTED") }.runOnQueue(Queues.MAIN)
    OnActivityEntersBackground { main.post { stopScan(); close("BACKGROUND"); event(mapOf("kind" to "state", "state" to "background")) } }
    OnDestroy { main.post { stopScan(); close("MODULE_DESTROYED"); if (registered) { runCatching { context.unregisterReceiver(radioReceiver) }; registered = false } } }
  }
  private fun ensureReceiver() {
    if (registered) return
    val filter = IntentFilter(BluetoothAdapter.ACTION_STATE_CHANGED)
    if (Build.VERSION.SDK_INT >= 33) context.registerReceiver(radioReceiver, filter, Context.RECEIVER_NOT_EXPORTED)
    else { @Suppress("DEPRECATION") context.registerReceiver(radioReceiver, filter) }
    registered = true
  }
  private val radioReceiver = object : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
      if (intent?.getIntExtra(BluetoothAdapter.EXTRA_STATE, BluetoothAdapter.ERROR) != BluetoothAdapter.STATE_ON) {
        stopScan(); close("BLUETOOTH_POWERED_OFF"); event(mapOf("kind" to "state", "state" to "powered_off"))
      }
    }
  }
  private fun stopScan() { main.removeCallbacks(scanTimeout); if (scanning) { scanning = false; runCatching { adapter?.bluetoothLeScanner?.stopScan(scanCallback) } } }
  private val scanCallback = object : ScanCallback() {
    override fun onScanResult(callbackType: Int, result: ScanResult) { main.post {
      if (!scanning) return@post
      try {
        val id = result.device.address
        if (discovered.containsKey(id) || discovered.size < 64) {
          discovered[id] = result.device
          event(mapOf("kind" to "discovered", "peripheralId" to id, "alias" to (result.scanRecord?.deviceName ?: "Unnamed OTGD peripheral").take(64), "rssi" to result.rssi))
        }
      } catch (_: SecurityException) { stopScan(); event(mapOf("kind" to "state", "state" to "unauthorized")) }
    } }
    override fun onScanFailed(errorCode: Int) { main.post { stopScan(); event(mapOf("kind" to "state", "state" to "unsupported")) } }
  }
  private fun close(reason: String) {
    val old = gatt; val id = peripheralId
    gatt = null; peripheralId = null; rx = null; capabilities = null; ready = false
    main.removeCallbacks(connectTimeout); main.removeCallbacks(writeTimeout)
    connectPromise?.let { reject(it, reason) }; connectPromise = null
    writePromise?.let { reject(it, reason) }; writePromise = null
    if (old != null) { runCatching { old.disconnect() }; runCatching { old.close() } }
    if (id != null) event(mapOf("kind" to "disconnected", "peripheralId" to id, "reason" to reason))
  }
  private fun readCapabilities(connection: BluetoothGatt, value: ByteArray, status: Int) {
    if (connection !== gatt) return
    if (status != BluetoothGatt.GATT_SUCCESS || value.isEmpty() || value.size > 1024) { close("CAPABILITIES_READ_FAILED"); return }
    capabilities = value.toString(Charsets.UTF_8)
    val tx = connection.getService(serviceId)?.getCharacteristic(txId)
    val descriptor = tx?.getDescriptor(cccdId)
    if (tx == null || descriptor == null) { close("NOTIFICATION_DESCRIPTOR_MISSING"); return }
    try {
      if (!connection.setCharacteristicNotification(tx, true)) { close("SUBSCRIBE_FAILED"); return }
      val accepted = if (Build.VERSION.SDK_INT >= 33) connection.writeDescriptor(descriptor, BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE) == BluetoothStatusCodes.SUCCESS
      else { @Suppress("DEPRECATION") descriptor.setValue(BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE); @Suppress("DEPRECATION") connection.writeDescriptor(descriptor) }
      if (!accepted) close("SUBSCRIBE_FAILED")
    } catch (_: SecurityException) { close("BLUETOOTH_PERMISSION_DENIED") }
  }
  private fun packet(connection: BluetoothGatt, characteristic: BluetoothGattCharacteristic, value: ByteArray, received: Double) {
    if (connection !== gatt || !ready || characteristic.uuid != txId) return
    if (value.size !in 13..20) { close("FRAGMENT_LENGTH"); return }
    event(mapOf("kind" to "packet", "peripheralId" to peripheralId, "base64" to Base64.encodeToString(value, Base64.NO_WRAP), "receivedAtMonotonicMs" to received))
  }
  private val callback = object : BluetoothGattCallback() {
    override fun onConnectionStateChange(connection: BluetoothGatt, status: Int, newState: Int) { main.post {
      if (connection !== gatt) return@post
      if (status != BluetoothGatt.GATT_SUCCESS || newState == BluetoothProfile.STATE_DISCONNECTED) close("LINK_DISCONNECTED")
      else if (newState == BluetoothProfile.STATE_CONNECTED) try { if (!connection.discoverServices()) close("SERVICE_DISCOVERY_FAILED") } catch (_: SecurityException) { close("BLUETOOTH_PERMISSION_DENIED") }
    } }
    override fun onServicesDiscovered(connection: BluetoothGatt, status: Int) { main.post {
      if (connection !== gatt) return@post
      val service = connection.getService(serviceId); val cap = service?.getCharacteristic(capId)
      val command = service?.getCharacteristic(rxId); val tx = service?.getCharacteristic(txId)
      if (status != BluetoothGatt.GATT_SUCCESS || cap == null || command == null || tx == null || cap.properties and BluetoothGattCharacteristic.PROPERTY_READ == 0 || command.properties and BluetoothGattCharacteristic.PROPERTY_WRITE == 0 || tx.properties and BluetoothGattCharacteristic.PROPERTY_NOTIFY == 0) close("UNSUPPORTED_DEVICE")
      else { rx = command; try { if (!connection.readCharacteristic(cap)) close("CAPABILITIES_READ_FAILED") } catch (_: SecurityException) { close("BLUETOOTH_PERMISSION_DENIED") } }
    } }
    override fun onCharacteristicRead(connection: BluetoothGatt, characteristic: BluetoothGattCharacteristic, value: ByteArray, status: Int) { val copy = value.copyOf(); main.post { if (characteristic.uuid == capId) readCapabilities(connection, copy, status) } }
    @Deprecated("Legacy Android callback")
    override fun onCharacteristicRead(connection: BluetoothGatt, characteristic: BluetoothGattCharacteristic, status: Int) { if (Build.VERSION.SDK_INT < 33) { @Suppress("DEPRECATION") val copy = characteristic.value?.copyOf() ?: byteArrayOf(); main.post { if (characteristic.uuid == capId) readCapabilities(connection, copy, status) } } }
    override fun onDescriptorWrite(connection: BluetoothGatt, descriptor: BluetoothGattDescriptor, status: Int) { main.post {
      if (connection !== gatt || descriptor.uuid != cccdId || descriptor.characteristic.uuid != txId) return@post
      if (status != BluetoothGatt.GATT_SUCCESS || capabilities == null) close("SUBSCRIBE_FAILED")
      else { main.removeCallbacks(connectTimeout); ready = true; val promise = connectPromise; connectPromise = null; promise?.resolve(mapOf("peripheralId" to peripheralId, "mtu" to 23, "capabilities" to capabilities)) }
    } }
    override fun onCharacteristicWrite(connection: BluetoothGatt, characteristic: BluetoothGattCharacteristic, status: Int) { main.post {
      if (connection !== gatt || characteristic.uuid != rxId) return@post
      if (status != BluetoothGatt.GATT_SUCCESS) close("WRITE_FAILED") else { main.removeCallbacks(writeTimeout); val promise = writePromise; writePromise = null; promise?.resolve(null) }
    } }
    override fun onCharacteristicChanged(connection: BluetoothGatt, characteristic: BluetoothGattCharacteristic, value: ByteArray) { val received = now(); val copy = value.copyOf(); main.post { packet(connection, characteristic, copy, received) } }
    @Deprecated("Legacy Android callback")
    override fun onCharacteristicChanged(connection: BluetoothGatt, characteristic: BluetoothGattCharacteristic) { if (Build.VERSION.SDK_INT < 33) { val received = now(); @Suppress("DEPRECATION") val copy = characteristic.value?.copyOf() ?: byteArrayOf(); main.post { packet(connection, characteristic, copy, received) } } }
  }
}
