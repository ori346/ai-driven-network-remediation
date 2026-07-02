import { useState } from "react";

export function IntegrationMatrix({ integrations, summary }) {
  const [open, setOpen] = useState(true);
  const items = integrations.integrations || [];

  return (
    <section className="panel">
      <div className="panel-title-row">
        <h2>Integration Status Matrix</h2>
        <button
          type="button"
          className="toggle-btn"
          onClick={() => setOpen((prev) => !prev)}
        >
          {open ? "Collapse" : "Expand"}
        </button>
      </div>
      <p className="meta">
        {items.length} integrations · Open incidents: {summary.open_incidents || 0}
      </p>
      {open ? (
        <div className="integration-grid">
          {items.map((item) => (
            <article className="integration-card" key={item.id || item.name}>
              <div className="integration-header">
                <h3>{item.name}</h3>
                <span
                  className={`pill ${item.status === "up" ? "up" : "down"}`}
                >
                  {item.status}
                </span>
              </div>
              <p className="meta">
                Group: {(item.group || "n/a").toUpperCase()}
              </p>
              <p className="meta">HTTP: {item.http_code || "n/a"}</p>
            </article>
          ))}
          {items.length === 0 && (
            <p className="meta">No integration data available.</p>
          )}
        </div>
      ) : (
        <p className="meta">
          Panel collapsed. Click Expand to view integrations.
        </p>
      )}
    </section>
  );
}
