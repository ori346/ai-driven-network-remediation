export function HeaderMetrics({ integrations, summary, lastUpdated }) {
  const updated = lastUpdated ? lastUpdated.toLocaleString() : "n/a";

  return (
    <section className="hero">
      <p className="badge">AI-DRIVEN NETWORK REMEDIATION · NOC DASHBOARD</p>
      <h1>Operations Command Center</h1>
      <p className="sub">
        Real-time operational surface for autonomous network failure detection
        and remediation across distributed edge infrastructure.
      </p>
      <div className="hero-metrics">
        <div>
          <span>Total Integrations</span>
          <strong>{integrations.total || 0}</strong>
        </div>
        <div>
          <span>Systems Up</span>
          <strong>{integrations.up || 0}</strong>
        </div>
        <div>
          <span>Systems Down</span>
          <strong>{integrations.down || 0}</strong>
        </div>
        <div>
          <span>Open Incidents</span>
          <strong>{summary.open_incidents || 0}</strong>
        </div>
        <div>
          <span>Last Updated</span>
          <strong>{updated}</strong>
        </div>
      </div>
    </section>
  );
}
