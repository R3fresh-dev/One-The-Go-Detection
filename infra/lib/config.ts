import { readFileSync } from 'node:fs';

export interface PlatformConfig {
  environment: 'qa' | 'prod';
  account: string;
  region: string;
  vpcCidr: string;
  domain: string;
  certificateArn: string;
  hostedZoneId?: string;
  hostedZoneName?: string;
  cognitoDomainPrefix: string;
  oauthRedirectUris: string[];
  oauthLogoutUris: string[];
  imageDigest: string;
  releaseId: string;
  monthlyBudgetUsd: number;
  alarmEmail: string;
  ownerRole: string;
  costCenter: string;
  costEstimatePath: string;
  databaseEngineVersion: string;
  databaseSnapshotIdentifier?: string;
  activateServices: boolean;
  recoveryRequired: boolean;
}

export function validateConfig(value: unknown, registryOnly = false): PlatformConfig {
  if (!value || typeof value !== 'object') throw new Error('A deployment configuration object is required');
  const c = value as PlatformConfig;
  const known = new Set(['environment','account','region','vpcCidr','domain','certificateArn','hostedZoneId','hostedZoneName','cognitoDomainPrefix','oauthRedirectUris','oauthLogoutUris','imageDigest','releaseId','monthlyBudgetUsd','alarmEmail','ownerRole','costCenter','costEstimatePath','databaseEngineVersion','databaseSnapshotIdentifier','activateServices','recoveryRequired']);
  for (const key of Object.keys(c)) if (!known.has(key)) throw new Error(`Unknown deployment setting: ${key}`);
  if (!['qa','prod'].includes(c.environment)) throw new Error('Only qa/prod can be cloud deployments');
  const placeholder = /CHANGEME|REPLACE|example\.(com|org)|YOUR_|<|>|^0{12}$|^1{12}$/i;
  for (const key of ['account','region','vpcCidr','domain','certificateArn','cognitoDomainPrefix','releaseId','alarmEmail','ownerRole','costCenter','costEstimatePath'] as const) {
    if (typeof c[key] !== 'string' || !c[key].trim() || placeholder.test(c[key])) throw new Error(`Set concrete ${key}; placeholders cannot deploy`);
  }
  if (!/^\d{12}$/.test(c.account)) throw new Error('account must be a 12-digit AWS account');
  if (!/^[a-z]{2}-[a-z]+-\d$/.test(c.region)) throw new Error('Invalid AWS region');
  if (!/^\d{1,3}(\.\d{1,3}){3}\/\d{1,2}$/.test(c.vpcCidr)) throw new Error('Invalid VPC CIDR');
  const [ip, bits] = c.vpcCidr.split('/');
  if (ip.split('.').some(x => Number(x) > 255) || Number(bits) < 16 || Number(bits) > 24) throw new Error('Use a valid /16 through /24 VPC CIDR');
  if (!/^[a-z0-9][a-z0-9.-]+\.[a-z]{2,}$/i.test(c.domain) || /localhost|localstack/i.test(c.domain)) throw new Error('A public TLS domain is required');
  if (!c.certificateArn.startsWith(`arn:aws:acm:${c.region}:${c.account}:certificate/`)) throw new Error('Certificate must belong to the selected account/region');
  if (Boolean(c.hostedZoneId) !== Boolean(c.hostedZoneName)) throw new Error('Optional Route 53 management requires both hostedZoneId and hostedZoneName');
  if (c.hostedZoneName && c.domain !== c.hostedZoneName && !c.domain.endsWith(`.${c.hostedZoneName}`)) throw new Error('API domain must belong to the supplied hosted zone');
  if (!/^[a-z0-9-]{3,63}$/.test(c.cognitoDomainPrefix)) throw new Error('Invalid Cognito hosted domain prefix');
  for (const key of ['oauthRedirectUris','oauthLogoutUris'] as const) {
    if (!Array.isArray(c[key]) || c[key].length === 0 || c[key].length > 8) throw new Error(`${key} needs 1–8 exact registered callbacks`);
    for (const url of c[key]) {
      const parsed = new URL(url);
      if (placeholder.test(url) || url.includes('*') || parsed.protocol === 'http:' || /local|test/.test(parsed.protocol)) throw new Error(`Unsafe cloud callback: ${url}`);
      if (parsed.protocol !== 'https:' && parsed.protocol !== `otgd-${c.environment}:`) throw new Error('Callback must be HTTPS or the fixed environment scheme');
    }
  }
  if (!registryOnly && !/^sha256:[0-9a-f]{64}$/.test(c.imageDigest)) throw new Error('Promote an immutable ECR imageDigest, not a tag');
  if (!registryOnly && /^sha256:0+$/.test(c.imageDigest)) throw new Error('A placeholder digest cannot deploy');
  if (!Number.isFinite(c.monthlyBudgetUsd) || c.monthlyBudgetUsd <= 0) throw new Error('An owner-set positive monthly budget is required');
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(c.alarmEmail)) throw new Error('Set the actual alarm/budget destination');
  if (!/^16\.\d+$/.test(c.databaseEngineVersion)) throw new Error('Record an exact supported PostgreSQL 16 minor');
  if (c.databaseSnapshotIdentifier && (!c.recoveryRequired || !c.databaseSnapshotIdentifier.startsWith(`arn:aws:rds:${c.region}:${c.account}:snapshot:`) || placeholder.test(c.databaseSnapshotIdentifier))) throw new Error('Snapshot recovery requires an exact same-account/region snapshot ARN and recoveryRequired=true');
  if (typeof c.activateServices !== 'boolean' || typeof c.recoveryRequired !== 'boolean') throw new Error('activateServices and recoveryRequired must be explicit booleans');
  // The deployment CLI requires a verified recovery task receipt before it will
  // activate a recovering environment. Keep the runtime readiness gate enabled.
  return c;
}

export function loadConfig(path: string, registryOnly = false): PlatformConfig {
  const c = validateConfig(JSON.parse(readFileSync(path, 'utf8')), registryOnly);
  const estimate = JSON.parse(readFileSync(c.costEstimatePath, 'utf8'));
  if (estimate.region !== c.region || !estimate.checked_at || !estimate.scenarios || estimate.unverified_rates?.length) throw new Error('Provide a current complete estimate for the selected region');
  const checkedAt=Date.parse(estimate.checked_at);
  if (!Number.isFinite(checkedAt) || checkedAt > Date.now()+86_400_000 || Date.now()-checkedAt > 31*86_400_000) throw new Error('Refresh the cost estimate; its date is invalid, in the future, or older than 31 days');
  return c;
}
