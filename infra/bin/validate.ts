import { loadConfig } from '../lib/config';
const path=process.argv[2];
if(!path) throw new Error('Configuration path is required');
const config=loadConfig(path,process.argv.includes('--registry'));
process.stdout.write(JSON.stringify(config));
