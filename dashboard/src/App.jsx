// dashboard/src/App.jsx
import { useWebSocket } from "./hooks/useWebSocket";
import StatsBar    from "./components/StatsBar";
import VideoFeed   from "./components/VideoFeed";
import RiskMeter   from "./components/RiskMeter";
import AlertPanel  from "./components/AlertPanel";

export default function App() {
  const { data, connected } = useWebSocket("ws://localhost:8000/ws");

  return (
    <div style={{
      minHeight: "100vh", background: "#020617",
      fontFamily: "'Inter', 'Segoe UI', sans-serif", color: "#e2e8f0"
    }}>
      {/* Top stats bar */}
      <StatsBar data={data} connected={connected} />

      {/* Main layout */}
      <div style={{
        display: "flex", gap: 16, padding: 16,
        height: "calc(100vh - 60px)", boxSizing: "border-box"
      }}>

        {/* Left — Video Feed */}
        <VideoFeed />

        {/* Right — Risk + Alerts */}
        <div style={{
          flex: 1, display: "flex", flexDirection: "column",
          gap: 16, minWidth: 300, maxWidth: 380
        }}>

          {/* Risk meters */}
          <div style={{
            background: "#0f172a", borderRadius: 12,
            border: "1px solid #1e293b", overflow: "hidden", flex: 1
          }}>
            <div style={{
              padding: "8px 16px", background: "#1e293b",
              fontSize: 12, color: "#94a3b8", fontWeight: 600, letterSpacing: 1
            }}>
              RISK MONITOR
            </div>
            <RiskMeter tracks={data?.active_tracks} />
          </div>

          {/* Alert panel */}
          <div style={{
            background: "#0f172a", borderRadius: 12,
            border: "1px solid #1e293b", overflow: "hidden", flex: 1.5
          }}>
            <AlertPanel newAlerts={data?.new_alerts} />
          </div>
        </div>
      </div>
    </div>
  );
}