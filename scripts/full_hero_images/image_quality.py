from __future__ import annotations

import io
import math
import statistics
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image, ImageFilter, ImageOps, ImageStat

from .common import Candidate, OUTPUT_SIZE, TIMEOUT, get_session, reject_text


def shannon_entropy(gray: Image.Image) -> float:
    hist = gray.histogram()
    total = sum(hist) or 1
    entropy = 0.0
    for count in hist:
        if count:
            p = count / total
            entropy -= p * math.log2(p)
    return entropy


def image_photo_metrics(image: Image.Image) -> dict[str, float]:
    sample = image.copy()
    sample.thumbnail((256, 256), Image.Resampling.LANCZOS)
    rgb = sample.convert("RGB")
    gray = rgb.convert("L")
    pixels = list(rgb.getdata())
    total = max(1, len(pixels))
    near_white = sum(1 for r, g, b in pixels if r > 238 and g > 238 and b > 238) / total
    near_black = sum(1 for r, g, b in pixels if r < 15 and g < 15 and b < 15) / total
    rg = [r - g for r, g, _ in pixels]
    yb = [0.5 * (r + g) - b for r, g, b in pixels]
    std_rg = statistics.pstdev(rg) if len(rg) > 1 else 0.0
    std_yb = statistics.pstdev(yb) if len(yb) > 1 else 0.0
    mean_rg = statistics.fmean(rg) if rg else 0.0
    mean_yb = statistics.fmean(yb) if yb else 0.0
    colorfulness = math.sqrt(std_rg ** 2 + std_yb ** 2) + 0.3 * math.sqrt(mean_rg ** 2 + mean_yb ** 2)
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_mean = ImageStat.Stat(edges).mean[0] / 255.0
    return {
        "near_white": near_white,
        "near_black": near_black,
        "entropy": shannon_entropy(gray),
        "colorfulness": colorfulness,
        "edge_mean": edge_mean,
    }


def validate_candidate(candidate: Candidate) -> tuple[bool, float, str, bytes | None]:
    if reject_text(candidate.url) or reject_text(candidate.alt):
        return False, -100.0, "命中文件名/替代文本拒绝规则", None
    response = get_session().get(candidate.url, timeout=TIMEOUT, allow_redirects=True)
    response.raise_for_status()
    content_type = response.headers.get("content-type", "").lower()
    if "svg" in content_type or candidate.url.lower().endswith(".svg"):
        return False, -100.0, "SVG/矢量图不属于真实硬件英雄图", None
    raw = response.content
    if len(raw) < 4_000 or len(raw) > 20_000_000:
        return False, -100.0, f"文件大小不合理 {len(raw)}", None

    try:
        with Image.open(io.BytesIO(raw)) as original:
            image = ImageOps.exif_transpose(original).convert("RGB")
            width, height = image.size
            if min(width, height) < 160:
                return False, -100.0, f"尺寸过小 {width}x{height}", None
            ratio = max(width, height) / max(1, min(width, height))
            if ratio > 4.0:
                return False, -100.0, f"横幅/长图比例异常 {width}x{height}", None

            metrics = image_photo_metrics(image)
            score = candidate.score
            ext = Path(urlparse(candidate.url).path).suffix.lower()
            if ext in {".jpg", ".jpeg"}:
                score += 3.0
            if width * height >= 800 * 500:
                score += 2.0
            elif width * height >= 400 * 300:
                score += 1.0

            if metrics["near_white"] > 0.82 and metrics["colorfulness"] < 24:
                return False, -100.0, f"疑似白底图纸/界面 near_white={metrics['near_white']:.2f}", None
            if metrics["near_white"] > 0.68 and metrics["edge_mean"] > 0.20 and metrics["colorfulness"] < 30:
                return False, -100.0, "疑似线框图/原理图", None
            if metrics["entropy"] < 3.2:
                return False, -100.0, f"图像信息量过低 entropy={metrics['entropy']:.2f}", None
            if metrics["near_black"] > 0.92:
                return False, -100.0, "几乎全黑", None

            score += min(metrics["entropy"], 8.0) * 0.45
            score += min(metrics["colorfulness"], 80.0) * 0.025
            if metrics["near_white"] < 0.55:
                score += 1.0
            if score < 16.0:
                return False, score, f"置信度不足 score={score:.2f}", None

            thumb = image.copy()
            thumb.thumbnail((OUTPUT_SIZE[0] - 8, OUTPUT_SIZE[1] - 8), Image.Resampling.LANCZOS)
            canvas = Image.new("RGB", OUTPUT_SIZE, "white")
            x = (OUTPUT_SIZE[0] - thumb.width) // 2
            y = (OUTPUT_SIZE[1] - thumb.height) // 2
            canvas.paste(thumb, (x, y))
            buffer = io.BytesIO()
            canvas.save(buffer, "JPEG", quality=84, optimize=True)
            reason = (
                f"通过：score={score:.2f}; source={candidate.source}; size={width}x{height}; "
                f"entropy={metrics['entropy']:.2f}; white={metrics['near_white']:.2f}; "
                f"color={metrics['colorfulness']:.1f}"
            )
            return True, score, reason, buffer.getvalue()
    except Exception as exc:
        return False, -100.0, f"图片解析失败 {type(exc).__name__}: {exc}", None
