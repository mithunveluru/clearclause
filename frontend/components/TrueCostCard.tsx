const ROWS: [string, string][] = [
  ["headline_rate", "Headline rate"],
  ["processing_fee", "Processing fee"],
  ["late_fee", "Late fee"],
  ["renewal_fee", "Renewal fee"],
  ["foreclosure_charge", "Foreclosure charge"],
  ["estimated_true_cost", "Estimated true cost"],
];

export default function TrueCostCard({ cost }: { cost: Record<string, number | null> }) {
  return (
    <div className="rounded-xl border bg-white p-5">
      <h3 className="mb-3 font-semibold">True-cost estimate</h3>
      <table className="w-full text-sm">
        <tbody>
          {ROWS.map(([key, label]) => (
            <tr key={key} className="border-b last:border-0">
              <td className="py-1.5 text-gray-600">{label}</td>
              <td className="py-1.5 text-right font-medium">
                {cost[key] != null ? cost[key] : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
