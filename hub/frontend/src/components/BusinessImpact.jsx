import { useMemo } from "react";

function formatMoney(value) {
  const amount = Number(value || 0);
  return `$${amount.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
}

export function BusinessImpact({ impact }) {
  const data = useMemo(() => {
    const d = impact || {};
    return {
      incidentsProcessed: Number(d.incidents_processed || 0),
      remediationSuccessPct: Number(d.remediation_success_pct || 0),
      ticketsAvoided: Number(d.tickets_avoided || 0),
      hoursReturned: Number(d.hours_returned_to_ops || 0),
      estimatedCostSaved: Number(d.estimated_cost_saved_usd || 0),
      modelConfidenceAvg: d.model_confidence_avg ?? null,
    };
  }, [impact]);

  return (
    <section className="panel">
      <h2>Business Impact</h2>
      <p className="meta">
        Value delivered from autonomous remediation over the current telemetry
        window.
      </p>
      <div className="impact-grid">
        <article className="impact-card">
          <h3>Incidents Processed</h3>
          <p className="impact-metric">{data.incidentsProcessed}</p>
        </article>
        <article className="impact-card">
          <h3>Remediation Success</h3>
          <p className="impact-metric">
            {data.remediationSuccessPct.toFixed(1)}%
          </p>
        </article>
        <article className="impact-card">
          <h3>Tickets Avoided</h3>
          <p className="impact-metric">{data.ticketsAvoided}</p>
        </article>
        <article className="impact-card">
          <h3>Hours Returned to Ops</h3>
          <p className="impact-metric">{data.hoursReturned.toFixed(2)}h</p>
        </article>
        <article className="impact-card">
          <h3>Estimated Cost Saved</h3>
          <p className="impact-metric">
            {formatMoney(data.estimatedCostSaved)}
          </p>
        </article>
        <article className="impact-card">
          <h3>Model Confidence</h3>
          <p className="impact-metric">
            {data.modelConfidenceAvg === null
              ? "n/a"
              : `${(Number(data.modelConfidenceAvg) * 100).toFixed(1)}%`}
          </p>
        </article>
      </div>
    </section>
  );
}
