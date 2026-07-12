import type { Metadata } from "next";
import Link from "next/link";
import { LegalDoc } from "@/components/legal/LegalDoc";

export const metadata: Metadata = {
  title: "Security — ClearClause",
  description: "The security measures that protect your documents and account.",
};

export default function SecurityPage() {
  return (
    <LegalDoc
      title="Security"
      updated="13 July 2026"
      current="/legal/security"
      intro={
        <p>
          You upload agreements that can contain personal and financial details, so security is
          designed in rather than bolted on. This page describes the measures that exist in the
          product today — nothing aspirational.
        </p>
      }
      sections={[
        {
          id: "philosophy",
          title: "Data protection philosophy",
          body: (
            <>
              <p>The safest data is data we do not hold. ClearClause is built on three habits:</p>
              <ul>
                <li>
                  <strong>Collect little.</strong> An email address and the documents you choose
                  to upload — no analytics trackers, no advertising identifiers, no behavioural
                  profiles.
                </li>
                <li>
                  <strong>Keep it briefly.</strong> Documents and everything derived from them
                  are deleted automatically after seven days, and you can delete them sooner.
                </li>
                <li>
                  <strong>Process on our own servers where possible.</strong> Text extraction,
                  OCR, clause detection, and risk scoring all run on our infrastructure. Only the
                  summary and question-answering features send excerpts of extracted text to
                  external AI providers.
                </li>
              </ul>
            </>
          ),
        },
        {
          id: "encryption",
          title: "Encryption",
          body: (
            <ul>
              <li>
                <strong>In transit:</strong> the service is served over HTTPS, including calls to
                our AI providers.
              </li>
              <li>
                <strong>At rest:</strong> uploaded files and generated reports are stored with
                AES-256 encryption.
              </li>
              <li>
                <strong>Report downloads</strong> are served through short-lived signed links
                that expire within minutes, so report files are never publicly addressable.
              </li>
            </ul>
          ),
        },
        {
          id: "authentication",
          title: "Authentication and sessions",
          body: (
            <ul>
              <li>Passwords are stored only as bcrypt hashes, never in recoverable form.</li>
              <li>
                Sessions use short-lived tokens held in <strong>httpOnly, Secure cookies</strong>{" "}
                that JavaScript cannot read: a 30-minute access token, and a seven-day refresh
                token that is only ever sent to the authentication endpoints.
              </li>
              <li>
                Sign-in and registration are rate-limited, and repeated failed sign-ins trigger a
                temporary lockout.
              </li>
            </ul>
          ),
        },
        {
          id: "authorization",
          title: "Private document access",
          body: (
            <p>
              Every document, finding, report, and answer is scoped to the account that uploaded
              it. Authorization is enforced on every request, and our automated tests
              specifically verify that one account can never read another&rsquo;s documents.
            </p>
          ),
        },
        {
          id: "uploads",
          title: "Upload safeguards",
          body: (
            <p>
              Uploads are limited by file type, size (10&nbsp;MB), and page count (50 pages), and
              are validated before they reach storage. These limits protect the service from
              resource exhaustion and keep processing predictable.
            </p>
          ),
        },
        {
          id: "disclosure",
          title: "Responsible disclosure",
          body: (
            <>
              <p>
                If you believe you have found a security vulnerability in ClearClause, email{" "}
                <a href="mailto:security@clearclause.demo">security@clearclause.demo</a> with
                enough detail to reproduce it. We will acknowledge good-faith reports, will not
                pursue researchers legally for responsible testing, and will credit reporters who
                wish to be named once a fix ships.
              </p>
              <p>
                Please do not access other users&rsquo; data while testing — a proof of concept
                against your own account is always sufficient.
              </p>
            </>
          ),
        },
        {
          id: "related",
          title: "Related documents",
          body: (
            <p>
              What we collect and why is covered by the{" "}
              <Link href="/legal/privacy">Privacy Policy</Link>; the two cookies we set are listed
              in the <Link href="/legal/cookies">Cookie Policy</Link>.
            </p>
          ),
        },
      ]}
    />
  );
}
