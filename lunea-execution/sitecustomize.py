"""D-01 probe-only HTTP diagnostics.

This file does not alter Genesis/Body semantics. It only surfaces the response
body of a provider HTTP error before re-raising it, so a physical provider
failure is falsifiable instead of opaque. Authorization headers are never
printed.
"""
from __future__ import annotations

import sys
import urllib.error
import urllib.request

_original_urlopen = urllib.request.urlopen


def _diagnostic_urlopen(*args, **kwargs):
    try:
        return _original_urlopen(*args, **kwargs)
    except urllib.error.HTTPError as exc:
        try:
            detail = exc.read()[:2000].decode("utf-8", "replace")
        except Exception:
            detail = "<unreadable provider error body>"
        url = getattr(exc, "url", "<unknown-url>")
        print(
            f"D01_PROVIDER_HTTP_ERROR status={exc.code} url={url} body={detail}",
            file=sys.stderr,
            flush=True,
        )
        raise


urllib.request.urlopen = _diagnostic_urlopen
