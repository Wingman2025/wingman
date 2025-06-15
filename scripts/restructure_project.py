"""One-off helper script to reorganise Wingman project files.

Run locally from project root:
    python scripts/restructure_project.py --dry-run  # preview moves
    python scripts/restructure_project.py            # execute moves

Moves legacy root-level files into the new modular structure (backend/, scripts/, tests/).
The script is idempotent and skips moves if destination already exists.

Feel free to adjust paths before executing in production.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Mapping: source relative path -> destination relative path
FILE_MOVES: dict[str, str] = {
    # Back-end
    "models.py": "backend/models/legacy.py",
    "companion_api.py": "backend/api/companion.py",
    # Utility / management scripts
    "seed_master_data.py": "scripts/seed_master_data.py",
    "seed_railway.py": "scripts/seed_railway.py",
    "seed_companion_data.py": "scripts/seed_companion_data.py",
    "run_seed.py": "scripts/run_seed.py",
    "simple_seed.py": "scripts/simple_seed.py",
    "diagnose_migrations.py": "scripts/diagnose_migrations.py",
    "deploy_companion_railway.py": "scripts/deploy_companion_railway.py",
    "create_admin.py": "scripts/create_admin.py",
    # Tests
    "test_api.ps1": "tests/test_api.ps1",
    # Core wrappers
    "app.py": "backend/app.py",
    "agent.py": "backend/services/agent.py",
    "run.py": "scripts/run_dev.py",
}


def move_file(src_rel: str, dst_rel: str, dry: bool = False) -> None:
    src = PROJECT_ROOT / src_rel
    dst = PROJECT_ROOT / dst_rel
    if not src.exists():
        print(f"[skip] {src_rel} not found")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        print(f"[skip] {dst_rel} already exists")
        return
    if dry:
        print(f"[dry] would move {src_rel} -> {dst_rel}")
    else:
        print(f"[move] {src_rel} -> {dst_rel}")
        shutil.move(src, dst)


def main() -> None:
    parser = argparse.ArgumentParser(description="Reorganise Wingman project files")
    parser.add_argument("--dry-run", action="store_true", help="preview without moving")
    args = parser.parse_args()

    for src, dst in FILE_MOVES.items():
        move_file(src, dst, dry=args.dry_run)

    print("\nDone. Review changes, run tests, and commit.")


if __name__ == "__main__":
    main()
