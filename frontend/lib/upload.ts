// Mirrors backend/app/core/files.py ALLOWED_EXTENSIONS and config MAX_UPLOAD_MB.
// ponytail: duplicated constants; the server still validates, this only saves a round trip.
export const ACCEPTED_EXTS = [".pdf", ".png", ".jpg", ".jpeg"];
export const MAX_UPLOAD_MB = 10;

/** "" when the file may be uploaded, otherwise the message to show. */
export function validateFile(f: { name: string; size: number }): string {
  const dot = f.name.lastIndexOf(".");
  const ext = dot === -1 ? "" : f.name.slice(dot).toLowerCase();
  if (!ACCEPTED_EXTS.includes(ext)) return "That file type isn't supported. Use a PDF, PNG or JPG.";
  if (f.size === 0) return "That file is empty.";
  if (f.size > MAX_UPLOAD_MB * 1024 * 1024) return `That file is larger than ${MAX_UPLOAD_MB} MB.`;
  return "";
}
