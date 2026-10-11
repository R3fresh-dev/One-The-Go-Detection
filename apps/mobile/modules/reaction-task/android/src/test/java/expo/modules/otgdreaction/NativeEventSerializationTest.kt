package expo.modules.otgdreaction

import com.facebook.react.bridge.JavaOnlyArray
import com.facebook.react.bridge.JavaOnlyMap
import com.facebook.react.bridge.WritableArray
import com.facebook.react.bridge.WritableMap
import expo.modules.kotlin.types.JSTypeConverterProvider
import org.junit.Assert.*
import org.junit.Test

/** Uses Expo's actual event conversion with RN's documented Java-only test
 * containers. This verifies null preservation, not a running JS/native bridge. */
class NativeEventSerializationTest {
  @Test fun explicitNullsSurviveEventConversionAtEveryDepth() {
    val containers = object : JSTypeConverterProvider.ContainerProvider {
      override fun createMap(): WritableMap = JavaOnlyMap()
      override fun createArray(): WritableArray = JavaOnlyArray()
    }
    val payload = linkedMapOf<String, Any?>(
      "features" to null,
      "timing" to linkedMapOf("terminalCutoffMs" to null, "modelEligible" to false),
      "trialEvents" to listOf(linkedMapOf("index" to 0, "responseTimeMs" to null)),
      "inputEvents" to emptyList<Any?>()
    )
    val converted = JSTypeConverterProvider.convertToJSValue(payload, containers)
    assertTrue(converted is WritableMap)
    val event = converted as WritableMap
    assertTrue(event.hasKey("features")); assertTrue(event.isNull("features"))
    assertFalse(event.hasKey("payload"))
    val timing = requireNotNull(event.getMap("timing"))
    assertTrue(timing.hasKey("terminalCutoffMs")); assertTrue(timing.isNull("terminalCutoffMs"))
    assertFalse(timing.getBoolean("modelEligible"))
    val trial = requireNotNull(requireNotNull(event.getArray("trialEvents")).getMap(0))
    assertEquals(0, trial.getInt("index")); assertTrue(trial.hasKey("responseTimeMs")); assertTrue(trial.isNull("responseTimeMs"))
    assertEquals(0, requireNotNull(event.getArray("inputEvents")).size())
    assertNull(payload["features"])
  }
}
