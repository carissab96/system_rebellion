# Add this to your transform_metrics_for_frontend function:


    # Transform CPU metrics
if "cpu" in metrics:
    cpu_data = metrics["cpu"]
        
    # Component expects these exact fields
    transformed["cores"] = (
            cpu_data.get("cores") or
            cpu_data.get("cores") or
            cpu_data.get("cores", 0)
        )
    transformed["cpu"] = (
            cpu_data.get("cpu") or
            cpu_data.get("cpu") or
            cpu_data.get("cpu", 0)
        )
    transformed["cpu_core_count"] = (
            cpu_data.get("cpu_core_count") or
            cpu_data.get("core_count") or
            cpu_data.get("cpucorecount", 0)
        )
    transformed["cpu_frequency"] = (
            cpu_data.get("cpu_frequency") or
            cpu_data.get("frequency") or
            cpu_data.get("cpufrequency", 0)
        )
    transformed["cpu_model"] = (
            cpu_data.get("cpu_model") or
            cpu_data.get("model") or
            cpu_data.get("cpumodel", 0)
        )
    transformed["cpu_percent"] = (
            cpu_data.get("cpu_percent") or
            cpu_data.get("percent") or
            cpu_data.get("cpupercent", 0)
        )
    transformed["cpu_temperature"] = (
            cpu_data.get("cpu_temperature") or
            cpu_data.get("temperature") or
            cpu_data.get("cputemperature", 0)
        )
    transformed["cpu_thread_count"] = (
            cpu_data.get("cpu_thread_count") or
            cpu_data.get("thread_count") or
            cpu_data.get("cputhreadcount", 0)
        )
    transformed["cpu_usage"] = (
            cpu_data.get("cpu_usage") or
            cpu_data.get("usage") or
            cpu_data.get("cpuusage", 0)
        )
    transformed["frequency_mhz"] = (
            cpu_data.get("frequency_mhz") or
            cpu_data.get("frequency_mhz") or
            cpu_data.get("frequencymhz", 0)
        )
    transformed["length"] = (
            cpu_data.get("length") or
            cpu_data.get("length") or
            cpu_data.get("length", 0)
        )
    transformed["model_name"] = (
            cpu_data.get("model_name") or
            cpu_data.get("model_name") or
            cpu_data.get("modelname", 0)
        )
    transformed["overall_usage"] = (
            cpu_data.get("overall_usage") or
            cpu_data.get("overall_usage") or
            cpu_data.get("overallusage", 0)
        )
    transformed["process_count"] = (
            cpu_data.get("process_count") or
            cpu_data.get("process_count") or
            cpu_data.get("processcount", 0)
        )
    transformed["reduce"] = (
            cpu_data.get("reduce") or
            cpu_data.get("reduce") or
            cpu_data.get("reduce", 0)
        )
    transformed["temperature"] = (
            cpu_data.get("temperature") or
            cpu_data.get("temperature") or
            cpu_data.get("temperature", 0)
        )
    transformed["thread_count"] = (
            cpu_data.get("thread_count") or
            cpu_data.get("thread_count") or
            cpu_data.get("threadcount", 0)
        )
    transformed["top_processes"] = (
            cpu_data.get("top_processes") or
            cpu_data.get("top_processes") or
            cpu_data.get("topprocesses", 0)
        )


    # Transform Disk metrics
    if "disk" in metrics:
        disk_data = metrics["disk"]
        
    # Component expects these exact fields
    transformed["directories"] = (
            disk_data.get("directories") or
            disk_data.get("directories") or
            disk_data.get("directories", 0)
        )


    # Transform Memory metrics
    if "memory" in metrics:
        memory_data = metrics["memory"]
        
    # Component expects these exact fields
    transformed["additional"] = (
            memory_data.get("additional") or
            memory_data.get("additional") or
            memory_data.get("additional", 0)
        )
    transformed["memory_available"] = (
            memory_data.get("memory_available") or
            memory_data.get("available") or
            memory_data.get("memoryavailable", 0)
        )
    transformed["memory_buffer"] = (
            memory_data.get("memory_buffer") or
            memory_data.get("buffer") or
            memory_data.get("memorybuffer", 0)
        )
    transformed["memory_cache"] = (
            memory_data.get("memory_cache") or
            memory_data.get("cache") or
            memory_data.get("memorycache", 0)
        )
    transformed["memory_percent"] = (
            memory_data.get("memory_percent") or
            memory_data.get("percent") or
            memory_data.get("memorypercent", 0)
        )
    transformed["memory_swap_free"] = (
            memory_data.get("memory_swap_free") or
            memory_data.get("swap_free") or
            memory_data.get("memoryswapfree", 0)
        )
    transformed["memory_swap_percent"] = (
            memory_data.get("memory_swap_percent") or
            memory_data.get("swap_percent") or
            memory_data.get("memoryswappercent", 0)
        )
    transformed["memory_swap_total"] = (
            memory_data.get("memory_swap_total") or
            memory_data.get("swap_total") or
            memory_data.get("memoryswaptotal", 0)
        )
    transformed["memory_swap_used"] = (
            memory_data.get("memory_swap_used") or
            memory_data.get("swap_used") or
            memory_data.get("memoryswapused", 0)
        )
    transformed["memory_total"] = (
            memory_data.get("memory_total") or
            memory_data.get("total") or
            memory_data.get("memorytotal", 0)
        )


    # Transform Network metrics
    if "network" in metrics:
        network_data = metrics["network"]
        
    # Component expects these exact fields
    transformed["average_latency"] = (
            network_data.get("average_latency") or
            network_data.get("average_latency") or
            network_data.get("averagelatency", 0)
        )
    transformed["connection_stability"] = (
            network_data.get("connection_stability") or
            network_data.get("connection_stability") or
            network_data.get("connectionstability", 0)
        )
    transformed["dns_latency"] = (
            network_data.get("dns_latency") or
            network_data.get("dns_latency") or
            network_data.get("dnslatency", 0)
        )
    transformed["gateway_latency"] = (
            network_data.get("gateway_latency") or
            network_data.get("gateway_latency") or
            network_data.get("gatewaylatency", 0)
        )
    transformed["internet_latency"] = (
            network_data.get("internet_latency") or
            network_data.get("internet_latency") or
            network_data.get("internetlatency", 0)
        )
    transformed["jitter"] = (
            network_data.get("jitter") or
            network_data.get("jitter") or
            network_data.get("jitter", 0)
        )
    transformed["network"] = (
            network_data.get("network") or
            network_data.get("network") or
            network_data.get("network", 0)
        )
    transformed["packet_loss_percent"] = (
            network_data.get("packet_loss_percent") or
            network_data.get("packet_loss_percent") or
            network_data.get("packetlosspercent", 0)
        )
    transformed["protocol_breakdown"] = (
            network_data.get("protocol_breakdown") or
            network_data.get("protocol_breakdown") or
            network_data.get("protocolbreakdown", 0)
        )
    transformed["protocol_stats"] = (
            network_data.get("protocol_stats") or
            network_data.get("protocol_stats") or
            network_data.get("protocolstats", 0)
        )
    transformed["top_bandwidth_processes"] = (
            network_data.get("top_bandwidth_processes") or
            network_data.get("top_bandwidth_processes") or
            network_data.get("topbandwidthprocesses", 0)
        )

