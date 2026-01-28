enable_chaos_pod_delete      = true
enable_chaos_network_latency = true
enable_chaos_cpu_stress      = true
enable_chaos_disk_stress     = true
enable_chaos_memory_stress   = true
kube_config_path     = "/home/marco/.kube/k3s.yaml"
wazuh_app_label = "app=wazuh"
chaos_service_account = "litmus-admin"