// src/hooks/useWebSocket.ts
export const useWebSocket = (url: string) => {
    const [isConnected, setIsConnected] = useState(false);
    const [messages, setMessages] = useState<AgentMessageType[]>([]);
    const [error, setError] = useState<string | null>(null);
    const ws = useRef<WebSocket | null>(null);
  
    useEffect(() => {
      const connectWebSocket = () => {
        try {
          ws.current = new WebSocket(url);
          
          ws.current.onopen = () => {
            setIsConnected(true);
            setError(null);
            console.log(`✅ Connected to ${url}`);
          };
  
          ws.current.onmessage = (event) => {
            try {
              const message: AgentMessageType = JSON.parse(event.data);
              setMessages(prev => [...prev, message]);
            } catch (err) {
              console.error('Failed to parse WebSocket message:', err);
            }
          };
  
          ws.current.onclose = () => {
            setIsConnected(false);
            console.log(`❌ Disconnected from ${url}`);
            // Reconnect after 3 seconds
            setTimeout(connectWebSocket, 3000);
          };
  
          ws.current.onerror = (error) => {
            setError('WebSocket connection error');
            console.error('WebSocket error:', error);
          };
        } catch (err) {
          setError('Failed to connect to WebSocket');
          console.error('WebSocket connection failed:', err);
        }
      };
  
      connectWebSocket();
  
      return () => {
        if (ws.current) {
          ws.current.close();
        }
      };
    }, [url]);
  
    const sendMessage = (message: any) => {
      if (ws.current && isConnected) {
        ws.current.send(JSON.stringify(message));
      }
    };
  
    return {
      isConnected,
      messages,
      error,
      sendMessage
    };
  };