import { useEffect, useRef, useState } from "react";

export function useWebSocket(url) {
  const [data, setData] = useState(null);
  const [connected, setConnected] = useState(false);
  const ws = useRef(null);

  useEffect(() => {
    function connect() {
      ws.current = new WebSocket(url);
      ws.current.onopen = () => {
        setConnected(true);
        console.log("[WS] Connected");
      };
      ws.current.onmessage = (e) => {
        try { setData(JSON.parse(e.data)); } catch {}
      };
      ws.current.onclose = () => {
        setConnected(false);
        console.log("[WS] Disconnected — retrying in 2s");
        setTimeout(connect, 2000);
      };
      ws.current.onerror = () => ws.current.close();
    }
    connect();
    return () => ws.current?.close();
  }, [url]);

  return { data, connected };
}