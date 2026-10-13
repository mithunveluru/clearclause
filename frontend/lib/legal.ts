/**
 * Facts about the operator, as opposed to statements of policy.
 *
 * Every one of these is a PLACEHOLDER. The legal pages render them verbatim, so this
 * service must not be offered to the public until each address is real and monitored
 * and the entity is really registered — a privacy policy that names an inbox nobody
 * reads is worse than one that names none.
 *
 * They live here rather than in the pages so that filling them in is a single edit.
 * lib/legal.test.ts fails the build if a page hardcodes a contact instead of importing
 * from this file, which is what keeps that true.
 */

/** Reserved for documentation, so a leftover placeholder is greppable and testable. */
export const PLACEHOLDER_DOMAIN = "clearclause.demo";

export const ENTITY = {
  /** Must match the name on the certificate of incorporation, not a product name. */
  name: "ClearClause Technologies",
  jurisdiction: "India",
};

export const CONTACT = {
  general: `hello@${PLACEHOLDER_DOMAIN}`,
  support: `support@${PLACEHOLDER_DOMAIN}`,
  privacy: `privacy@${PLACEHOLDER_DOMAIN}`,
  security: `security@${PLACEHOLDER_DOMAIN}`,
} as const;

/**
 * The DPDP Act requires a Data Fiduciary to publish the contact of a person who
 * answers grievances.
 *
 * An empty name hides the section instead of printing an officer who does not exist.
 * Naming a placeholder person would be inventing a compliance contact, which is worse
 * than publishing none — so fill this in before launch rather than leaving it.
 */
export const GRIEVANCE_OFFICER = {
  name: "",
  email: CONTACT.privacy,
};

/** True while any contact is still a placeholder. Gate a launch checklist on this. */
export function usesPlaceholderContacts(): boolean {
  return Object.values(CONTACT).some((address) => address.endsWith(PLACEHOLDER_DOMAIN));
}
