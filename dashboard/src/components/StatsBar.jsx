export default function StatsBar({ data, connected }) {
  return (
    <div style={{
      display: "flex", gap: 24, padding: "12px 24px",
      background: "#0f172a", borderBottom: "1px solid #1e293b",
      alignItems: "center", flexWrap: "wrap"
    }}>
      <div style={{ fontSize: 18, fontWeight: 700, color: "#38bdf8", marginRight: 16 }}>
        🛡️ SentinelAI
      </div>
      <Stat label="STATUS"
        value={connected ? "LIVE" : "OFFLINE"}
        color={connected ? "#22c55e" : "#ef4444"} />
      <Stat label="PERSONS"
        value={data?.persons_detected ?? 0}
        color="#38bdf8" />
      <Stat label="TOTAL ALERTS"
        value={data?.total_alerts ?? 0}
        color="#f59e0b" />
      <Stat label="ACTIVE THREATS"
        value={(data?.active_tracks ?? []).filter(t => t.risk_score >= 60).length}
        color="#ef4444" />
      <div style={{ marginLeft: "auto", fontSize: 12, color: "#64748b" }}>
        {data?.timestamp ?? "--"}
      </div>
    </div>
  );
}

function Stat({ label, value, color }) {
  return (
    <div style={{ textAlign: "center" }}>
      <div style={{ fontSize: 10, color: "#64748b", letterSpacing: 1 }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 700, color }}>{value}</div>
    </div>
  );
}