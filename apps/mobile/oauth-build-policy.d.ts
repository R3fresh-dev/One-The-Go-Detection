/** Public values compiled from the admitted environment, never from API metadata. */
export interface OAuthPolicy {
  environment: string;
  issuer: string;
  clientId: string;
  oauthOrigin: string;
  redirectUris: readonly string[];
}
export function validateOAuthPolicy(policy: OAuthPolicy): void;
