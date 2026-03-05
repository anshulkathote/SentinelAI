import { useState, useEffect } from "react";

export default function AlertPanel({ newAlerts }) {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    if (newAlerts && newAlerts.length > 0) {
      setAlerts(prev => [...newAlerts, ...prev].slice(0, 50));
    }
  }, [newAlerts]);

  const dismiss = (id) => {
    setAlerts(prev => prev.filter(a => a.id !== id));
    fetch(`http://localhost:8000/alerts/${id}`, { method: "DELETE" }).catch(() => {});
  };

  const clearAll = () => {
    setAlerts([]);
    fetch("http://localhost:8000/alerts/", { method: "DELETE" }).catch(() => {});
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div style={{
        display: "flex", justifyContent: "space-between", alignItems: "center",
        padding: "10px 14px", background: "#1e293b", borderBottom: "1px solid #334155"
      }}>
        <span style={{ color: "#f87171", fontWeight: 700, fontSize: 13 }}>
          🚨 ALERTS ({alerts.length})
        </span>
        {alerts.length > 0 && (
          <button onClick={clearAll} style={{
            background: "none", border: "1px solid #475569", color: "#94a3b8",
            padding: "2px 10px", borderRadius: 4, cursor: "pointer", fontSize: 11
          }}>
            Clear All
          </button>
        )}
      </div>

      <div style={{ overflowY: "auto", flex: 1 }}>
        {alerts.length === 0 ? (
          <div style={{ padding: 24, textAlign: "center", color: "#475569", fontSize: 13 }}>
            No alerts — system monitoring...
          </div>
        ) : (
          alerts.map((alert) => (
            <AlertCard key={alert.id} alert={alert} onDismiss={dismiss} />
          ))
        )}
      </div>
    </div>
  );
}

function AlertCard({ alert, onDismiss }) {
  return (
    <div style={{
      margin: 10, padding: 12, background: "#1e293b", borderRadius: 8,
      border: "1px solid #ef4444", borderLeft: "4px solid #ef4444"
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
        <span style={{ color: "#ef4444", fontWeight: 700, fontSize: 13 }}>
          ⚠ Person #{alert.track_id}
        </span>
        <span style={{ color: "#ef4444", fontWeight: 800, fontSize: 18 }}>
          {alert.risk_score}
        </span>
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginBottom: 6 }}>
        {alert.behaviors?.map((b, i) => (
          <span key={i} style={{
            background: "#450a0a", color: "#fca5a5",
            padding: "2px 8px", borderRadius: 4, fontSize: 10, fontWeight: 600
          }}>
            {b.split(":")[0].toUpperCase()}
          </span>
        ))}
      </div>
      {alert.snapshot && (
        <img
          src={`http://localhost:8000/${alert.snapshot}`}
          alt="snapshot"
          style={{ width: "100%", borderRadius: 6, marginBottom: 6, maxHeight: 120, objectFit: "cover" }}
          onError={(e) => { e.target.style.display = "none"; }}
        />
      )}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: 10, color: "#475569" }}>
          {alert.timestamp} · {alert.duration}s in frame
        </span>
        <button onClick={() => onDismiss(alert.id)} style={{
          background: "none", border: "none", color: "#475569",
          cursor: "pointer", fontSize: 11
        }}>
          Dismiss
        </button>
      </div>
    </div>
  );
}