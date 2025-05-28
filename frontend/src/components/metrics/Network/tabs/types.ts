// frontend/src/components/metrics/NetworkMetrics/types.ts

export interface NetworkIOStats {
    bytes_sent: number;
    bytes_recv: number;
    sent_rate: number;
    recv_rate: number;
  }
  
  export interface ConnectionQuality {
    connection_stability: number;
    average_latency: number;
    packet_loss_percent: number;
    jitter: number;
    gateway_latency: number;
    dns_latency: number;
    internet_latency: number;
  }
  
  export interface ProtocolStats {
    tcp: { active: number; established: number };
    udp: { active: number };
    http: { connections: number };
    https: { connections: number };
    dns: { queries: number };
  }
  
  export interface ProtocolBreakdown {
    web: number;
    email: number;
    streaming: number;
    gaming: number;
    file_transfer: number;
    other: number;
  }
  
  export interface NetworkProcess {
    name: string;
    pid: number;
    write_rate: number;
    read_rate: number;
    connection_count: number;
  }
  
  export interface NetworkInterface {
    name: string;
    isup: boolean;
    address?: string;
    mac_address?: string;
    speed?: number;
    mtu?: number;
    bytes_sent: number;
    bytes_recv: number;
  }