import * as AuthSession from "expo-auth-session";
import * as WebBrowser from "expo-web-browser";
import { Platform } from "react-native";
import { BUILD } from "../platform/config";
import { vault } from "../platform/storage";
import type { AppConfig, Identity } from "../core/types";
import {
  IntegrityError,
  parseBoundedJson,
  requireObject,
} from "../core/integrity";
import { ApiError, type TokenProvider } from "./api";
import { SerializedVault, refreshTokenForGrant } from "../core/serializedVault";
import { AuthorizationAttemptGuard } from "../core/operationGuards";

WebBrowser.maybeCompleteAuthSession();
export interface OAuthTokens {
  accessToken: string;
  refreshToken: string | null;
  expiresAt: number;
  auth: AppConfig["auth"];
}
interface StoredSession {
  identity: Identity;
  refreshToken: string | null;
  auth: AppConfig["auth"];
}
export class AuthManager implements TokenProvider {
  private tokens: OAuthTokens | null = null;
  private stored: StoredSession | null = null;
  private refreshing: Promise<string | null> | null = null;
  private epoch = 0;
  private readonly persistence = new SerializedVault(vault);
  private readonly key = `otgd.auth.${BUILD.environment}`;
  private readonly authorizationAttempts = new AuthorizationAttemptGuard();
  constructor(private readonly onSessionInvalidated: () => void = () => {}) {}
  get identity(): Identity | null {
    return this.stored?.identity ?? null;
  }
  get generation(): number {
    return this.epoch;
  }
  async restore(): Promise<Identity | null> {
    const generation = this.epoch,
      raw = await this.persistence.get(this.key);
    if (!raw || generation !== this.epoch) return null;
    const parsed = parseBoundedJson(raw, 32_768) as StoredSession;
    if (
      parsed.identity?.issuer !== BUILD.issuer ||
      parsed.auth?.issuer !== BUILD.issuer ||
      parsed.auth?.client_id !== BUILD.clientId ||
      !parsed.identity.accountRef
    )
      throw new IntegrityError(
        "AUTH_STORE_MISMATCH",
        "The saved sign-in belongs to another service.",
      );
    this.stored = parsed;
    return parsed.identity;
  }
  async authorize(
    config: AppConfig,
    forceLogin = false,
  ): Promise<OAuthTokens | null> {
    const attempt = this.authorizationAttempts.begin(Date.now());
    const generation = this.epoch;
    const redirectUri =
      Platform.OS === "web"
        ? `${globalThis.location.origin}/`
        : BUILD.redirectUri;
    if (!config.auth.redirect_uris.includes(redirectUri))
      throw new IntegrityError(
        "CALLBACK_NOT_CONFIGURED",
        `This build’s OAuth callback is not registered. Configure ${redirectUri} for this environment.`,
      );
    const request = new AuthSession.AuthRequest({
      clientId: BUILD.clientId,
      redirectUri,
      scopes: ["openid", "profile"],
      responseType: AuthSession.ResponseType.Code,
      usePKCE: true,
      codeChallengeMethod: AuthSession.CodeChallengeMethod.S256,
      extraParams: forceLogin ? { prompt: "login", max_age: "0" } : {},
    });
    const discovery = {
      authorizationEndpoint: config.auth.authorization_endpoint,
      tokenEndpoint: config.auth.token_endpoint,
      revocationEndpoint: config.auth.revocation_endpoint,
    };
    const result = await request.promptAsync(discovery);
    if (result.type === "cancel" || result.type === "dismiss") return null;
    this.authorizationAttempts.assertCurrent(attempt, Date.now());
    if (generation !== this.epoch)
      throw new ApiError(
        401,
        "AUTH_CHANGED",
        "The sign-in was canceled or the account changed.",
      );
    if (
      result.type !== "success" ||
      result.params.state !== request.state ||
      !result.params.code ||
      !request.codeVerifier
    )
      throw new IntegrityError(
        "OAUTH_REJECTED",
        "Sign-in could not be verified. Start a new sign-in attempt.",
      );
    this.authorizationAttempts.consume(attempt, Date.now());
    const tokens = await this.exchange(config.auth, {
      grant_type: "authorization_code",
      client_id: BUILD.clientId,
      code: result.params.code,
      redirect_uri: redirectUri,
      code_verifier: request.codeVerifier,
    });
    this.authorizationAttempts.assertCurrent(attempt, Date.now());
    if (generation !== this.epoch)
      throw new ApiError(
        401,
        "AUTH_CHANGED",
        "The sign-in was canceled or the account changed.",
      );
    return tokens;
  }
  private async exchange(
    auth: AppConfig["auth"],
    fields: Record<string, string>,
    capturedRefreshToken: string | null = null,
  ): Promise<OAuthTokens> {
    if (auth.issuer !== BUILD.issuer || auth.client_id !== BUILD.clientId)
      throw new IntegrityError(
        "AUTH_CONFIG_MISMATCH",
        "The authentication service changed.",
      );
    const controller = new AbortController(),
      timeout = setTimeout(() => controller.abort(), 15_000);
    try {
      const response = await fetch(auth.token_endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          Accept: "application/json",
        },
        body: new URLSearchParams(fields).toString(),
        signal: controller.signal,
        redirect: "error",
      });
      const body = requireObject(
        parseBoundedJson(await response.text(), 32_768),
      );
      if (
        !response.ok ||
        typeof body.access_token !== "string" ||
        (body.token_type !== "Bearer" && body.token_type !== "bearer") ||
        typeof body.expires_in !== "number" ||
        body.expires_in <= 0
      )
        throw new ApiError(
          401,
          "AUTH_REQUIRED",
          "Sign-in expired or was refused. Sign in again to continue.",
        );
      return {
        accessToken: body.access_token,
        refreshToken: refreshTokenForGrant(
          fields.grant_type!,
          body.refresh_token,
          capturedRefreshToken,
        ),
        expiresAt: Date.now() + body.expires_in * 1000,
        auth,
      };
    } catch (error) {
      if (error instanceof ApiError || error instanceof IntegrityError)
        throw error;
      throw new ApiError(
        0,
        "AUTH_NETWORK_UNAVAILABLE",
        "Sign-in service could not be reached. Try again when connected.",
        true,
      );
    } finally {
      clearTimeout(timeout);
    }
  }
  async commit(
    tokens: OAuthTokens,
    identity: Identity,
    expectedGeneration = this.epoch,
  ): Promise<void> {
    // Identity is returned by the protected API; decoded token/email claims never select a database.
    if (identity.issuer !== BUILD.issuer)
      throw new IntegrityError(
        "AUTH_IDENTITY_MISMATCH",
        "The signed-in account belongs to another issuer.",
      );
    if (this.epoch !== expectedGeneration)
      throw new ApiError(
        401,
        "AUTH_CHANGED",
        "The sign-in was canceled or the account changed.",
      );
    const epoch = ++this.epoch;
    this.tokens = tokens;
    this.stored = {
      identity,
      refreshToken: tokens.refreshToken,
      auth: tokens.auth,
    };
    const stored = this.stored;
    await this.persistence.set(
      this.key,
      JSON.stringify(stored),
      () => this.epoch === epoch && this.stored === stored,
    );
    if (this.epoch !== epoch || this.stored !== stored)
      throw new ApiError(
        401,
        "AUTH_CHANGED",
        "The sign-in changed while credentials were being protected.",
      );
  }
  async accessToken(force = false): Promise<string | null> {
    if (!force && this.tokens && this.tokens.expiresAt > Date.now() + 30_000)
      return this.tokens.accessToken;
    if (this.refreshing) return this.refreshing;
    if (!this.stored?.refreshToken) return null;
    this.refreshing = (async () => {
      const stored = this.stored!,
        epoch = this.epoch;
      let tokens: OAuthTokens;
      try {
        tokens = await this.exchange(
          stored.auth,
          {
            grant_type: "refresh_token",
            client_id: BUILD.clientId,
            refresh_token: stored.refreshToken!,
          },
          stored.refreshToken,
        );
      } catch (error) {
        if (
          error instanceof ApiError &&
          error.status === 401 &&
          this.epoch === epoch &&
          this.stored?.identity.issuer === stored.identity.issuer &&
          this.stored?.identity.accountRef === stored.identity.accountRef &&
          this.stored?.refreshToken === stored.refreshToken
        ) {
          await this.clear();
          this.onSessionInvalidated();
        }
        throw error;
      }
      if (
        this.epoch !== epoch ||
        this.stored?.identity.accountRef !== stored.identity.accountRef ||
        this.stored?.refreshToken !== stored.refreshToken
      )
        throw new ApiError(
          401,
          "AUTH_CHANGED",
          "The sign-in changed while refreshing.",
        );
      await this.commit(tokens, this.stored.identity, epoch);
      return tokens.accessToken;
    })();
    try {
      return await this.refreshing;
    } finally {
      this.refreshing = null;
    }
  }
  async clear(): Promise<void> {
    this.authorizationAttempts.invalidate();
    this.epoch++;
    this.tokens = null;
    this.stored = null;
    await this.persistence.remove(this.key);
  }
  async updateIdentity(identity: Identity): Promise<void> {
    if (!this.stored || identity.accountRef !== this.stored.identity.accountRef)
      return;
    const epoch = this.epoch;
    this.stored = { ...this.stored, identity };
    const stored = this.stored;
    await this.persistence.set(
      this.key,
      JSON.stringify(stored),
      () => this.epoch === epoch && this.stored === stored,
    );
  }
  logoutReceiptToken(): string | null {
    return this.tokens?.accessToken ?? null;
  }
  async whenRefreshSettled(): Promise<void> {
    await this.refreshing?.catch(() => null);
  }
  providerLogoutUrl(): string | null {
    const endpoint = this.stored?.auth.logout_endpoint;
    if (!endpoint) return null;
    const redirect =
      Platform.OS === "web"
        ? `${globalThis.location.origin}/`
        : BUILD.redirectUri;
    const url = new URL(endpoint);
    url.searchParams.set("client_id", BUILD.clientId);
    url.searchParams.set("logout_uri", redirect);
    return url.toString();
  }
  async openProviderLogout(url: string): Promise<void> {
    const redirect =
      Platform.OS === "web"
        ? `${globalThis.location.origin}/`
        : BUILD.redirectUri;
    await WebBrowser.openAuthSessionAsync(url, redirect);
  }
  async revokeProvider(): Promise<void> {
    const saved = this.stored;
    if (!saved?.refreshToken || !saved.auth.revocation_endpoint) return;
    const controller = new AbortController(),
      timeout = setTimeout(() => controller.abort(), 10_000);
    try {
      await fetch(saved.auth.revocation_endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
          token: saved.refreshToken,
          token_type_hint: "refresh_token",
          client_id: BUILD.clientId,
        }).toString(),
        signal: controller.signal,
        redirect: "error",
      });
    } finally {
      clearTimeout(timeout);
    }
  }
  async browserLogout(): Promise<void> {
    const endpoint = this.stored?.auth.logout_endpoint;
    if (!endpoint) return;
    const url = new URL(endpoint);
    url.searchParams.set("client_id", BUILD.clientId);
    url.searchParams.set("logout_uri", BUILD.redirectUri);
    await WebBrowser.openAuthSessionAsync(url.toString(), BUILD.redirectUri);
  }
}
