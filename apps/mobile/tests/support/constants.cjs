module.exports = {
  __esModule: true,
  default: {
    expoConfig: {
      version: "0.2.0",
      extra: {
        environment: "test",
        apiUrl: "http://localhost:8000",
        issuer: "http://localhost:8081",
        clientId: "otgd-local-mobile",
        redirectUri: "otgd-local://oauth/callback",
      },
    },
  },
};
