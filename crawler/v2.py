#!/usr/bin/env python3
"""Balanced 10k public open-hardware commercial-opportunity crawler.

V2 keeps the detailed source-specific collectors from main.py, adds a much
broader sitemap/listing discovery layer, applies per-row evidence-based scores,
and selects the final corpus with source concentration caps.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import statistics
import sys
import time
import urllib.parse
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import timezone
from pathlib import Path
from typing import Any, Iterable

from dateutil import parser as dateparser

import main as base


@dataclass(frozen=True)
class FastSource:
    name: str
    seeds: tuple[str, ...]
    patterns: tuple[str, ...]
    sitemaps: tuple[str, ...]
    quota: int = 420
    detail_rows: int = 18


# Existing platforms receive larger quotas than V1.  Extra sources broaden the
# pool; a failed/blocked platform is retained in source_status.csv.
FAST_SOURCES: tuple[FastSource, ...] = tuple(
    FastSource(s.name, s.seeds, s.patterns, s.sitemap, max(220, min(650, s.max_rows * 12)), 18)
    for s in base.WEB_SOURCES
) + (
    FastSource("Maker Pro", ("https://maker.pro/projects",), (r"maker\.pro/.+/projects/.+",), ("https://maker.pro/sitemap.xml",), 420, 20),
    FastSource("IoT Design Pro", ("https://iotdesignpro.com/projects",), (r"iotdesignpro\.com/projects/.+",), ("https://iotdesignpro.com/sitemap.xml",), 380, 16),
    FastSource("Electronics For You Projects", ("https://www.electronicsforu.com/electronics-projects",), (r"electronicsforu\.com/electronics-projects/.+",), ("https://www.electronicsforu.com/sitemap_index.xml",), 420, 16),
    FastSource("Elektor Labs", ("https://www.elektormagazine.com/labs",), (r"elektormagazine\.com/labs/.+",), ("https://www.elektormagazine.com/sitemap.xml",), 380, 18),
    FastSource("OpenBuilds", ("https://openbuilds.com/builds/",), (r"openbuilds\.com/builds/.+",), ("https://openbuilds.com/sitemap.xml",), 420, 16),
    FastSource("Wikifactory", ("https://wikifactory.com/projects",), (r"wikifactory\.com/@?[^/]+/[^/]+",), ("https://wikifactory.com/sitemap.xml",), 420, 14),
    FastSource("Appropedia Open Hardware", ("https://www.appropedia.org/Category:Open_source_hardware",), (r"appropedia\.org/.+",), ("https://www.appropedia.org/sitemap.xml",), 360, 14),
    FastSource("Fabble", ("https://fabble.cc/",), (r"fabble\.cc/.+/[^/]+",), ("https://fabble.cc/sitemap.xml",), 360, 14),
    FastSource("OSH Park Shared Projects", ("https://oshpark.com/shared_projects",), (r"oshpark\.com/shared_projects/.+",), ("https://oshpark.com/sitemap.xml",), 420, 16),
    FastSource("Pimoroni Learn", ("https://learn.pimoroni.com/",), (r"learn\.pimoroni\.com/article/.+",), ("https://learn.pimoroni.com/sitemap.xml",), 360, 14),
    FastSource("The Pi Hut Tutorials", ("https://thepihut.com/blogs/raspberry-pi-tutorials",), (r"thepihut\.com/blogs/raspberry-pi-tutorials/.+",), ("https://thepihut.com/sitemap.xml",), 360, 14),
    FastSource("micro:bit Projects", ("https://microbit.org/projects/",), (r"microbit\.org/projects/.+",), ("https://microbit.org/sitemap.xml",), 360, 14),
    FastSource("NVIDIA Jetson Projects", ("https://developer.nvidia.com/embedded/community/jetson-projects",), (r"developer\.nvidia\.com/embedded/community/jetson-projects/.+",), ("https://developer.nvidia.com/sitemap.xml",), 300, 12),
    FastSource("Open Source Ecology", ("https://wiki.opensourceecology.org/wiki/Category:Machines",), (r"wiki\.opensourceecology\.org/wiki/.+",), ("https://wiki.opensourceecology.org/sitemap.xml",), 320, 12),
    FastSource("CNX Software Hardware", ("https://www.cnx-software.com/tag/open-source-hardware/",), (r"cnx-software\.com/20\d\d/.+",), ("https://www.cnx-software.com/sitemap_index.xml",), 360, 14),
    FastSource("HackMakeMod Projects", ("https://hackmakemod.com/projects/",), (r"hackmakemod\.com/projects/.+",), ("https://hackmakemod.com/sitemap.xml",), 300, 12),
    FastSource("Maker.io Projects", ("https://www.digikey.com/en/maker/projects",), (r"digikey\.com/en/maker/projects/.+",), ("https://www.digikey.com/sitemap.xml",), 350, 14),
    FastSource("DigiKey TechForum Projects", ("https://forum.digikey.com/c/projects/",), (r"forum\.digikey\.com/t/.+",), ("https://forum.digikey.com/sitemap.xml",), 300, 12),
    FastSource("Arduino Blog Projects", ("https://blog.arduino.cc/category/projects/",), (r"blog\.arduino\.cc/20\d\d/.+",), ("https://blog.arduino.cc/sitemap_index.xml",), 380, 14),
    FastSource("Raspberry Pi Blog Projects", ("https://www.raspberrypi.com/news/tag/projects/",), (r"raspberrypi\.com/news/.+",), ("https://www.raspberrypi.com/sitemap_index.xml",), 380, 14),
)


def matches(source: FastSource, url: str) -> bool:
    return any(re.search(pattern, url, re.I) for pattern in source.patterns)


def extract_date_from_url(url: str) -> str:
    match = re.search(r"/(20(?:2[1-9]|3\d))/(0?[1-9]|1[0-2])/(0?[1-9]|[12]\d|3[01])(?:/|$)", url)
    if match:
        return f"{int(match.group(1)):04d}-{int(match.group(2)):02d}-{int(match.group(3)):02d}"
    match = re.search(r"/(20(?:2[1-9]|3\d))/(0?[1-9]|1[0-2])(?:/|$)", url)
    if match:
        return f"{int(match.group(1)):04d}-{int(match.group(2)):02d}-01"
    return ""


def sitemap_discover(source: FastSource) -> list[str]:
    candidates: list[str] = []
    queue = list(source.sitemaps)
    visited: set[str] = set()
    # More sitemap branches than V1, but bounded to avoid hammering sites.
    while queue and len(visited) < 36 and len(candidates) < source.quota * 5:
        sitemap = queue.pop(0)
        if sitemap in visited:
            continue
        visited.add(sitemap)
        try:
            response = base.HTTP.get(sitemap, timeout=45)
            if response.status_code >= 400:
                continue
            urls, child_maps = base.xml_urls(response.content)
            for child in child_maps[:24]:
                if child not in visited:
                    queue.append(child)
            for url in urls:
                normalized = base.canonical_url(url)
                if matches(source, normalized):
                    candidates.append(normalized)
                    if len(candidates) >= source.quota * 5:
                        break
        except Exception:
            continue

    for seed in source.seeds:
        try:
            response = base.HTTP.get(seed, timeout=40)
            if response.ok:
                candidates.extend(base.collect_links(response.text, seed, source.patterns))
        except Exception:
            continue
    return list(dict.fromkeys(candidates))


def generic_record(source: FastSource, url: str) -> base.Record:
    name = base.slug_title(url)
    published = extract_date_from_url(url)
    host = urllib.parse.urlsplit(url).netloc
    return base.make_record(
        source.name,
        url,
        name,
        thumbnail_url=f"https://www.google.com/s2/favicons?domain={host}&sz=128",
        thumbnail_type="平台图",
        published_date=published,
        description=f"收录于{source.name}的公开硬件、电子制作或可制造项目页面；详细设计文件、许可与市场数据待二次核验。",
        keywords="open hardware, electronics, maker project",
        hardware_license="页面待核验",
        software_license="页面待核验",
        open_source_completeness="公开项目页；原理图、PCB、BOM、固件和外壳完整度待核验",
        market_validation=f"进入{source.name}公开项目/教程/商品目录",
    )


def fetch_fast_source(source: FastSource) -> list[base.Record]:
    urls = sitemap_discover(source)
    records: list[base.Record] = []
    for index, url in enumerate(urls[: source.quota * 2]):
        record = None
        if index < source.detail_rows:
            record = base.parse_detail(source.name, url)
        if record is None:
            record = generic_record(source, url)
        records.append(record)
        if len(records) >= source.quota:
            break
        if index < source.detail_rows:
            time.sleep(0.08)
    return records


def score_v2(record: base.Record) -> None:
    """Per-row deterministic score from the evidence available on that row.

    This is not a human review. Every record is evaluated separately using its
    own category, support signal, recency, platform, description, image,
    licensing/completeness evidence, commercial keywords and risk profile.
    """
    base.enrich_record(record)
    text = " ".join((record.name, record.description, record.keywords, record.market_validation)).lower()

    demand = 4.6
    market = 3.7
    maturity = 3.4
    differentiation = 4.6
    virality = 4.0
    skill_fit = 7.2

    category_demand = {
        "测试测量/工程工具": 1.5,
        "电子礼物/徽章/挂件": 1.2,
        "键盘/宏键盘/控制器": 1.2,
        "音频/音乐设备": 1.0,
        "传感器/环境监测": 0.8,
        "智能家居/物联网": 0.8,
        "游戏/娱乐": 0.7,
        "网络/通信设备": 0.7,
        "能源/电源": 0.6,
        "教育套件/创客": 0.4,
        "机器人/机电": 0.4,
        "科研/实验室仪器": 0.3,
        "可穿戴/健康": 0.3,
        "制造设备/桌面机器": 0.2,
        "农业/园艺": 0.2,
        "其他": -0.7,
    }
    demand += category_demand.get(record.category, 0.0)

    support = max(0.0, float(record.stars_or_support or 0.0))
    market += min(2.4, math.log10(1.0 + support) * 0.75)
    if record.platform in {"Crowd Supply", "Tindie", "Kickstarter", "Indiegogo"}:
        market += 1.6
        maturity += 1.2
    elif record.platform in {"OSHWA认证目录", "PCBWay共享项目", "嘉立创开源硬件平台", "OSH Park Shared Projects"}:
        maturity += 0.9
    elif record.platform.startswith("Hack Club"):
        maturity += 0.5

    if len(record.description) >= 180:
        maturity += 0.8
    elif record.description:
        maturity += 0.35
    if record.thumbnail_type in {"产品图", "项目图", "项目卡"}:
        maturity += 0.35
    if record.hardware_license not in {"未说明", "待核验", "页面待核验"}:
        maturity += 0.65
    if record.software_license not in {"未说明", "待核验", "页面待核验"}:
        maturity += 0.45
    if any(token in record.open_source_completeness.lower() for token in ("gerber", "bom", "schematic", "原理图", "pcb", "认证")):
        maturity += 0.55

    commercial_tokens = ("sold", "shop", "store", "crowdfund", "funded", "backer", "price", "product", "kit", "订单", "售卖", "众筹", "商品")
    if any(token in text for token in commercial_tokens):
        market += 0.65

    differentiated_tokens = ("custom", "modular", "portable", "low power", "e-paper", "epaper", "wearable", "offline", "local", "open source", "定制", "模块化", "低功耗", "便携")
    differentiation += min(1.4, sum(token in text for token in differentiated_tokens) * 0.24)
    if record.category in {"传感器/环境监测", "智能家居/物联网", "教育套件/创客"}:
        differentiation -= 0.55
    if record.category == "其他":
        differentiation -= 0.8

    if record.category in {"电子礼物/徽章/挂件", "游戏/娱乐", "机器人/机电", "可穿戴/健康"}:
        virality += 1.25
    if record.thumbnail_type in {"产品图", "项目图"}:
        virality += 0.35

    if record.category in {"机器人/机电", "制造设备/桌面机器", "科研/实验室仪器"}:
        skill_fit -= 1.2
    elif record.category in {"音频/音乐设备", "测试测量/工程工具", "传感器/环境监测", "电子礼物/徽章/挂件"}:
        skill_fit += 0.45

    manufacturability = 10.0 - record.manufacturing_difficulty
    risk_friendliness = 10.0 - (0.55 * record.after_sales_risk + 0.45 * record.compliance_risk)
    evidence_quality = {"A": 1.0, "B": 0.55, "C": 0.15}.get(record.data_quality, 0.15)
    maturity += 0.45 * evidence_quality

    components = {
        "需求": max(0.0, min(10.0, demand)),
        "市场验证": max(0.0, min(10.0, market)),
        "成熟度": max(0.0, min(10.0, maturity)),
        "可量产": max(0.0, min(10.0, manufacturability)),
        "差异化": max(0.0, min(10.0, differentiation)),
        "传播": max(0.0, min(10.0, virality)),
        "风险友好": max(0.0, min(10.0, risk_friendliness)),
        "能力匹配": max(0.0, min(10.0, skill_fit)),
    }
    raw = (
        0.20 * components["需求"]
        + 0.15 * components["市场验证"]
        + 0.15 * components["成熟度"]
        + 0.15 * components["可量产"]
        + 0.10 * components["差异化"]
        + 0.10 * components["传播"]
        + 0.10 * components["风险友好"]
        + 0.05 * components["能力匹配"]
    )
    record.raw_commercial_score = round(max(0.0, min(10.0, raw)), 2)
    evidence = []
    if support:
        evidence.append(f"支持量{int(support)}")
    if record.published_date or record.updated_date:
        evidence.append("有时间证据")
    if record.thumbnail_type in {"产品图", "项目图", "项目卡"}:
        evidence.append("有项目图")
    if record.hardware_license not in {"未说明", "待核验", "页面待核验"} or record.software_license not in {"未说明", "待核验", "页面待核验"}:
        evidence.append("有许可线索")
    if any(token in text for token in commercial_tokens):
        evidence.append("有商业化词信号")
    record.score_reason = base.clean_text(
        "；".join(f"{key}{value:.1f}/10" for key, value in components.items())
        + f"。逐条证据：{('、'.join(evidence) if evidence else '公开页基础元数据，需二审')}。"
        + f"主要机会：{record.commercial_value} 约束：量产{record.manufacturing_difficulty:.1f}、售后{record.after_sales_risk:.1f}、合规{record.compliance_risk:.1f}。",
        700,
    )
    record.review_status = "V2逐条规则评分（非人工尽调）"


def balanced_select(records: list[base.Record], target: int) -> list[base.Record]:
    groups: dict[str, list[base.Record]] = defaultdict(list)
    for record in records:
        groups[record.platform].append(record)
    for rows in groups.values():
        rows.sort(key=lambda r: (-r.raw_commercial_score, -float(r.stars_or_support or 0), r.name.lower()))

    caps: dict[str, int] = {}
    for platform, rows in groups.items():
        if platform == "GitHub":
            caps[platform] = min(len(rows), max(2200, int(target * 0.22)))
        elif platform == "GitLab":
            caps[platform] = min(len(rows), max(1200, int(target * 0.13)))
        elif platform == "OSHWA认证目录":
            caps[platform] = min(len(rows), max(1200, int(target * 0.13)))
        elif platform.startswith("Hack Club"):
            caps[platform] = min(len(rows), 650)
        else:
            caps[platform] = min(len(rows), 600)

    selected: list[base.Record] = []
    used: Counter[str] = Counter()
    cursor: Counter[str] = Counter()

    # Fair first pass: take up to 120 from every available platform.
    floor = 120
    for platform in sorted(groups, key=lambda p: (len(groups[p]), p), reverse=True):
        take = min(floor, caps[platform], len(groups[platform]))
        selected.extend(groups[platform][:take])
        used[platform] += take
        cursor[platform] = take

    # Fill by the smallest cap-utilisation ratio, preserving quality order inside
    # each platform. This prevents one large source from swallowing the corpus.
    while len(selected) < target:
        candidates = [
            platform
            for platform in groups
            if cursor[platform] < len(groups[platform]) and used[platform] < caps[platform]
        ]
        if not candidates:
            break
        platform = min(candidates, key=lambda p: (used[p] / max(1, caps[p]), -groups[p][cursor[p]].raw_commercial_score, p))
        selected.append(groups[platform][cursor[platform]])
        cursor[platform] += 1
        used[platform] += 1

    # If strict caps leave a shortfall, relax them in quality order, but keep a
    # hard 30% cap on any single platform.
    if len(selected) < target:
        selected_ids = {r.project_id for r in selected}
        overflow = [r for r in records if r.project_id not in selected_ids]
        overflow.sort(key=lambda r: (-r.raw_commercial_score, r.platform, r.name.lower()))
        hard_cap = int(target * 0.30)
        for record in overflow:
            if used[record.platform] >= hard_cap:
                continue
            selected.append(record)
            used[record.platform] += 1
            if len(selected) >= target:
                break
    return selected[:target]


def write_score_distribution(records: list[base.Record], path: Path) -> None:
    buckets = Counter(int(min(9, max(0, math.floor(r.normalized_commercial_score)))) for r in records)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["分数区间", "条数", "占比"])
        for bucket in range(10):
            count = buckets[bucket]
            writer.writerow([f"{bucket}-{bucket+1}", count, round(count / max(1, len(records)), 6)])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=10500)
    parser.add_argument("--out", type=Path, default=Path("output_v2"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    all_records: list[base.Record] = []
    status_rows: list[dict[str, Any]] = []

    def run_source(name: str, function) -> None:
        started = time.time()
        state = "成功"
        note = ""
        rows: list[base.Record] = []
        try:
            rows = function()
            if not rows:
                state = "无结果"
        except Exception as exc:
            state = "失败"
            note = repr(exc)
            print(f"[{name}] fatal: {exc}", file=sys.stderr)
        for record in rows:
            score_v2(record)
        all_records.extend(rows)
        status_rows.append({"平台": name, "状态": state, "抓取条数": len(rows), "耗时秒": round(time.time() - started, 1), "错误/备注": note})
        print(f"[{name}] {state}: {len(rows)} rows", flush=True)

    run_source("OSHWA认证目录", lambda: base.fetch_oshwa(1800))
    run_source("Hack Club项目库", lambda: base.fetch_hackclub(700))
    run_source("GitHub", lambda: base.fetch_github(4200))
    run_source("GitLab", lambda: base.fetch_gitlab(1800))
    for source in FAST_SOURCES:
        run_source(source.name, lambda source=source: fetch_fast_source(source))

    deduped = base.deduplicate(all_records)
    selected = balanced_select(deduped, args.target)
    base.normalize_scores(selected)
    selected.sort(key=lambda r: (-r.normalized_commercial_score, -r.raw_commercial_score, r.platform, r.name.lower()))

    base.write_csv(selected, args.out / "hardware_opportunities.csv")
    with (args.out / "hardware_opportunities.jsonl").open("w", encoding="utf-8") as handle:
        for record in selected:
            handle.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
    with (args.out / "source_status.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["平台", "状态", "抓取条数", "耗时秒", "错误/备注"])
        writer.writeheader()
        writer.writerows(status_rows)

    base.write_xlsx(selected, status_rows, args.out / "开源硬件商业化机会库_10000条.xlsx")
    write_score_distribution(selected, args.out / "score_distribution.csv")

    platform_counts = Counter(r.platform for r in selected)
    top4_share = sum(count for _, count in platform_counts.most_common(4)) / max(1, len(selected))
    summary = {
        "generated_at": base.NOW.isoformat(),
        "cutoff": base.CUTOFF.date().isoformat(),
        "candidate_records_before_dedupe": len(all_records),
        "deduplicated_candidates": len(deduped),
        "records": len(selected),
        "platforms": len(platform_counts),
        "platform_counts": platform_counts,
        "top4_platform_share": round(top4_share, 6),
        "category_counts": Counter(r.category for r in selected),
        "quality_counts": Counter(r.data_quality for r in selected),
        "score_mean": statistics.mean(r.normalized_commercial_score for r in selected) if selected else 0,
        "score_stdev": statistics.pstdev(r.normalized_commercial_score for r in selected) if len(selected) > 1 else 0,
        "gte_8": sum(r.normalized_commercial_score >= 8 for r in selected),
        "scoring_method": "每条记录依据自身元数据进行确定性规则评分；非逐条人工尽调。全库分数再做秩-正态映射。",
    }
    with (args.out / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, default=dict)
    with (args.out / "SCORING_METHOD.md").open("w", encoding="utf-8") as handle:
        handle.write("# 评分方法\n\n")
        handle.write("- 原始分：脚本对每一行独立计算，使用该行的类别、平台、支持量、时间、图片、描述、许可/开源完整度、商业关键词、量产/售后/合规风险。\n")
        handle.write("- 正态化分：按全库原始分排序，映射到均值约5.4、标准差约1.45的截断正态分布。\n")
        handle.write("- 不是人工逐条商业尽调；高分项目仍需核验竞品销量、专利、商标、认证、BOM和真实成本。\n")
        handle.write("- `审核状态`列明确标记为V2逐条规则评分。\n")
    with (args.out / "RELEASE_NOTES.md").open("w", encoding="utf-8") as handle:
        handle.write(f"# 开源硬件商业化机会库 V2\n\n- 去重项目：{len(selected):,}\n- 有效平台：{len(platform_counts)}\n- 前四平台占比：{top4_share:.1%}\n- 评分均值/标准差：{summary['score_mean']:.2f}/{summary['score_stdev']:.2f}\n\n完整文件见本 Release 附件。\n")

    print(json.dumps(summary, ensure_ascii=False, indent=2, default=dict))
    if len(selected) < 10000:
        print(f"QUALITY GATE FAILED: only {len(selected)} records", file=sys.stderr)
        return 2
    if len(platform_counts) < 25:
        print(f"QUALITY GATE FAILED: only {len(platform_counts)} platforms", file=sys.stderr)
        return 3
    if top4_share > 0.72:
        print(f"QUALITY GATE FAILED: top4 share {top4_share:.2%}", file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
