import participantFixture from "../../testfixtures/backend-participant-acquisition.json";
import { clone, digest, digestText } from "../../src/core/integrity";

/** Controlled instructional contract only; no physical setup or study admission. */
export function preparationConfiguration(rest = 30) {
  const configuration = clone(
    participantFixture.import_flow.capabilities.channels.saliva
      .configurations[0],
  ) as any;
  const text =
    "Fictional cardiac setup instructions for the browser software test.";
  configuration.participant_protocol = {
    schema_version: "1.0.0",
    kind: "cardiac",
    instruction_id: "fictional-preparation-clock",
    version: "v1",
    text,
    sha256: digestText(text),
    maximum_acknowledgment_age_seconds: 120,
    required_confirmations: [
      "rest_completed",
      "posture_confirmed",
      "activity_confirmed",
      "contact_confirmed",
      "isolation_confirmed",
    ].map((id) => ({ id, text: id })),
    operating_scope: "engineering_bench",
    operating_state_verifier: "participant_declaration_only",
    rest_duration_seconds: rest,
    posture_instruction: "Fictional seated posture",
    activity_instruction: "Remain still",
    contact_instruction: "Fictional bench contacts only",
    isolation_instruction: "No human leads; software test only",
    permitted_setups: [
      {
        id: "fictional-bench",
        description: "Fictional portable bench",
        power_state: "battery",
        charging_state: "off",
        cable_state: "none",
        contact_or_lead_configuration: "bench contacts",
      },
    ],
  };
  configuration.participant_protocol_sha256 = digest(
    configuration.participant_protocol,
  );
  configuration.submitted_sha256 = digest({
    fixture: "fictional-clock-component",
    protocol: configuration.participant_protocol,
  });
  return configuration;
}
