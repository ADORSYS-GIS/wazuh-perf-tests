module "global_test_example" {
  source = "./"

  kube_config_path = "~/.kube/config" 

  enable_wazuh_log_generator = true
  wazuh_log_generator_config = {
    replicas = 2
    log_script_content = "import time\\nwhile True: print('Hello from wazuh-log-generator'); time.sleep(1)"
  }

  enable_stress_cpu = true
  stress_cpu_config = {
    image = "ubuntu/stress-ng"
    args  = ["--cpu", "4", "--timeout", "120s"]
  }

  enable_chaos_network_delay = true
  chaos_network_delay_config = {
    target_namespace = "default"
    pod_selector_labels = {
      "app" = "my-app"
    }
    delay_duration = "500ms"
  }
}

output "global_test_namespace" {
  value = module.global_test_example.namespace_name
}