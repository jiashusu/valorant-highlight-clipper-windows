from __future__ import annotations

import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request
import base64
from dataclasses import dataclass

from .build_info import BUILD_DATE, BUILD_SHA


REPO = "jiashusu/valorant-highlight-clipper-windows"
MANIFEST_API_URL = (
    "https://api.github.com/repos/"
    "jiashusu/valorant-highlight-clipper-windows-update/contents/latest.json?ref=main"
)
MANIFEST_RAW_URL = (
    "https://raw.githubusercontent.com/"
    "jiashusu/valorant-highlight-clipper-windows-update/main/latest.json"
)
MANIFEST_URL = MANIFEST_API_URL
REPO_URL = f"https://github.com/{REPO}"
DOWNLOAD_URL = f"{REPO_URL}/releases/latest"


@dataclass
class UpdateResult:
    current_sha: str
    remote_sha: str | None
    update_available: bool
    message: str
    download_url: str = DOWNLOAD_URL

    @property
    def current_short(self) -> str:
        return short_version(self.current_sha)

    @property
    def remote_short(self) -> str:
        return short_version(self.remote_sha or "")


def short_version(value: str) -> str:
    value = (value or "").strip()
    if not value or value == "unknown":
        return "unknown"
    if value.startswith("v"):
        return value
    return value[:7]


def equivalent_version(left: str, right: str | None) -> bool:
    left_short = comparable_version(left)
    right_short = comparable_version(right or "")
    return left_short != "unknown" and left_short == right_short


def comparable_version(value: str) -> str:
    short = short_version(value)
    if short.endswith("-windows"):
        short = short[:-8]
    return short


def hidden_subprocess_kwargs() -> dict:
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    if os.name == "nt" and creationflags:
        return {"creationflags": creationflags}
    return {}


def check_for_update() -> UpdateResult:
    current_tag = BUILD_SHA.strip() or "unknown"
    latest_tag, release_url = fetch_latest_release()
    if current_tag == "unknown":
        return UpdateResult(
            current_sha=current_tag,
            remote_sha=latest_tag,
            update_available=False,
            message=f"当前程序没有打包版本信息。最新版本: {short_version(latest_tag)}",
            download_url=release_url,
        )

    if equivalent_version(current_tag, latest_tag):
        return UpdateResult(
            current_sha=current_tag,
            remote_sha=latest_tag,
            update_available=False,
            message=f"已经是最新版本。当前 {short_version(current_tag)}，打包时间 {BUILD_DATE}",
            download_url=release_url,
        )

    return UpdateResult(
        current_sha=current_tag,
        remote_sha=latest_tag,
        update_available=True,
        message=f"发现新版本。当前 {short_version(current_tag)}，最新 {short_version(latest_tag)}",
        download_url=release_url,
    )


def fetch_latest_release() -> tuple[str, str]:
    errors: list[str] = []
    for fetcher_name, fetcher in (
        ("更新清单", fetch_latest_release_manifest),
        ("GitHub Release", fetch_latest_release_public),
        ("gh CLI", fetch_latest_release_with_gh),
    ):
        try:
            return fetcher()
        except Exception as exc:
            errors.append(f"{fetcher_name}: {exc}")

    raise RuntimeError("无法检查 Windows 版更新。" + "；".join(errors))


def fetch_latest_release_manifest() -> tuple[str, str]:
    errors: list[str] = []
    for manifest_url in (MANIFEST_API_URL, MANIFEST_RAW_URL):
        try:
            payload = fetch_manifest_payload(manifest_url)
            break
        except Exception as exc:
            errors.append(f"{manifest_url}: {exc}")
    else:
        raise RuntimeError("; ".join(errors))

    tag = str(payload.get("tag_name") or payload.get("version") or "").strip()
    if not tag:
        raise RuntimeError("response missing tag_name")
    release_url = str(
        payload.get("download_url") or payload.get("html_url") or DOWNLOAD_URL
    ).strip() or DOWNLOAD_URL
    return tag, release_url


def fetch_manifest_payload(manifest_url: str) -> dict:
    request = urllib.request.Request(
        manifest_url,
        headers={
            "Accept": "application/vnd.github+json, application/json",
            "User-Agent": "ValorantHighlightClipperWindows",
            "Cache-Control": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code}") from exc

    if "content" in payload and payload.get("encoding") == "base64":
        content = str(payload["content"]).replace("\n", "")
        return json.loads(base64.b64decode(content).decode("utf-8"))
    return payload


def fetch_latest_release_public() -> tuple[str, str]:
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/releases/latest",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "ValorantHighlightClipperWindows",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code}") from exc

    tag = str(payload.get("tag_name", "")).strip()
    if not tag:
        raise RuntimeError("response missing tag_name")
    release_url = str(payload.get("html_url", DOWNLOAD_URL)).strip() or DOWNLOAD_URL
    return tag, release_url


def fetch_latest_release_with_gh() -> tuple[str, str]:
    gh_path = find_gh()
    if not gh_path:
        raise RuntimeError("未找到 gh 命令")

    result = subprocess.run(
        [gh_path, "api", f"repos/{REPO}/releases/latest"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10,
        env=github_cli_env(),
        **hidden_subprocess_kwargs(),
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "gh api failed")

    payload = json.loads(result.stdout)
    tag = str(payload.get("tag_name", "")).strip()
    if not tag:
        raise RuntimeError("gh response missing tag_name")
    release_url = str(payload.get("html_url", DOWNLOAD_URL)).strip() or DOWNLOAD_URL
    return tag, release_url


def find_gh() -> str | None:
    candidates = [
        shutil.which("gh.exe"),
        shutil.which("gh"),
        r"C:\Program Files\GitHub CLI\gh.exe",
        "/opt/homebrew/bin/gh",
        "/usr/local/bin/gh",
        "/usr/bin/gh",
    ]
    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return candidate
    return None


def github_cli_env() -> dict[str, str]:
    env = os.environ.copy()
    extra_paths = [
        r"C:\Program Files\GitHub CLI",
        "/opt/homebrew/bin",
        "/usr/local/bin",
        "/usr/bin",
        "/bin",
        "/usr/sbin",
        "/sbin",
    ]
    env["PATH"] = os.pathsep.join(extra_paths + [env.get("PATH", "")])
    return env
