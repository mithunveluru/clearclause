import type { Metadata } from "next";
import Link from "next/link";
import { LegalDoc } from "@/components/legal/LegalDoc";

export const metadata: Metadata = {
  title: "AI Disclaimer — ClearClause",
  description: "What automated analysis can and cannot do, and where you remain responsible.",
};

export default function AiDisclaimer() {
  return (
    <LegalDoc
      title="AI Disclaimer"
      updated="13 July 2026"
      current="/legal/ai-disclaimer"
      intro={
        <p>
          ClearClause exists to make dense agreements understandable. To do that honestly, we
          need to be equally clear about the limits of automated analysis. This page is part
          of our <Link href="/legal/terms">Terms of Service</Link>.
        </p>
      }
      sections={[
        {
          id: "how-analysis-works",
          title: "How the analysis works",
          body: (
            <>
              <p>
                Most of what ClearClause does is deterministic: text is extracted from your
                document (using OCR for scans), split into clauses, and matched against a
                rule-based library of patterns that commonly disadvantage consumers. Every
                finding cites the clause and page it came from, so you can verify it against
                the original wording.
              </p>
              <p>
                A language model additionally generates the plain-language summary and answers
                your questions about the document. Those answers are grounded in passages
                retrieved from your document and cite their sources — but they are generated
                text, not verified fact.
              </p>
            </>
          ),
        },
        {
          id: "what-can-go-wrong",
          title: "What can go wrong",
          body: (
            <ul>
              <li>
                <strong>Reading errors.</strong> Poor scans and photos can be misread. The
                service measures OCR confidence and warns you when a scan was hard to read —
                take that warning seriously.
              </li>
              <li>
                <strong>Missed or misjudged clauses.</strong> Rules cannot anticipate every
                drafting style. A risky clause may be missed, and a flagged clause may be less
                serious than its assigned severity suggests. Confidence indicators on each
                finding show how sure the system is.
              </li>
              <li>
                <strong>AI mistakes.</strong> Summaries and answers can be incomplete,
                overconfident, or simply wrong, even when they cite a source. Check the cited
                clause before acting on an answer.
              </li>
              <li>
                <strong>No context beyond the document.</strong> The analysis does not know
                your financial situation, your negotiation position, or the law applicable to
                your specific circumstances.
              </li>
            </ul>
          ),
        },
        {
          id: "your-responsibility",
          title: "Your responsibility",
          body: (
            <>
              <p>
                ClearClause informs your judgement; it does not replace it. You remain
                responsible for decisions you make about any agreement, including whether to
                sign, renegotiate, or walk away.
              </p>
              <p>
                The service is not a law firm, a financial advisor, or a government authority,
                and its output is not legal, financial, or tax advice. For significant
                commitments — loans, property, anything with penalties you could not
                comfortably absorb — have the agreement reviewed by a qualified professional.
                A good use of ClearClause is to arrive at that conversation already knowing
                which clauses to ask about.
              </p>
            </>
          ),
        },
        {
          id: "what-we-do-about-it",
          title: "What we do to keep the analysis honest",
          body: (
            <ul>
              <li>Every finding links to the exact clause and page it came from.</li>
              <li>Each finding carries a visible confidence indicator.</li>
              <li>Low-quality scans trigger an explicit warning on the report.</li>
              <li>
                Risk scoring is rule-based and inspectable, not an opaque model verdict.
              </li>
              <li>
                We never claim certified accuracy, government approval, or guaranteed
                completeness — and you should be sceptical of any tool that does.
              </li>
            </ul>
          ),
        },
      ]}
    />
  );
}
