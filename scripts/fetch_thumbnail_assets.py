#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from PIL import Image, ImageDraw

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/150 Safari/537.36"
_thread_local = threading.local()


def get_session() -> requests.Session:
    session = getattr(_thread_local, "session", None)
    if session is None:
        session = requests.Session()
        session.headers.update({"User-Agent": UA, "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8"})
        _thread_local.session = session
    return session


def placeholder(path: Path, size: tuple[int, int]) -> None:
    image = Image.new("RGB", size, "#E5E7EB")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, size[0] - 1, size[1] - 1), outline="#9CA3AF", width=2)
    draw.line((12, size[1] - 14, size[0] // 2, size[1] // 2, size[0] - 14, size[1] - 20), fill="#9CA3AF", width=3)
    draw.ellipse((size[0] - 30, 12, size[0] - 18, 24), fill="#9CA3AF")
    image.save(path, "JPEG", quality=76, optimize=True)


def fetch_one(url: str, images_dir: Path, size: tuple[int, int]) -> dict[str, object]:
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()
    filename = f"{digest}.jpg"
    target = images_dir / filename
    if target.exists() and target.stat().st_size > 0:
        return {"url": url, "file": f"images/{filename}", "ok": True, "cached": True}

    error = ""
    for attempt in range(3):
        try:
            response = get_session().get(url, timeout=(12, 25), allow_redirects=True)
            response.raise_for_status()
            if len(response.content) > 8_000_000:
                raise ValueError("image too large")
            with Image.open(io.BytesIO(response.content)) as source:
                source.load()
                if source.mode in ("RGBA", "LA"):
                    canvas = Image.new("RGB", source.size, "white")
                    alpha = source.getchannel("A") if "A" in source.getbands() else None
                    canvas.paste(source.convert("RGB"), mask=alpha)
                    source = canvas
                else:
                    source = source.convert("RGB")
                source.thumbnail(size, Image.Resampling.LANCZOS)
                canvas = Image.new("RGB", size, "white")
                x = (size[0] - source.width) // 2
                y = (size[1] - source.height) // 2
                canvas.paste(source, (x, y))
                canvas.save(target, "JPEG", quality=72, optimize=True, progressive=False)
            return {
                "url": url,
                "file": f"images/{filename}",
                "ok": True,
                "bytes": target.stat().st_size,
                "content_type": response.headers.get("content-type", ""),
            }
        except Exception as exc:  # noqa: BLE001
            error = f"{type(exc).__name__}: {exc}"
    return {"url": url, "file": "placeholder.jpg", "ok": False, "error": error[:500]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--workers", type=int, default=32)
    parser.add_argument("--width", type=int, default=96)
    parser.add_argument("--height", type=int, default=72)
    args = parser.parse_args()

    out = Path(args.out)
    images_dir = out / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    size = (args.width, args.height)
    placeholder(out / "placeholder.jpg", size)

    urls: list[str] = []
    with open(args.csv, encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            url = (row.get("thumbnail_url") or "").strip()
            if url:
                urls.append(url)
    unique_urls = list(dict.fromkeys(urls))
    print(f"rows={len(urls)} unique_urls={len(unique_urls)} workers={args.workers}", flush=True)

    results: dict[str, dict[str, object]] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(fetch_one, url, images_dir, size): url for url in unique_urls}
        for index, future in enumerate(as_completed(futures), start=1):
            url = futures[future]
            try:
                item = future.result()
            except Exception as exc:  # noqa: BLE001
                item = {"url": url, "file": "placeholder.jpg", "ok": False, "error": f"worker: {exc}"}
            results[url] = item
            if index % 100 == 0 or index == len(unique_urls):
                ok = sum(bool(value.get("ok")) for value in results.values())
                print(f"processed={index}/{len(unique_urls)} ok={ok} failed={index-ok}", flush=True)

    ordered = {url: results[url] for url in unique_urls}
    (out / "mapping.json").write_text(json.dumps(ordered, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {
        "rows": len(urls),
        "unique_urls": len(unique_urls),
        "downloaded": sum(bool(value.get("ok")) for value in ordered.values()),
        "failed": sum(not bool(value.get("ok")) for value in ordered.values()),
        "width": args.width,
        "height": args.height,
        "image_files": len(list(images_dir.glob("*.jpg"))),
    }
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
