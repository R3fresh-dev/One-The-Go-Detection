idf_component_register(SRCS "reader.cpp" "../../nano_esp32_signed_reader/RyuDouble.cpp" "../../nano_esp32_signed_reader/SparkFunBioSensor.cpp"
  INCLUDE_DIRS "../../nano_esp32_signed_reader" "${OTGD_ARDUINO_JSON}/src"
  REQUIRES arduino nvs_flash mbedtls bt bootloader_support)
target_compile_features(${COMPONENT_LIB} PUBLIC cxx_std_17)
