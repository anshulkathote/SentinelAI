export default function VideoFeed() {
  return (
    <div style={{
      background: "#0f172a", borderRadius: 12,
      overflow: "hidden", border: "1px solid #1e293b",
      flex: 2, minWidth: 0
    }}>
      <div style={{
        padding: "8px 16px", background: "#1e293b",
        fontSize: 12, color: "#94a3b8", display: "flex",
        alignItems: "center", gap: 8
      }}>
        <span style={{
          width: 8, height: 8, borderRadius: "50%",
          background: "#22c55e", display: "inline-block"
        }} />
        CAMERA 01 — LIVE FEED
      </div>
      <img
        src="http://localhost:8000/stream"
        alt="Live Feed"
        style={{ width: "100%", display: "block", maxHeight: 540, objectFit: "contain" }}
      />
    </div>
  );
}