import type { Metadata } from "next";
import Link from "next/link";
import { LegalDoc } from "@/components/legal/LegalDoc";

export const metadata: Metadata = {
  title: "Cookie Policy — ClearClause",
  description: "The two essential cookies ClearClause sets, and nothing else.",
};

export default function CookiePolicy() {
  return (
    <LegalDoc
      title="Cookie Policy"
      updated="13 July 2026"
      current="/legal/cookies"
      intro={
        <p>
          This is a short policy because there is little to disclose: ClearClause sets exactly
          two cookies, both strictly necessary for signing you in. There are no analytics
          cookies, no advertising cookies, no third-party cookies, and no tracking via browser
          storage.
        </p>
      }
      sections={[
        {
          id: "cookies-we-set",
          title: "Cookies we set",
          body: (
            <>
              <table>
                <thead>
                  <tr>
                    <th>Cookie</th>
                    <th>Purpose</th>
                    <th>Lifetime</th>
                    <th>Scope</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>
                      <strong>cc_token</strong>
                    </td>
                    <td>Keeps you signed in (session access token)</td>
                    <td>30 minutes</td>
                    <td>Whole application</td>
                  </tr>
                  <tr>
                    <td>
                      <strong>cc_refresh</strong>
                    </td>
                    <td>Renews your session without asking you to sign in again</td>
                    <td>7 days</td>
                    <td>Sent only to the authentication endpoints</td>
                  </tr>
                </tbody>
              </table>
              <p>
                Both cookies are <strong>httpOnly</strong> (unreadable by JavaScript, which
                protects them from script-injection attacks), marked <strong>Secure</strong> in
                production (sent only over HTTPS), and set to <strong>SameSite=Lax</strong>{" "}
                (not sent on cross-site requests, which protects against request forgery).
              </p>
            </>
          ),
        },
        {
          id: "what-we-dont-use",
          title: "What we do not use",
          body: (
            <ul>
              <li>No analytics or measurement cookies (we run no third-party analytics at all).</li>
              <li>No advertising or cross-site tracking cookies.</li>
              <li>No third-party cookies of any kind.</li>
              <li>No fingerprinting, and no tracking data in localStorage or sessionStorage.</li>
            </ul>
          ),
        },
        {
          id: "managing",
          title: "Managing cookies",
          body: (
            <>
              <p>
                You can view and delete cookies through your browser&rsquo;s settings.
                Because both of our cookies are essential, blocking them prevents signing in —
                the public pages of the site work without any cookies at all.
              </p>
              <p>
                Signing out deletes the session cookies immediately; otherwise they expire on
                the schedule above.
              </p>
            </>
          ),
        },
        {
          id: "changes",
          title: "If this ever changes",
          body: (
            <p>
              If we ever introduce non-essential cookies, we will update this policy first and
              ask for your consent before setting them, as the{" "}
              <Link href="/legal/privacy">Privacy Policy</Link> describes.
            </p>
          ),
        },
      ]}
    />
  );
}
