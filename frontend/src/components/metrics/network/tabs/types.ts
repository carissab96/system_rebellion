// network/tabs/types.ts - COMPLETE CONSOLIDATED FILE

export interface NetworkIOStats {
  bytes_sent: number;
  bytes_recv: number;
  packets_sent: number;
  packets_recv: number;
  sent_rate: number;
  recv_rate: number;
  errors_in: number;
  errors_out: number;
  drops_in: number;
  drops_out: number;
}

export interface ConnectionQuality {
  average_latency: number;
  packet_loss_percent: number;
  connection_stability: number;
  jitter: number;
  gateway_latency: number;
  dns_latency: number;
  internet_latency: number;
}

export interface ProtocolStats {
  tcp: {
    active: number;
    listening?: number;
    established: number;
    time_wait?: number;
    close_wait?: number;
    fin_wait1?: number;
    fin_wait2?: number;
    last_ack?: number;
    syn_sent?: number;
    syn_recv?: number;
    closing?: number;
  };
  udp: {
    active: number;
    datagrams_sent?: number;
    datagrams_received?: number;
  };
  http: {
    connections: number;
    get_requests?: number;
    post_requests?: number;
  };
  https: {
    connections: number;
    tls_handshakes?: number;
  };
  dns: {
    queries: number;
    responses?: number;
    timeouts?: number;
  };
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
  read_rate?: number;
  write_rate?: number;
  total_rate?: number;
  connection_count?: number;
}

export interface NetworkInterface {
  name: string;
  address?: string;
  mac_address?: string;
  isup: boolean;
  speed?: number;
  mtu?: number;
  bytes_sent?: number;
  bytes_recv?: number;
  stats?: {
    bytes_sent: number;
    bytes_recv: number;
    packets_sent: number;
    packets_recv: number;
    errin: number;
    errout: number;
    dropin: number;
    dropout: number;
  };
}

export interface NetworkConnection {
  fd: number | null;
  pid: number | null;
  type: string;
  local_address: string;
  remote_address: string;
  status: string;
}

// CONSOLIDATED NetworkDetails - All network types in one place
export interface NetworkDetails {
  // Core metrics
  bytes_sent: number;
  bytes_recv: number;
  packets_sent: number;
  packets_recv: number;
  rate_mbps: number;
  sent_rate_bps?: number;
  recv_rate_bps?: number;
  
  // Enhanced I/O stats
  io_stats?: NetworkIOStats;
  
  // Connection quality metrics
  connection_quality?: ConnectionQuality;
  
  // Protocol statistics
  protocol_stats?: ProtocolStats;
  
  // Usage breakdown
  protocol_breakdown?: ProtocolBreakdown;
  
  // Process information
  top_bandwidth_processes?: NetworkProcess[];
  
  // Network interfaces
  interfaces?: NetworkInterface[];
  
  // DNS metrics
  dns_metrics?: {
    query_time_ms: number;
    success_rate: number;
    cache_hit_ratio: number;
  };
  
  // Internet connectivity
  internet_metrics?: {
    connected: boolean;
    download_speed: number;
    upload_speed: number;
    isp_latency: number;
  };
}