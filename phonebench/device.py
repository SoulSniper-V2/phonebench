"""Thin, audited wrapper over the phonedriver CLI (https://www.npmjs.com/package/phonedriver).

No shell, no guard overrides, no --autonomous: phonedriver itself refuses taps that spend money
or can't be undone unless a human approved them.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

from .providers import redact

SESSION = "phonebench"


def binary():
    if os.environ.get("PHONEDRIVER_BIN"):
        return [os.environ["PHONEDRIVER_BIN"]]
    found = shutil.which("phonedriver")
    if found:
        return [found]
    cache = Path.home() / "Library/Caches/phonedriver/npm"
    bins = list(cache.glob("*/aarch64-apple-darwin/phonedriver")) if cache.exists() else []
    return [str(max(bins, key=lambda p: p.stat().st_mtime))] if bins else ["npx", "-y", "phonedriver"]


def driver(*args, timeout=35, settle=False):
    dev = os.environ.get("PHONEBENCH_DEVICE")
    cmd = binary() + ["--session", SESSION, "--timeout", "1000"] + (["--device", dev] if dev else []) + ([] if settle else ["--no-settle"]) + list(args)
    audit = os.environ.get("PHONEBENCH_AUDIT")
    t0 = time.time()

    def log(rec):
        if audit:
            with open(audit, "a") as f:
                f.write(json.dumps({"started": t0, "finished": time.time(), "args": list(args), **rec}) + "\n")
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        log({"error": "timeout"})
        raise RuntimeError("phonedriver timed out") from None
    log({"returncode": p.returncode, "stdout": redact(p.stdout)[:20000], "stderr": redact(p.stderr)[:2000]})
    if p.returncode:
        raise RuntimeError(redact((p.stderr + p.stdout).strip()))
    return p.stdout.strip()


def save_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, prefix="." + path.name, suffix=".tmp", delete=False) as f:
        tmp = Path(f.name)
        f.write(json.dumps(obj, indent=1) + "\n")
    tmp.chmod(0o600)
    os.replace(tmp, path)


def snapshot():
    return json.loads(driver("--json", "snapshot", timeout=40))


def elements(s):
    return s.get("elements", [])


def app_of(s):
    return (s.get("header") or {}).get("app", {}).get("id")


def center(e):
    b = e["bounds"]
    return f"{b['x'] + b['w'] / 2:.1f},{b['y'] + b['h'] / 2:.1f}"


def tap_element(e):
    return driver("tap", center(e), settle=True)


def launch_verified(app):
    """Launch; if the CLI times out, accept only when an independent snapshot shows the app in front."""
    try:
        return driver("launch", app, settle=True, timeout=65)
    except RuntimeError as exc:
        if "timed out" not in str(exc):
            raise
        if app_of(snapshot()) != app:
            raise
        return "launch timed out; foreground app verified"


def back_gesture():
    g = {"fingers": [[{"x": 3, "y": 420, "t_ms": 0}, {"x": 260, "y": 420, "t_ms": 220}]]}
    return driver("gesture", json.dumps(g), settle=True)


def observe(folder, index):
    """AX snapshot + screenshot, saved as NN.snapshot.json / NN.png."""
    folder = Path(folder)
    t = time.perf_counter()
    s = snapshot()
    save_json(folder / f"{index:02d}.snapshot.json", s)
    png = folder / f"{index:02d}.png"
    driver("screenshot", "-o", str(png))
    return s, png.read_bytes(), {"observation_ms": round((time.perf_counter() - t) * 1000, 1)}
