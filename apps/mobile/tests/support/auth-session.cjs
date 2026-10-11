const { randomUUID } = require("node:crypto");
class AuthRequest {
  constructor(options) {
    Object.assign(this, options);
    this.state = randomUUID();
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
