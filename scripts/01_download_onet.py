"""Stage 1a: get one pinned release of the O*NET database and record where it came from.

Why this script exists
----------------------
Clicking "download" works once. A script means anyone can rebuild the same raw
layer, and the manifest proves which release and which exact file you used.

Usage (run from the project root)
---------------------------------
    python scripts/01_download_onet.py
    python scripts/01_download_onet.py --zip path/to/db_31_0_csv.zip

Use --zip if a network blocks the script: download the ZIP in your browser, then
point this script at it. Everything after the download step is identical.
"""

import argparse
import hashlib
import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import requests

# Pin the release. O*NET updates quarterly, so never point at "latest" silently.
# To upgrade: change these two values, rerun, and review what changed.
ONET_VERSION = "31.0"
ONET_URL = "https://www.onetcenter.org/dl_files/database/db_31_0_csv.zip"

# Resolve paths from this file, so the script works from any working directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "onet" / ONET_VERSION


def download(url: str, destination: Path) -> None:
    """Stream the file to disk in chunks, so a large file never fills memory."""
    temporary = destination.with_suffix(".part")
    headers = {"User-Agent": "workforce-skills-intelligence (portfolio project)"}
    with requests.get(url, stream=True, timeout=60, headers=headers) as response:
        response.raise_for_status()  # Turn a 403 or 404 into a clear error.
        with temporary.open("wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                file.write(chunk)
    # Rename only after success, so a failed run never leaves a "complete" ZIP.
    temporary.replace(destination)


def sha256_of(path: Path) -> str:
    """Return a fingerprint of the file. Same file, same fingerprint."""
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_csvs(zip_path: Path, destination: Path) -> int:
    """Flatten every CSV into one folder, whatever folders the ZIP uses inside."""
    count = 0
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            name = Path(member.filename).name  # Dropping folders also blocks path tricks.
            if member.is_dir() or not name.lower().endswith(".csv"):
                continue
            (destination / name).write_bytes(archive.read(member))
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--zip", type=Path, help="Use a ZIP you already downloaded.")
    parser.add_argument("--url", default=ONET_URL, help="Override the download URL.")
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = RAW_DIR / "db_31_0_csv.zip"

    try:
        if args.zip:
            if not args.zip.is_file():
                print(f"ERROR: file not found: {args.zip}")
                return 1
            zip_path.write_bytes(args.zip.read_bytes())
            source = f"manual copy of {args.zip.name}; published at {ONET_URL}"
        elif zip_path.exists():
            print(f"Using the ZIP already on disk: {zip_path}")
            source = args.url
        else:
            print(f"Downloading O*NET {ONET_VERSION} ...")
            download(args.url, zip_path)
            source = args.url

        file_count = extract_csvs(zip_path, RAW_DIR)
    except requests.RequestException as error:
        print(f"ERROR: download failed: {error}")
        print("Download the ZIP in your browser, then rerun with --zip <path>.")
        return 1
    except zipfile.BadZipFile:
        zip_path.unlink(missing_ok=True)  # Remove the bad file so a rerun starts clean.
        print("ERROR: that file is not a valid ZIP. It may be a blocked-page response.")
        return 1

    if file_count == 0:
        print("ERROR: the ZIP contained no CSV files.")
        return 1

    manifest = {
        "dataset": "O*NET Database",
        "version": ONET_VERSION,
        "source": source,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "zip_sha256": sha256_of(zip_path),
        "csv_file_count": file_count,
        "license": "CC BY 4.0",
    }
    (RAW_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Extracted {file_count} CSV files to {RAW_DIR}")
    print("Wrote manifest.json. Next: python scripts/02_verify_onet.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
