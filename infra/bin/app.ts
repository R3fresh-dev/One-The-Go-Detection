#!/usr/bin/env node
import { App } from 'aws-cdk-lib';
import { loadConfig } from '../lib/config';
import { PlatformStack, RegistryStack } from '../lib/platform-stack';

const app = new App();
const path = app.node.tryGetContext('config');
if (typeof path !== 'string') throw new Error('Pass -c config=/absolute/path/to/environment.local.json');
const registryOnly = app.node.tryGetContext('phase') === 'registry';
const config = loadConfig(path, registryOnly);
const env = {account: config.account, region: config.region};
const registry = new RegistryStack(app, `otgd-${config.environment}-registry`, {env, config});
if (!registryOnly) {
  const platform = new PlatformStack(app, `otgd-${config.environment}-platform`, {env, config, repository: registry.repository});
  platform.addDependency(registry);
}
