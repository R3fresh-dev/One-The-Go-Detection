import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import canonicalize from 'canonicalize';

const here = path.dirname(fileURLToPath(import.meta.url));
const repository = path.resolve(here, '../../../..');
const moduleRoot = path.resolve(here, '../reaction-task');
const specification = path.join(repository, 'openspec/changes/production-mobile-platform/fixtures');
const hash = value => createHash('sha256').update(canonicalize(value)).digest('hex');
const read = async file => JSON.parse(await readFile(file, 'utf8'));
const config = await read(path.join(moduleRoot, 'fixtures/configuration.json'));
const expected = await read(path.join(specification, 'reaction-task-config-v1.json'));
const golden = await read(path.join(moduleRoot, 'fixtures/golden.json'));
const expectedGolden = await read(path.join(specification, 'reaction-task-golden-v1.json'));
if (canonicalize(config) !== canonicalize(expected) || canonicalize(golden) !== canonicalize(expectedGolden)) throw new Error('Native assets differ from the reviewed OpenSpec fixtures');
const digest = hash(config);
if (digest !== golden.configuration_sha256) throw new Error('Configuration hash mismatch');
for (const schedule of golden.schedules) if (hash(schedule.schedule) !== schedule.schedule_sha256) throw new Error('Literal schedule hash mismatch');
for (const file of ['types.ts', 'android/src/main/java/expo/modules/otgdreaction/ReactionCore.kt', 'ios/ReactionCore.swift']) {
  if (!(await readFile(path.join(moduleRoot, file), 'utf8')).includes(digest)) throw new Error(`${file} uses a different configuration hash`);
}
const shape = await read(path.join(moduleRoot, 'fixtures/native-result-valid-contract-fixture.json'));
if (!shape.timing.simulator || shape.timing.deviceModel !== 'Host contract fixture (not acquired)' || shape.configurationSha256 !== digest) throw new Error('Host contract fixture label/configuration mismatch');
console.log(`Reviewed native configuration and three literal schedules verified: ${digest}`);
console.log('This checks source fixtures only; it does not claim a native device run or physical timing accuracy.');
