"""Simple decoder for blind bundle metadata (ISSUE-33 helper).

Provides decode_blind_bundle to load manifest and extract bundle IDs.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from generator.blind_bundle_generator import MANIFEST_FILENAME


@dataclass(frozen=True)
class BundleMetadata:
    """Bundle metadata extracted from manifest."""

    bundle_id: str
    manifest_id: str


def decode_blind_bundle(bundle_path: Path) -> BundleMetadata:
    """Load bundle manifest and extract metadata.

    Args:
        bundle_path: Path to the blind bundle directory.

    Returns:
        BundleMetadata with bundle_id and manifest_id.

    Raises:
        RuntimeError: If manifest cannot be loaded or is invalid.
    """
    manifest_path = bundle_path / MANIFEST_FILENAME

    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise RuntimeError(f"bundle manifest could not be loaded: {exc}") from exc

    if not isinstance(manifest, dict):
        raise RuntimeError("bundle manifest must be a YAML mapping")

    bundle_id = manifest.get("bundle_id")
    manifest_id = manifest.get("manifest_id")

    if not bundle_id or not manifest_id:
        raise RuntimeError("manifest missing bundle_id or manifest_id")

    return BundleMetadata(bundle_id=str(bundle_id), manifest_id=str(manifest_id))
