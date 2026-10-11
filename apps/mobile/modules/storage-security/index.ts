import { requireOptionalNativeModule } from 'expo-modules-core';
export interface StorageSecurityAvailability { available: boolean; platform: 'ios' | 'android' | 'unavailable'; backupExclusion: boolean; secureWindow: boolean }
export interface DirectoryProtection { excludedFromBackup: true; method: 'ios_resource_value' | 'android_backup_disabled' }
interface SecurityNative {
  getAvailability(): StorageSecurityAvailability;
  protectDatabaseDirectoryAsync(uri: string): Promise<DirectoryProtection>;
  enableSecureWindowAsync(): Promise<{platform: 'ios' | 'android'; secureWindow: boolean}>;
}
const native = requireOptionalNativeModule<SecurityNative>('OTGDStorageSecurity');
export function getStorageSecurityAvailability(): StorageSecurityAvailability { return native?.getAvailability() ?? { available: false, platform: 'unavailable', backupExclusion: false, secureWindow: false }; }
export async function protectDatabaseDirectoryAsync(directoryUri: string): Promise<DirectoryProtection> { if (!native) throw new Error('NATIVE_STORAGE_SECURITY_UNAVAILABLE'); return native.protectDatabaseDirectoryAsync(directoryUri); }
export async function enableSecureWindowAsync(): Promise<{platform: 'ios' | 'android'; secureWindow: boolean}> { if (!native) throw new Error('NATIVE_STORAGE_SECURITY_UNAVAILABLE'); return native.enableSecureWindowAsync(); }
