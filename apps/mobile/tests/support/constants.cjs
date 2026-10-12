module.exports = {
  __esModule: true,
  default: {
    expoConfig: {
      version: "0.2.0",
      extra: {
        environment:
          process.env.OTGD_UNIT_PREVIEW === "true" ? "local" : "test",
        hostedPreview: process.env.OTGD_UNIT_PREVIEW === "true",
        apiUrl: "http://localhost:8000",
        issuer: "http://localhost:8081",
        clientId: "otgd-local-mobile",
        redirectUri: "otgd-local://oauth/callback",
      },
    },
  },
};
