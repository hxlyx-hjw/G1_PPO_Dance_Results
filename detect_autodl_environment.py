"""Inspect an AutoDL host and write a project-specific runtime profile."""

from __future__ import annotations

import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROFILES = ROOT / "profiles"
CONFIG = ROOT / "config"
CONFIG.mkdir(parents=True, exist_ok=True)


def read_env(path: Path) -> dict[str, str]:
    values = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def run_text(command: list[str]) -> str:
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=20, check=False
        )
        return (result.stdout or "").strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def os_release() -> str:
    path = Path("/etc/os-release")
    if path.is_file():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("PRETTY_NAME="):
                return line.split("=", 1)[1].strip().strip('"')
    return platform.platform()


def memory_gb() -> float:
    path = Path("/proc/meminfo")
    if path.is_file():
        match = re.search(r"MemTotal:\s+(\d+)\s+kB", path.read_text())
        if match:
            return round(int(match.group(1)) / 1024 / 1024, 1)
    try:
        import psutil  # type: ignore

        return round(psutil.virtual_memory().total / 1024**3, 1)
    except Exception:
        return 0.0


def cpu_model() -> str:
    path = Path("/proc/cpuinfo")
    if path.is_file():
        for line in path.read_text(errors="replace").splitlines():
            if line.lower().startswith("model name"):
                return line.split(":", 1)[1].strip()
    return platform.processor() or "unknown"


def gpu_info() -> list[dict[str, str]]:
    text = run_text(
        [
            "nvidia-smi",
            "--query-gpu=name,memory.total,driver_version,compute_cap",
            "--format=csv,noheader,nounits",
        ]
    )
    rows = []
    for line in text.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) >= 3:
            rows.append(
                {
                    "name": parts[0],
                    "memory_mb": parts[1],
                    "driver": parts[2],
                    "compute_cap": parts[3] if len(parts) > 3 else "unknown",
                }
            )
    return rows


def torch_info() -> dict[str, object]:
    try:
        import torch

        return {
            "version": torch.__version__,
            "cuda_build": torch.version.cuda,
            "cuda_available": bool(torch.cuda.is_available()),
            "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        }
    except Exception as exc:
        return {"version": None, "cuda_build": None, "cuda_available": False, "error": str(exc)}


def choose_profile(gpu: dict[str, str] | None) -> str:
    if gpu is None:
        return "cpu_fallback"
    name = gpu["name"].upper()
    try:
        memory = int(float(gpu["memory_mb"]))
    except ValueError:
        memory = 0
    if "5090" in name or memory >= 30000:
        return "rtx5090_32g"
    if "4090" in name:
        return "rtx4090_24g"
    if "3090" in name:
        return "rtx3090_24g"
    if memory >= 22000:
        return "a10_24g"
    if memory >= 14000:
        return "rtx4080_16g"
    return "generic_12g"


def main() -> None:
    gpus = gpu_info()
    primary = gpus[0] if gpus else None
    profile_name = choose_profile(primary)
    profile = read_env(PROFILES / f"{profile_name}.env")

    cpu_cores = os.cpu_count() or 1
    ram_gb = memory_gb()
    disk_path = Path("/root/autodl-tmp") if Path("/root/autodl-tmp").is_dir() else ROOT
    disk_free_gb = round(shutil.disk_usage(disk_path).free / 1024**3, 1)

    base_envs = int(profile.get("BASE_ENVS", "4"))
    envs = min(base_envs, max(2, int(cpu_cores * 0.75)))
    if ram_gb and ram_gb < 24:
        envs = max(2, envs // 2)
    if primary is None:
        envs = min(envs, 4)
    elif int(float(primary["memory_mb"])) < 10000:
        envs = min(envs, 4)
    if disk_free_gb < 20:
        envs = min(envs, 2)

    gpu_memory = int(float(primary["memory_mb"])) if primary else 0
    suitable = bool(primary and gpu_memory >= 10000 and disk_free_gb >= 20)
    output = (
        "/root/autodl-tmp/runs/gwa_100k"
        if Path("/root/autodl-tmp").is_dir()
        else str(ROOT / "outputs" / "gwa_100k")
    )

    info = {
        "detected_at": __import__("datetime").datetime.now().astimezone().isoformat(),
        "os": os_release(),
        "kernel": platform.release(),
        "python": sys.version.split()[0],
        "python_executable": sys.executable,
        "cpu_model": cpu_model(),
        "cpu_cores": cpu_cores,
        "ram_gb": ram_gb,
        "disk_path": str(disk_path),
        "disk_free_gb": disk_free_gb,
        "gpu_count": len(gpus),
        "gpus": gpus,
        "gpu_primary": primary,
        "torch": torch_info(),
        "profile": profile_name,
        "profile_label": profile.get("PROFILE_LABEL", ""),
        "suitable": suitable,
        "recommended_envs": envs,
        "recommended_vcpu": max(8, envs * 2),
        "recommended_ram_gb": max(32, envs * 4),
        "output": output,
    }
    (CONFIG / "autodl_environment.json").write_text(
        json.dumps(info, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    values = {
        **profile,
        "PROFILE_NAME": profile_name,
        "AUTODL_PROFILE": profile_name,
        "GPU_NAME": primary["name"] if primary else "none",
        "GPU_MEMORY_MB": str(gpu_memory),
        "GPU_DRIVER": primary["driver"] if primary else "none",
        "GPU_COMPUTE_CAP": primary["compute_cap"] if primary else "none",
        "GPU_SUITABLE": "1" if suitable else "0",
        "CPU_CORES": str(cpu_cores),
        "RAM_GB": str(ram_gb),
        "DISK_FREE_GB": str(disk_free_gb),
        "SYSTEM_PYTHON": sys.version.split()[0],
        "ENVS": str(envs),
        "OUTPUT": output,
        "G1_MUJOCO_GL": "disable",
    }
    lines = [
        "# Auto-generated by detect_autodl_environment.py",
        f"# profile={profile_name} gpu={values['GPU_NAME']} vram={gpu_memory}MB envs={envs}",
    ]
    for key, value in values.items():
        lines.append(f"{key}={shlex.quote(str(value))}")
    generated = PROFILES / "autodl_detected.env"
    generated.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(info, indent=2, ensure_ascii=False))
    print("generated:", generated)
    print("generated:", CONFIG / "autodl_environment.json")


if __name__ == "__main__":
    main()
