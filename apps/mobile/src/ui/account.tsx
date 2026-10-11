import React, { useEffect, useRef, useState } from "react";
import {
  AccessibilityInfo,
  Linking,
  Platform,
  Text,
  TextInput,
  View,
} from "react-native";
import type { AppController, AppModel } from "../controller";
import {
  convertHeight,
  convertWeight,
  emptyProfile,
  normalizeProfile,
} from "../core/domain";
import { clone, IntegrityError } from "../core/integrity";
import {
  formatLocaleNumber,
  localeDecimal,
  validateProfileFields,
  type ProfileErrors,
  type ProfileField,
  type ProfileFields,
} from "../core/profileForm";
import type { CheckRecord, ProfileEnvelope } from "../core/types";
import { BUILD } from "../platform/config";
import {
  ActionRow,
  Badge,
  Button,
  Card,
  Choice,
  Fact,
  Field,
  Label,
  Metric,
  Notice,
  Page,
  Paragraph,
  Row,
  SwitchRow,
  Title,
  layout,
} from "./components";
import { useTheme } from "./theme";

export interface ScreenProps {
  controller: AppController;
  model: AppModel;
}
export const friendly = (value: unknown): string =>
  value === null || value === undefined
    ? "Not provided"
    : String(value).replaceAll("_", " ");
export const dateLabel = (value: string): string =>
  new Date(value).toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
export const shortId = (value: string | null): string =>
  value ? `${value.slice(0, 8)}…${value.slice(-6)}` : "None";
export const action =
  (controller: AppController, callback: () => Promise<unknown> | void) =>
  () => {
    void controller.run(async () => {
      await callback();
    });
  };
export function WelcomeScreen({ controller, model }: ScreenProps) {
  const [intro, setIntro] = useState(false),
    c = useTheme();
  return (
    <Page
      title={intro ? "Try a complete check" : "Your measurements, in one place"}
      eyebrow="One The Go · measurement companion"
      subtitle={
        intro
          ? "Explore the whole journey before connecting hardware."
          : "Collect a saliva result, eye and pulse measurements, and one reaction task. This release reports measurements only."
      }
    >
      <View
        style={{
          backgroundColor: c.navy,
          borderRadius: 26,
          padding: 28,
          gap: 22,
        }}
      >
        <Text
          style={{
            color: "#A9DDCF",
            fontSize: 12,
            letterSpacing: 2,
            fontWeight: "700",
          }}
        >
          A CLEARER VIEW OF YOUR DATA
        </Text>
        <Text
          style={{
            color: "#FFFFFF",
            fontSize: 29,
            fontWeight: "600",
            lineHeight: 37,
          }}
        >
          One check. Every measurement in context.
        </Text>
        <Row>
          {["01  Sample", "02  Measurements", "03  Reaction"].map((text) => (
            <View
              key={text}
              style={{
                borderWidth: 1,
                borderColor: "#45616D",
                borderRadius: 11,
                padding: 12,
              }}
            >
              <Text style={{ color: "#DAE9EC", fontSize: 13 }}>{text}</Text>
            </View>
          ))}
        </Row>
      </View>
      <Card>
        <Label>What this release does</Label>
        <Paragraph>
          Collect and organize measurement evidence, show its quality and
          source, and keep a clear history.
        </Paragraph>
        <Notice>
          It does not determine whether someone is intoxicated, impaired, or
          safe to drive. No validated impairment model is available.
        </Notice>
      </Card>
      {intro && (
        <Card>
          <Fact label="One sample" value="Fictional saliva example" />
          <Fact label="Guided measurements" value="Synthetic sensor examples" />
          <Fact
            label="One reaction task"
            value="Native practice on supported builds"
          />
          <Notice tone="warning">
            Demo sample and sensor values are synthetic. Reaction taps are a
            practice measurement. Guest demo records remain on this device and
            never upload.
          </Notice>
        </Card>
      )}
      <Button
        title={intro ? "Start demo" : "Explore the demo"}
        onPress={
          intro
            ? action(controller, () => controller.enterDemo())
            : () => setIntro(true)
        }
        busy={model.busy}
        testID="explore-demo"
      />
      <Button
        title="Sign in"
        secondary
        busy={model.busy}
        onPress={action(controller, () => controller.signIn())}
        testID="sign-in"
      />
      {intro && (
        <Button secondary title="Back" onPress={() => setIntro(false)} />
      )}
      <Row>
        <Button
          compact
          secondary
          title="Privacy"
          onPress={action(controller, () => controller.navigate("privacy"))}
        />
        <Button
          compact
          secondary
          title="About this release"
          onPress={action(controller, () => controller.navigate("about"))}
        />
      </Row>
      {BUILD.environment !== "prod" && (
        <Paragraph muted>
          {BUILD.environment.toUpperCase()} environment.{" "}
          {BUILD.environment === "local"
            ? "Account sign-in uses the isolated local fixture issuer. No real participants belong in this environment."
            : "Use the designated engineering or QA account."}
        </Paragraph>
      )}
    </Page>
  );
}
export function NoticeScreen({ controller, model }: ScreenProps) {
  const [ack, setAck] = useState(false),
    notice = model.state?.notice;
  return (
    <Page
      title="How your data is handled"
      eyebrow="Application notice"
      onBack={action(controller, () =>
        controller.navigate(model.identity ? "settings" : "welcome"),
      )}
    >
      {notice ? (
        <>
          <Card>
            <Row>
              <Badge>{notice.version}</Badge>
              <Badge>Verified plain text</Badge>
            </Row>
            <Paragraph>{notice.text}</Paragraph>
            <Fact label="SHA-256" value={notice.sha256} />
          </Card>
          <SwitchRow
            title="I have read how this app handles data."
            detail="This acknowledgment does not enroll you in research or upload a check."
            value={ack}
            onChange={setAck}
          />
          <Button
            title="Continue"
            disabled={!ack}
            busy={model.busy}
            onPress={action(controller, () => controller.acknowledgeNotice())}
            testID="acknowledge-notice"
          />
        </>
      ) : (
        <Card>
          <Paragraph>
            The current notice has not been loaded and verified yet.
          </Paragraph>
          <Button
            title="Retry loading notice"
            onPress={action(controller, async () => {
              await controller.refreshConfig();
              await controller.loadNotice();
            })}
          />
        </Card>
      )}
      <Button
        title="Privacy controls"
        secondary
        onPress={action(controller, () => controller.navigate("privacy"))}
      />
    </Page>
  );
}
export function LockedScreen({ controller, model }: ScreenProps) {
  return (
    <Page
      title="Your records are locked"
      eyebrow="Private workspace"
      subtitle="Use your device credential or enrolled biometrics to open this account’s encrypted records."
    >
      <Card>
        <Title small>Only this account can open its cache</Title>
        <Paragraph>
          After signing out, the same account must sign in again. Device
          authentication alone cannot open a signed-out account.
        </Paragraph>
        <Button
          title="Unlock records"
          busy={model.busy}
          onPress={action(controller, () => controller.unlock())}
          testID="unlock-records"
        />
        <Button
          title="Sign in again"
          secondary
          onPress={action(controller, () => controller.signIn())}
        />
      </Card>
      <Button
        title="Sign out on this device"
        secondary
        onPress={action(controller, () =>
          controller.ask({
            title: "Keep encrypted records and sign out?",
            text: "This account’s encrypted records stay locked on this device. They can be opened only after the same account signs in again.",
            confirm: "Keep records and sign out",
            action: () => controller.signOut(false),
          }),
        )}
      />
      <Button
        title="Recover local storage"
        secondary
        onPress={action(controller, () =>
          controller.ask({
            title: "Remove this account’s local storage?",
            text: "Use this only if the encryption key or database cannot be recovered. Unsynced records in this workspace will be lost. This does not delete cloud records.",
            confirm: "Remove local storage",
            danger: true,
            action: () => controller.resetStore(),
          }),
        )}
      />
    </Page>
  );
}
export function ContextFacts({ profile }: { profile: ProfileEnvelope }) {
  return (
    <>
      <Fact
        label="Age"
        value={
          profile.profile.age_years === null
            ? "Not provided"
            : `${profile.profile.age_years} years`
        }
      />
      <Fact
        label="Height / weight"
        value={`${profile.profile.height_cm === null ? "—" : `${profile.profile.height_cm.toFixed(1)} cm`} / ${profile.profile.weight_kg === null ? "—" : `${profile.profile.weight_kg.toFixed(1)} kg`}`}
      />
      <Fact
        label="BMI"
        value={
          profile.profile.bmi === null
            ? "Not available"
            : profile.profile.bmi.toFixed(1)
        }
      />
      <Fact label="Prior use" value={friendly(profile.history.use_frequency)} />
      <Fact
        label="Last use"
        value={
          profile.context.last_use_status === "known" &&
          profile.context.last_use_at
            ? dateLabel(profile.context.last_use_at)
            : friendly(profile.context.last_use_status)
        }
      />
      <Fact
        label="Sleep / recent exercise"
        value={`${profile.history.sleep_hours === null ? "Unknown" : `${profile.history.sleep_hours} h`} / ${profile.history.recent_exercise === null ? "Unknown" : profile.history.recent_exercise ? "Reported" : "Not reported"}`}
      />
    </>
  );
}
export function HomeScreen({ controller, model }: ScreenProps) {
  const state = model.state!,
    c = useTheme(),
    draft = state.checks.find(
      (x) =>
        !x.frozen &&
        x.generation === state.generation &&
        x.delivery !== "quarantined",
    ),
    [confirm, setConfirm] = useState(false),
    [mode, setMode] = useState<"measurement" | "engineering_fixture">(
      "measurement",
    );
  const fixtureAllowed =
      !!model.identity && ["local", "qa", "test"].includes(BUILD.environment),
    accountPaused =
      !!model.identity && state.capabilities?.account_state !== "active";
  const checks = state.checks.filter(
    (x) => x.generation === state.generation && x.delivery !== "quarantined",
  );
  return (
    <Page
      title="A check with context"
      eyebrow={
        model.identity ? "Your account workspace" : "Explore · guest demo"
      }
      subtitle="A clear record of what was measured, when, and how."
    >
      <View
        style={{
          backgroundColor: c.navy,
          borderRadius: 24,
          padding: 25,
          gap: 20,
        }}
      >
        <Text style={{ color: "#D2E7E9", fontSize: 13, letterSpacing: 1.5 }}>
          MEASUREMENT ONLY
        </Text>
        <Text
          style={{
            color: "#FFFFFF",
            fontSize: 25,
            fontWeight: "600",
            lineHeight: 33,
          }}
        >
          Understand the evidence. Keep its limitations visible.
        </Text>
        <Text style={{ color: "#BBD2D7", fontSize: 15, lineHeight: 23 }}>
          There is no intoxication score in this release. Valid measurements and
          uncalibrated practice remain distinct.
        </Text>
      </View>
      {model.pendingReplacement && (
        <Notice>
          Replacement for {shortId(model.pendingReplacement)}. Review the
          current context before starting. All acquisitions will be new.
        </Notice>
      )}
      {accountPaused && (
        <Card>
          <Notice tone="warning">
            Account data is {friendly(state.capabilities?.account_state)}. New
            account data is paused while the privacy request is resolved.
          </Notice>
          <Button
            title="Open privacy request"
            onPress={action(controller, () => controller.navigate("privacy"))}
          />
        </Card>
      )}
      {draft ? (
        <Card>
          <Badge tone="accent">Draft saved on this device</Badge>
          <Title small>Continue your check</Title>
          <Paragraph muted>
            Started {dateLabel(draft.snapshot.created_at)}. Your profile context
            is already frozen.
          </Paragraph>
          <Button
            title="Resume check"
            onPress={action(controller, () => controller.selectCheck(draft.id))}
            testID="resume-check"
          />
        </Card>
      ) : (
        <Card>
          <Row style={{ justifyContent: "space-between" }}>
            <Title small>Start a check</Title>
            <Badge>{model.identity ? "Private account" : "Guest demo"}</Badge>
          </Row>
          {fixtureAllowed && (
            <Choice
              label="Check type"
              value={mode}
              options={[
                { value: "measurement", label: "Measurements / practice" },
                {
                  value: "engineering_fixture",
                  label: "Fictional engineering fixture",
                },
              ]}
              onChange={setMode}
            />
          )}
          {model.identity && mode === "engineering_fixture" ? (
            <Notice>
              Fictional fixtures use a separate synthetic profile with all
              demographics and context unknown. Your saved personal profile is
              not included.
            </Notice>
          ) : (
            <ContextFacts profile={state.profile} />
          )}
          <Paragraph muted>
            These optional self-reported values freeze when you start. They
            cannot predict metabolism or impairment. Original last-use time is
            retained; elapsed time is recalculated at this check’s start.
          </Paragraph>
          <Button
            secondary
            title="Edit profile and context"
            onPress={action(controller, () => controller.navigate("profile"))}
          />
          <SwitchRow
            title="I have reviewed this check’s context."
            detail="Blank or unknown values are allowed. Updates after starting apply to a new check."
            value={confirm}
            onChange={setConfirm}
          />
          <Button
            title={
              model.identity && mode === "engineering_fixture"
                ? "Start fictional fixture"
                : model.identity
                  ? "Start check"
                  : "Start demo check"
            }
            disabled={!confirm || accountPaused}
            busy={model.busy}
            onPress={action(controller, () =>
              controller.beginCheck(
                model.identity ? mode : "guest_demo",
                confirm,
              ),
            )}
            testID="start-check"
          />
        </Card>
      )}
      <View style={layout.grid}>
        <Card style={layout.column}>
          <Label>Workspace</Label>
          <Row>
            <Metric
              label="Saved checks"
              value={String(checks.filter((x) => x.frozen).length)}
            />
            <Metric
              label="Queued"
              value={String(
                state.queue.filter(
                  (x) =>
                    x.kind === "check" &&
                    x.state !== "synced" &&
                    x.state !== "quarantined",
                ).length,
              )}
            />
          </Row>
          <Button
            title="View history"
            secondary
            onPress={action(controller, () => controller.navigate("history"))}
          />
        </Card>
        <Card style={layout.column}>
          <Label>Connected hardware</Label>
          <Paragraph>
            Qualified saliva, eye, ECG and alcohol instruments are unavailable
            in this release. Device discovery and fictional protocol transport
            are available for engineering.
          </Paragraph>
          <Button
            title="Devices and connection"
            secondary
            onPress={action(controller, () => controller.navigate("device"))}
          />
        </Card>
      </View>
      <Card>
        <ActionRow
          title="Alcohol measurement"
          detail="Unavailable · see requirements and separate units"
          onPress={action(controller, () => controller.navigate("alcohol"))}
        />
        <ActionRow
          title="Profile"
          detail="Optional context and units"
          onPress={action(controller, () => controller.navigate("profile"))}
        />
        <ActionRow
          title="Service and feature availability"
          detail={
            model.offline
              ? "Offline or service unavailable"
              : "Measurement-only release"
          }
          onPress={action(controller, () => controller.navigate("status"))}
        />
      </Card>
      {checks.slice(0, 3).map((check) => (
        <CheckRow
          key={check.id}
          check={check}
          onPress={action(controller, () => controller.selectCheck(check.id))}
        />
      ))}
    </Page>
  );
}
export function CheckRow({
  check,
  onPress,
}: {
  check: CheckRecord;
  onPress: () => void;
}) {
  return (
    <Card>
      <Row>
        <Badge tone={check.kind !== "measurement" ? "warning" : "neutral"}>
          {check.kind === "guest_demo"
            ? "Guest demo"
            : check.kind === "engineering_fixture"
              ? "Fictional fixture"
              : "Measurement record"}
        </Badge>
        <Badge>{friendly(check.delivery)}</Badge>
      </Row>
      <ActionRow
        title={dateLabel(check.snapshot.created_at)}
        detail={`${check.frozen ? "Measurements only" : `Draft · ${friendly(check.stage)}`} · ${shortId(check.id)}`}
        onPress={onPress}
      />
    </Card>
  );
}
export function ProfileScreen({ controller, model }: ScreenProps) {
  const base = model.state!.profile;
  const locale = new Intl.NumberFormat().resolvedOptions().locale;
  const [form, setForm] = useState(() => clone(base)),
    [units, setUnits] = useState(model.state!.preferences.units),
    [dirty, setDirty] = useState(false),
    [error, setError] = useState<string | null>(null),
    [errors, setErrors] = useState<ProfileErrors>({});
  const canonical = useRef({
    heightCm: base.profile.height_cm,
    weightKg: base.profile.weight_kg,
  });
  const edited = useRef({ height: false, weight: false }),
    revision = useRef(0),
    fieldRefs = useRef<Partial<Record<ProfileField, TextInput | null>>>({});
  const totalInches =
    base.profile.height_cm === null ? null : base.profile.height_cm / 2.54;
  const [age, setAge] = useState(
      formatLocaleNumber(base.profile.age_years, locale, 0),
    ),
    [height, setHeight] = useState(
      formatLocaleNumber(base.profile.height_cm, locale, 1),
    ),
    [feet, setFeet] = useState(
      formatLocaleNumber(
        totalInches === null ? null : Math.floor(totalInches / 12),
        locale,
        0,
      ),
    ),
    [inches, setInches] = useState(
      formatLocaleNumber(
        totalInches === null ? null : totalInches % 12,
        locale,
        2,
      ),
    ),
    [weight, setWeight] = useState(
      formatLocaleNumber(
        base.profile.weight_kg === null
          ? null
          : units === "imperial"
            ? base.profile.weight_kg / 0.45359237
            : base.profile.weight_kg,
        locale,
        2,
      ),
    ),
    [sleep, setSleep] = useState(
      formatLocaleNumber(base.history.sleep_hours, locale, 2),
    ),
    [lastUse, setLastUse] = useState(base.context.last_use_at ?? "");
  const fields = (): ProfileFields => ({
    age,
    height,
    feet,
    inches,
    weight,
    sleep,
    lastUse,
    units,
  });
  const unchangedCanonical = () => ({
    ...(!edited.current.height ? { heightCm: canonical.current.heightCm } : {}),
    ...(!edited.current.weight ? { weightKg: canonical.current.weightKg } : {}),
  });
  const markDirty = (field?: ProfileField) => {
    revision.current++;
    setDirty(true);
    if (field) {
      setErrors((old) => {
        const next = { ...old };
        delete next[field];
        return next;
      });
      if (["height", "feet", "inches"].includes(field))
        edited.current.height = true;
      if (field === "weight") edited.current.weight = true;
    }
  };
  const focusErrors = (values: ProfileErrors) => {
    const first = (
      [
        "age",
        "height",
        "feet",
        "inches",
        "weight",
        "lastUse",
        "sleep",
      ] as ProfileField[]
    ).find((key) => values[key]);
    const summary = Object.values(values).join(" ");
    setErrors(values);
    setError(summary);
    AccessibilityInfo.announceForAccessibility(`Review profile. ${summary}`);
    if (first) fieldRefs.current[first]?.focus();
  };
  const update = (change: (value: ProfileEnvelope) => void) => {
    setForm((old) => {
      const next = clone(old);
      change(next);
      return next;
    });
    markDirty();
  };
  const save = async () => {
    try {
      setError(null);
      const draftRevision = revision.current;
      const checked = validateProfileFields(
        form,
        fields(),
        locale,
        new Date().toISOString(),
        unchangedCanonical(),
      );
      if (!checked.profile) {
        focusErrors(checked.errors);
        return;
      }
      setErrors({});
      await controller.saveProfile(checked.profile);
      if (revision.current === draftRevision) {
        canonical.current = {
          heightCm: checked.profile.profile.height_cm,
          weightKg: checked.profile.profile.weight_kg,
        };
        edited.current = { height: false, weight: false };
        setDirty(false);
        AccessibilityInfo.announceForAccessibility(
          "Profile saved. Completed checks keep their original profile.",
        );
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Review the profile fields.");
    }
  };
  const displayCanonical = (value: "metric" | "imperial") => {
    const h = canonical.current.heightCm,
      w = canonical.current.weightKg,
      total = h === null ? null : h / 2.54;
    setHeight(formatLocaleNumber(h, locale, 1));
    setFeet(
      formatLocaleNumber(
        total === null ? null : Math.floor(total / 12),
        locale,
        0,
      ),
    );
    setInches(
      formatLocaleNumber(total === null ? null : total % 12, locale, 2),
    );
    setWeight(
      formatLocaleNumber(
        w === null ? null : value === "metric" ? w : w / 0.45359237,
        locale,
        2,
      ),
    );
  };
  const changeUnits = (value: "metric" | "imperial") => {
    if (value === units) return;
    const neutral = clone(form);
    neutral.context.last_use_status = "unknown";
    const checked = validateProfileFields(
      neutral,
      { ...fields(), age: "", sleep: "", lastUse: "" },
      locale,
      new Date().toISOString(),
      unchangedCanonical(),
    );
    if (!checked.profile) {
      focusErrors(checked.errors);
      return;
    }
    canonical.current = {
      heightCm: checked.profile.profile.height_cm,
      weightKg: checked.profile.profile.weight_kg,
    };
    edited.current = { height: false, weight: false };
    displayCanonical(value);
    setUnits(value);
    void controller
      .changePreferences({ units: value })
      .catch((e) => controller.report(e));
  };
  useEffect(() => {
    if (dirty) return;
    setForm(clone(base));
    canonical.current = {
      heightCm: base.profile.height_cm,
      weightKg: base.profile.weight_kg,
    };
    edited.current = { height: false, weight: false };
    setAge(formatLocaleNumber(base.profile.age_years, locale, 0));
    setSleep(formatLocaleNumber(base.history.sleep_hours, locale, 2));
    setLastUse(base.context.last_use_at ?? "");
    displayCanonical(units);
  }, [base.profile_version_id, base.revision, base.etag, dirty]);
  const back = action(controller, () =>
    dirty
      ? controller.ask({
          title: "Leave without saving this profile?",
          text: "Your edits have not been saved. Existing checks keep their original frozen context.",
          confirm: "Discard edits and leave",
          action: () => controller.navigate("home"),
        })
      : controller.navigate("home"),
  );
  const calculatedBmi =
    validateProfileFields(
      form,
      fields(),
      locale,
      new Date().toISOString(),
      unchangedCanonical(),
    ).profile?.profile.bmi ?? null;
  return (
    <Page
      title="Your profile & context"
      eyebrow="Optional self report"
      onBack={back}
      subtitle="Enter only what you want to share. These values are context, not a metabolic-rate or intoxication model."
    >
      {model.profileConflict && (
        <Card>
          <Notice tone="warning">
            Another device changed this profile. Your edits have not overwritten
            it.
          </Notice>
          <Title small>Server profile</Title>
          <ContextFacts profile={model.profileConflict} />
          <Button
            title="Use server profile"
            secondary
            onPress={action(controller, () => controller.resolveProfile(true))}
          />
          <Button
            title="Apply reviewed local values to current revision"
            onPress={action(controller, () =>
              controller.ask({
                title: "Replace the current profile with your reviewed values?",
                text: "This creates a new profile revision. Existing checks keep their frozen snapshots. The service will reject another concurrent change.",
                confirm: "Apply local profile",
                action: () => controller.resolveProfile(false),
              }),
            )}
          />
        </Card>
      )}
      <Card>
        <Label>Body context</Label>
        <Choice
          label="Display units"
          value={units}
          options={[
            { value: "metric", label: "cm / kg" },
            { value: "imperial", label: "ft + in / lb" },
          ]}
          onChange={changeUnits}
        />
        <Field
          label="Age (years)"
          value={age}
          inputRef={(ref) => {
            fieldRefs.current.age = ref;
          }}
          error={errors.age}
          onChangeText={(v) => {
            setAge(v);
            markDirty("age");
          }}
          keyboardType="number-pad"
          helper="Optional whole number, 18–125. Leave blank for unknown."
        />
        <View style={layout.grid}>
          {units === "metric" ? (
            <Field
              label="Height (cm)"
              value={height}
              inputRef={(ref) => {
                fieldRefs.current.height = ref;
              }}
              error={errors.height}
              onChangeText={(v) => {
                setHeight(v);
                markDirty("height");
              }}
              keyboardType="decimal-pad"
              helper={`Optional, up to one decimal place. Decimal separator: ${localeDecimal(locale)}.`}
            />
          ) : (
            <>
              <Field
                label="Height (whole feet)"
                value={feet}
                inputRef={(ref) => {
                  fieldRefs.current.feet = ref;
                }}
                error={errors.feet}
                onChangeText={(v) => {
                  setFeet(v);
                  markDirty("feet");
                }}
                keyboardType="number-pad"
                helper="Optional; provide feet and inches together."
              />
              <Field
                label="Additional height (inches)"
                value={inches}
                inputRef={(ref) => {
                  fieldRefs.current.inches = ref;
                }}
                error={errors.inches}
                onChangeText={(v) => {
                  setInches(v);
                  markDirty("inches");
                }}
                keyboardType="decimal-pad"
                helper="At least 0 and less than 12 inches."
              />
            </>
          )}
          <Field
            label={`Weight (${units === "metric" ? "kg" : "lb"})`}
            value={weight}
            inputRef={(ref) => {
              fieldRefs.current.weight = ref;
            }}
            error={errors.weight}
            onChangeText={(v) => {
              setWeight(v);
              markDirty("weight");
            }}
            keyboardType="decimal-pad"
            helper={`Optional, up to two decimal places. Decimal separator: ${localeDecimal(locale)}.`}
          />
        </View>
        <Fact
          label="Calculated BMI"
          value={
            calculatedBmi === null
              ? "Not available"
              : `${formatLocaleNumber(calculatedBmi, locale, 1)} kg/m²`
          }
        />
        <Paragraph muted>
          Calculated from your entered height and weight. Missing or invalid
          fields keep BMI unavailable; no health category is assigned.
        </Paragraph>
      </Card>
      <Card>
        <Label>Prior cannabis use</Label>
        <Choice
          label="How would you describe prior use?"
          value={form.history.use_frequency}
          options={[
            { value: "never", label: "Never" },
            { value: "occasional", label: "Occasional" },
            { value: "frequent", label: "Frequent" },
            { value: "daily", label: "Daily" },
            { value: "unknown", label: "Unknown" },
            { value: "declined", label: "Prefer not to say" },
          ]}
          onChange={(v) =>
            update((f) => {
              f.history.use_frequency = v;
            })
          }
        />
        <Paragraph muted>
          Your description; not a clinical tolerance category.
        </Paragraph>
        <Choice
          label="Most recent route"
          value={form.history.route}
          options={[
            { value: "inhaled", label: "Inhaled" },
            { value: "oral", label: "Oral" },
            { value: "other", label: "Other" },
            { value: "unknown", label: "Unknown" },
            { value: "declined", label: "Prefer not to say" },
          ]}
          onChange={(v) =>
            update((f) => {
              f.history.route = v;
            })
          }
        />
        <Choice
          label="Last use date and time"
          value={form.context.last_use_status}
          options={[
            { value: "known", label: "Enter date & time" },
            { value: "unknown", label: "Unknown" },
            { value: "declined", label: "Prefer not to say" },
          ]}
          onChange={(v) =>
            update((f) => {
              f.context.last_use_status = v;
            })
          }
        />
        {form.context.last_use_status === "known" && (
          <Field
            label="Last use (date, time and UTC offset)"
            value={lastUse}
            inputRef={(ref) => {
              fieldRefs.current.lastUse = ref;
            }}
            error={errors.lastUse}
            onChangeText={(v) => {
              setLastUse(v);
              markDirty("lastUse");
            }}
            autoCapitalize="none"
            autoCorrect={false}
            placeholder="2026-10-11T12:30:00+00:00"
            helper="Include a timezone offset or Z. A future time is rejected. The original timestamp is retained."
          />
        )}
      </Card>
      <Card>
        <Label>Other recent context</Label>
        <Field
          label="Sleep in the last 24 hours"
          value={sleep}
          inputRef={(ref) => {
            fieldRefs.current.sleep = ref;
          }}
          error={errors.sleep}
          onChangeText={(v) => {
            setSleep(v);
            markDirty("sleep");
          }}
          keyboardType="decimal-pad"
          helper="Optional, 0–24 hours."
        />
        <Choice
          label="Recent exercise"
          value={
            form.history.recent_exercise === null
              ? "unknown"
              : form.history.recent_exercise
                ? "yes"
                : "no"
          }
          options={[
            { value: "yes", label: "Reported" },
            { value: "no", label: "Not reported" },
            { value: "unknown", label: "Unknown" },
          ]}
          onChange={(v) =>
            update((f) => {
              f.history.recent_exercise = v === "unknown" ? null : v === "yes";
            })
          }
        />
        <Choice
          label="Alcohol co-use"
          value={form.history.alcohol_co_use}
          options={[
            { value: "reported", label: "Reported" },
            { value: "not_reported", label: "Not reported" },
            { value: "unknown", label: "Unknown" },
            { value: "declined", label: "Prefer not to say" },
          ]}
          onChange={(v) =>
            update((f) => {
              f.history.alcohol_co_use = v;
            })
          }
        />
      </Card>
      <Notice>
        {model.identity
          ? "Saving explicitly requests an account profile update. It does not queue any check for upload or change an existing check."
          : "This profile belongs only to the guest workspace and never uploads."}
      </Notice>
      {error && <Notice tone="danger">{error}</Notice>}
      <Button
        title="Save profile"
        busy={model.busy}
        onPress={action(controller, save)}
        testID="save-profile"
      />
      <Fact
        label="Saved revision"
        value={`${base.revision} · ${friendly(base.sync)}`}
      />
    </Page>
  );
}
