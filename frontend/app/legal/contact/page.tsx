import type { Metadata } from "next";
import Link from "next/link";
import { LegalDoc } from "@/components/legal/LegalDoc";
import { CONTACT, ENTITY } from "@/lib/legal";
import { MailLink } from "@/components/legal/MailLink";

export const metadata: Metadata = {
  title: "Contact — ClearClause",
  description: "How to reach ClearClause for support, privacy requests, and security reports.",
};

export default function ContactPage() {
  return (
    <LegalDoc
      title="Contact"
      updated="13 July 2026"
      current="/legal/contact"
      intro={
        <p>
          {ENTITY.name} operates this service. Every route to reach us is below,
          along with what to expect when you do.
        </p>
      }
      sections={[
        {
          id: "general",
          title: "General enquiries",
          body: (
            <p>
              Anything that does not fit the categories below:{" "}
              <MailLink address={CONTACT.general} />.
            </p>
          ),
        },
        {
          id: "support",
          title: "Product support",
          body: (
            <p>
              Questions about using ClearClause, a document that failed to analyze, or trouble
              with your account:{" "}
              <MailLink address={CONTACT.support} />. Tell us the
              document name — never attach the document itself — and roughly when the problem
              occurred.
            </p>
          ),
        },
        {
          id: "privacy",
          title: "Privacy requests and complaints",
          body: (
            <>
              <p>
                To exercise any right described in the{" "}
                <Link href="/legal/privacy#your-rights">Privacy Policy</Link> — access,
                correction, erasure, account deletion, or nomination — email{" "}
                <MailLink address={CONTACT.privacy} /> from the
                address you registered with. The same address handles complaints about how your
                data has been handled.
              </p>
              <p>
                Deleting documents needs no request: the control is in your workspace, and
                automatic seven-day deletion runs regardless.
              </p>
            </>
          ),
        },
        {
          id: "security",
          title: "Security reports",
          body: (
            <p>
              Suspected vulnerabilities go to{" "}
              <MailLink address={CONTACT.security} />. The{" "}
              <Link href="/legal/security#disclosure">Security page</Link> sets out our
              responsible-disclosure commitments.
            </p>
          ),
        },
      ]}
    />
  );
}
