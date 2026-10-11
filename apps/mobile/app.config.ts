import type { ExpoConfig, ConfigContext } from "expo/config";

export default ({ config }: ConfigContext): ExpoConfig => {
  const environment = process.env.APP_ENV ?? "local";
  if (!["local", "qa", "prod", "test"].includes(environment))
    throw new Error("Unsupported APP_ENV");
  if (
    process.env.EXPO_PUBLIC_APP_ENV &&
    process.env.EXPO_PUBLIC_APP_ENV !== environment
  )
    throw new Error("EXPO_PUBLIC_APP_ENV must match APP_ENV");
  process.env.EXPO_PUBLIC_APP_ENV = environment;
  const local = environment === "local" || environment === "test";
  const previewValue = process.env.EXPO_PUBLIC_HOSTED_PREVIEW ?? "false";
  if (!["true", "false"].includes(previewValue))
    throw new Error("EXPO_PUBLIC_HOSTED_PREVIEW must be true or false");
  const hostedPreview = previewValue === "true";
  if (hostedPreview && environment !== "local")
    throw new Error(
      "The fictional hosted preview is permitted only in APP_ENV=local",
    );
  const buildNumber = Number(process.env.APP_BUILD_NUMBER ?? "1");
  if (
    !Number.isSafeInteger(buildNumber) ||
    buildNumber < 1 ||
    buildNumber > 2100000000
  )
    throw new Error(
      "APP_BUILD_NUMBER must be a positive integer no greater than 2100000000",
    );
  const apiUrl =
    process.env.EXPO_PUBLIC_API_URL ?? (local ? "http://localhost:8000" : "");
  const issuer =
    process.env.EXPO_PUBLIC_OAUTH_ISSUER ??
    (local ? "http://localhost:8081" : "");
  const clientId =
    process.env.EXPO_PUBLIC_OAUTH_CLIENT_ID ??
    (local ? "otgd-local-mobile" : "");
  for (const url of [apiUrl, issuer]) {
    if (
      !url ||
      (!local &&
        (!url.startsWith("https://") ||
          /localhost|127\.0\.0\.1|10\.0\.2\.2|localstack|example\./i.test(url)))
    )
      throw new Error(
        "Set real environment-specific API and OAuth HTTPS origins",
      );
  }
  if (!clientId || (!local && /local|placeholder|example/i.test(clientId)))
    throw new Error("Set the environment Cognito public client ID");
  const suffix = environment === "prod" ? "" : `.${environment}`;
  const scheme = `otgd${environment === "prod" ? "" : `-${environment}`}`;
  return {
    ...config,
    name: `One The Go${environment === "prod" ? "" : ` · ${environment.toUpperCase()}`}`,
    slug: "one-the-go-detection",
    version: "0.2.0",
    orientation: "portrait",
    scheme,
    userInterfaceStyle: "automatic",
    ios: {
      bundleIdentifier: `dev.r3fresh.otgd${suffix}`,
      supportsTablet: true,
      buildNumber: String(buildNumber),
      infoPlist: {
        ...(hostedPreview ? { OTGDHostedPreview: true } : {}),
        NSCameraUsageDescription:
          "Show an optional eye-positioning preview. Preview does not record images or measure pupils.",
        NSFaceIDUsageDescription:
          "Unlock this account’s encrypted records on this device.",
        NSBluetoothAlwaysUsageDescription:
          "Connect to your measurement reader after you choose Find device.",

        ...(local
          ? {
              NSAppTransportSecurity: {
                NSExceptionDomains: Object.fromEntries(
                  [
                    ...new Set([
                      new URL(apiUrl).hostname,
                      new URL(issuer).hostname,
                    ]),
                  ].map((host) => [
                    host,
                    {
                      NSExceptionAllowsInsecureHTTPLoads: true,
                      NSIncludesSubdomains: false,
                    },
                  ]),
                ),
              },
            }
          : {}),
      },
    },
    android: {
      package: `dev.r3fresh.otgd${suffix}`,
      allowBackup: false,
      versionCode: buildNumber,
      permissions: [
        "android.permission.CAMERA",
        "android.permission.BLUETOOTH_SCAN",
        "android.permission.BLUETOOTH_CONNECT",
      ],
      blockedPermissions: [
        "android.permission.RECORD_AUDIO",
        "android.permission.READ_MEDIA_IMAGES",
        "android.permission.READ_MEDIA_VIDEO",
      ],
    },
    web: {
      bundler: "metro",
      output: "single",
      name: "One The Go · application preview",
    },
    plugins: [
      [
        "expo-build-properties",
        {
          android: {
            minSdkVersion: 24,
            compileSdkVersion: 36,
            targetSdkVersion: 36,
          },
          ios: { deploymentTarget: "16.4" },
        },
      ],
      ["expo-sqlite", { useSQLCipher: true }],
      [
        "expo-camera",
        {
          cameraPermission: "Show an optional eye-positioning preview.",
          recordAudioAndroid: false,
        },
      ],
      ["expo-secure-store", { configureAndroidBackup: true }],
      [
        "expo-local-authentication",
        { faceIDPermission: "Unlock this account’s encrypted records." },
      ],
      "expo-status-bar",
      "expo-web-browser",
      "expo-sharing",
      "./plugins/withLocalTransport",
    ],
    extra: {
      environment,
      hostedPreview,
      buildNumber: String(buildNumber),
      apiUrl,
      issuer,
      clientId,
      redirectUri: `${scheme}://oauth/callback`,
      ...(process.env.EAS_PROJECT_ID
        ? { eas: { projectId: process.env.EAS_PROJECT_ID } }
        : {}),
    },
  };
};
