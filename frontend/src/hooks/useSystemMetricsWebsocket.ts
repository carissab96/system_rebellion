// frontend/src/hooks/useSystemMetricsWebSocket.ts
import { useEffect, useRef } from "react";
import { useDispatch } from "react-redux";
import { setConnectionStatus, setSystemInfo, setAllAgents, setError } from "../store/slices/metricSlice";
import { WebSocketService } from "../services/websocket";

// Pick ONE route shape to match your backend include.
// If your FastAPI mounts the router WITHOUT a prefix:
//   use "/api/ws/system-metrics"
// If your main app does app.include_router(router, prefix="/api"):
//   use "/ws/system-metrics"
const WS_ROUTE = "/ws/system-metrics"; // change to "/ws/system-metrics" if you're prefixing at include time

type AnyMsg = { type?: string; [k: string]: any };

const normalizeAgentKeys = (raw: Record<string, unknown> | undefined) => {
  if (!raw || typeof raw !== "object") return {};
  const map: Record<string, string> = {
    sir_hawkington: "sir_hawkington",
    meth_snail: "meth_snail",
    hamsters: "hamsters",
    quantum_shadow: "quantum_shadow",
    "quantum-shadow": "quantum_shadow",
    quantum: "quantum_shadow",
    the_stick: "the_stick",
    "the-stick": "the_stick",
    vic20_sage: "vic20_sage",
    "vic20-sage": "vic20_sage",
    vic20: "vic20_sage",
  };
  const out: Record<string, unknown> = {};
  Object.entries(raw).forEach(([k, v]) => {
    const nk = map[k];
    if (nk) out[nk] = v;
  });
  return out;
};

export function useSystemMetricsWebSocket(wsBaseUrl: string) {
  const dispatch = useDispatch();
  const svcRef = useRef<WebSocketService | null>(null);
  const unsubRef = useRef<null | (() => void)>(null);

  useEffect(() => {
    // Singleton service
    if (!svcRef.current) {
      svcRef.current = WebSocketService.getInstance(wsBaseUrl);
    }
    const svc = svcRef.current;

    // Connect to the correct route; token is appended by the service
    const sock = svc.ensureConnected(WS_ROUTE);

    // Status wiring
    const onOpen = () => dispatch(setConnectionStatus("connected"));
    const onClose = () => dispatch(setConnectionStatus("closed"));
    const onError = () => dispatch(setConnectionStatus("error"));

    // Subscribe to parsed messages via service fan-out
    const unsubscribe = svc.subscribe((msg: AnyMsg) => {
      try {
        switch (msg.type) {
          case "connection_established": {
            dispatch(setConnectionStatus("connected"));
            break;
          }
          case "registration_error": {
            dispatch(setError(msg.message ?? "registration_error"));
            break;
          }
          case "system_info": {
            // server sends { type: "system_info", data: {...} }
            dispatch(setSystemInfo(msg.data ?? {}));
            break;
          }
          case "metrics_update": {
            // Try msg.data.agents first, then msg.agents
            const agents = normalizeAgentKeys(msg?.data?.agents ?? msg?.agents);
            if (Object.keys(agents).length) {
              dispatch(setAllAgents(agents));
            }
            break;
          }
          case "persist_result": {
            // Non-fatal; surface error if present
            if (msg.ok === false) {
              dispatch(setError(`persist_error: ${String(msg.error ?? "unknown")}`));
            }
            break;
          }
          case "ingest_down":
          case "circuit_open": {
            // Informational; consider toast if you want drama
            break;
          }
          case "error": {
            dispatch(setError(String(msg.message ?? "unknown_error")));
            break;
          }
          default: {
            // Unknown type — do not crash, but record it
            if (msg && typeof msg === "object" && "type" in msg) {
              dispatch(setError(`unknown_type: ${String(msg.type)}`));
            } else {
              dispatch(setError("bad_json"));
            }
            break;
          }
        }
      } catch {
        dispatch(setError("hook_handler_error"));
      }
    });

    // Raw socket events for connection status
    sock.addEventListener("open", onOpen);
    sock.addEventListener("close", onClose);
    sock.addEventListener("error", onError);

    unsubRef.current = () => {
      // Clean up subscription and listeners.
      unsubscribe?.();
      sock.removeEventListener("open", onOpen);
      sock.removeEventListener("close", onClose);
      sock.removeEventListener("error", onError);
      // Do NOT close the socket here; singleton stays alive until explicitly closed elsewhere.
    };

    // If the socket is already open, reflect that immediately
    if (svc.isConnected()) {
      dispatch(setConnectionStatus("connected"));
    }

    return () => {
      unsubRef.current?.();
      unsubRef.current = null;
    };
  }, [wsBaseUrl]);
}
