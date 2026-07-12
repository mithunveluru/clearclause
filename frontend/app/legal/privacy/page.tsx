import type { Metadata } from "next";
import Link from "next/link";
import { LegalDoc } from "@/components/legal/LegalDoc";

export const metadata: Metadata = {
  title: "Privacy Policy — ClearClause",
  description: "How ClearClause collects, uses, protects, and deletes your information.",
};

export default function PrivacyPolicy() {
  return (
    <LegalDoc
      title="Privacy Policy"
      updated="13 July 2026"
      current="/legal/privacy"
      intro={
        <>
          <p>
            ClearClause helps you understand loan agreements, subscription terms, and similar
            documents before you sign them. Because you upload documents that can contain
            personal and financial details, the service is designed to collect little, keep it
            briefly, and delete it thoroughly. This policy explains exactly what we collect,
            why, and what happens to it.
          </p>
          <p>
            ClearClause is operated by ClearClause Technologies (&ldquo;ClearClause&rdquo;,
            &ldquo;we&rdquo;, &ldquo;us&rdquo;). It is written with reference to the Digital
            Personal Data Protection Act, 2023 and the Information Technology Act, 2000, and
            it describes how the application actually works today.
          </p>
        </>
      }
      sections={[
        {
          id: "what-we-collect",
          title: "Information we collect",
          body: (
            <>
              <p>
                <strong>Account information.</strong> Your email address and a password. The
                password is never stored as you typed it — only a one-way bcrypt hash is kept,
                which cannot be reversed to reveal your password.
              </p>
              <p>
                <strong>Documents you upload.</strong> PDF, PNG, or JPG files of up to 10&nbsp;MB
                and 50 pages, and the text extracted from them. Agreements often contain
                personal and financial details — names, amounts, account references — and every
                uploaded document is treated as sensitive by default.
              </p>
              <p>
                <strong>Analysis results.</strong> The clauses, findings, risk scores,
                summaries, and PDF reports generated from your document. These are stored
                alongside the document and deleted with it.
              </p>
              <p>
                <strong>Technical and security data.</strong> Standard server logs and metrics
                (such as request paths, timestamps, and status codes), and short-lived
                rate-limiting counters that protect sign-in from abuse. We run no third-party
                analytics, advertising, or tracking tools.
              </p>
            </>
          ),
        },
        {
          id: "why-we-collect",
          title: "Why we collect it",
          body: (
            <>
              <ul>
                <li>To create and secure your account and keep you signed in.</li>
                <li>
                  To analyze the documents you upload and show you the findings, scores,
                  reports, and answers you asked for — the entire purpose of the service.
                </li>
                <li>To protect the service against abuse, fraud, and attacks.</li>
                <li>To operate, monitor, and troubleshoot the service.</li>
              </ul>
              <p>
                We do not use your documents or their contents for advertising, we do not sell
                or rent personal data, and we do not use your documents to train AI models.
              </p>
            </>
          ),
        },
        {
          id: "how-processing-works",
          title: "How your documents are processed",
          body: (
            <>
              <p>
                Processing starts automatically when you upload. Text is read from the
                PDF&rsquo;s own text layer where one exists; scanned pages and photographs are
                read using optical character recognition (OCR) that runs{" "}
                <strong>on our own servers</strong> — no external OCR service receives your
                file. The clause detection, risk scoring, and report generation that follow are
                rule-based and also run on our servers.
              </p>
              <p>
                Analysis is automated from beginning to end. Staff access to stored documents
                is restricted and is not part of routine operation.
              </p>
            </>
          ),
        },
        {
          id: "ai-features",
          title: "AI features and what they receive",
          body: (
            <>
              <p>
                ClearClause can generate a plain-language summary of your document and answer
                questions about it. Where these AI features are enabled:
              </p>
              <ul>
                <li>
                  <strong>Summaries and answers</strong> are produced by sending relevant
                  excerpts of the extracted text to Groq, Inc., an AI inference provider, over
                  an encrypted connection. Your original file is never sent — only extracted
                  text.
                </li>
                <li>
                  <strong>Embeddings</strong> — numerical representations of text passages,
                  used to find the right clause for a question — are computed by sending text
                  passages to Jina AI over an encrypted connection. The resulting vectors are
                  held in a vector database we host ourselves and are deleted when the document
                  is deleted.
                </li>
                <li>
                  <strong>Questions you type</strong> are used to produce an answer and are not
                  stored afterwards. Generated summaries are stored with the document and
                  deleted with it.
                </li>
              </ul>
              <p>
                These providers process the text to return a response and handle it under their
                own terms. Where AI features are switched off, no document content leaves our
                infrastructure at all.
              </p>
            </>
          ),
        },
        {
          id: "retention",
          title: "How long we keep data",
          body: (
            <>
              <p>
                <strong>Documents and everything derived from them are deleted automatically
                seven days after upload</strong> — the file, the extracted text, the clauses and
                findings, the risk score, the generated report, any AI summary, and any
                embedding vectors. You do not need to do anything for this to happen.
              </p>
              <p>
                You can also delete any document yourself at any time from your workspace,
                which removes the same set of data immediately.
              </p>
              <p>
                Account information — your email address and password hash — is kept while your
                account exists. Operational logs and metrics are retained for a limited period
                for troubleshooting and security, and are not used to profile you.
              </p>
            </>
          ),
        },
        {
          id: "deleting-data",
          title: "Deleting your data",
          body: (
            <ul>
              <li>
                <strong>Documents:</strong> delete them from your workspace at any time, or let
                automatic seven-day deletion handle it.
              </li>
              <li>
                <strong>Your account:</strong> email{" "}
                <a href="mailto:privacy@clearclause.demo">privacy@clearclause.demo</a> from the
                address you registered with, and we will delete your account and any remaining
                data associated with it. Account deletion is handled on request rather than
                through an in-app control.
              </li>
            </ul>
          ),
        },
        {
          id: "security",
          title: "How we protect data",
          body: (
            <p>
              Documents and reports are stored encrypted at rest, and the service is served
              over HTTPS. Sign-in is protected by hashed passwords, short-lived session
              cookies, rate limiting, and a temporary lockout after repeated failed attempts.
              Every document is accessible only to the account that uploaded it. The{" "}
              <Link href="/legal/security">Security page</Link> describes these measures in
              detail.
            </p>
          ),
        },
        {
          id: "third-parties",
          title: "Third-party processors",
          body: (
            <>
              <p>We share data only with the providers needed to run the service:</p>
              <table>
                <thead>
                  <tr>
                    <th>Provider</th>
                    <th>Purpose</th>
                    <th>What they receive</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Cloud hosting and storage providers</td>
                    <td>Run our servers, database, and encrypted file storage</td>
                    <td>Service data held on our infrastructure, encrypted at rest</td>
                  </tr>
                  <tr>
                    <td>Groq, Inc.</td>
                    <td>AI summaries and answers</td>
                    <td>Excerpts of extracted text</td>
                  </tr>
                  <tr>
                    <td>Jina AI</td>
                    <td>Text embeddings used to retrieve the right clause</td>
                    <td>Passages of extracted text</td>
                  </tr>
                </tbody>
              </table>
              <p>
                We may also disclose information where required by law or by a valid order of a
                court or authority. We do not sell personal data to anyone.
              </p>
            </>
          ),
        },
        {
          id: "cross-border",
          title: "Cross-border transfers",
          body: (
            <p>
              Where AI features are enabled, excerpts of extracted text are processed by Groq
              and Jina AI on servers that may be located outside India, including in the United
              States. No other document data leaves our infrastructure. If you would rather no
              text left the country at all, avoid using the summary and question-and-answer
              features — the rule-based analysis, findings, and report are produced entirely on
              our own servers.
            </p>
          ),
        },
        {
          id: "your-rights",
          title: "Your rights",
          body: (
            <>
              <p>
                Under the Digital Personal Data Protection Act, 2023 you have the right to
                access a summary of your personal data and how it is processed, to have it
                corrected or completed, to have it erased, to have your concerns addressed, and
                to nominate another person to exercise these rights on your behalf.
              </p>
              <p>
                To exercise any of these rights, email{" "}
                <a href="mailto:privacy@clearclause.demo">privacy@clearclause.demo</a>. Deleting
                documents requires no request at all — the control is in your workspace, and
                automatic deletion runs regardless.
              </p>
            </>
          ),
        },
        {
          id: "children",
          title: "Children",
          body: (
            <p>
              ClearClause is intended for adults reviewing financial and legal agreements. You
              must be at least 18 years old to create an account. We do not knowingly collect
              personal data from children; if you believe a child has created an account,
              contact us and we will delete it.
            </p>
          ),
        },
        {
          id: "cookies",
          title: "Cookies",
          body: (
            <p>
              We use exactly two cookies, both essential for signing you in, and no analytics or
              advertising cookies of any kind. The{" "}
              <Link href="/legal/cookies">Cookie Policy</Link> lists them.
            </p>
          ),
        },
        {
          id: "changes",
          title: "Changes to this policy",
          body: (
            <p>
              If we change this policy we will update the date at the top and, for material
              changes, notify you within the application before the change takes effect. We will
              not retroactively weaken the protections described here for data we already hold.
            </p>
          ),
        },
        {
          id: "contact",
          title: "Contact",
          body: (
            <p>
              Privacy questions, requests, and complaints:{" "}
              <a href="mailto:privacy@clearclause.demo">privacy@clearclause.demo</a>. If a
              concern is not resolved to your satisfaction, you may approach the Data Protection
              Board of India under the Digital Personal Data Protection Act, 2023. Other ways to
              reach us are listed on the <Link href="/legal/contact">Contact</Link> page.
            </p>
          ),
        },
      ]}
    />
  );
}
