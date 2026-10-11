import canonicalize from 'canonicalize';
import { sha256 } from '@noble/hashes/sha2.js';

export class IntegrityError extends Error { constructor(public readonly code: string, message: string) { super(message); this.name = 'IntegrityError'; } }
export function assertPlainJson(value: unknown, depth = 0): void {
  if (depth > 40) throw new IntegrityError('JSON_DEPTH', 'Record nesting exceeds the supported limit.');
  if (typeof value === 'number' && (!Number.isFinite(value) || (Number.isInteger(value) && !Number.isSafeInteger(value)))) throw new IntegrityError('INVALID_NUMBER', 'A numeric field cannot be represented safely.');
  if (typeof value === 'string' && /[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/u.test(value)) throw new IntegrityError('INVALID_UNICODE', 'Text contains an invalid Unicode sequence.');
  if (value === null || ['string', 'boolean', 'number'].includes(typeof value)) return;
  if (Array.isArray(value)) { value.forEach(v => assertPlainJson(v, depth + 1)); return; }
  if (typeof value !== 'object' || Object.getPrototypeOf(value) !== Object.prototype) throw new IntegrityError('INVALID_JSON', 'Record contains an unsupported value.');
  for (const [key, item] of Object.entries(value as Record<string, unknown>)) { assertPlainJson(key, depth + 1); assertPlainJson(item, depth + 1); }
}
export function utf8(text: string): Uint8Array {
  assertPlainJson(text);
  const bytes: number[] = [];
  for (const char of text) { const n = char.codePointAt(0)!; if (n < 128) bytes.push(n); else if (n < 2048) bytes.push(192 | n >> 6, 128 | n & 63); else if (n < 65536) bytes.push(224 | n >> 12, 128 | n >> 6 & 63, 128 | n & 63); else bytes.push(240 | n >> 18, 128 | n >> 12 & 63, 128 | n >> 6 & 63, 128 | n & 63); }
  return Uint8Array.from(bytes);
}
export function digestBytes(bytes: Uint8Array): string { return [...sha256(bytes)].map(b => b.toString(16).padStart(2, '0')).join(''); }
export function digestText(text: string): string { return digestBytes(utf8(text)); }
export function canonicalJson(value: unknown): string { assertPlainJson(value); const result = canonicalize(value); if (result === undefined) throw new IntegrityError('INVALID_JSON', 'Record could not be canonicalized.'); return result; }
export function digest(value: unknown): string { return digestText(canonicalJson(value)); }
export function clone<T>(value: T): T { return JSON.parse(canonicalJson(value)) as T; }
export function assertBytes(value: unknown, limit: number): void { if (utf8(canonicalJson(value)).byteLength > limit) throw new IntegrityError('LIMIT_EXCEEDED', 'This record exceeds the supported size. Start a new check.'); }
export function parseBoundedJson(text: string, maxBytes = 1_048_576): unknown {
  if (utf8(text).byteLength > maxBytes) throw new IntegrityError('LIMIT_EXCEEDED', 'The response exceeds the supported size.');
  // Lexical walk detects duplicate object keys before JSON.parse loses them.
  let p = 0;
  const ws = () => { while (/\s/.test(text[p] ?? '') && p < text.length) p++; };
  const string = (): string => { const start = p++; let escaped = false; while (p < text.length) { const ch = text[p++]!; if (!escaped && ch === '"') return JSON.parse(text.slice(start, p)) as string; if (!escaped && ch === '\\') escaped = true; else escaped = false; } throw new IntegrityError('INVALID_JSON', 'The response is incomplete.'); };
  const value = (depth = 0): void => { if (depth > 40) throw new IntegrityError('JSON_DEPTH', 'The response is too deeply nested.'); ws(); const ch = text[p]; if (ch === '"') { string(); return; } if (ch === '{') { p++; ws(); const keys = new Set<string>(); if (text[p] === '}') { p++; return; } while (p < text.length) { ws(); if (text[p] !== '"') throw new Error('Invalid JSON'); const key = string(); if (keys.has(key)) throw new IntegrityError('DUPLICATE_KEY', 'The response contains duplicate fields.'); keys.add(key); ws(); if (text[p++] !== ':') throw new Error('Invalid JSON'); value(depth + 1); ws(); if (text[p] === '}') { p++; return; } if (text[p++] !== ',') throw new Error('Invalid JSON'); } } else if (ch === '[') { p++; ws(); if (text[p] === ']') { p++; return; } while (p < text.length) { value(depth + 1); ws(); if (text[p] === ']') { p++; return; } if (text[p++] !== ',') throw new Error('Invalid JSON'); } } else { const start = p; while (p < text.length && !/[\s,\]}]/.test(text[p]!)) p++; if (p === start) throw new Error('Invalid JSON'); } };
  value(); ws(); if (p !== text.length) throw new IntegrityError('INVALID_JSON', 'The response has unexpected content.'); const parsed: unknown = JSON.parse(text); assertPlainJson(parsed); return parsed;
}
export function requireObject(value: unknown): Record<string, unknown> { if (!value || typeof value !== 'object' || Array.isArray(value)) throw new IntegrityError('UNSUPPORTED_RESPONSE', 'The service returned an unsupported record.'); return value as Record<string, unknown>; }
export function knownKeys(value: Record<string, unknown>, keys: readonly string[]): void { for (const key of Object.keys(value)) if (!keys.includes(key)) throw new IntegrityError('UNSUPPORTED_FIELD', `Unsupported response field: ${key}`); }
export function requiredString(value: unknown, max = 256): string { if (typeof value !== 'string' || !value.length || value.length > max) throw new IntegrityError('INVALID_FIELD', 'A required text field is invalid.'); return value; }
export function safeInteger(value: unknown, min = 0): number { if (!Number.isSafeInteger(value) || (value as number) < min) throw new IntegrityError('INVALID_FIELD', 'A required integer is invalid.'); return value as number; }
