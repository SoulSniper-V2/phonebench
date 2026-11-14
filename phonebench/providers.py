"""Decision-model adapters. One question contract, three wire formats.

Every provider receives the same `state` (JSON) and `questions` (typed: choice / noul / score),
optionally a screenshot, and returns answers + usage + latency. Python standard library only.
"""
import base64
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request
import uuid

# name -> (family, wire model id)
PROVIDERS = {
    "jev-1.14": ("typesafe", "jev-1.14.0"),
    "jev-1.13": ("typesafe", "jev-1.13.0"),
    "gemini-decision-1": ("gemini", "gemini-decision-1"),
    "clef-flash": ("cloudflare", "clef-flash"),
    "clef": ("cloudflare", "clef"),
    "clef-omni": ("cloudflare", "clef-omni"),
}
SECRET_KEYS = ("TYPESAFE_API_KEY", "CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID", "GEMINI_API_KEY")


def load_env():
    """Read KEY=VALUE lines from $PHONEBENCH_ENV, ./.env or ~/.config/phonebench/env (never committed)."""
    for p in (os.environ.get("PHONEBENCH_ENV"), ".env", str(Path.home() / ".config/phonebench/env")):
        if p and Path(p).exists():
            for line in Path(p).read_text().splitlines():
                if "=" in line and not line.lstrip().startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())


def redact(value):
    text = str(value)
    for key in SECRET_KEYS:
        secret = os.environ.get(key)
        if secret:
            text = text.replace(secret, "[REDACTED]")
    return text


def _need(key):
    v = os.environ.get(key)
    if not v:
        raise ValueError(f"Missing {key}")
    return v


def request_spec(provider, state, questions, image=None, image_format="png"):
    family, model = PROVIDERS[provider]
    headers = {"Content-Type": "application/json"}
    enc = base64.b64encode(image).decode() if image else None
    mime = "image/png" if image_format == "png" else "image/jpeg"
    if family == "gemini":
        headers["x-goog-api-key"] = _need("GEMINI_API_KEY")
        content = [{"type": "text", "text": json.dumps(state)}]
        if enc:
            content.append({"type": "image", "data": enc, "mime_type": mime, "resolution": "medium"})
        return "https://generativelanguage.googleapis.com/v1beta/decisions", headers, {"model": model, "input": content, "questions": questions}
    if family == "typesafe":
        headers["Authorization"] = "Bearer " + _need("TYPESAFE_API_KEY")
        body = {"model": model, "state": state, "questions": questions}
        if enc:
            headers["TypeSafe-Danger-Zone-Images"] = "true"
            ref = str(uuid.uuid4())
            body["state"] = {"context": state, "screen": ref}
            body["assets"] = {ref: {"type": "image", "format": image_format, "data_base64": enc}}
        return "https://api.typesafe.ai/v1/systemone", headers, body
    headers["Authorization"] = "Bearer " + _need("CLOUDFLARE_API_TOKEN")
    account = _need("CLOUDFLARE_ACCOUNT_ID")
    if not account.isalnum():
        raise ValueError("Invalid Cloudflare account id")
    body = {"model": model, "state": state, "questions": questions}
    if enc:
        body["images"] = [f"data:{mime};base64,{enc}"]
    return f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/@cf/cloudflare/{model}", headers, body


def ask(provider, state, questions, image=None, image_format="png", timeout=30):
    url, headers, body = request_spec(provider, state, questions, image, image_format)
    start = time.perf_counter()
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{provider}: HTTP {e.code}: {redact(e.read().decode(errors='replace'))[:800]}") from None
    except (urllib.error.URLError, TimeoutError) as e:
        raise RuntimeError(f"{provider}: {redact(e)}") from None
    if "success" in data and not data["success"]:
        raise RuntimeError(f"{provider}: {redact(data.get('errors'))}")
    result = data.get("result", data)
    answers = result.get("answers") if isinstance(result, dict) else None
    if not isinstance(answers, dict) or set(questions) - set(answers):
        raise RuntimeError(f"{provider}: missing answers")
    return {"provider": provider, "model": result.get("model", body["model"]),
            "ms": round((time.perf_counter() - start) * 1000, 1), "answers": answers, "usage": result.get("usage")}


def usage_tokens(u):
    """(input, output) tokens across the providers' differing usage shapes."""
    if not isinstance(u, dict):
        return 0, 0
    i = u.get("input_tokens") or u.get("total_input_tokens") or u.get("prompt_tokens") or 0
    o = u.get("output_tokens") or u.get("total_output_tokens") or u.get("completion_tokens") or 0
    return int(i or 0), int(o or 0)
