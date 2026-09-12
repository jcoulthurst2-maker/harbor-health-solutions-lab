from __future__ import annotations

import base64
import hashlib
import json
import pathlib
import secrets
import sys
import time
import urllib.error
import urllib.request
import uuid

API = "https://api.cloudflare.com/client/v4"
SCRIPT = "frontier1-primitive-probe"
DUE_AFTER_MS = 90_000
OBSERVE_AFTER_MS = 125_000


def call(method, path, *, payload=None, token=None, headers=None, body=None, timeout=90):
    h = {"accept": "application/json"}
    if headers:
        h.update(headers)
    if token:
        h["authorization"] = "Bearer " + token
    data = body
    if payload is not None:
        h["content-type"] = "application/json"
        data = json.dumps(payload, separators=(",", ":")).encode()
    req = urllib.request.Request(API + path, method=method, headers=h, data=data)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def ok_json(method, path, **kw):
    status, raw = call(method, path, **kw)
    try:
        data = json.loads(raw)
    except Exception:
        raise SystemExit(f"provider returned non-JSON at {path}: HTTP {status}")
    if not (200 <= status < 300 and data.get("success") is True):
        errs = data.get("errors") or []
        msg = "; ".join(str(x.get("message", x)) for x in errs) or f"HTTP {status}"
        raise SystemExit(f"provider rejected {path}: {msg}")
    return data


def acquire_account():
    challenge = (ok_json("POST", "/provisioning/previews/challenge", payload={}).get("result") or {})
    challenge_token = str(challenge.get("challengeToken") or "")
    seed_s = str(challenge.get("seed") or "")
    k = int(challenge.get("k") or 0)
    g = int(challenge.get("g") or 0)
    if not challenge_token or k <= 0 or g <= 0 or k * g > 64_000_000:
        raise SystemExit("provider challenge violated probe bounds")
    seed = base64.urlsafe_b64decode(seed_s + "=" * ((4 - len(seed_s) % 4) % 4))
    if len(seed) != 32:
        raise SystemExit("provider challenge seed invalid")
    current = hashlib.sha256(seed).digest()
    checkpoints = [current]
    for _ in range(k):
        for __ in range(g):
            current = hashlib.sha256(current).digest()
        checkpoints.append(current)
    result = ok_json(
        "POST",
        "/provisioning/previews",
        payload={
            "termsOfService": "https://www.cloudflare.com/terms/",
            "privacyPolicy": "https://www.cloudflare.com/privacypolicy/",
            "acceptTermsOfService": "yes",
            "challengeToken": challenge_token,
            "solution": {"checkpoints": base64.b64encode(b"".join(checkpoints)).decode()},
        },
    ).get("result") or {}
    account = result.get("account") or {}
    account_id = str(account.get("id") or "")
    api_token = str(account.get("apiToken") or "")
    if not account_id or not api_token:
        raise SystemExit("temporary account missing private material")
    return account_id, api_token


def upload(account_id, api_token, script_path):
    probe_token = secrets.token_urlsafe(32)
    metadata = {
        "main_module": "cloudflare_probe.mjs",
        "compatibility_date": "2026-09-11",
        "bindings": [
            {"name": "PROBE", "type": "durable_object_namespace", "class_name": "ProbeCell"},
            {"name": "PROBE_TOKEN", "type": "secret_text", "text": probe_token},
        ],
        "exports": {
            "ProbeCell": {"type": "durable-object", "storage": "sqlite"}
        },
    }
    boundary = "----frontier1-primitive-" + uuid.uuid4().hex
    chunks = []

    def part(name, content, ctype, filename=None):
        chunks.append(f"--{boundary}\r\n".encode())
        disp = f'Content-Disposition: form-data; name="{name}"' + (f'; filename="{filename}"' if filename else "")
        chunks.extend([(disp + "\r\n").encode(), f"Content-Type: {ctype}\r\n\r\n".encode(), content, b"\r\n"])

    part("metadata", json.dumps(metadata, separators=(",", ":"), sort_keys=True).encode(), "application/json")
    part("cloudflare_probe.mjs", script_path.read_bytes(), "application/javascript+module", "cloudflare_probe.mjs")
    chunks.append(f"--{boundary}--\r\n".encode())

    status, raw = call(
        "PUT",
        f"/accounts/{account_id}/workers/scripts/{SCRIPT}",
        token=api_token,
        headers={"content-type": f"multipart/form-data; boundary={boundary}"},
        body=b"".join(chunks),
    )
    try:
        data = json.loads(raw)
    except Exception:
        raise SystemExit(f"probe upload returned non-JSON: HTTP {status}")
    if not (200 <= status < 300 and data.get("success") is True):
        errs = data.get("errors") or []
        msg = "; ".join(str(x.get("message", x)) for x in errs) or f"HTTP {status}"
        raise SystemExit("provider rejected primitive probe upload: " + msg)
    return probe_token


def worker_json(url, *, method="GET", token=None, timeout=30):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140.0 Safari/537.36",
        "Accept": "application/json,text/plain,*/*",
    }
    if token:
        headers["x-probe-token"] = token
    req = urllib.request.Request(url, method=method, headers=headers, data=(b"" if method == "POST" else None))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read()), {"cf_ray": r.headers.get("cf-ray"), "server": r.headers.get("server")}
    except urllib.error.HTTPError as e:
        detail = e.read()[:500].decode("utf-8", "replace")
        raise SystemExit(f"probe endpoint HTTP {e.code}: {detail}")


def route(account_id, api_token):
    enabled = ok_json(
        "POST",
        f"/accounts/{account_id}/workers/scripts/{SCRIPT}/subdomain",
        token=api_token,
        payload={"enabled": True, "previews_enabled": False},
    ).get("result") or {}
    if enabled.get("enabled") is not True:
        raise SystemExit("provider did not enable probe route")
    sub = str((ok_json("GET", f"/accounts/{account_id}/workers/subdomain", token=api_token).get("result") or {}).get("subdomain") or "")
    if not sub or "/" in sub:
        raise SystemExit("workers.dev subdomain missing")
    return f"https://{SCRIPT}.{sub}.workers.dev"


def main():
    root = pathlib.Path(__file__).resolve().parent
    script_path = root / "cloudflare_probe.mjs"
    account_id, api_token = acquire_account()
    probe_token = upload(account_id, api_token, script_path)
    base = route(account_id, api_token)

    health = None
    last = None
    for _ in range(20):
        try:
            health, _ = worker_json(base + "/health")
            break
        except SystemExit as exc:
            last = str(exc)
            time.sleep(2)
        except Exception as exc:
            last = f"{type(exc).__name__}: {exc}"
            time.sleep(2)
    if not health:
        raise SystemExit("probe route failed to become healthy: " + str(last))
    if health.get("canonical_luneacore_body_present") is not False:
        raise SystemExit("primitive probe contaminated by canonical Body")

    start, start_edge = worker_json(base + f"/start?due_after_ms={DUE_AFTER_MS}", method="POST", token=probe_token)
    if start.get("status") != "armed":
        raise SystemExit("probe failed to arm")

    print(json.dumps({
        "primitive_probe_armed": True,
        "canonical_luneacore_body_present": False,
        "due_after_ms": DUE_AFTER_MS,
        "observer_causes_wake": False,
        "start_edge_observed": bool(start_edge.get("cf_ray")),
    }, sort_keys=True), flush=True)

    time.sleep(OBSERVE_AFTER_MS / 1000)

    receipt, receipt_edge = worker_json(base + "/receipt", token=probe_token)
    fired = receipt.get("alarm_fired") is True
    digest_preserved = receipt.get("material_sha256") == start.get("material_sha256")
    no_ingress_before_wake = receipt.get("ingress_count_at_wake") == 1
    due_reached = isinstance(receipt.get("t1_ms"), int) and receipt.get("t1_ms") >= start.get("due_at_ms", 10**30)
    incarnation_changed = bool(receipt.get("r0_evidence")) and bool(receipt.get("r1_evidence")) and receipt.get("r0_evidence") != receipt.get("r1_evidence")

    verdicts = {
        "P1": "OBSERVED" if fired and digest_preserved else "UNKNOWN",
        "P2": "OBSERVED" if fired and digest_preserved and bool(receipt_edge.get("cf_ray")) else "UNKNOWN",
        "P3": "OBSERVED" if fired and due_reached and incarnation_changed else "UNKNOWN",
        "P4": "OBSERVED" if fired and due_reached and no_ingress_before_wake else "UNKNOWN",
        "P5": "OBSERVED" if fired and incarnation_changed else "UNKNOWN",
        "P6": "OBSERVED" if fired and no_ingress_before_wake else "UNKNOWN",
    }
    overall = "PASS_PRIMITIVE_ENVIRONMENT" if all(v == "OBSERVED" for v in verdicts.values()) else "UNRESOLVED_SUBSTRATE"

    safe = {
        "schema": "luneacore-frontier1-substrate-receipt-v1",
        "substrate": "cloudflare-preview-disposable",
        "alarm_fired": fired,
        "digest_preserved": digest_preserved,
        "due_reached": due_reached,
        "ingress_count_at_wake": receipt.get("ingress_count_at_wake"),
        "runtime_incarnation_changed": incarnation_changed,
        "verdicts": verdicts,
        "overall": overall,
        "eligible_for_adapter": overall == "PASS_PRIMITIVE_ENVIRONMENT",
        "awards_gestation": False,
        "awards_birth": False,
        "provider_credentials_retained": False,
        "claim_url_disclosed": False,
    }
    print(json.dumps(safe, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
