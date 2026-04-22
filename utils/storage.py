"""
Cloudflare R2 Storage sync layer for Streamlit Cloud persistence.

Strategy:
  - On container startup: sync_to_local() pulls all objects from R2 to disk.
  - On every file write: upload() pushes the file to R2 after the local write.
  - On every file delete: delete() removes the object from R2.
  - XeLaTeX compilation is unchanged — it always operates on local files.

Configuration (.streamlit/secrets.toml):
    [r2]
    enabled    = true
    account_id = "<your-cloudflare-account-id>"
    access_key = "<your-r2-access-key-id>"
    secret_key = "<your-r2-secret-access-key>"
    bucket     = "barometer"

Set enabled = false (or omit the section) for local development — all calls
become no-ops and the app behaves exactly as it did before.
"""
from __future__ import annotations

import logging
import streamlit as st
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

_log = logging.getLogger("eces_storage")

# Prefixes never downloaded at startup — reports are regenerated on demand;
# templates/ placeholder PNGs are recreated by ensure_template_charts().
_SYNC_SKIP_PREFIXES = frozenset(["reports/", "templates/"])

# For issues/ only pull the tiny metadata.json at startup so the issue list
# renders correctly. The full archive (charts, content, overrides) is fetched
# on demand via sync_issue() when the user actually loads an issue.
_ISSUES_METADATA_ONLY = True


# ── Config helpers ────────────────────────────────────────────────────────────

def _enabled() -> bool:
    try:
        return st.secrets.get("r2", {}).get("enabled", False)
    except Exception:
        return False


@st.cache_resource
def _client():
    """Return a cached boto3 S3 client pointed at Cloudflare R2."""
    import boto3
    from botocore.config import Config
    cfg = st.secrets["r2"]
    return boto3.client(
        "s3",
        endpoint_url=f"https://{cfg['account_id']}.r2.cloudflarestorage.com",
        aws_access_key_id=cfg["access_key"],
        aws_secret_access_key=cfg["secret_key"],
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


def _bucket_name() -> str:
    return st.secrets["r2"]["bucket"]


def _base_dir() -> Path:
    from utils.config import BASE_DIR
    return Path(BASE_DIR).resolve()


def _key(local_path: str | Path) -> str:
    """Convert an absolute local path to a relative cloud storage key."""
    return str(Path(local_path).resolve().relative_to(_base_dir())).replace("\\", "/")


def _content_type(path: str | Path) -> str:
    ext = Path(path).suffix.lower().lstrip(".")
    return {
        "png":  "image/png",
        "jpg":  "image/jpeg",
        "jpeg": "image/jpeg",
        "pdf":  "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "json": "application/json",
        "tex":  "text/plain",
        "log":  "text/plain",
    }.get(ext, "application/octet-stream")


# ── Core operations ───────────────────────────────────────────────────────────

def upload(local_path: str | Path):
    """Upload a single local file to R2 (upsert) in a background thread."""
    if not _enabled():
        return
    # Fire-and-forget: the file is already saved locally; cloud sync is async.
    threading.Thread(target=_upload_sync, args=(local_path,), daemon=True).start()


def _upload_sync(local_path: str | Path):
    """Blocking upload — runs in a background thread so the UI is never blocked."""
    try:
        key = _key(local_path)
        with open(local_path, "rb") as f:
            _client().put_object(
                Bucket=_bucket_name(),
                Key=key,
                Body=f.read(),
                ContentType=_content_type(local_path),
            )
    except Exception as e:
        _log.warning("Upload failed for %s: %s", local_path, e)


def upload_bytes(data: bytes, key: str, content_type: str = "application/octet-stream"):
    """Upload raw bytes to a specific cloud key."""
    if not _enabled():
        return
    try:
        _client().put_object(
            Bucket=_bucket_name(),
            Key=key,
            Body=data,
            ContentType=content_type,
        )
    except Exception as e:
        _log.warning("Upload bytes failed for key %s: %s", key, e)


def download(key: str, local_path: str | Path):
    """Download an object from R2 to a local path, creating parent dirs."""
    if not _enabled():
        return
    try:
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)
        response = _client().get_object(Bucket=_bucket_name(), Key=key)
        data = response["Body"].read()
        with open(local_path, "wb") as f:
            f.write(data)
    except Exception as e:
        _log.warning("Download failed for key %s: %s", key, e)


def delete(local_path_or_key: str | Path):
    """Delete a single object from R2."""
    if not _enabled():
        return
    try:
        p = Path(local_path_or_key)
        key = _key(p) if p.is_absolute() else str(local_path_or_key).replace("\\", "/")
        _client().delete_object(Bucket=_bucket_name(), Key=key)
    except Exception as e:
        _log.warning("Delete failed for %s: %s", local_path_or_key, e)


def delete_prefix(prefix: str):
    """Delete all objects under a folder prefix (e.g. 'issues/en/77')."""
    if not _enabled():
        return
    try:
        keys = _list_all_keys(prefix.rstrip("/"))
        if not keys:
            return
        # S3 batch delete supports up to 1000 keys per request
        for i in range(0, len(keys), 1000):
            batch = keys[i : i + 1000]
            _client().delete_objects(
                Bucket=_bucket_name(),
                Delete={"Objects": [{"Key": k} for k in batch]},
            )
    except Exception as e:
        _log.warning("Delete prefix failed for %s: %s", prefix, e)


def upload_dir(local_dir: str | Path, cloud_prefix: str | None = None):
    """Recursively upload all files in a local directory."""
    if not _enabled():
        return
    for path in Path(local_dir).rglob("*"):
        if not path.is_file():
            continue
        try:
            if cloud_prefix:
                rel = str(path.relative_to(local_dir)).replace("\\", "/")
                key = cloud_prefix.rstrip("/") + "/" + rel
            else:
                key = _key(path)
            with open(path, "rb") as f:
                _client().put_object(
                    Bucket=_bucket_name(),
                    Key=key,
                    Body=f.read(),
                    ContentType=_content_type(path),
                )
        except Exception as e:
            _log.warning("Upload dir failed for %s: %s", path, e)


# ── Directory listing ─────────────────────────────────────────────────────────

def _list_all_keys(prefix: str = "") -> list[str]:
    """List all object keys under a prefix using paginated S3 listing."""
    keys: list[str] = []
    try:
        paginator = _client().get_paginator("list_objects_v2")
        kwargs: dict = {"Bucket": _bucket_name()}
        if prefix:
            kwargs["Prefix"] = prefix.rstrip("/") + "/"
        for page in paginator.paginate(**kwargs):
            for obj in page.get("Contents", []):
                keys.append(obj["Key"])
    except Exception as e:
        _log.warning("List keys failed for prefix '%s': %s", prefix, e)
    return keys


def _list_all_key_sizes(prefix: str = "") -> dict[str, int]:
    """List all objects under a prefix, returning {key: size_bytes}.

    The size is used by sync_to_local() to skip files whose local copy already
    matches the cloud byte count, avoiding redundant downloads on warm containers.
    """
    result: dict[str, int] = {}
    try:
        paginator = _client().get_paginator("list_objects_v2")
        kwargs: dict = {"Bucket": _bucket_name()}
        if prefix:
            kwargs["Prefix"] = prefix.rstrip("/") + "/"
        for page in paginator.paginate(**kwargs):
            for obj in page.get("Contents", []):
                result[obj["Key"]] = obj["Size"]
    except Exception as e:
        _log.warning("List key sizes failed for prefix '%s': %s", prefix, e)
    return result


# ── Startup sync ──────────────────────────────────────────────────────────────

def sync_issue(lang: str, issue_num: str | int):
    """Download a full archived issue from R2 on demand.

    Called by issue_manager.load_issue() when the local archive is incomplete
    (e.g. only metadata.json was fetched at startup). Already-present files
    are skipped so repeated calls are cheap.
    """
    if not _enabled():
        return
    prefix = f"issues/{lang}/{issue_num}"
    base = _base_dir()
    for key in _list_all_keys(prefix):
        local_path = base / key
        if local_path.exists():
            continue  # already downloaded — skip
        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            response = _client().get_object(Bucket=_bucket_name(), Key=key)
            local_path.write_bytes(response["Body"].read())
        except Exception as e:
            _log.warning("sync_issue failed for %s: %s", key, e)


def sync_to_local():
    """
    Download essential R2 objects to the local filesystem (called once at startup).
    R2 always wins over git-cloned defaults so user-saved data is restored.
    Safe to overwrite because this function runs only once per session (guarded by
    _startup_done in session state), so in-session writes are never clobbered.

    Egress optimisations applied here:
      • _SYNC_SKIP_PREFIXES  — reports/ and templates/ are excluded entirely
        (reports are regenerated; template placeholder PNGs are recreated locally).
      • _ISSUES_METADATA_ONLY — only issues/*/metadata.json is fetched so the
        issue list renders correctly; full archives are pulled on demand via sync_issue().
      • Size-based deduplication — a file whose local byte count already matches
        the cloud size is skipped, saving redundant downloads on warm containers.

    Downloads are parallelised (up to 8 concurrent connections) to minimise wait time.
    """
    if not _enabled():
        return

    # Test connectivity before attempting a full sync.
    try:
        _client().list_objects_v2(Bucket=_bucket_name(), MaxKeys=1)
    except Exception:
        st.warning(
            "⚠️ **Cloud storage is unreachable.** The R2 bucket could not be accessed. "
            "Check your API credentials and bucket name in secrets.toml. "
            "The app is running on local files only until the connection is restored.",
            icon="⚠️",
        )
        return

    base = _base_dir()
    all_objects = _list_all_key_sizes()  # {key: size_bytes}

    def _should_sync(key: str) -> bool:
        for prefix in _SYNC_SKIP_PREFIXES:
            if key.startswith(prefix):
                return False
        if _ISSUES_METADATA_ONLY and key.startswith("issues/"):
            return key.endswith("/metadata.json")
        return True

    filtered = {k: v for k, v in all_objects.items() if _should_sync(k)}

    def _download_one(key_size: tuple):
        key, cloud_size = key_size
        local_path = base / key
        # Skip when the local file already has the exact same byte count
        if cloud_size > 0 and local_path.exists() and local_path.stat().st_size == cloud_size:
            return
        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            response = _client().get_object(Bucket=_bucket_name(), Key=key)
            local_path.write_bytes(response["Body"].read())
        except Exception as e:
            _log.warning("Startup download failed for %s: %s", key, e)

    # Parallel downloads — dramatically faster than sequential for many files
    with ThreadPoolExecutor(max_workers=8) as pool:
        pool.map(_download_one, filtered.items())
