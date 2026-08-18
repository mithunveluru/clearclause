/**
 * Keeps lib/legal.ts the only place the operator's real details live.
 *
 * The addresses on these pages are currently placeholders. That is a launch blocker,
 * not a build failure, so this suite does not assert they are real — it asserts they
 * are all in one file, so that fixing them is one edit and cannot be done partially.
 * A half-updated privacy policy is the failure worth preventing here: it looks correct
 * and quietly points a third of its readers at an inbox that does not exist.
 */
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { CONTACT, GRIEVANCE_OFFICER, PLACEHOLDER_DOMAIN, usesPlaceholderContacts } from "./legal";

const LEGAL_DIR = join(__dirname, "..", "app", "legal");

function legalPages(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) =>
    entry.isDirectory()
      ? legalPages(join(dir, entry.name))
      : entry.name.endsWith(".tsx")
        ? [join(dir, entry.name)]
        : [],
  );
}

describe("legal page contacts", () => {
  const pages = legalPages(LEGAL_DIR);

  it("finds the legal pages at all", () => {
    // Otherwise every assertion below passes over an empty list
    expect(pages.length).toBeGreaterThan(4);
  });

  it.each(pages)("%s hardcodes no email address", (page) => {
    const source = readFileSync(page, "utf8");
    const hardcoded = source.match(/mailto:[^$`"'\s>]*@[^$`"'\s>]+/g) ?? [];
    expect(hardcoded).toEqual([]);
  });

  it.each(pages)("%s does not spell out the placeholder domain", (page) => {
    expect(readFileSync(page, "utf8")).not.toContain(PLACEHOLDER_DOMAIN);
  });

  it("does not publish a grievance officer who has not been appointed", () => {
    // An invented name is worse than an absent section: people write to it
    if (!GRIEVANCE_OFFICER.name) {
      const privacy = readFileSync(join(LEGAL_DIR, "privacy", "page.tsx"), "utf8");
      expect(privacy).toContain("GRIEVANCE_OFFICER.name");
    }
  });

  it("still reports that the contacts are placeholders", () => {
    // Flips to false the moment the addresses become real. When it does, delete this
    // test and check the launch checklist in docs/deploy-vps.md instead.
    expect(usesPlaceholderContacts()).toBe(true);
    expect(Object.values(CONTACT).every((a) => a.includes("@"))).toBe(true);
  });
});
