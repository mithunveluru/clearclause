import { describe, expect, it } from "vitest";
import { validateFile } from "./upload";

const MB = 1024 * 1024;

describe("validateFile", () => {
  it("accepts supported types regardless of case", () => {
    expect(validateFile({ name: "Loan.PDF", size: MB })).toBe("");
    expect(validateFile({ name: "scan.jpeg", size: MB })).toBe("");
  });
  it("rejects unsupported or missing extensions", () => {
    expect(validateFile({ name: "terms.docx", size: MB })).toMatch(/isn't supported/);
    expect(validateFile({ name: "pdf", size: MB })).toMatch(/isn't supported/);
  });
  it("enforces the size limit at the boundary", () => {
    expect(validateFile({ name: "a.pdf", size: 10 * MB })).toBe("");
    expect(validateFile({ name: "a.pdf", size: 10 * MB + 1 })).toMatch(/larger than 10 MB/);
    expect(validateFile({ name: "a.pdf", size: 0 })).toMatch(/empty/);
  });
});
