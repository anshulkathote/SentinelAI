function getRiskColor(score) {
  if (score >= 60) return "#ef4444";
  if (score >= 30) return "#f59e0b";
  return "#22c55e";
}

function getRiskLabel(score) {
  if (score >= 60) return "HIGH THREAT";
  if (score >= 30) return "SUSPICIOUS";
  return "SAFE";
}

export default function RiskMeter({ tracks }) {
  if (!tracks || tracks.length === 0) {
    return (
      <div style={{ padding: 16, color: "#475569", fontSize: 13, textAlign: "center" }}>
        No active persons detected
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12, padding: 12 }}>
      {tracks.map((track) => {
        const color = getRiskColor(track.risk_score);
        const label = getRiskLabel(track.risk_score);
        const pct   = Math.min(track.risk_score, 100);

        return (
          <div key={track.track_id} style={{
            background: "#1e293b", borderRadius: 8, padding: 12,
            border: `1px solid ${track.risk_score >= 60 ? "#ef4444" : "#334155"}`
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
              <span style={{ color: "#e2e8f0", fontWeight: 600, fontSize: 13 }}>
                Person #{track.track_id}
              </span>
              <span style={{ color, fontSize: 11, fontWeight: 700 }}>{label}</span>
            </div>
            <div style={{ height: 8, background: "#0f172a", borderRadius: 4, overflow: "hidden" }}>
              <div style={{
                width: `${pct}%`, height: "100%",
                background: color, borderRadius: 4,
                transition: "width 0.3s ease"
              }} />
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", marginTop: 6 }}>
              <div style={{ fontSize: 11, color: "#94a3b8" }}>
                {track.behaviors?.map(b => b.split(":")[0]).join(" · ") || "monitoring"}
              </div>
              <div style={{ fontSize: 20, fontWeight: 700, color }}>{track.risk_score}</div>
            </div>
            <div style={{ fontSize: 10, color: "#475569", marginTop: 2 }}>
              In frame: {track.duration}s
            </div>
          </div>
        );
      })}
    </div>
  );
}