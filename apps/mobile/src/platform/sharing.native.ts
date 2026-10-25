import { Directory, File, Paths } from "expo-file-system";
import * as Sharing from "expo-sharing";
import { IntegrityError } from "../core/integrity";
const folder = () => new Directory(Paths.cache, "otgd-private-exports");
export async function cleanupExports(): Promise<void> {
  const directory = folder();
  if (!directory.exists) return;
  for (const file of directory.list())
    if (file instanceof File && file.name.startsWith("otgd-")) file.delete();
}
export async function shareArchive(
  bytes: Uint8Array,
  id: string,
  assertCurrent: () => void = () => {},
  authorizeRelease?: () => Promise<void>,
): Promise<void> {
  if (!(await Sharing.isAvailableAsync()))
    throw new IntegrityError(
      "SHARING_UNAVAILABLE",
      "The system share sheet is unavailable on this device.",
    );
  if (authorizeRelease) await authorizeRelease();
  assertCurrent();
  const directory = folder();
  directory.create({ intermediates: true, idempotent: true });
  const file = new File(
    directory,
    `otgd-${id.replace(/[^a-z0-9-]/gi, "")}.zip`,
  );
  try {
    file.create({ overwrite: true });
    file.write(bytes);
    assertCurrent();
    await Sharing.shareAsync(file.uri, {
      mimeType: "application/zip",
      UTI: "public.zip-archive",
      dialogTitle: "Share your selected records",
    });
  } finally {
    if (file.exists) file.delete();
  }
}
