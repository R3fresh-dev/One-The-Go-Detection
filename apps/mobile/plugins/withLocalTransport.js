const { withAndroidManifest, withDangerousMod } = require('expo/config-plugins');
const fs = require('node:fs/promises');
const path = require('node:path');

module.exports = function withLocalTransport(config) {
  const local = ['local', 'test'].includes(config.extra?.environment);
  if (!local) return config;
  const hosts = [...new Set([config.extra.apiUrl, config.extra.issuer].map(v => new URL(v).hostname))];
  if (hosts.some(v => !/^[a-zA-Z0-9.:-]+$/.test(v))) throw new Error('Invalid local transport host');
  config = withAndroidManifest(config, config => {
    const app = config.modResults.manifest.application?.[0];
    if (app) app.$['android:networkSecurityConfig'] = '@xml/otgd_local_network_security';
    return config;
  });
  return withDangerousMod(config, ['android', async config => {
    const dir = path.join(config.modRequest.platformProjectRoot, 'app/src/main/res/xml');
    await fs.mkdir(dir, { recursive: true });
    await fs.writeFile(path.join(dir, 'otgd_local_network_security.xml'), `<?xml version="1.0" encoding="utf-8"?><network-security-config><base-config cleartextTrafficPermitted="false"/><domain-config cleartextTrafficPermitted="true">${hosts.map(host => `<domain includeSubdomains="false">${host}</domain>`).join('')}</domain-config></network-security-config>`);
    return config;
  }]);
};
