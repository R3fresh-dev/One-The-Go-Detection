import type { JsonObject } from '../core/types';

export interface MeasurementFact { label: string; value: string }
export interface SalivaPresentation { name: string; title: string; explanation: string; facts: MeasurementFact[] }
const finite = (value: unknown): value is number => typeof value === 'number' && Number.isFinite(value) && value >= 0;
const text = (value: unknown): string => typeof value === 'string' && value.length > 0 ? value : 'Not reported';
const object = (value: unknown): Record<string, unknown> => value !== null && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {};
const quantity = (value: unknown, unit = 'ng/mL'): string => finite(value) ? `${value} ${unit}` : 'Not reported';
const named = (value: unknown, names: Record<string, string>): string => typeof value === 'string' ? names[value] ?? value : 'Not reported';

/** Presentation only: no imputation, concentration calculation, dilution correction, or clinical classification. */
export function formatSalivaMeasurement(measurement: JsonObject): SalivaPresentation {
  const limits = object(measurement.limits), report = object(measurement.original_report);
  let title: string, explanation: string;
  switch (measurement.qualifier) {
    case 'quantified':
      title = finite(measurement.value_ng_ml) ? quantity(measurement.value_ng_ml) : 'Numeric result unavailable';
      explanation = 'Reported oral-fluid concentration. Analytical limits describe the method and do not establish an intoxication threshold.';
      break;
    case 'below_loq':
      title = `Below quantification limit${finite(limits.loq_ng_ml) ? ` (<${limits.loq_ng_ml} ng/mL)` : ''}`;
      explanation = 'The report places this result below the method’s quantification limit. Its concentration remains unknown; no substitute numeric value is assigned.';
      break;
    case 'above_range':
      title = `Above reportable range${finite(limits.upper_ng_ml) ? ` (>${limits.upper_ng_ml} ng/mL)` : ''}`;
      explanation = 'The result exceeds the reported upper quantification limit. The exact concentration is not available from this report.';
      break;
    case 'not_detected':
      title = `Not detected${finite(limits.lod_ng_ml) ? ` (<${limits.lod_ng_ml} ng/mL)` : ''}`;
      explanation = 'The method did not report detection for this analyte. This is not a measured zero concentration and does not establish an intoxication verdict.';
      break;
    case 'not_measured':
      title = 'Not measured';
      explanation = 'This analyte was not measured for this sample. There is no concentration result to interpret.';
      break;
    case 'invalid':
      title = 'Invalid measurement';
      explanation = 'The measurement could not be accepted under its quality rules. No usable concentration is assigned.';
      break;
    default:
      title = 'Unsupported measurement qualifier';
      explanation = 'This application cannot interpret the recorded qualifier. No numeric result is inferred.';
  }
  const originalValue = finite(report.value) ? `${report.value} ${text(report.unit)}` : `No numeric value (${text(report.unit)})`;
  return {
    name: named(measurement.analyte, { THC: 'THC', OH11_THC: '11-hydroxy-THC', THC_COOH: 'THC-COOH' }),
    title, explanation,
    facts: [
      { label: 'Detection limit (LOD)', value: quantity(limits.lod_ng_ml) },
      { label: 'Quantification limit (LOQ)', value: quantity(limits.loq_ng_ml) },
      { label: 'Upper quantification limit', value: quantity(limits.upper_ng_ml) },
      { label: 'Reported uncertainty', value: quantity(measurement.uncertainty_ng_ml) },
      { label: 'Collected (UTC)', value: text(measurement.collected_at) },
      { label: 'Measured (UTC)', value: text(measurement.measured_at) },
      { label: 'Assay basis', value: named(measurement.assay_basis, { free: 'Free analyte (as reported)', total_after_hydrolysis: 'Total after hydrolysis', unspecified: 'Not specified' }) },
      { label: 'Matrix / concentration basis', value: named(measurement.concentration_basis, { neat_oral_fluid: 'Neat oral fluid', collected_mixture: 'Collected oral-fluid mixture', unspecified: 'Not specified' }) },
      { label: 'Dilution correction', value: named(measurement.correction_status, { not_corrected: 'Not corrected', laboratory_corrected: 'Corrected by reporting laboratory', unspecified: 'Not specified' }) },
      { label: 'Original report qualifier', value: text(report.qualifier) },
      { label: 'Original report value / unit', value: originalValue },
      { label: 'Source', value: named(measurement.source, { simulated: 'Simulated — fictional values', reference_lab: 'Reference laboratory', prototype_sensor: 'Prototype sensor', validated_sensor: 'Validated sensor' }) },
      { label: 'Method', value: text(measurement.method_id) },
      { label: 'Calibration', value: text(measurement.calibration_id) },
      { label: 'Instrument', value: text(measurement.instrument_id) },
      { label: 'Cartridge lot', value: text(measurement.cartridge_lot) },
      { label: 'Operator reference', value: text(measurement.operator_ref) },
      { label: 'Quality flags', value: Array.isArray(measurement.quality_flags) ? measurement.quality_flags.filter(v => typeof v === 'string').join(', ') || 'None reported' : 'Not reported' },
      { label: 'Measurement ID', value: text(measurement.measurement_id) },
      { label: 'Sample ID', value: text(measurement.sample_id) },
    ],
  };
}
