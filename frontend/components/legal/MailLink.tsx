/** An email address rendered as itself, so the page text and the link cannot drift apart. */
export function MailLink({ address }: { address: string }) {
  return <a href={`mailto:${address}`}>{address}</a>;
}
