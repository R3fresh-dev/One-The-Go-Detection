import React from 'react';
import { requireOptionalNativeModule, requireNativeViewManager } from 'expo-modules-core';
import type { ReactionTaskAvailability, ReactionTaskViewProps, ReactionTaskViewRef } from './types';
import { REACTION_CONFIGURATION_ID, REACTION_CONFIGURATION_SHA256 } from './types';
export * from './types';

const native = requireOptionalNativeModule<{ getAvailability(): ReactionTaskAvailability }>('OTGDReactionTask');
/** Availability is explicit: this module never replaces native acquisition with JS timers. */
export function getReactionTaskAvailability(): ReactionTaskAvailability {
  return native?.getAvailability() ?? {
    available: false, platform: 'unavailable', configurationId: REACTION_CONFIGURATION_ID,
    configurationSha256: REACTION_CONFIGURATION_SHA256, modelEligible: false, reason: 'NATIVE_MODULE_UNAVAILABLE',
  };
}
export const getAvailability = getReactionTaskAvailability;
const NativeView = native ? requireNativeViewManager<ReactionTaskViewProps>('OTGDReactionTask') : null;
export const ReactionTaskView = React.forwardRef<ReactionTaskViewRef, ReactionTaskViewProps>((props, ref) => {
  if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(props.runId) || !Number.isInteger(props.seed) || props.seed < 0 || props.seed > 0xffffffff || !props.workspaceEpoch || props.workspaceEpoch.length > 128) throw new Error('INVALID_NATIVE_TASK_REQUEST');
  if (props.configurationId !== REACTION_CONFIGURATION_ID || props.configurationSha256 !== REACTION_CONFIGURATION_SHA256) throw new Error('TASK_CONFIGURATION_UNSUPPORTED');
  if (!NativeView) throw new Error('NATIVE_MODULE_UNAVAILABLE: use the availability screen before rendering ReactionTaskView');
  return React.createElement(NativeView, { ...props, ref } as ReactionTaskViewProps & { ref: React.ForwardedRef<ReactionTaskViewRef> });
});
ReactionTaskView.displayName = 'ReactionTaskView';
