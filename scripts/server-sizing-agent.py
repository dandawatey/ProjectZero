#!/usr/bin/env python3
"""
server-sizing-agent.py — Agentic server sizing for ProjectZero deployments.

Uses claude-opus-4-6 with adaptive thinking + streaming + prompt caching.
Gathers requirements, calculates VM allocation across physical servers,
generates sizing report + Proxmox configs + Ansible inventory.

Usage:
  python scripts/server-sizing-agent.py
  python scripts/server-sizing-agent.py --apps 10 --users 10000 --envs dev,test,prod \
      --servers 2 --storage 50 --stack nextjs+fastapi+postgres+redis+temporal
"""

import argparse
import json
import math
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import anthropic

# ── Constants ────────────────────────────────────────────────────────────────

MODEL    = "claude-opus-4-6"
SCRIPTS  = Path(__file__).parent
FACTORY  = SCRIPTS.parent
OUTPUT   = FACTORY / "output" / "server-sizing"

# ── Service resource profiles (per instance) ─────────────────────────────────

SERVICE_PROFILES: dict[str, dict] = {
    "nextjs": {
        "cpu": 1.0, "ram_gb": 1.0,
        "description": "Next.js frontend server",
        "replicas": {"dev": 1, "test": 2, "prod": 3},
    },
    "fastapi": {
        "cpu": 1.0, "ram_gb": 1.0,
        "description": "FastAPI backend server",
        "replicas": {"dev": 1, "test": 2, "prod": 3},
    },
    "postgres": {
        "cpu": 4.0, "ram_gb": 16.0,
        "description": "PostgreSQL database",
        "replicas": {"dev": 1, "test": 2, "prod": 3},  # primary + replicas
    },
    "redis": {
        "cpu": 1.0, "ram_gb": 4.0,
        "description": "Redis cache + session store",
        "replicas": {"dev": 1, "test": 1, "prod": 3},
    },
    "temporal": {
        "cpu": 2.0, "ram_gb": 4.0,
        "description": "Temporal workflow engine",
        "replicas": {"dev": 1, "test": 1, "prod": 2},
    },
    "pgbouncer": {
        "cpu": 0.5, "ram_gb": 0.5,
        "description": "PostgreSQL connection pooler",
        "replicas": {"dev": 0, "test": 1, "prod": 2},
    },
    "prometheus": {
        "cpu": 2.0, "ram_gb": 8.0,
        "description": "Metrics collection",
        "replicas": {"dev": 0, "test": 1, "prod": 1},
    },
    "grafana": {
        "cpu": 1.0, "ram_gb": 2.0,
        "description": "Metrics dashboards",
        "replicas": {"dev": 0, "test": 1, "prod": 1},
    },
    "loki": {
        "cpu": 2.0, "ram_gb": 4.0,
        "description": "Log aggregation",
        "replicas": {"dev": 0, "test": 0, "prod": 1},
    },
    "nginx": {
        "cpu": 1.0, "ram_gb": 1.0,
        "description": "Ingress / load balancer",
        "replicas": {"dev": 1, "test": 1, "prod": 2},
    },
    "k8s_overhead": {
        "cpu": 2.0, "ram_gb": 4.0,
        "description": "K8s / K3s system overhead",
        "replicas": {"dev": 1, "test": 1, "prod": 1},
    },
}

# ── Tool definitions ──────────────────────────────────────────────────────────

TOOLS: list[dict] = [
    {
        "name": "gather_requirements",
        "description": (
            "Collect deployment requirements from user if not already provided via CLI. "
            "Returns a requirements dict with apps, users_per_app, environments, "
            "physical_servers, storage_gb_per_app, stack_services."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "apps":             {"type": "integer", "description": "Number of applications to deploy"},
                "users_per_app":    {"type": "integer", "description": "Peak concurrent users per app"},
                "environments":     {"type": "array",  "items": {"type": "string"},
                                     "description": "List of environments e.g. ['dev','test','prod']"},
                "physical_servers": {"type": "integer", "description": "Number of physical servers available"},
                "storage_gb_per_app": {"type": "integer", "description": "Storage in GB required per app"},
                "stack_services":   {"type": "array",  "items": {"type": "string"},
                                     "description": "Services in stack e.g. ['nextjs','fastapi','postgres','redis','temporal']"},
                "hypervisor":       {"type": "string",
                                     "enum": ["proxmox", "vmware", "kvm", "none"],
                                     "description": "Hypervisor / virtualization platform"},
            },
            "required": ["apps","users_per_app","environments","physical_servers",
                         "storage_gb_per_app","stack_services"],
        },
    },
    {
        "name": "calculate_workload",
        "description": (
            "Calculate total CPU, RAM, and storage required per environment "
            "based on number of apps and service profiles. Returns workload dict."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "apps":           {"type": "integer"},
                "environments":   {"type": "array", "items": {"type": "string"}},
                "stack_services": {"type": "array", "items": {"type": "string"}},
                "storage_gb_per_app": {"type": "integer"},
                "users_per_app":  {"type": "integer"},
            },
            "required": ["apps","environments","stack_services","storage_gb_per_app","users_per_app"],
        },
    },
    {
        "name": "recommend_physical_specs",
        "description": (
            "Given total workload across all environments and number of physical servers, "
            "recommend CPU, RAM, and storage specs for each physical server. "
            "Applies 20% overhead buffer and balances load."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "workload":         {"type": "object", "description": "Output from calculate_workload"},
                "physical_servers": {"type": "integer"},
                "hypervisor":       {"type": "string"},
            },
            "required": ["workload","physical_servers"],
        },
    },
    {
        "name": "allocate_vms",
        "description": (
            "Distribute VMs across physical servers per environment. "
            "Returns VM allocation plan: which VMs go on which physical server, "
            "with CPU/RAM/disk specs for each VM."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "workload":        {"type": "object"},
                "physical_specs":  {"type": "object"},
                "apps":            {"type": "integer"},
                "environments":    {"type": "array", "items": {"type": "string"}},
                "stack_services":  {"type": "array", "items": {"type": "string"}},
                "storage_gb_per_app": {"type": "integer"},
                "hypervisor":      {"type": "string"},
            },
            "required": ["workload","physical_specs","apps","environments","stack_services"],
        },
    },
    {
        "name": "validate_capacity",
        "description": (
            "Validate that VM allocation fits within physical server limits. "
            "Checks CPU overcommit ratio (max 4:1), RAM overcommit (max 1.2:1), "
            "and storage capacity. Returns validation result with warnings."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "vm_allocation":  {"type": "object"},
                "physical_specs": {"type": "object"},
            },
            "required": ["vm_allocation","physical_specs"],
        },
    },
    {
        "name": "generate_network_design",
        "description": (
            "Design network layout: VLANs per environment, IP ranges, "
            "inter-server links, firewall zones. Returns network design dict."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "environments":     {"type": "array", "items": {"type": "string"}},
                "physical_servers": {"type": "integer"},
                "vm_allocation":    {"type": "object"},
            },
            "required": ["environments","physical_servers"],
        },
    },
    {
        "name": "generate_proxmox_config",
        "description": (
            "Generate Proxmox VM configuration snippets (qm create commands) "
            "for all VMs in the allocation plan."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "vm_allocation":   {"type": "object"},
                "network_design":  {"type": "object"},
            },
            "required": ["vm_allocation"],
        },
    },
    {
        "name": "generate_ansible_inventory",
        "description": (
            "Generate Ansible inventory file (INI format) grouping hosts "
            "by environment and role."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "vm_allocation":  {"type": "object"},
                "network_design": {"type": "object"},
            },
            "required": ["vm_allocation"],
        },
    },
    {
        "name": "generate_sizing_report",
        "description": (
            "Produce complete markdown sizing report: executive summary, "
            "per-environment breakdown, VM table, physical server specs, "
            "network layout, cost estimate, recommendations."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "requirements":    {"type": "object"},
                "workload":        {"type": "object"},
                "physical_specs":  {"type": "object"},
                "vm_allocation":   {"type": "object"},
                "validation":      {"type": "object"},
                "network_design":  {"type": "object"},
            },
            "required": ["requirements","workload","physical_specs","vm_allocation"],
        },
    },
    {
        "name": "save_output",
        "description": "Save generated files (report, configs, inventory) to output directory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "sizing_report":       {"type": "string", "description": "Markdown report content"},
                "proxmox_config":      {"type": "string", "description": "Proxmox qm commands"},
                "ansible_inventory":   {"type": "string", "description": "Ansible INI inventory"},
                "vm_allocation_json":  {"type": "string", "description": "JSON allocation plan"},
            },
            "required": ["sizing_report"],
        },
    },
]

# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are an expert infrastructure architect specializing in on-premises server sizing
for multi-application, multi-environment deployments using virtualization (Proxmox/KVM/VMware).

Your job: given deployment requirements, produce a precise, buildable server sizing plan.

## Sizing Principles

1. **CPU**: Overcommit up to 4:1 (vCPU:pCPU) for app workloads. Never overcommit DB.
2. **RAM**: 1.1:1 max overcommit. Buffer 20% for OS + hypervisor overhead.
3. **Storage**: NVMe for DB. SSD for app. Add 30% buffer on all storage estimates.
4. **HA**: Dev = no HA. Test = DB replica only. Prod = full HA (3 masters, N replicas).
5. **Network**: Separate VLANs per environment. 10GbE inter-server minimum.
6. **Environments share physical hardware** via VMs — never co-locate prod DB with dev.

## Tool Flow

Execute in this exact order:
1. gather_requirements — confirm or collect all parameters
2. calculate_workload  — compute total resources per env
3. recommend_physical_specs — spec each physical server
4. allocate_vms        — assign VMs to servers
5. validate_capacity   — check overcommit ratios
6. generate_network_design — VLANs + IP plan
7. generate_proxmox_config — VM create commands
8. generate_ansible_inventory — hosts file
9. generate_sizing_report — full markdown report
10. save_output         — write files to disk

## Output Standard

Every VM must have: name, vcpu, ram_gb, disk_gb, vlan, ip, physical_server, environment, role.
Every physical server must have: total_cpu, total_ram_gb, total_storage_tb, role.
Report must include: executive summary, per-env VM table, overcommit analysis, network layout,
hardware BOM (bill of materials), and next steps.
"""

# ── Tool handlers ─────────────────────────────────────────────────────────────

def _tool_gather_requirements(args: dict, cli_args: argparse.Namespace) -> dict:
    """Merge CLI args with tool call args. Prompt for missing values."""
    req = {
        "apps":              args.get("apps")             or cli_args.apps,
        "users_per_app":     args.get("users_per_app")    or cli_args.users,
        "environments":      args.get("environments")     or cli_args.envs,
        "physical_servers":  args.get("physical_servers") or cli_args.servers,
        "storage_gb_per_app":args.get("storage_gb_per_app") or cli_args.storage,
        "stack_services":    args.get("stack_services")   or cli_args.stack,
        "hypervisor":        args.get("hypervisor")       or cli_args.hypervisor,
    }
    # Interactive prompts for anything still missing
    if not req["apps"]:
        req["apps"] = int(input("  Number of applications: ").strip())
    if not req["users_per_app"]:
        req["users_per_app"] = int(input("  Peak concurrent users per app: ").strip())
    if not req["environments"]:
        envs = input("  Environments (comma-separated) [dev,test,prod]: ").strip()
        req["environments"] = [e.strip() for e in (envs or "dev,test,prod").split(",")]
    if not req["physical_servers"]:
        req["physical_servers"] = int(input("  Number of physical servers: ").strip())
    if not req["storage_gb_per_app"]:
        req["storage_gb_per_app"] = int(input("  Storage GB per app: ").strip())
    if not req["stack_services"]:
        svc = input("  Stack services [nextjs,fastapi,postgres,redis,temporal]: ").strip()
        req["stack_services"] = [s.strip() for s in
                                  (svc or "nextjs,fastapi,postgres,redis,temporal").split(",")]
    if not req["hypervisor"]:
        req["hypervisor"] = input("  Hypervisor [proxmox/vmware/kvm/none] (proxmox): ").strip() or "proxmox"

    print(f"\n  Requirements confirmed:")
    for k, v in req.items():
        print(f"    {k}: {v}")
    return req


def _tool_calculate_workload(args: dict) -> dict:
    """Calculate total CPU/RAM/storage per environment."""
    apps       = args["apps"]
    envs       = args["environments"]
    services   = args["stack_services"]
    storage_gb = args["storage_gb_per_app"]
    users      = args["users_per_app"]

    # Scale replicas by user count
    user_scale = max(1.0, users / 1000)

    workload: dict[str, Any] = {}
    for env in envs:
        total_cpu  = 0.0
        total_ram  = 0.0
        total_disk = 0.0
        vm_list    = []

        for svc in services:
            if svc not in SERVICE_PROFILES:
                continue
            profile  = SERVICE_PROFILES[svc]
            replicas = profile["replicas"].get(env, 1)

            # Scale prod replicas with users
            if env == "prod":
                replicas = max(replicas, math.ceil(user_scale * replicas / 2))

            if replicas == 0:
                continue

            # Per-app instances for stateless services
            is_stateless = svc in ("nextjs", "fastapi", "nginx")
            count = (apps * replicas) if is_stateless else replicas

            cpu  = profile["cpu"]  * count
            ram  = profile["ram_gb"] * count
            disk = storage_gb * apps if svc == "postgres" else (
                   storage_gb * 0.1 * apps if svc in ("redis",) else 10 * count
            )

            total_cpu  += cpu
            total_ram  += ram
            total_disk += disk

            vm_list.append({
                "service":  svc,
                "count":    count,
                "cpu_each": profile["cpu"],
                "ram_each": profile["ram_gb"],
                "total_cpu": cpu,
                "total_ram": ram,
                "total_disk_gb": disk,
                "replicas_per_app": replicas,
            })

        # Add K8s overhead
        k8s = SERVICE_PROFILES["k8s_overhead"]
        total_cpu  += k8s["cpu"]
        total_ram  += k8s["ram_gb"]

        # Add monitoring for test+prod
        if env in ("test", "prod"):
            for mon_svc in ("prometheus", "grafana", "loki"):
                if mon_svc in SERVICE_PROFILES:
                    p = SERVICE_PROFILES[mon_svc]
                    r = p["replicas"].get(env, 0)
                    if r > 0:
                        total_cpu  += p["cpu"]  * r
                        total_ram  += p["ram_gb"] * r
                        total_disk += 50 * r  # monitoring storage

        # 20% overhead buffer
        total_cpu  = math.ceil(total_cpu  * 1.2)
        total_ram  = math.ceil(total_ram  * 1.2)
        total_disk = math.ceil(total_disk * 1.3)

        workload[env] = {
            "total_vcpu":    total_cpu,
            "total_ram_gb":  total_ram,
            "total_disk_gb": total_disk,
            "services":      vm_list,
        }

    return workload


def _tool_recommend_physical_specs(args: dict) -> dict:
    """Recommend physical server specs to fit all workloads."""
    workload   = args["workload"]
    n_servers  = args["physical_servers"]
    hypervisor = args.get("hypervisor", "proxmox")

    # Hypervisor overhead per server
    hypervisor_cpu_overhead  = 4   # vCPUs for hypervisor
    hypervisor_ram_overhead  = 8   # GB for hypervisor

    # Sum totals across all environments
    grand_cpu  = sum(w["total_vcpu"]    for w in workload.values())
    grand_ram  = sum(w["total_ram_gb"]  for w in workload.values())
    grand_disk = sum(w["total_disk_gb"] for w in workload.values())

    # Physical CPU: max 4:1 overcommit for app tier, 1:1 for DB
    # Approximate: 30% of workload is DB (no overcommit), 70% is app (4:1)
    db_cpu  = grand_cpu  * 0.3
    app_cpu = grand_cpu  * 0.7
    physical_cpu_needed = math.ceil(db_cpu + (app_cpu / 4))

    # Physical RAM: 1.1:1 max overcommit
    physical_ram_needed = math.ceil(grand_ram / 1.1)

    # Distribute across N servers
    per_server_cpu   = math.ceil((physical_cpu_needed + hypervisor_cpu_overhead) / n_servers)
    per_server_ram   = math.ceil((physical_ram_needed + hypervisor_ram_overhead * n_servers) / n_servers)
    per_server_disk  = math.ceil(grand_disk / n_servers * 1.2)  # 20% buffer

    # Round up to standard server configs
    cpu_options  = [8, 16, 24, 32, 48, 64, 96, 128]
    ram_options  = [32, 64, 128, 256, 384, 512, 768, 1024]
    disk_options = [500, 1000, 2000, 4000, 8000, 16000]

    rec_cpu  = next((c for c in cpu_options  if c >= per_server_cpu),  cpu_options[-1])
    rec_ram  = next((r for r in ram_options  if r >= per_server_ram),  ram_options[-1])
    rec_disk = next((d for d in disk_options if d >= per_server_disk), disk_options[-1])

    specs = {}
    for i in range(1, n_servers + 1):
        # Server 1 bias: app + control plane (more CPU)
        # Server 2 bias: data tier (more RAM + storage)
        if n_servers >= 2:
            if i == 1:
                specs[f"server_{i}"] = {
                    "role":      "app-control",
                    "purpose":   "K8s control plane + app workloads (all envs)",
                    "cpu_cores": rec_cpu,
                    "ram_gb":    rec_ram,
                    "storage_tb": round(rec_disk / 1000, 1),
                    "storage_type": "NVMe SSD (RAID-10 recommended)",
                    "network":   "2× 10GbE (bonded)",
                    "example":   "Dell PowerEdge R650 / HP DL380 Gen10",
                }
            else:
                # Data servers need more RAM + storage
                data_ram  = max(rec_ram,  math.ceil(grand_ram * 0.6 / (n_servers - 1)))
                data_disk = max(rec_disk, math.ceil(grand_disk * 0.7 / (n_servers - 1)))
                data_ram_r  = next((r for r in ram_options  if r >= data_ram),  ram_options[-1])
                data_disk_r = next((d for d in disk_options if d >= data_disk), disk_options[-1])
                specs[f"server_{i}"] = {
                    "role":      "data-monitoring",
                    "purpose":   "Postgres + Redis + Temporal + Monitoring (all envs)",
                    "cpu_cores": rec_cpu,
                    "ram_gb":    data_ram_r,
                    "storage_tb": round(data_disk_r / 1000, 1),
                    "storage_type": "NVMe SSD (RAID-10 recommended)",
                    "network":   "2× 10GbE (bonded)",
                    "example":   "Dell PowerEdge R750xs / HP DL380 Gen10",
                }
        else:
            specs[f"server_{i}"] = {
                "role":      "all-in-one",
                "purpose":   "All services across all environments",
                "cpu_cores": rec_cpu,
                "ram_gb":    rec_ram,
                "storage_tb": round(rec_disk / 1000, 1),
                "storage_type": "NVMe SSD (RAID-10 recommended)",
                "network":   "2× 10GbE (bonded)",
                "example":   "Dell PowerEdge R750 / HP DL380 Gen10",
            }

    specs["_summary"] = {
        "total_workload_vcpu":   grand_cpu,
        "total_workload_ram_gb": grand_ram,
        "total_workload_disk_gb":grand_disk,
        "physical_cpu_needed":   physical_cpu_needed,
        "physical_ram_needed":   physical_ram_needed,
    }
    return specs


def _tool_allocate_vms(args: dict) -> dict:
    """Assign VMs to physical servers."""
    workload    = args["workload"]
    phys        = args["physical_specs"]
    apps        = args["apps"]
    envs        = args["environments"]
    services    = args["stack_services"]
    storage_gb  = args["storage_gb_per_app"]
    hypervisor  = args.get("hypervisor", "proxmox")

    n_servers   = len([k for k in phys if k.startswith("server_")])
    vm_id_start = 100
    allocation: dict[str, list] = {f"server_{i}": [] for i in range(1, n_servers + 1)}

    # VLAN map per environment
    vlan_map = {"dev": 10, "test": 20, "prod": 30}
    ip_map   = {"dev": "10.10", "test": "10.20", "prod": "10.30"}

    vm_id = vm_id_start

    # Assign rules:
    # Server 1: app-tier VMs (nextjs, fastapi, nginx, k8s)
    # Server 2: data-tier VMs (postgres, redis, temporal, monitoring)
    # If only 1 server: everything on server_1

    app_services  = {"nextjs", "fastapi", "nginx", "k8s_overhead", "pgbouncer"}
    data_services = {"postgres", "redis", "temporal", "prometheus", "grafana", "loki"}

    for env_idx, env in enumerate(envs):
        env_vlan = vlan_map.get(env, 10 + env_idx * 10)
        env_ip   = ip_map.get(env, f"10.{10 + env_idx * 10}")
        ip_host  = 10

        for svc in services + ["nginx", "k8s_overhead"]:
            if svc not in SERVICE_PROFILES:
                continue
            profile  = SERVICE_PROFILES[svc]
            replicas = profile["replicas"].get(env, 1)
            if replicas == 0:
                continue

            is_stateless = svc in ("nextjs", "fastapi", "nginx")
            count = apps if is_stateless else 1

            for idx in range(replicas if not is_stateless else 1):
                for app_n in (range(1, apps + 1) if is_stateless else [0]):
                    # CPU/RAM per VM
                    vcpu     = int(profile["cpu"] * (3 if env == "prod" else (2 if env == "test" else 1)))
                    vcpu     = max(1, vcpu)
                    ram_gb   = int(profile["ram_gb"] * (2 if env == "prod" else (1.5 if env == "test" else 1)))
                    ram_gb   = max(1, ram_gb)

                    # Disk per VM
                    if svc == "postgres":
                        disk_gb = storage_gb + 10 + (20 if env == "prod" else 0)
                    elif svc in ("redis",):
                        disk_gb = max(10, int(storage_gb * 0.1))
                    elif svc in ("prometheus", "loki"):
                        disk_gb = 50
                    else:
                        disk_gb = 20

                    # Naming
                    suffix = f"-app{app_n}" if is_stateless else (f"-{idx+1}" if replicas > 1 else "")
                    role_suffix = "-primary" if (svc == "postgres" and idx == 0) else (
                                  "-replica" if (svc == "postgres" and idx > 0) else suffix)
                    vm_name = f"{env}-{svc}{role_suffix}"

                    # Assign to server
                    target_server = "server_1"
                    if n_servers >= 2:
                        if svc in data_services:
                            target_server = "server_2"
                        else:
                            target_server = "server_1"

                    vm = {
                        "vm_id":           vm_id,
                        "name":            vm_name,
                        "environment":     env,
                        "service":         svc,
                        "role":            "primary" if idx == 0 else "replica",
                        "vcpu":            vcpu,
                        "ram_gb":          ram_gb,
                        "disk_gb":         disk_gb,
                        "disk_type":       "nvme" if svc in ("postgres",) else "ssd",
                        "vlan":            env_vlan,
                        "ip":              f"{env_ip}.{ip_host}",
                        "physical_server": target_server,
                        "os":              "Ubuntu 22.04 LTS",
                    }
                    allocation[target_server].append(vm)
                    vm_id  += 1
                    ip_host += 1

        # Add monitoring for test+prod
        if env in ("test", "prod"):
            for mon_svc in ("prometheus", "grafana", "loki"):
                if mon_svc not in SERVICE_PROFILES:
                    continue
                p = SERVICE_PROFILES[mon_svc]
                r = p["replicas"].get(env, 0)
                if r == 0:
                    continue
                vm = {
                    "vm_id":           vm_id,
                    "name":            f"{env}-{mon_svc}",
                    "environment":     env,
                    "service":         mon_svc,
                    "role":            "monitoring",
                    "vcpu":            int(p["cpu"]),
                    "ram_gb":          int(p["ram_gb"]),
                    "disk_gb":         50,
                    "disk_type":       "ssd",
                    "vlan":            env_vlan,
                    "ip":              f"{env_ip}.{ip_host}",
                    "physical_server": "server_2" if n_servers >= 2 else "server_1",
                    "os":              "Ubuntu 22.04 LTS",
                }
                allocation[f"server_2" if n_servers >= 2 else "server_1"].append(vm)
                vm_id  += 1
                ip_host += 1

    return allocation


def _tool_validate_capacity(args: dict) -> dict:
    """Validate VM totals fit within physical server limits."""
    allocation = args["vm_allocation"]
    phys       = args["physical_specs"]

    results = {}
    all_valid = True

    for server_key, vms in allocation.items():
        if not isinstance(vms, list):
            continue
        spec = phys.get(server_key, {})
        if not spec:
            continue

        total_vcpu   = sum(v["vcpu"]    for v in vms)
        total_ram    = sum(v["ram_gb"]  for v in vms)
        total_disk   = sum(v["disk_gb"] for v in vms)

        phys_cpu     = spec.get("cpu_cores", 0)
        phys_ram     = spec.get("ram_gb",    0)
        phys_disk    = spec.get("storage_tb", 0) * 1000

        cpu_ratio  = round(total_vcpu  / phys_cpu,  2) if phys_cpu  else 0
        ram_ratio  = round(total_ram   / phys_ram,  2) if phys_ram  else 0
        disk_ratio = round(total_disk  / phys_disk, 2) if phys_disk else 0

        warnings = []
        if cpu_ratio  > 4.0: warnings.append(f"CPU overcommit {cpu_ratio}:1 exceeds 4:1 limit")
        if ram_ratio  > 1.2: warnings.append(f"RAM overcommit {ram_ratio}:1 exceeds 1.2:1 limit")
        if disk_ratio > 0.85: warnings.append(f"Disk usage {disk_ratio*100:.0f}% exceeds 85% threshold")

        valid = len(warnings) == 0
        if not valid:
            all_valid = False

        results[server_key] = {
            "valid":       valid,
            "warnings":    warnings,
            "total_vcpu":  total_vcpu,
            "total_ram_gb":total_ram,
            "total_disk_gb":total_disk,
            "cpu_overcommit_ratio":  cpu_ratio,
            "ram_overcommit_ratio":  ram_ratio,
            "disk_usage_ratio":      disk_ratio,
            "vm_count":    len(vms),
        }

    results["_all_valid"] = all_valid
    return results


def _tool_generate_network_design(args: dict) -> dict:
    """Design VLAN layout and IP scheme."""
    envs     = args["environments"]
    n_phys   = args["physical_servers"]

    vlans = {}
    env_vlan_map = {"dev": 10, "test": 20, "prod": 30}
    env_ip_map   = {"dev": "10.10.0.0/24", "test": "10.20.0.0/24", "prod": "10.30.0.0/24"}

    for i, env in enumerate(envs):
        vlans[env] = {
            "vlan_id":   env_vlan_map.get(env, 10 + i * 10),
            "subnet":    env_ip_map.get(env,   f"10.{10 + i*10}.0.0/24"),
            "gateway":   env_ip_map.get(env,   f"10.{10 + i*10}.0.0/24").replace(".0/24", ".1"),
            "purpose":   f"{env.upper()} environment traffic",
        }

    return {
        "vlans":        vlans,
        "mgmt_vlan":    {"vlan_id": 1, "subnet": "192.168.1.0/24", "purpose": "Management / IPMI / Hypervisor"},
        "storage_vlan": {"vlan_id": 100, "subnet": "10.100.0.0/24", "purpose": "Storage replication (Postgres WAL)"},
        "inter_server_link": f"10GbE bonded (2× ports) between {n_phys} physical servers",
        "switch_req":   "Managed L2/L3 switch with VLAN support (Cisco/HP/Ubiquiti)",
        "firewall_zones": {
            "dmz":   "Internet-facing ingress (nginx/HAProxy VMs only)",
            "app":   "App tier VMs — no direct internet",
            "data":  "Data tier VMs — only accessible from app VLAN",
            "mgmt":  "Management access — SSH bastion only",
        },
    }


def _tool_generate_proxmox_config(args: dict) -> str:
    """Generate Proxmox qm create commands."""
    allocation    = args["vm_allocation"]
    network_design = args.get("network_design", {})

    lines = [
        "#!/bin/bash",
        "# Proxmox VM Creation Script",
        f"# Generated: {datetime.now().isoformat()}",
        "# Run on each Proxmox node as root",
        "",
    ]

    for server_key, vms in allocation.items():
        if not isinstance(vms, list):
            continue
        node = server_key.replace("_", "-")
        lines.append(f"# ═══════════════════════════════════════")
        lines.append(f"# {server_key.upper()} ({node})")
        lines.append(f"# ═══════════════════════════════════════")
        lines.append("")

        for vm in vms:
            disk_type = "scsi0" if vm.get("disk_type") == "nvme" else "scsi0"
            storage   = "local-nvme" if vm.get("disk_type") == "nvme" else "local-ssd"
            vlan_tag  = vm.get("vlan", 10)
            lines += [
                f"# VM {vm['vm_id']}: {vm['name']} ({vm['environment']} / {vm['service']})",
                f"qm create {vm['vm_id']} \\",
                f"  --name {vm['name']} \\",
                f"  --cores {vm['vcpu']} \\",
                f"  --memory {vm['ram_gb'] * 1024} \\",
                f"  --{disk_type} {storage}:{vm['disk_gb']} \\",
                f"  --net0 virtio,bridge=vmbr0,tag={vlan_tag} \\",
                f"  --ostype l26 \\",
                f"  --agent enabled=1",
                "",
            ]

    return "\n".join(lines)


def _tool_generate_ansible_inventory(args: dict) -> str:
    """Generate Ansible INI inventory."""
    allocation = args["vm_allocation"]
    lines = [
        "# Ansible Inventory — Generated by server-sizing-agent",
        f"# {datetime.now().isoformat()}",
        "",
    ]

    # Group by environment
    env_groups: dict[str, list] = {}
    role_groups: dict[str, list] = {}

    for server_key, vms in allocation.items():
        if not isinstance(vms, list):
            continue
        for vm in vms:
            env = vm["environment"]
            svc = vm["service"]
            env_groups.setdefault(env, []).append(vm)
            role_groups.setdefault(svc, []).append(vm)

    for env, vms in env_groups.items():
        lines.append(f"[{env}]")
        for vm in vms:
            lines.append(f"{vm['name']} ansible_host={vm['ip']} vm_id={vm['vm_id']}")
        lines.append("")

    for role, vms in role_groups.items():
        lines.append(f"[{role}]")
        for vm in vms:
            lines.append(f"{vm['name']} ansible_host={vm['ip']}")
        lines.append("")

    lines += [
        "[all:vars]",
        "ansible_user=ubuntu",
        "ansible_ssh_private_key_file=~/.ssh/projectzero",
        "ansible_python_interpreter=/usr/bin/python3",
    ]

    return "\n".join(lines)


def _tool_generate_sizing_report(args: dict) -> str:
    """Generate full markdown sizing report."""
    req       = args["requirements"]
    workload  = args["workload"]
    phys      = args["physical_specs"]
    alloc     = args["vm_allocation"]
    val       = args.get("validation", {})
    net       = args.get("network_design", {})

    ts    = datetime.now().strftime("%Y-%m-%d %H:%M")
    apps  = req["apps"]
    users = req["users_per_app"]
    envs  = req["environments"]
    n_srv = req["physical_servers"]

    lines = [
        f"# Server Sizing Report",
        f"",
        f"**Generated**: {ts}  ",
        f"**Apps**: {apps} | **Users/app**: {users:,} | **Environments**: {', '.join(envs)}  ",
        f"**Physical servers**: {n_srv} | **Stack**: {', '.join(req['stack_services'])}",
        f"",
        f"---",
        f"",
        f"## Executive Summary",
        f"",
    ]

    # Grand totals
    total_vms  = sum(len(v) for v in alloc.values() if isinstance(v, list))
    total_vcpu = sum(sum(vm["vcpu"]    for vm in v) for v in alloc.values() if isinstance(v, list))
    total_ram  = sum(sum(vm["ram_gb"]  for vm in v) for v in alloc.values() if isinstance(v, list))
    total_disk = sum(sum(vm["disk_gb"] for vm in v) for v in alloc.values() if isinstance(v, list))

    lines += [
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total VMs | {total_vms} |",
        f"| Total vCPUs | {total_vcpu} |",
        f"| Total RAM | {total_ram} GB |",
        f"| Total Storage | {total_disk:,} GB ({total_disk/1000:.1f} TB) |",
        f"| Physical Servers | {n_srv} |",
        f"",
    ]

    # Physical server specs
    lines += ["## Physical Server Specifications", ""]
    for sk, spec in phys.items():
        if sk.startswith("_"):
            continue
        lines += [
            f"### {sk.replace('_',' ').title()} — {spec.get('role','').upper()}",
            f"",
            f"**Purpose**: {spec.get('purpose','')}  ",
            f"**Example hardware**: {spec.get('example','')}",
            f"",
            f"| Component | Spec |",
            f"|-----------|------|",
            f"| CPU | {spec['cpu_cores']} cores |",
            f"| RAM | {spec['ram_gb']} GB DDR4 ECC |",
            f"| Storage | {spec['storage_tb']} TB ({spec.get('storage_type','NVMe SSD')}) |",
            f"| Network | {spec.get('network','2× 10GbE bonded')} |",
            f"| OS | Ubuntu 22.04 LTS (hypervisor host) |",
            f"",
        ]
        v = val.get(sk, {})
        if v:
            status = "✅ VALID" if v.get("valid") else "⚠️  WARNINGS"
            lines += [
                f"**Capacity validation**: {status}  ",
                f"CPU overcommit: {v.get('cpu_overcommit_ratio',0):.1f}:1 | "
                f"RAM overcommit: {v.get('ram_overcommit_ratio',0):.1f}:1 | "
                f"Disk: {v.get('disk_usage_ratio',0)*100:.0f}% used",
            ]
            for w in v.get("warnings", []):
                lines.append(f"  - ⚠️  {w}")
            lines.append("")

    # Per-environment workload
    lines += ["## Workload Per Environment", ""]
    for env in envs:
        w = workload.get(env, {})
        lines += [
            f"### {env.upper()}",
            f"",
            f"| Resource | Required (with 20% buffer) |",
            f"|----------|---------------------------|",
            f"| vCPU | {w.get('total_vcpu',0)} |",
            f"| RAM | {w.get('total_ram_gb',0)} GB |",
            f"| Storage | {w.get('total_disk_gb',0)} GB |",
            f"",
        ]

    # VM allocation table
    lines += ["## VM Allocation", ""]
    for sk, vms in alloc.items():
        if not isinstance(vms, list) or not vms:
            continue
        lines += [
            f"### {sk.replace('_',' ').title()}",
            f"",
            f"| VM Name | Env | Service | vCPU | RAM | Disk | IP | VLAN |",
            f"|---------|-----|---------|------|-----|------|----|------|",
        ]
        for vm in vms:
            lines.append(
                f"| {vm['name']} | {vm['environment']} | {vm['service']} "
                f"| {vm['vcpu']} | {vm['ram_gb']}GB | {vm['disk_gb']}GB "
                f"| {vm['ip']} | {vm['vlan']} |"
            )
        lines.append("")

    # Network
    if net:
        lines += ["## Network Design", ""]
        lines += [
            f"**Inter-server link**: {net.get('inter_server_link','')}  ",
            f"**Switch requirement**: {net.get('switch_req','')}",
            f"",
            f"| VLAN | ID | Subnet | Purpose |",
            f"|------|----|--------|---------|",
        ]
        for env, vlan in net.get("vlans", {}).items():
            lines.append(f"| {env.upper()} | {vlan['vlan_id']} | {vlan['subnet']} | {vlan['purpose']} |")
        mgmt = net.get("mgmt_vlan", {})
        if mgmt:
            lines.append(f"| MGMT | {mgmt['vlan_id']} | {mgmt['subnet']} | {mgmt['purpose']} |")
        stor = net.get("storage_vlan", {})
        if stor:
            lines.append(f"| STORAGE | {stor['vlan_id']} | {stor['subnet']} | {stor['purpose']} |")
        lines.append("")

    # Bill of materials
    lines += [
        "## Bill of Materials (BOM)",
        "",
        "| Item | Qty | Spec | Est. Unit Cost |",
        "|------|-----|------|----------------|",
    ]
    for sk, spec in phys.items():
        if sk.startswith("_"):
            continue
        cpu  = spec["cpu_cores"]
        ram  = spec["ram_gb"]
        disk = spec["storage_tb"]
        # Rough pricing
        cost = 3000 + (cpu * 100) + (ram * 15) + (disk * 200)
        lines.append(f"| Physical Server ({spec['role']}) | 1 | {cpu}C/{ram}GB/{disk}TB NVMe | ~${cost:,} |")

    lines += [
        "| Managed 10GbE Switch | 1 | 24-port L3 | ~$2,000 |",
        "| 10GbE NICs (per server) | {n_srv} | 2-port SFP+ | ~$300 |".format(n_srv=n_srv),
        "| Rack + PDU + UPS | 1 | 12U min | ~$3,000 |",
        "",
    ]

    # Recommendations
    lines += [
        "## Recommendations",
        "",
        "1. **Hypervisor**: Proxmox VE (free, KVM-based, web UI, HA clustering)",
        "2. **Storage**: Local NVMe in RAID-10 per server. No shared SAN needed at this scale.",
        "3. **Backup**: Proxmox Backup Server on separate USB/NAS. Daily snapshots.",
        "4. **HA**: Prod Postgres uses streaming replication (primary on server_1, replica on server_2).",
        "5. **Orchestration**: K3s (lightweight K8s) — install once, namespace per environment.",
        "6. **Monitoring**: Prometheus + Grafana + Loki on server_2. Alerts via Alertmanager.",
        "7. **Network**: Bond 2× 10GbE ports per server (LACP). VLAN trunking on hypervisor bridge.",
        "8. **Security**: No direct prod DB access from DEV VLAN. Bastion SSH for management.",
        "",
        "## Next Steps",
        "",
        "- [ ] Procure hardware per BOM",
        "- [ ] Install Proxmox VE on both servers",
        "- [ ] Run `proxmox-setup.sh` to create VMs",
        "- [ ] Run `ansible-playbook site.yml -i inventory.ini` to provision",
        "- [ ] Deploy K3s cluster per environment",
        "- [ ] Deploy apps via Helm or kubectl",
    ]

    return "\n".join(lines)


def _tool_save_output(args: dict) -> dict:
    """Save generated files to output directory."""
    OUTPUT.mkdir(parents=True, exist_ok=True)
    ts       = datetime.now().strftime("%Y%m%d-%H%M%S")
    saved    = []

    report_path = OUTPUT / f"sizing-report-{ts}.md"
    report_path.write_text(args["sizing_report"])
    saved.append(str(report_path))

    if pc := args.get("proxmox_config"):
        p = OUTPUT / f"proxmox-vms-{ts}.sh"
        p.write_text(pc)
        p.chmod(0o755)
        saved.append(str(p))

    if ai := args.get("ansible_inventory"):
        p = OUTPUT / f"inventory-{ts}.ini"
        p.write_text(ai)
        saved.append(str(p))

    if vj := args.get("vm_allocation_json"):
        p = OUTPUT / f"vm-allocation-{ts}.json"
        p.write_text(vj)
        saved.append(str(p))

    return {"saved": saved, "output_dir": str(OUTPUT)}


# ── Tool dispatch ─────────────────────────────────────────────────────────────

def dispatch_tool(name: str, args: dict, cli_args: argparse.Namespace,
                  state: dict) -> Any:
    if name == "gather_requirements":
        result = _tool_gather_requirements(args, cli_args)
        state["requirements"] = result
        return result

    if name == "calculate_workload":
        result = _tool_calculate_workload(args)
        state["workload"] = result
        return result

    if name == "recommend_physical_specs":
        result = _tool_recommend_physical_specs(args)
        state["physical_specs"] = result
        return result

    if name == "allocate_vms":
        result = _tool_allocate_vms(args)
        state["vm_allocation"] = result
        return result

    if name == "validate_capacity":
        result = _tool_validate_capacity(args)
        state["validation"] = result
        return result

    if name == "generate_network_design":
        result = _tool_generate_network_design(args)
        state["network_design"] = result
        return result

    if name == "generate_proxmox_config":
        result = _tool_generate_proxmox_config(args)
        state["proxmox_config"] = result
        return result

    if name == "generate_ansible_inventory":
        result = _tool_generate_ansible_inventory(args)
        state["ansible_inventory"] = result
        return result

    if name == "generate_sizing_report":
        result = _tool_generate_sizing_report(args)
        state["sizing_report"] = result
        return result

    if name == "save_output":
        result = _tool_save_output(args)
        return result

    return {"error": f"Unknown tool: {name}"}


# ── Agentic loop ──────────────────────────────────────────────────────────────

def run_agent(cli_args: argparse.Namespace) -> None:
    client  = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    state: dict = {}

    initial_msg = (
        f"Size an on-prem server deployment with these parameters:\n"
        f"- Physical servers: {cli_args.servers}\n"
        f"- Applications: {cli_args.apps}\n"
        f"- Users per app: {cli_args.users:,}\n"
        f"- Environments: {', '.join(cli_args.envs)}\n"
        f"- Storage per app: {cli_args.storage} GB\n"
        f"- Stack: {', '.join(cli_args.stack)}\n"
        f"- Hypervisor: {cli_args.hypervisor}\n\n"
        f"Execute the full tool flow: gather_requirements → calculate_workload → "
        f"recommend_physical_specs → allocate_vms → validate_capacity → "
        f"generate_network_design → generate_proxmox_config → generate_ansible_inventory → "
        f"generate_sizing_report → save_output.\n\n"
        f"Produce a complete, buildable sizing plan."
    )

    messages: list[dict] = [{"role": "user", "content": initial_msg}]

    print(f"\n{'═'*60}")
    print(f"  Server Sizing Agent — ProjectZero")
    print(f"  {cli_args.servers} servers · {cli_args.apps} apps · "
          f"{cli_args.users:,} users · {', '.join(cli_args.envs)}")
    print(f"{'═'*60}\n")

    iteration = 0
    max_iterations = 25

    while iteration < max_iterations:
        iteration += 1
        print(f"[iter {iteration}] Thinking...", end=" ", flush=True)

        with client.beta.messages.stream(
            model=MODEL,
            max_tokens=8192,
            system=[{
                "type":  "text",
                "text":  SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }],
            tools=TOOLS,
            messages=messages,
            thinking={"type": "adaptive"},
            betas=["interleaved-thinking-2025-05-14"],
        ) as stream:
            final = stream.get_final_message()

        # Summarize what Claude did this turn
        text_parts = [b.text for b in final.content if hasattr(b, "text") and b.type == "text"]
        tool_calls = [b       for b in final.content if b.type == "tool_use"]

        if text_parts:
            snippet = text_parts[0][:100].replace("\n", " ")
            print(f"{snippet}...")
        else:
            print(f"{len(tool_calls)} tool call(s)")

        # Append assistant turn
        content_dicts = [
            b.model_dump() if hasattr(b, "model_dump") else dict(b)
            for b in final.content
        ]
        messages.append({"role": "assistant", "content": content_dicts})

        # Done?
        if final.stop_reason == "end_turn":
            print("\n✓ Agent complete\n")
            break

        # Execute tool calls
        if final.stop_reason == "tool_use":
            tool_results = []
            for tool_call in tool_calls:
                name = tool_call.name
                args = tool_call.input
                print(f"  → {name}({', '.join(f'{k}={str(v)[:40]}' for k,v in args.items() if k not in ('workload','vm_allocation','physical_specs'))})")

                try:
                    result = dispatch_tool(name, args, cli_args, state)
                    result_str = json.dumps(result, indent=2) if not isinstance(result, str) else result
                    # Truncate large results to avoid context bloat
                    if len(result_str) > 4000:
                        result_str = result_str[:4000] + "\n... [truncated]"
                    tool_results.append({
                        "type":        "tool_result",
                        "tool_use_id": tool_call.id,
                        "content":     result_str,
                    })
                except Exception as exc:
                    print(f"  ✗ Error in {name}: {exc}")
                    tool_results.append({
                        "type":        "tool_result",
                        "tool_use_id": tool_call.id,
                        "content":     json.dumps({"error": str(exc)}),
                        "is_error":    True,
                    })

            messages.append({"role": "user", "content": tool_results})

    # Print saved files
    if "sizing_report" in state:
        print("─" * 60)
        print(state["sizing_report"][:3000])
        if len(state["sizing_report"]) > 3000:
            print("\n... [see full report in output/server-sizing/]")

    print(f"\n{'═'*60}")
    print(f"  Output saved to: {OUTPUT}")
    print(f"{'═'*60}\n")


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Server Sizing Agent — ProjectZero on-prem deployments"
    )
    p.add_argument("--apps",       type=int,   default=10,
                   help="Number of applications (default: 10)")
    p.add_argument("--users",      type=int,   default=10000,
                   help="Peak concurrent users per app (default: 10000)")
    p.add_argument("--envs",       type=lambda s: s.split(","),
                   default=["dev","test","prod"],
                   help="Environments comma-separated (default: dev,test,prod)")
    p.add_argument("--servers",    type=int,   default=2,
                   help="Number of physical servers (default: 2)")
    p.add_argument("--storage",    type=int,   default=50,
                   help="Storage GB per app (default: 50)")
    p.add_argument("--stack",      type=lambda s: s.split(","),
                   default=["nextjs","fastapi","postgres","redis","temporal"],
                   help="Stack services comma-separated")
    p.add_argument("--hypervisor", type=str,   default="proxmox",
                   choices=["proxmox","vmware","kvm","none"],
                   help="Hypervisor platform (default: proxmox)")
    return p.parse_args()


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        # Try loading from factory .env
        env_file = FACTORY / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("ANTHROPIC_API_KEY="):
                    os.environ["ANTHROPIC_API_KEY"] = line.split("=", 1)[1].strip()
                    break

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set. Export it or add to factory .env")
        sys.exit(1)

    run_agent(parse_args())
