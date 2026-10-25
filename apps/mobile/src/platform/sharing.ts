export async function cleanupExports(): Promise<void> {}
export async function shareArchive(
  bytes: Uint8Array,
  id: string,
  assertCurrent: () => void = () => {},
  authorizeRelease?: () => Promise<void>,
): Promise<void> {
  if (authorizeRelease) await authorizeRelease();
  assertCurrent();
  const blob = new Blob([new Uint8Array(bytes).buffer], {
      type: "application/zip",
    }),
    url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `otgd-${id.replace(/[^a-z0-9-]/gi, "")}.zip`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
