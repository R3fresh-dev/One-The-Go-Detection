const { randomBytes } = require("node:crypto");
class AuthRequest {
  constructor(options) {
    Object.assign(this, options);
    // Match the SDK default length and preserve an explicitly supplied state.
    this.state = options.state ?? randomBytes(5).toString("hex");
    this.codeVerifier = "unit-bound-pkce-verifier";
  }
  promptAsync() {
    return globalThis.__otgdUnitRuntime.prompt(this);
  }
}
module.exports = {
  AuthRequest,
  ResponseType: { Code: "code" },
  CodeChallengeMethod: { S256: "S256" },
};
