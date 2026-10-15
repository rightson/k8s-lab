"""Read-only environment evidence; never reads kubeconfig or credentials."""
import json, os, platform, shutil, sys
from datetime import datetime, timezone
from pathlib import Path

def small(path):
    try: return Path(path).read_text().strip()
    except OSError: return None

def inspect():
    tools = {x: shutil.which(x) for x in ("docker", "podman", "nerdctl", "containerd", "kind", "kubectl")}
    caps = {line.split(":")[0]: line.split(":")[1].strip()
            for line in Path("/proc/self/status").read_text().splitlines()
            if line.startswith(("CapEff:", "CapBnd:"))} if sys.platform == "linux" else {}
    missing = [x for x in ("docker", "kind", "kubectl") if not tools[x]]
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "os_release": small("/etc/os-release"), "kernel": platform.release(),
        "architecture": platform.machine(), "python": platform.python_version(),
        "logical_cpu_count": os.cpu_count(), "cpu_max": small("/sys/fs/cgroup/cpu.max"),
        "memory_max_bytes": small("/sys/fs/cgroup/memory.max"),
        "numa_visible_nodes": sorted(p.name for p in Path("/sys/devices/system/node").glob("node[0-9]*")),
        "tools": tools, "capabilities": caps,
        "sockets": {p: Path(p).exists() for p in ("/run/docker.sock",
            "/var/run/docker.sock", "/run/containerd/containerd.sock", "/dev/kvm")},
        "missing_required_tools": missing,
        "kubernetes": "not_instantiated", "runtime": "not_instantiated",
        "cni": "not_instantiated", "csi": "not_used", "image_digest": "not_built",
        "feature_gates": "not_instantiated",
        "status": "blocked" if missing else "tools_present_cluster_unverified",
        "limits": "No daemon connection, namespace creation, credential read or external-cluster operation attempted. Zero capabilities do not authorize escalation. CPU/NUMA visibility is container-level, not physical host ownership."
    }

if __name__ == "__main__":
    record = inspect()
    print(json.dumps(record, ensure_ascii=False, indent=2))
    sys.exit(2 if record["missing_required_tools"] else 0)

