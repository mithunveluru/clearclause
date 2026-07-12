import type { Metadata } from "next";
import Link from "next/link";
import { LegalDoc } from "@/components/legal/LegalDoc";

export const metadata: Metadata = {
  title: "Terms of Service — ClearClause",
  description: "The terms that govern your use of ClearClause.",
};

export default function TermsOfService() {
  return (
    <LegalDoc
      title="Terms of Service"
      updated="13 July 2026"
      current="/legal/terms"
      intro={
        <p>
          These terms are an agreement between you and ClearClause Technologies
          (&ldquo;ClearClause&rdquo;, &ldquo;we&rdquo;, &ldquo;us&rdquo;). By creating an
          account or using the service you accept them. They are written to describe the
          service as it actually works — if anything here is unclear, ask us before relying on
          it.
        </p>
      }
      sections={[
        {
          id: "service",
          title: "What ClearClause is",
          body: (
            <>
              <p>
                ClearClause is an automated document-review tool. You upload a loan agreement,
                subscription terms, or a similar consumer document; the service extracts the
                text, identifies clauses that commonly disadvantage consumers — fees,
                penalties, auto-renewals, consent traps — estimates their financial impact, and
                presents the findings in plain language, along with a summary and the ability
                to ask questions about the document.
              </p>
              <p>
                <strong>ClearClause is an informational tool, not an advisor.</strong> It does
                not provide legal, financial, or professional advice, and its output is not a
                substitute for reading your agreement or consulting a qualified professional.
                The <Link href="/legal/ai-disclaimer">AI Disclaimer</Link> forms part of these
                terms.
              </p>
            </>
          ),
        },
        {
          id: "eligibility",
          title: "Eligibility",
          body: (
            <p>
              You must be at least 18 years old and capable of entering into a binding contract
              under the Indian Contract Act, 1872 to use ClearClause. By creating an account you
              confirm that you meet these requirements.
            </p>
          ),
        },
        {
          id: "accounts",
          title: "Your account",
          body: (
            <>
              <ul>
                <li>Provide a valid email address when registering.</li>
                <li>
                  Keep your password confidential. You are responsible for activity under your
                  account.
                </li>
                <li>Tell us promptly if you believe your account has been compromised.</li>
              </ul>
              <p>
                Sign-in is protected by rate limiting and temporary lockouts after repeated
                failed attempts. These protections are part of the service and you agree not to
                circumvent them.
              </p>
            </>
          ),
        },
        {
          id: "acceptable-use",
          title: "Acceptable use",
          body: (
            <>
              <p>
                <strong>You may</strong> upload documents that you have the right to possess and
                share for review — your own agreements, or documents you are authorised to
                analyze.
              </p>
              <p>
                <strong>You may not:</strong>
              </p>
              <ul>
                <li>
                  upload documents you have no right to share, or content that is unlawful to
                  possess or distribute;
                </li>
                <li>
                  use the service to break the law, or to infringe anyone&rsquo;s privacy or
                  intellectual property;
                </li>
                <li>
                  probe, overload, or disrupt the service, attempt to reach other users&rsquo;
                  documents or accounts, or bypass usage limits and security controls;
                </li>
                <li>
                  scrape the service, resell it, or present its output as a professional legal
                  or financial opinion.
                </li>
              </ul>
            </>
          ),
        },
        {
          id: "your-documents",
          title: "Your documents",
          body: (
            <>
              <p>
                <strong>You own your documents.</strong> Uploading them transfers no ownership
                to us. You grant us a limited licence to store, extract text from, analyze, and
                generate reports from each document, solely to provide the service to you. That
                licence ends when the document is deleted — automatically seven days after
                upload, or sooner if you delete it yourself.
              </p>
              <p>
                We do not use your documents to train AI models, and we do not share their
                contents except as described in the{" "}
                <Link href="/legal/privacy">Privacy Policy</Link>.
              </p>
            </>
          ),
        },
        {
          id: "our-ip",
          title: "Our intellectual property",
          body: (
            <p>
              The ClearClause software, design, brand, and analysis methodology belong to us or
              our licensors. These terms give you a personal, non-exclusive, non-transferable
              right to use the service; they give you no right to copy, modify, or create
              derivative works from the software itself.
            </p>
          ),
        },
        {
          id: "analysis-limits",
          title: "Limits of automated analysis",
          body: (
            <>
              <p>By using the service you acknowledge that:</p>
              <ul>
                <li>
                  analysis is automated and may miss clauses, misread text — particularly in
                  poor scans, where the service warns you that quality was low — or assign an
                  inaccurate severity;
                </li>
                <li>
                  AI-generated summaries and answers can contain errors, and each finding should
                  be checked against the clause it cites before you rely on it;
                </li>
                <li>
                  risk scores are indicative comparisons, not certifications that a document is
                  safe or fair;
                </li>
                <li>
                  significant decisions — signing a loan, ending a contract, starting a dispute
                  — deserve advice from a qualified professional.
                </li>
              </ul>
            </>
          ),
        },
        {
          id: "fees",
          title: "Fees",
          body: (
            <p>
              ClearClause is free to use. There are no charges, no subscriptions, and no
              payments of any kind, so no refund policy is needed. If paid plans are ever
              introduced, pricing and refund terms will be published and agreed before anyone is
              charged.
            </p>
          ),
        },
        {
          id: "availability",
          title: "Availability and changes to the service",
          body: (
            <>
              <p>
                We work to keep ClearClause available and fast, but we do not guarantee
                uninterrupted operation. The service may be briefly unavailable during
                maintenance or incidents, and analysis of an individual document can
                occasionally fail — you can re-upload if it does.
              </p>
              <p>
                We may add, change, or remove features, and we may discontinue the service. If
                we discontinue it, we will give reasonable notice where practicable; automatic
                deletion means little of your data would remain in any case.
              </p>
            </>
          ),
        },
        {
          id: "termination",
          title: "Termination",
          body: (
            <>
              <p>
                You may stop using ClearClause at any time and ask us to delete your account —
                see the <Link href="/legal/privacy#deleting-data">Privacy Policy</Link>. We may
                suspend or terminate accounts that breach these terms, abuse the service, or
                create legal or security risk; where reasonable, we will tell you why.
              </p>
              <p>
                On termination, your documents and analyses are deleted on the same schedule as
                always. Sections that by their nature should survive — ownership, disclaimers,
                liability limits, governing law — survive.
              </p>
            </>
          ),
        },
        {
          id: "disclaimers",
          title: "Disclaimers",
          body: (
            <p>
              The service is provided <strong>&ldquo;as is&rdquo; and &ldquo;as
              available&rdquo;</strong>. To the extent permitted by law, we disclaim implied
              warranties of merchantability, fitness for a particular purpose, and
              non-infringement. Nothing in these terms excludes liability that cannot be
              excluded under applicable Indian law.
            </p>
          ),
        },
        {
          id: "liability",
          title: "Limitation of liability",
          body: (
            <>
              <p>
                To the extent permitted by applicable law, we are not liable for indirect,
                incidental, or consequential losses, including decisions taken in reliance on
                automated analysis. Because ClearClause is provided free of charge, our
                aggregate liability arising out of the service is limited to the amount you have
                paid us for it, which is nil.
              </p>
              <p>
                Nothing here limits liability for fraud, wilful misconduct, or anything that
                cannot lawfully be limited.
              </p>
            </>
          ),
        },
        {
          id: "indemnity",
          title: "Indemnity",
          body: (
            <p>
              If your breach of these terms — in particular uploading documents you had no right
              to share, or unlawful use of the service — causes a third-party claim against us,
              you agree to indemnify us for the resulting losses and reasonable costs.
            </p>
          ),
        },
        {
          id: "law",
          title: "Governing law",
          body: (
            <p>
              These terms are governed by the laws of India, and disputes arising from them are
              subject to the jurisdiction of the Indian courts. Nothing here removes any
              mandatory protection available to you as a consumer under Indian law.
            </p>
          ),
        },
        {
          id: "changes",
          title: "Changes to these terms",
          body: (
            <p>
              We may update these terms as the service evolves. The date at the top always
              reflects the current version, and material changes will be announced in the
              application before they take effect. Continuing to use ClearClause after a change
              takes effect means you accept the updated terms.
            </p>
          ),
        },
        {
          id: "contact",
          title: "Contact",
          body: (
            <p>
              Questions about these terms:{" "}
              <a href="mailto:support@clearclause.demo">support@clearclause.demo</a>. Other ways
              to reach us are on the <Link href="/legal/contact">Contact</Link> page.
            </p>
          ),
        },
      ]}
    />
  );
}
