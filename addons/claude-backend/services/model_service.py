"""Model service: manage model blocklists and NVIDIA model caching."""

import json
import os
import logging
import time
from typing import Optional

try:
    import model_catalog
    MODEL_CATALOG_AVAILABLE = True
except ImportError:
    MODEL_CATALOG_AVAILABLE = False

logger = logging.getLogger(__name__)

# ---- NVIDIA Model Blocklist ----

# NVIDIA models that are known to fail (API errors, etc.)
NVIDIA_MODEL_BLOCKLIST: set[str] = set()

# NVIDIA models that have been successfully chat-tested (per current key)
NVIDIA_MODEL_TESTED_OK: set[str] = set()

MODEL_BLOCKLIST_FILE = "/config/amira/model_blocklist.json"

# Cache for NVIDIA /v1/models discovery (to keep UI in sync with what's available for the current key)
_NVIDIA_MODELS_CACHE: dict[str, object] = {"ts": 0.0, "models": []}
_NVIDIA_MODELS_CACHE_TTL_SECONDS = 10 * 60


def load_model_blocklists() -> None:
    """Load persistent NVIDIA model blocklist from disk."""
    global NVIDIA_MODEL_BLOCKLIST, NVIDIA_MODEL_TESTED_OK
    try:
        if os.path.isfile(MODEL_BLOCKLIST_FILE):
            with open(MODEL_BLOCKLIST_FILE, "r") as f:
                data = json.load(f) or {}
            nvidia = data.get("nvidia") or []

            # Backward compatible formats:
            # - {"nvidia": [..]} (legacy blocked-only)
            # - {"nvidia": {"blocked": [..], "tested_ok": [..]}}
            if isinstance(nvidia, dict):
                blocked = nvidia.get("blocked") or []
                tested_ok = nvidia.get("tested_ok") or []
                if isinstance(blocked, list):
                    NVIDIA_MODEL_BLOCKLIST.update([m for m in blocked if isinstance(m, str) and m.strip()])
                if isinstance(tested_ok, list):
                    NVIDIA_MODEL_TESTED_OK.update([m for m in tested_ok if isinstance(m, str) and m.strip()])
            elif isinstance(nvidia, list):
                NVIDIA_MODEL_BLOCKLIST.update([m for m in nvidia if isinstance(m, str) and m.strip()])
            if NVIDIA_MODEL_BLOCKLIST or NVIDIA_MODEL_TESTED_OK:
                logger.debug(
                    f"Loaded NVIDIA model lists: blocked={len(NVIDIA_MODEL_BLOCKLIST)}, tested_ok={len(NVIDIA_MODEL_TESTED_OK)}"
                )
    except Exception as e:
        logger.warning(f"Could not load model blocklists: {e}")


def save_model_blocklists() -> None:
    """Persist NVIDIA model blocklist to disk."""
    try:
        os.makedirs(os.path.dirname(MODEL_BLOCKLIST_FILE), exist_ok=True)
        payload = {
            "nvidia": {
                "blocked": sorted(NVIDIA_MODEL_BLOCKLIST),
                "tested_ok": sorted(NVIDIA_MODEL_TESTED_OK),
            },
        }
        with open(MODEL_BLOCKLIST_FILE, "w") as f:
            json.dump(payload, f, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"Could not save model blocklists: {e}")


def mark_nvidia_model_tested_ok(model_id: str) -> None:
    """Mark a NVIDIA model as successfully tested and persist it."""
    if not isinstance(model_id, str) or not model_id.strip():
        return
    model_id = model_id.strip()
    if model_id in NVIDIA_MODEL_BLOCKLIST:
        return
    NVIDIA_MODEL_TESTED_OK.add(model_id)
    save_model_blocklists()


def blocklist_nvidia_model(model_id: str) -> None:
    """Add a model to NVIDIA blocklist, persist it, and drop it from cache."""
    if not isinstance(model_id, str) or not model_id.strip():
        return
    model_id = model_id.strip()
    NVIDIA_MODEL_BLOCKLIST.add(model_id)
    if model_id in NVIDIA_MODEL_TESTED_OK:
        NVIDIA_MODEL_TESTED_OK.discard(model_id)
    try:
        cached = _NVIDIA_MODELS_CACHE.get("models") or []
        if isinstance(cached, list) and model_id in cached:
            _NVIDIA_MODELS_CACHE["models"] = [m for m in cached if m != model_id]
    except Exception:
        pass
    save_model_blocklists()


def blocklist_model(provider: str, model_id: str) -> None:
    """Add a model to the blocklist for a provider.

    NVIDIA: persisted via the dedicated NVIDIA_MODEL_BLOCKLIST mechanism.
    All other providers: delegated to ModelCatalog.remove_model() which
    handles in-memory removal, refresh-survival, and disk persistence.
    """
    if not isinstance(model_id, str) or not model_id.strip():
        return
    model_id = model_id.strip()
    if provider == "nvidia":
        blocklist_nvidia_model(model_id)
    else:
        if MODEL_CATALOG_AVAILABLE:
            model_catalog.get_catalog().remove_model(provider, model_id)


def _fetch_nvidia_models_live(nvidia_api_key: str) -> Optional[list[str]]:
    """Fetch available NVIDIA models from the OpenAI-compatible endpoint.

    Returns a sorted list of model IDs, or None if unavailable.
    """
    if not nvidia_api_key:
        return None
    try:
        import requests
        url = "https://integrate.api.nvidia.com/v1/models"
        headers = {"Authorization": f"Bearer {nvidia_api_key}"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json() if resp.content else {}
        models: list[str] = []
        for item in (data.get("data") or []):
            if isinstance(item, dict):
                mid = item.get("id") or item.get("model")
                if isinstance(mid, str) and mid.strip():
                    models.append(mid.strip())
        models = sorted(set(models))
        return models or None
    except Exception as e:
        logger.warning(f"NVIDIA: unable to fetch /v1/models ({type(e).__name__}): {e}")
        return None


def get_nvidia_models_cached(nvidia_api_key: str) -> Optional[list[str]]:
    """Return cached NVIDIA model IDs, refreshing periodically."""
    if not nvidia_api_key:
        return None

    now = time.time()
    ts = float(_NVIDIA_MODELS_CACHE.get("ts") or 0.0)
    cached_models = _NVIDIA_MODELS_CACHE.get("models") or []
    if cached_models and (now - ts) < _NVIDIA_MODELS_CACHE_TTL_SECONDS:
        if NVIDIA_MODEL_BLOCKLIST:
            return [m for m in list(cached_models) if m not in NVIDIA_MODEL_BLOCKLIST]
        return list(cached_models)

    live = _fetch_nvidia_models_live(nvidia_api_key)
    if live:
        _NVIDIA_MODELS_CACHE["ts"] = now
        _NVIDIA_MODELS_CACHE["models"] = list(live)
        if NVIDIA_MODEL_BLOCKLIST:
            return [m for m in live if m not in NVIDIA_MODEL_BLOCKLIST]
        return live

    # Fallback to stale cache if present
    if cached_models:
        if NVIDIA_MODEL_BLOCKLIST:
            return [m for m in list(cached_models) if m not in NVIDIA_MODEL_BLOCKLIST]
        return list(cached_models)
    return None
