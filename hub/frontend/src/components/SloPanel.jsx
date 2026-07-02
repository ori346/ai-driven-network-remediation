import { useMemo } from "react";

function formatDuration(seconds) {
  if (seconds === null || seconds === undefined || Number.isNaN(Number(seconds))) {
    return "n/a";
  }
  const value = Number(seconds);
  if (value < 60) return `${value.toFixed(1)}s`;
  if (value < 3600) return `${(value / 60).toFixed(1)}m`;
  return `${(value / 3600).toFixed(2)}h`;
}

export function SloPanel({ slo, integrations }) {
  const metrics = useMemo(() => {
    const s = slo || {};
    const items = Array.isArray(integrations?.integrations) ? integrations.integrations : [];
    const total = items.length;
    const up = items.filter((i) => i.status === "up").length;
    const availability = Number(
      s.platform_availability_pct ?? (total > 0 ? (up / total) * 100 : 0)
    );

    return {
      sampleSize: Number(s.sample_size || 0),
      windowHours: Number(s.window_hours || 24),
      availability,
      availabilityPass: availability >= 99.0,
      mttdSeconds: s.mttd_seconds ?? null,
      mttrSeconds: s.mttr_seconds ?? null,
      p95RecoverySeconds: s.p95_recovery_seconds ?? null,
      mttdEstimated: Boolean(s.mttd_estimated),
      autoRemediationPct: Number(s.auto_remediation_pct ?? 0),
      escalationPct: Number(s.escalation_pct ?? 0),
      incidentsPerHour: Number(s.incidents_per_hour ?? 0),
    };
  }, [slo, integrations]);

  return (
    <section className="panel">
      <h2>Critical SLO (Live Data)</h2>
      <p className="meta">
        Live SLO posture over the last {metrics.windowHours}h (
        {metrics.sampleSize} events).
      </p>
      <div className="slo-grid">
        <article className="slo-card">
          <h3>Platform Availability</h3>
          <p className="slo-metric">
            {metrics.availability.toFixed(1)}%
            <span className={metrics.availabilityPass ? "pill up" : "pill down"}>
              target 99.0%
            </span>
          </p>
        </article>

        <article className="slo-card">
          <h3>MTTD</h3>
          <p className="slo-metric">
            {formatDuration(metrics.mttdSeconds)}
            <span
              className={metrics.mttdSeconds !== null ? "pill up" : "pill down"}
            >
              {metrics.mttdEstimated ? "estimated" : "measured"}
            </span>
          </p>
        </article>

        <article className="slo-card">
          <h3>MTTR</h3>
          <p className="slo-metric">
            {formatDuration(metrics.mttrSeconds)}
            <span
              className={metrics.mttrSeconds !== null ? "pill up" : "pill down"}
            >
              live
            </span>
          </p>
        </article>

        <article className="slo-card">
          <h3>P95 Recovery</h3>
          <p className="slo-metric">
            {formatDuration(metrics.p95RecoverySeconds)}
            <span
              className={
                metrics.p95RecoverySeconds !== null ? "pill up" : "pill down"
              }
            >
              tail latency
            </span>
          </p>
        </article>

        <article className="slo-card">
          <h3>Auto-Remediation %</h3>
          <p className="slo-metric">
            {metrics.autoRemediationPct.toFixed(1)}%
            <span
              className={
                metrics.autoRemediationPct >= 60 ? "pill up" : "pill down"
              }
            >
              no ticket
            </span>
          </p>
        </article>

        <article className="slo-card">
          <h3>Escalation %</h3>
          <p className="slo-metric">
            {metrics.escalationPct.toFixed(1)}%
            <span
              className={metrics.escalationPct <= 35 ? "pill up" : "pill down"}
            >
              to humans
            </span>
          </p>
        </article>

        <article className="slo-card">
          <h3>Incident Throughput</h3>
          <p className="slo-metric">
            {metrics.incidentsPerHour.toFixed(2)}/h
            <span
              className={metrics.incidentsPerHour <= 3 ? "pill up" : "pill down"}
            >
              rolling rate
            </span>
          </p>
        </article>
      </div>
    </section>
  );
}
