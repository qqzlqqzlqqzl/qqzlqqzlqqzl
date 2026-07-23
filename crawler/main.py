#!/usr/bin/env python3
"""Public-web open-hardware opportunity crawler.

Only public pages/APIs are used. Requests are rate-limited and every record
retains source provenance and a data-quality grade.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import statistics
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from statistics import NormalDist
from typing import Any, Iterable

import requests
import xlsxwriter
from bs4 import BeautifulSoup
from dateutil import parser as dateparser
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

NOW = datetime.now(timezone.utc)
CUTOFF = datetime(2021, 1, 1, tzinfo=timezone.utc)
UA = "OpenHardwareCommercialResearch/1.0 (+public research; polite crawler)"


def clean_text(value: Any, limit: int = 600) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()[:limit]


def parse_date(value: Any) -> str:
    if not value:
        return ""
    try:
        dt = dateparser.parse(str(value))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).date().isoformat()
    except Exception:
        return ""


def recent_enough(value: Any) -> bool:
    d = parse_date(value)
    return not d or d >= CUTOFF.date().isoformat()


def canonical_url(url: str) -> str:
    try:
        p = urllib.parse.urlsplit(url)
        path = re.sub(r"/+", "/", p.path).rstrip("/")
        return urllib.parse.urlunsplit((p.scheme.lower(), p.netloc.lower(), path, "", ""))
    except Exception:
        return url.strip()


def slug_title(url: str) -> str:
    p = urllib.parse.urlsplit(url)
    token = urllib.parse.unquote(p.path.rstrip("/").split("/")[-1]) or p.netloc
    return clean_text(re.sub(r"[-_]+", " ", token).title(), 180)


def stable_id(platform: str, url: str) -> str:
    return hashlib.sha1(f"{platform}|{canonical_url(url)}".encode()).hexdigest()[:16]


def make_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(total=3, backoff_factor=0.8, status_forcelist=(429, 500, 502, 503, 504), allowed_methods=("GET", "HEAD"), respect_retry_after_header=True)
    s.mount("https://", HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=20))
    s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.8,zh-CN;q=0.6"})
    return s


HTTP = make_session()


@dataclass
class Record:
    project_id: str
    name: str
    platform: str
    url: str
    source_domain: str = ""
    thumbnail_url: str = ""
    thumbnail_type: str = "缺失"
    published_date: str = ""
    updated_date: str = ""
    description: str = ""
    keywords: str = ""
    category: str = "其他"
    stars_or_support: float = 0.0
    hardware_license: str = "未说明"
    software_license: str = "未说明"
    open_source_completeness: str = "未知"
    market_validation: str = ""
    typical_competitors: str = ""
    commercial_value: str = ""
    improvement_direction: str = ""
    target_customer: str = ""
    suggested_price_low_cny: int = 0
    suggested_price_high_cny: int = 0
    manufacturing_difficulty: float = 5.0
    after_sales_risk: float = 5.0
    compliance_risk: float = 5.0
    raw_commercial_score: float = 0.0
    normalized_commercial_score: float = 0.0
    score_reason: str = ""
    data_quality: str = "C"
    review_status: str = "自动初筛"
    crawl_time: str = field(default_factory=lambda: NOW.isoformat(timespec="seconds"))


def make_record(platform: str, url: str, name: str = "", **kwargs: Any) -> Record:
    cu = canonical_url(url)
    return Record(project_id=stable_id(platform, cu), name=clean_text(name or slug_title(cu), 180), platform=platform, url=cu, source_domain=urllib.parse.urlsplit(cu).netloc, **kwargs)


CATEGORY_RULES = [
    ("电子礼物/徽章/挂件", ["badge", "keychain", "gift", "name tag", "nametag", "电子徽章", "钥匙扣", "挂件", "留言", "quote", "epaper badge", "e-paper badge"]),
    ("键盘/宏键盘/控制器", ["keyboard", "keypad", "macropad", "macro pad", "controller", "stream deck", "midi controller", "键盘", "控制器"]),
    ("音频/音乐设备", ["audio", "midi", "synth", "synthesizer", "speaker", "amplifier", "dac", "microphone", "guitar", "eurorack", "音频", "合成器"]),
    ("测试测量/工程工具", ["oscilloscope", "logic analyzer", "multimeter", "tester", "programmer", "debugger", "power meter", "测试仪", "示波器", "逻辑分析", "烧录器"]),
    ("传感器/环境监测", ["sensor", "weather", "air quality", "temperature", "humidity", "monitor", "detector", "传感器", "环境监测", "气象"]),
    ("智能家居/物联网", ["smart home", "home automation", "iot", "matter", "home assistant", "doorbell", "thermostat", "智能家居", "物联网"]),
    ("机器人/机电", ["robot", "rover", "drone", "quadruped", "robot arm", "servo", "机器人", "机械臂", "无人机"]),
    ("可穿戴/健康", ["wearable", "watch", "fitness", "health", "ecg", "heart rate", "assistive", "可穿戴", "健康", "心率"]),
    ("游戏/娱乐", ["game", "gaming", "console", "joystick", "arcade", "toy", "游戏", "掌机", "玩具"]),
    ("教育套件/创客", ["education", "learning", "stem", "kit", "trainer", "tutorial", "教育", "开发板", "套件"]),
    ("农业/园艺", ["garden", "plant", "farm", "irrigation", "hydroponic", "农业", "植物", "浇水"]),
    ("能源/电源", ["solar", "battery", "charger", "power supply", "ups", "energy", "充电", "电源", "太阳能"]),
    ("制造设备/桌面机器", ["3d printer", "cnc", "pick and place", "laser", "plotter", "printer", "3d打印", "贴片机", "雕刻机"]),
    ("科研/实验室仪器", ["microscope", "spectrometer", "laboratory", "lab", "centrifuge", "pcr", "scientific", "显微镜", "实验室", "光谱"]),
    ("网络/通信设备", ["lora", "radio", "sdr", "router", "network", "wifi", "bluetooth", "mesh", "无线", "通信", "路由"]),
]

CATEGORY_INFO = {
    "电子礼物/徽章/挂件": {"competitors": "亚克力定制挂件、录音钥匙扣、电子墨水名牌、LED胸牌、定制礼品店", "value": "适合情绪礼赠、活动周边和小批量联名；内容、外形与包装可形成明显溢价。", "improve": "强化专属内容、隐藏彩蛋、裸板审美、低功耗与批量烧录流程；避免只卖电子参数。", "customer": "情侣与朋友送礼者、毕业班、婚礼/展览/创作者周边采购方", "price": (59, 199), "mfg": 3.5, "after": 3.5, "compliance": 3.5},
    "键盘/宏键盘/控制器": {"competitors": "机械键盘、Stream Deck、可编程宏键盘、MIDI控制器、游戏手柄", "value": "用户愿意为手感、布局、旋钮、灯效与软件生态付费，模块化和垂直场景可差异化。", "improve": "聚焦单一职业或软件场景，改善外观、键帽、旋钮手感和配置工具。", "customer": "程序员、设计师、视频剪辑、直播、音乐制作与游戏用户", "price": (99, 699), "mfg": 5.0, "after": 5.0, "compliance": 3.0},
    "音频/音乐设备": {"competitors": "USB声卡、耳放、效果器、合成器、MIDI控制器、桌面音频品牌", "value": "音频用户客单价较高，审美、操控与声音特色能够支撑小众品牌。", "improve": "选择明确乐器/桌面场景，重做交互和工业设计，并严控噪声、EMC与兼容性。", "customer": "音乐人、发烧友、播客/直播用户、桌面音频爱好者", "price": (199, 1999), "mfg": 7.0, "after": 7.0, "compliance": 5.0},
    "测试测量/工程工具": {"competitors": "廉价万用表、逻辑分析仪、示波器、USB测试仪、烧录调试器", "value": "需求清晰、复购与口碑驱动明显；只要精度、软件和可靠性可信就有商业空间。", "improve": "用更好的夹具、保护、电气安全、自动报告和跨平台软件做差异化。", "customer": "电子工程师、维修人员、实验室、学校与创客", "price": (99, 1999), "mfg": 6.5, "after": 6.0, "compliance": 6.0},
    "传感器/环境监测": {"competitors": "米家/涂鸦传感器、空气质量仪、气象站、工业数据采集器", "value": "场景广泛但同质化严重；垂直行业、精度、离线能力和数据服务决定溢价。", "improve": "针对宠物、仓储、乐器、实验室等细分场景，提供校准、历史数据与告警。", "customer": "家庭、办公室、仓储、实验室、农业与设备运维用户", "price": (79, 799), "mfg": 4.5, "after": 5.5, "compliance": 4.0},
    "智能家居/物联网": {"competitors": "米家、涂鸦、Home Assistant生态、Aqara、Shelly及各类Wi-Fi设备", "value": "市场已验证但竞争激烈；本地化、开放协议、隐私和特殊传感能力可形成机会。", "improve": "优先本地控制、Matter/Home Assistant兼容、简单配网与长期固件维护。", "customer": "智能家居爱好者、租房用户、小型商业空间和系统集成商", "price": (99, 999), "mfg": 5.5, "after": 7.0, "compliance": 6.0},
    "机器人/机电": {"competitors": "教育机器人、桌面机械臂、四足机器人、无人机和开源套件", "value": "传播力强、客单价高，但结构、供应链与售后门槛显著。", "improve": "缩小功能范围，减少定制件，突出桌面陪伴、教育或单一任务价值。", "customer": "学校、创客、机器人爱好者、展馆和研发团队", "price": (299, 4999), "mfg": 8.0, "after": 8.0, "compliance": 6.5},
    "可穿戴/健康": {"competitors": "智能手表、运动手环、姿态提醒器、健康监测设备", "value": "用户需求强但合规、准确性和佩戴体验要求高；非医疗定位更适合小团队。", "improve": "避免医疗宣称，聚焦提醒、记录、无障碍或趣味互动，并优化重量和续航。", "customer": "运动用户、久坐办公、无障碍人群和创客", "price": (129, 1299), "mfg": 7.0, "after": 7.0, "compliance": 8.0},
    "游戏/娱乐": {"competitors": "掌机、电子宠物、桌游配件、街机控制器、发光玩具", "value": "容易传播和冲动消费，IP、玩法、外观与社区内容决定生命周期。", "improve": "加入可分享玩法、联机或内容包，控制BOM并避免仅靠一次性新鲜感。", "customer": "学生、玩家、礼物消费者、活动与IP周边采购方", "price": (59, 699), "mfg": 4.5, "after": 5.0, "compliance": 5.0},
    "教育套件/创客": {"competitors": "Arduino/树莓派套件、micro:bit、机器人教育包、国产开发板", "value": "采购路径成熟，但需要完整课程、中文文档和可靠售后来避免沦为低价板卡。", "improve": "围绕可完成作品设计课程、工具链与耗材包，而不是只卖裸板。", "customer": "学校、培训机构、家长、学生和创客空间", "price": (79, 999), "mfg": 4.0, "after": 6.0, "compliance": 4.5},
    "农业/园艺": {"competitors": "自动浇水器、土壤传感器、温室控制器、智能花盆", "value": "痛点真实但环境可靠性要求高；家庭园艺和小型温室更适合小批量切入。", "improve": "做防水、防腐、断网运行和可更换探头，提供植物模板与维护提醒。", "customer": "家庭园艺、小农场、温室、学校与植物店", "price": (99, 1299), "mfg": 6.0, "after": 7.0, "compliance": 5.0},
    "能源/电源": {"competitors": "充电器、移动电源、UPS、可调电源、太阳能控制器", "value": "需求明确但安全、认证与供应链门槛高；专业细分功能可形成高客单价。", "improve": "增加保护、热设计、认证余量和清晰规格，避免未经验证的电池/市电方案。", "customer": "电子工程师、户外用户、家庭备电与工业设备用户", "price": (129, 2999), "mfg": 7.5, "after": 7.5, "compliance": 8.5},
    "制造设备/桌面机器": {"competitors": "3D打印机、桌面CNC、激光雕刻机、贴片机、绘图机", "value": "高客单价且开源商业化路径成熟，但机械、校准、物流和售后成本很高。", "improve": "聚焦单一材料/任务，模块化易损件，提供校准流程、耗材和服务收入。", "customer": "工作室、创客空间、学校、小型工厂和设计师", "price": (999, 19999), "mfg": 9.0, "after": 9.0, "compliance": 7.0},
    "科研/实验室仪器": {"competitors": "传统实验室仪器、低成本教学仪器、开源科学硬件", "value": "单位价值高、客户痛点强，适合定制和服务；但准确性、校准和责任边界重要。", "improve": "明确非诊断用途，提供校准件、数据导出、实验协议和可追溯BOM。", "customer": "高校实验室、中学、科研团队、生物创客和小型企业", "price": (499, 9999), "mfg": 7.5, "after": 7.0, "compliance": 8.0},
    "网络/通信设备": {"competitors": "LoRa节点、路由器、SDR、网关、Mesh通信设备", "value": "垂直通信和离线场景有需求，但射频、认证、天线和软件维护提高门槛。", "improve": "聚焦户外、应急、农业或实验用途，优化天线、配置工具与协议兼容性。", "customer": "无线电爱好者、户外团队、农业、实验室和系统集成商", "price": (129, 1999), "mfg": 6.5, "after": 7.0, "compliance": 7.5},
    "其他": {"competitors": "同类消费电子、DIY套件和低价模块", "value": "需要进一步验证使用场景、目标用户和付费理由。", "improve": "先把技术功能收敛成单一用户任务，再用外观、内容或服务建立差异化。", "customer": "创客与潜在垂直场景用户", "price": (99, 999), "mfg": 5.5, "after": 5.5, "compliance": 5.0},
}


def classify(text: str) -> str:
    low = text.lower()
    for category, words in CATEGORY_RULES:
        if any(word in low for word in words):
            return category
    return "其他"


def enrich_record(r: Record) -> None:
    text = " ".join([r.name, r.description, r.keywords]).lower()
    r.category = classify(text)
    info = CATEGORY_INFO[r.category]
    r.typical_competitors = info["competitors"]
    r.commercial_value = info["value"]
    r.improvement_direction = info["improve"]
    r.target_customer = info["customer"]
    r.suggested_price_low_cny, r.suggested_price_high_cny = info["price"]
    r.manufacturing_difficulty = info["mfg"]
    r.after_sales_risk = info["after"]
    r.compliance_risk = info["compliance"]

    demand, market, maturity, differentiation, virality, skill_fit = 5.0, 4.5, 4.0, 5.0, 4.5, 7.5
    if r.category in {"电子礼物/徽章/挂件", "键盘/宏键盘/控制器", "音频/音乐设备", "测试测量/工程工具"}: demand += 1.0
    if r.category in {"制造设备/桌面机器", "机器人/机电", "科研/实验室仪器"}: demand += 0.5; skill_fit -= 1.5
    if r.stars_or_support >= 1000: market += 2.0
    elif r.stars_or_support >= 100: market += 1.2
    elif r.stars_or_support >= 10: market += 0.5
    if r.platform in {"Crowd Supply", "Kickstarter", "Indiegogo", "Tindie"}: market += 1.5; maturity += 1.5
    if r.platform == "OSHWA认证目录": maturity += 1.5
    if r.hardware_license != "未说明" or r.software_license != "未说明": maturity += 0.8
    if r.description: maturity += 0.5
    if r.thumbnail_type in {"产品图", "项目图"}: maturity += 0.3
    if r.category in {"电子礼物/徽章/挂件", "游戏/娱乐", "机器人/机电"}: virality += 1.5
    if r.category in {"传感器/环境监测", "智能家居/物联网", "教育套件/创客"}: differentiation -= 0.8
    if any(k in text for k in ["modular", "open source", "custom", "portable", "low power", "wearable"]): differentiation += 0.6

    manufacturability = 10 - r.manufacturing_difficulty
    risk = 10 - (0.55 * r.after_sales_risk + 0.45 * r.compliance_risk)
    raw = 0.20*demand + 0.15*market + 0.15*maturity + 0.15*manufacturability + 0.10*differentiation + 0.10*virality + 0.10*risk + 0.05*skill_fit
    r.raw_commercial_score = round(max(0, min(10, raw)), 2)
    r.score_reason = clean_text(f"需求{demand:.1f}/10；市场验证{market:.1f}/10；产品成熟{maturity:.1f}/10；可量产{manufacturability:.1f}/10；差异化{differentiation:.1f}/10；传播{virality:.1f}/10；风险友好度{risk:.1f}/10。主要机会：{r.commercial_value} 主要约束：量产难度{r.manufacturing_difficulty:.1f}、售后{r.after_sales_risk:.1f}、合规{r.compliance_risk:.1f}。", 600)
    quality_points = sum([bool(r.description), bool(r.thumbnail_url), bool(r.published_date or r.updated_date), r.hardware_license != "未说明" or r.software_license != "未说明", bool(r.market_validation)])
    r.data_quality = "A" if quality_points >= 4 else "B" if quality_points >= 2 else "C"


def github_headers() -> dict[str, str]:
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_github(limit: int = 2400) -> list[Record]:
    queries = ["open hardware pcb", "esp32 hardware", "arduino hardware", "e-paper badge", "oled badge", "macropad pcb", "mechanical keyboard pcb", "midi controller hardware", "synthesizer hardware", "logic analyzer hardware", "portable oscilloscope", "sensor board open hardware", "air quality monitor pcb", "home assistant hardware", "matter device hardware", "lora node hardware", "sdr hardware", "robot controller pcb", "desktop robot open source", "wearable electronics", "smartwatch open hardware", "electronic game badge", "open source lab instrument", "open source microscope", "battery tester pcb", "usb power meter", "solar charger open hardware", "pick and place open source", "3d printer controller", "open source audio interface", "guitar pedal pcb", "eurorack module", "electronic keychain", "stem electronics kit", "assistive hardware device", "environmental data logger"]
    out, seen = [], set()
    for query in queries:
        for page in (1, 2, 3):
            if len(out) >= limit:
                return out
            params = {"q": f'{query} pushed:>={CUTOFF.date().isoformat()} archived:false', "sort": "stars", "order": "desc", "per_page": 100, "page": page}
            try:
                response = HTTP.get("https://api.github.com/search/repositories", headers=github_headers(), params=params, timeout=30)
                if response.status_code == 403 and "rate limit" in response.text.lower():
                    time.sleep(65)
                    continue
                response.raise_for_status()
                items = response.json().get("items", [])
            except Exception as exc:
                print(f"[GitHub] query failed {query!r}: {exc}", file=sys.stderr)
                break
            if not items:
                break
            for item in items:
                full, url = item.get("full_name", ""), item.get("html_url", "")
                if not full or not url or full in seen:
                    continue
                seen.add(full)
                topics = item.get("topics") or []
                license_id = (item.get("license") or {}).get("spdx_id") or "未说明"
                stars = float(item.get("stargazers_count") or 0)
                out.append(make_record("GitHub", url, item.get("name") or full, thumbnail_url=f"https://opengraph.githubassets.com/1/{full}", thumbnail_type="项目卡", published_date=parse_date(item.get("created_at")), updated_date=parse_date(item.get("pushed_at") or item.get("updated_at")), description=clean_text(item.get("description")), keywords=", ".join(topics), stars_or_support=stars, software_license=license_id, hardware_license="待核验", open_source_completeness="仓库可访问；PCB/BOM/外壳完整度待二次核验", market_validation=f"GitHub {int(stars)} stars，{int(item.get('forks_count') or 0)} forks"))
            time.sleep(2.1)
    return out


def fetch_gitlab(limit: int = 650) -> list[Record]:
    terms = ["open hardware", "pcb", "esp32", "arduino", "keyboard", "badge", "sensor", "robot", "lora", "synthesizer", "microscope"]
    out, seen = [], set()
    for term in terms:
        for page in (1, 2, 3):
            if len(out) >= limit:
                return out
            try:
                response = HTTP.get("https://gitlab.com/api/v4/projects", params={"search": term, "simple": "true", "per_page": 100, "page": page, "order_by": "last_activity_at", "sort": "desc"}, timeout=30)
                response.raise_for_status()
                items = response.json()
            except Exception as exc:
                print(f"[GitLab] {term}: {exc}", file=sys.stderr)
                break
            for item in items:
                pid = item.get("id")
                if pid in seen or not recent_enough(item.get("last_activity_at")):
                    continue
                seen.add(pid)
                url = item.get("web_url")
                if not url:
                    continue
                stars = float(item.get("star_count") or 0)
                thumb = item.get("avatar_url") or "https://www.google.com/s2/favicons?domain=gitlab.com&sz=128"
                out.append(make_record("GitLab", url, item.get("name") or item.get("path_with_namespace"), thumbnail_url=thumb, thumbnail_type="项目图" if item.get("avatar_url") else "平台图", published_date=parse_date(item.get("created_at")), updated_date=parse_date(item.get("last_activity_at")), description=clean_text(item.get("description")), keywords=", ".join(item.get("tag_list") or []), stars_or_support=stars, software_license="待核验", hardware_license="待核验", open_source_completeness="仓库可访问；设计文件完整度待二次核验", market_validation=f"GitLab {int(stars)} stars，{int(item.get('forks_count') or 0)} forks"))
            time.sleep(0.7)
    return out


def fetch_oshwa(limit: int = 1100) -> list[Record]:
    out = []
    url = "https://certification.oshwa.org/list.html"
    try:
        response = HTTP.get(url, timeout=60)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for row in soup.select("table#project_data tbody tr"):
            link, cells = row.select_one("td a"), row.find_all("td")
            if not link or len(cells) < 4:
                continue
            name = clean_text(link.get_text(" "))
            detail = urllib.parse.urljoin(url, link.get("href", ""))
            project_type = clean_text(cells[2].get_text(" "))
            cert_date = parse_date(cells[3].get_text(" "))
            if cert_date and cert_date < CUTOFF.date().isoformat():
                continue
            out.append(make_record("OSHWA认证目录", detail, name, thumbnail_url="https://www.google.com/s2/favicons?domain=certification.oshwa.org&sz=128", thumbnail_type="平台图", published_date=cert_date, description=f"OSHWA认证开放硬件项目；类型：{project_type}", keywords=project_type, hardware_license="已声明（详情页待提取）", software_license="已声明或不适用（待核验）", open_source_completeness="通过OSHWA认证，具备公开设计资料要求", market_validation=f"OSHWA认证；项目类型：{project_type}"))
            if len(out) >= limit:
                break
    except Exception as exc:
        print(f"[OSHWA] failed: {exc}", file=sys.stderr)
    return out


HACKCLUB_REPOS = [("Hack Club OnBoard", "hackclub/OnBoard", "projects/"), ("Hack Club Solder", "hackclub/solder", "projects/"), ("Hack Club Blueprint", "hackclub/blueprint", "projects/"), ("Hack Club Highway", "hackclub/highway", "projects/"), ("Hack Club Winter", "hackclub/winter", "projects/")]


def fetch_hackclub(limit_each: int = 220) -> list[Record]:
    out, headers = [], github_headers()
    for platform, repo, prefix in HACKCLUB_REPOS:
        try:
            meta_response = HTTP.get(f"https://api.github.com/repos/{repo}", headers=headers, timeout=30)
            meta_response.raise_for_status()
            meta = meta_response.json()
            branch = meta.get("default_branch", "main")
            response = HTTP.get(f"https://api.github.com/repos/{repo}/git/trees/{branch}", headers=headers, params={"recursive": "1"}, timeout=60)
            response.raise_for_status()
            tree = response.json().get("tree", [])
        except Exception as exc:
            print(f"[{platform}] tree failed: {exc}", file=sys.stderr)
            continue
        projects = {}
        for node in tree:
            path = node.get("path", "")
            if not path.startswith(prefix):
                continue
            rest = path[len(prefix):]
            if not rest or "/" not in rest:
                continue
            folder = rest.split("/", 1)[0]
            if folder.startswith("!") or folder.lower() in {"template", "example"}:
                continue
            projects.setdefault(folder, f"https://github.com/{repo}/tree/{branch}/{prefix}{folder}")
        for folder, url in list(projects.items())[:limit_each]:
            name = clean_text(re.sub(r"[-_]+", " ", folder), 180)
            out.append(make_record(platform, url, name, thumbnail_url=f"https://opengraph.githubassets.com/1/{repo}", thumbnail_type="项目卡", updated_date=parse_date(meta.get("pushed_at")), description=f"{platform}公开硬件项目提交：{name}", keywords="PCB, open hardware, student project", hardware_license="项目级待核验", software_license="项目级待核验", open_source_completeness="通常含Gerber、原理图与设计源文件；逐项待核验", market_validation=f"进入{platform}公开项目库，具备可制造提交要求"))
    return out


@dataclass(frozen=True)
class WebSource:
    name: str
    seeds: tuple[str, ...]
    patterns: tuple[str, ...]
    sitemap: tuple[str, ...] = ()
    max_rows: int = 35


WEB_SOURCES = (
    WebSource("Hackaday.io", ("https://hackaday.io/projects",), (r"hackaday\.io/project/\d+",), ("https://hackaday.io/sitemap.xml",), 50),
    WebSource("Hackster.io", ("https://www.hackster.io/projects",), (r"hackster\.io/.+/.+",), ("https://www.hackster.io/sitemap.xml",), 45),
    WebSource("Arduino Project Hub", ("https://projecthub.arduino.cc/",), (r"projecthub\.arduino\.cc/.+/.+",), ("https://projecthub.arduino.cc/sitemap.xml",), 45),
    WebSource("Instructables", ("https://www.instructables.com/circuits/projects/",), (r"instructables\.com/.+",), ("https://www.instructables.com/sitemap.xml",), 40),
    WebSource("Crowd Supply", ("https://www.crowdsupply.com/browse",), (r"crowdsupply\.com/[^/]+/[^/]+$",), ("https://www.crowdsupply.com/sitemap.xml",), 40),
    WebSource("Tindie", ("https://www.tindie.com/browse/diy-electronics/",), (r"tindie\.com/products/[^/]+/[^/]+",), ("https://www.tindie.com/sitemap.xml",), 35),
    WebSource("Kitspace", ("https://kitspace.org/boards/",), (r"kitspace\.org/boards/.+",), ("https://kitspace.org/sitemap.xml",), 35),
    WebSource("PCBWay共享项目", ("https://www.pcbway.com/project/shareproject/",), (r"pcbway\.com/project/shareproject/.+",), ("https://www.pcbway.com/sitemap.xml",), 30),
    WebSource("嘉立创开源硬件平台", ("https://oshwhub.com/explore",), (r"oshwhub\.com/.+/.+",), ("https://oshwhub.com/sitemap.xml",), 35),
    WebSource("Seeed Project Hub", ("https://project.seeedstudio.com/",), (r"project\.seeedstudio\.com/.+",), ("https://project.seeedstudio.com/sitemap.xml",), 30),
    WebSource("DFRobot社区", ("https://community.dfrobot.com/",), (r"community\.dfrobot\.com/.+",), ("https://community.dfrobot.com/sitemap.xml",), 30),
    WebSource("Adafruit Learning System", ("https://learn.adafruit.com/",), (r"learn\.adafruit\.com/[^/]+/?$",), ("https://learn.adafruit.com/sitemap.xml",), 35),
    WebSource("SparkFun教程项目", ("https://learn.sparkfun.com/tutorials",), (r"learn\.sparkfun\.com/tutorials/.+",), ("https://learn.sparkfun.com/sitemap.xml",), 30),
    WebSource("element14 Community", ("https://community.element14.com/challenges-projects/project14/",), (r"community\.element14\.com/.+/b/blog/posts/.+",), ("https://community.element14.com/sitemap.xml",), 25),
    WebSource("Electromaker", ("https://www.electromaker.io/projects",), (r"electromaker\.io/project/view/.+",), ("https://www.electromaker.io/sitemap.xml",), 35),
    WebSource("CircuitDigest", ("https://circuitdigest.com/electronic-circuits",), (r"circuitdigest\.com/.+",), ("https://circuitdigest.com/sitemap.xml",), 30),
    WebSource("All About Circuits Projects", ("https://www.allaboutcircuits.com/projects/",), (r"allaboutcircuits\.com/projects/.+",), ("https://www.allaboutcircuits.com/sitemap.xml",), 30),
    WebSource("Raspberry Pi Projects", ("https://projects.raspberrypi.org/en/projects",), (r"projects\.raspberrypi\.org/.+/projects/.+",), ("https://projects.raspberrypi.org/sitemap.xml",), 30),
    WebSource("Printables", ("https://www.printables.com/model?category=90",), (r"printables\.com/model/\d+-.+",), ("https://www.printables.com/sitemap.xml",), 25),
    WebSource("Thingiverse", ("https://www.thingiverse.com/search?q=electronics&type=things",), (r"thingiverse\.com/thing:\d+",), ("https://www.thingiverse.com/sitemap.xml",), 25),
    WebSource("MakerWorld", ("https://makerworld.com/en/search/models?keyword=electronics",), (r"makerworld\.com/.+/models/\d+",), ("https://makerworld.com/sitemap.xml",), 25),
    WebSource("Maker Faire", ("https://makerfaire.com/maker/",), (r"makerfaire\.com/maker/.+",), ("https://makerfaire.com/sitemap.xml",), 25),
    WebSource("Open Hardware Repository", ("https://ohwr.org/projects",), (r"ohwr\.org/project/.+",), ("https://ohwr.org/sitemap.xml",), 25),
    WebSource("Open Hardware Observatory", ("https://en.oho.wiki/wiki/Home",), (r"en\.oho\.wiki/wiki/.+",), ("https://en.oho.wiki/sitemap.xml",), 25),
    WebSource("OpenMV Projects", ("https://openmv.io/pages/projects",), (r"openmv\.io/.+",), ("https://openmv.io/sitemap.xml",), 20),
    WebSource("Hackaday文章项目", ("https://hackaday.com/category/hardware/",), (r"hackaday\.com/20\d\d/\d\d/\d\d/.+",), ("https://hackaday.com/sitemap.xml",), 30),
    WebSource("Make: Projects", ("https://makezine.com/projects/",), (r"makezine\.com/projects/.+",), ("https://makezine.com/sitemap_index.xml",), 25),
    WebSource("Elecrow Projects", ("https://www.elecrow.com/share-projects.html",), (r"elecrow\.com/.+",), ("https://www.elecrow.com/sitemap.xml",), 20),
)


def xml_urls(content: bytes) -> tuple[list[str], list[str]]:
    urls, maps = [], []
    try:
        root = ET.fromstring(content)
    except Exception:
        return urls, maps
    if root.tag.lower().endswith("sitemapindex"):
        for loc in root.findall(".//{*}loc"):
            if loc.text: maps.append(loc.text.strip())
    else:
        for item in root.findall(".//{*}url"):
            loc, last = item.find("{*}loc"), item.find("{*}lastmod")
            if loc is not None and loc.text and recent_enough(last.text if last is not None else ""):
                urls.append(loc.text.strip())
    return urls, maps


def collect_links(html: str, base: str, patterns: tuple[str, ...]) -> list[str]:
    soup, out = BeautifulSoup(html, "html.parser"), []
    for link in soup.find_all("a", href=True):
        url = canonical_url(urllib.parse.urljoin(base, link["href"]))
        if any(re.search(pattern, url, re.I) for pattern in patterns):
            out.append(url)
    return list(dict.fromkeys(out))


def parse_detail(platform: str, url: str) -> Record | None:
    try:
        response = HTTP.get(url, timeout=25)
        if response.status_code >= 400:
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        title = ""
        for selector in ('meta[property="og:title"]', 'meta[name="twitter:title"]'):
            tag = soup.select_one(selector)
            if tag and tag.get("content"):
                title = clean_text(tag["content"], 180); break
        if not title and soup.title: title = clean_text(soup.title.get_text(" "), 180)
        description = ""
        for selector in ('meta[property="og:description"]', 'meta[name="description"]', 'meta[name="twitter:description"]'):
            tag = soup.select_one(selector)
            if tag and tag.get("content"):
                description = clean_text(tag["content"], 600); break
        image = ""
        for selector in ('meta[property="og:image"]', 'meta[name="twitter:image"]'):
            tag = soup.select_one(selector)
            if tag and tag.get("content"):
                image = urllib.parse.urljoin(url, tag["content"]); break
        date = ""
        for selector in ('meta[property="article:published_time"]', 'meta[name="date"]', 'time[datetime]'):
            tag = soup.select_one(selector)
            if tag:
                date = parse_date(tag.get("content") or tag.get("datetime"))
                if date: break
        if date and date < CUTOFF.date().isoformat():
            return None
        keyword_tag = soup.select_one('meta[name="keywords"]')
        return make_record(platform, url, title or slug_title(url), thumbnail_url=image or f"https://www.google.com/s2/favicons?domain={urllib.parse.urlsplit(url).netloc}&sz=128", thumbnail_type="产品图" if image else "平台图", published_date=date, description=description, keywords=clean_text(keyword_tag.get("content", "") if keyword_tag else "", 300), hardware_license="页面待核验", software_license="页面待核验", open_source_completeness="公开项目页；设计文件与许可需二次核验", market_validation=f"收录于{platform}公开项目/商品目录")
    except Exception as exc:
        print(f"[{platform}] detail failed {url}: {exc}", file=sys.stderr)
        return None


def fetch_web_source(source: WebSource) -> list[Record]:
    candidates, queue, seen_maps = [], list(source.sitemap), set()
    while queue and len(seen_maps) < 8 and len(candidates) < source.max_rows * 8:
        sitemap = queue.pop(0)
        if sitemap in seen_maps: continue
        seen_maps.add(sitemap)
        try:
            response = HTTP.get(sitemap, timeout=30); response.raise_for_status()
            urls, maps = xml_urls(response.content)
            queue.extend(maps[:6])
            candidates.extend(canonical_url(url) for url in urls if any(re.search(pattern, url, re.I) for pattern in source.patterns))
        except Exception:
            pass
    for seed in source.seeds:
        try:
            response = HTTP.get(seed, timeout=30)
            if response.ok: candidates.extend(collect_links(response.text, seed, source.patterns))
        except Exception:
            continue
    out = []
    for url in list(dict.fromkeys(candidates))[: source.max_rows * 4]:
        record = parse_detail(source.name, url)
        if record: out.append(record)
        if len(out) >= source.max_rows: break
        time.sleep(0.15)
    return out


def deduplicate(records: Iterable[Record]) -> list[Record]:
    by_url, by_title = {}, {}
    priority = {"OSHWA认证目录": 4, "GitHub": 3, "GitLab": 2}
    for record in records:
        key = canonical_url(record.url)
        title_key = re.sub(r"\W+", "", record.name.lower())[:100]
        existing = by_url.get(key) or (by_title.get(title_key) if title_key and len(title_key) >= 12 else None)
        if existing is None:
            by_url[key] = record
            if title_key: by_title[title_key] = record
            continue
        old = (existing.data_quality, priority.get(existing.platform, 1), len(existing.description))
        new = (record.data_quality, priority.get(record.platform, 1), len(record.description))
        if new > old:
            by_url.pop(canonical_url(existing.url), None)
            by_url[key] = record
            if title_key: by_title[title_key] = record
    return list(by_url.values())


def normalize_scores(records: list[Record]) -> None:
    ordered = sorted(records, key=lambda record: (record.raw_commercial_score, hashlib.md5(record.project_id.encode()).hexdigest()))
    count, normal = len(ordered), NormalDist()
    for index, record in enumerate(ordered):
        z = normal.inv_cdf((index + 0.5) / count)
        record.normalized_commercial_score = round(max(0.3, min(9.7, 5.4 + 1.45*z)), 2)


def write_csv(records: list[Record], path: Path) -> None:
    fields = list(asdict(records[0]).keys()) if records else list(Record.__dataclass_fields__)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader()
        for record in records: writer.writerow(asdict(record))


def write_xlsx(records: list[Record], source_status: list[dict[str, Any]], output: Path) -> None:
    workbook = xlsxwriter.Workbook(output)
    workbook.set_properties({"title": "开源硬件商业化机会库", "comments": "公开网页自动抓取；需人工复核许可与市场结论"})
    projects = workbook.add_worksheet("项目机会库")
    summary = workbook.add_worksheet("摘要")
    status = workbook.add_worksheet("来源状态")
    method = workbook.add_worksheet("评分方法")

    headers = ["项目ID", "缩略图", "名称", "平台", "原始链接", "发布时间", "最近更新", "类别", "描述", "核心关键词", "市场验证", "典型竞品", "商业价值", "建议改进", "目标客户", "建议售价下限(元)", "建议售价上限(元)", "量产难度", "售后风险", "合规风险", "原始商业评分", "正态化商业评分", "评分理由", "硬件许可", "软件许可", "开源完整度", "数据质量", "审核状态", "缩略图URL", "缩略图类型", "抓取时间"]
    attributes = ["project_id", None, "name", "platform", "url", "published_date", "updated_date", "category", "description", "keywords", "market_validation", "typical_competitors", "commercial_value", "improvement_direction", "target_customer", "suggested_price_low_cny", "suggested_price_high_cny", "manufacturing_difficulty", "after_sales_risk", "compliance_risk", "raw_commercial_score", "normalized_commercial_score", "score_reason", "hardware_license", "software_license", "open_source_completeness", "data_quality", "review_status", "thumbnail_url", "thumbnail_type", "crawl_time"]
    title_fmt = workbook.add_format({"bold": True, "font_size": 16, "font_color": "#FFFFFF", "bg_color": "#17365D", "align": "left", "valign": "vcenter"})
    header_fmt = workbook.add_format({"bold": True, "font_color": "#FFFFFF", "bg_color": "#1F4E78", "border": 1, "align": "center", "valign": "vcenter", "text_wrap": True})
    text_fmt = workbook.add_format({"valign": "top", "text_wrap": True, "border": 1, "border_color": "#D9E2F3"})
    link_fmt = workbook.add_format({"font_color": "#0563C1", "underline": True, "valign": "top", "border": 1, "border_color": "#D9E2F3"})
    number_fmt = workbook.add_format({"num_format": "0.00", "valign": "top", "border": 1, "border_color": "#D9E2F3"})
    integer_fmt = workbook.add_format({"num_format": "0", "valign": "top", "border": 1, "border_color": "#D9E2F3"})
    note_fmt = workbook.add_format({"font_color": "#666666", "italic": True, "text_wrap": True})

    projects.merge_range(0, 0, 0, len(headers)-1, f"开源硬件商业化机会库（{len(records):,}条）", title_fmt)
    projects.write(1, 0, "说明：评分为规则化商业初筛，不代表许可授权；产品开发前必须人工核验许可证、专利、商标和安全合规。", note_fmt)
    projects.set_row(0, 28); projects.set_row(2, 38)
    for column, header in enumerate(headers): projects.write(2, column, header, header_fmt)
    for row_index, record in enumerate(records, start=3):
        projects.set_row(row_index, 72)
        for column, attribute in enumerate(attributes):
            if column == 1:
                formula = f'=IFERROR(IMAGE("{record.thumbnail_url.replace(chr(34), "")}","缩略图",0),"")' if record.thumbnail_url else ""
                projects.write_formula(row_index, column, formula, text_fmt, "") if formula else projects.write_blank(row_index, column, None, text_fmt)
                continue
            value = getattr(record, attribute) if attribute else ""
            if attribute == "url": projects.write_url(row_index, column, value, link_fmt, "打开项目")
            elif isinstance(value, float): projects.write_number(row_index, column, value, number_fmt)
            elif isinstance(value, int): projects.write_number(row_index, column, value, integer_fmt)
            else: projects.write(row_index, column, value, text_fmt)
    projects.freeze_panes(3, 2); projects.autofilter(2, 0, 2+len(records), len(headers)-1)
    widths = [18, 14, 26, 18, 14, 12, 12, 20, 44, 24, 24, 36, 42, 42, 30, 13, 13, 11, 11, 11, 13, 15, 52, 18, 18, 30, 10, 12, 40, 12, 22]
    for index, width in enumerate(widths): projects.set_column(index, index, width)
    score_column = headers.index("正态化商业评分")
    projects.conditional_format(3, score_column, 2+len(records), score_column, {"type": "3_color_scale", "min_color": "#F8696B", "mid_color": "#FFEB84", "max_color": "#63BE7B"})
    for name in ("量产难度", "售后风险", "合规风险"):
        column = headers.index(name); projects.conditional_format(3, column, 2+len(records), column, {"type": "data_bar", "bar_color": "#5B9BD5"})

    platform_counts, category_counts, quality_counts = Counter(r.platform for r in records), Counter(r.category for r in records), Counter(r.data_quality for r in records)
    summary.merge_range("A1:H1", "开源硬件商业化机会库 — 摘要", title_fmt)
    summary.write("A3", "项目总数", header_fmt); summary.write_number("B3", len(records), integer_fmt)
    summary.write("D3", "平台数量", header_fmt); summary.write_number("E3", len(platform_counts), integer_fmt)
    summary.write("G3", "8分以上", header_fmt); summary.write_number("H3", sum(r.normalized_commercial_score >= 8 for r in records), integer_fmt)
    summary.write("A5", "平台", header_fmt); summary.write("B5", "条数", header_fmt)
    for i, (key, value) in enumerate(platform_counts.most_common(), start=5): summary.write(i, 0, key, text_fmt); summary.write_number(i, 1, value, integer_fmt)
    summary.write("D5", "类别", header_fmt); summary.write("E5", "条数", header_fmt)
    for i, (key, value) in enumerate(category_counts.most_common(), start=5): summary.write(i, 3, key, text_fmt); summary.write_number(i, 4, value, integer_fmt)
    summary.write("G5", "数据质量", header_fmt); summary.write("H5", "条数", header_fmt)
    for i, (key, value) in enumerate(sorted(quality_counts.items()), start=5): summary.write(i, 6, key, text_fmt); summary.write_number(i, 7, value, integer_fmt)
    summary.set_column("A:A", 28); summary.set_column("B:B", 12); summary.set_column("D:D", 28); summary.set_column("E:E", 12); summary.set_column("G:G", 16); summary.set_column("H:H", 12)
    if platform_counts:
        chart = workbook.add_chart({"type": "column"}); topn = min(15, len(platform_counts))
        chart.add_series({"name": "项目数", "categories": ["摘要", 5, 0, 4+topn, 0], "values": ["摘要", 5, 1, 4+topn, 1]})
        chart.set_title({"name": "主要平台项目数"}); chart.set_legend({"none": True}); chart.set_y_axis({"major_gridlines": {"visible": False}})
        summary.insert_chart("J3", chart, {"x_scale": 1.35, "y_scale": 1.2})

    status_headers = ["平台", "状态", "抓取条数", "耗时秒", "错误/备注"]
    for column, header in enumerate(status_headers): status.write(0, column, header, header_fmt)
    for row_index, row in enumerate(source_status, start=1):
        for column, header in enumerate(status_headers): status.write(row_index, column, row.get(header, ""), text_fmt)
    status.set_column(0, 0, 28); status.set_column(1, 3, 14); status.set_column(4, 4, 70); status.freeze_panes(1, 0)

    method.merge_range("A1:F1", "评分与使用说明", title_fmt)
    notes = [("原始商业评分", "需求明确度20%、市场验证15%、产品成熟15%、量产可控15%、差异化10%、传播性10%、风险友好度10%、与你的能力匹配5%。"), ("正态化评分", "按全体原始分排序后映射至均值约5.4、标准差约1.45的截断正态分布；大多数项目集中在4–7分，9分以上极少。"), ("竞品与商业价值", "大批量行采用类别规则形成典型竞品方向和初筛建议，并非逐条完成电商审计。高分项目需要二次市场搜索。"), ("许可", "公开可访问不等于允许商用。必须逐项核验硬件、软件、文档、字体、图片、商标和专利许可。"), ("缩略图", "优先使用页面OG产品图；GitHub使用项目卡；缺失时使用平台图，并在缩略图类型中标明。"), ("时间范围", "优先采集2021年1月1日之后创建、认证、更新或仍活跃的项目；日期缺失的公开项目会保留并降低数据质量等级。")]
    method.write("A3", "项目", header_fmt); method.write("B3", "说明", header_fmt)
    for index, (key, value) in enumerate(notes, start=3): method.write(index, 0, key, text_fmt); method.write(index, 1, value, text_fmt)
    method.set_column("A:A", 22); method.set_column("B:B", 110)
    workbook.close()


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--target", type=int, default=3500); parser.add_argument("--out", type=Path, default=Path("data")); args = parser.parse_args(); args.out.mkdir(parents=True, exist_ok=True)
    all_records, status_rows = [], []

    def run_source(name: str, function) -> None:
        started, state, note, rows = time.time(), "成功", "", []
        try:
            rows = function()
            if not rows: state = "无结果"
        except Exception as exc:
            state, note = "失败", repr(exc); print(f"[{name}] fatal: {exc}", file=sys.stderr)
        for record in rows: enrich_record(record)
        all_records.extend(rows)
        status_rows.append({"平台": name, "状态": state, "抓取条数": len(rows), "耗时秒": round(time.time()-started, 1), "错误/备注": note})
        print(f"[{name}] {state}: {len(rows)} rows")

    run_source("OSHWA认证目录", lambda: fetch_oshwa(1100))
    run_source("Hack Club项目库", lambda: fetch_hackclub(220))
    run_source("GitHub", lambda: fetch_github(max(2400, args.target)))
    run_source("GitLab", lambda: fetch_gitlab(650))
    for source in WEB_SOURCES: run_source(source.name, lambda source=source: fetch_web_source(source))

    records = deduplicate(all_records)
    if len(records) > args.target + 900:
        non_github = [record for record in records if record.platform != "GitHub"]
        github = [record for record in records if record.platform == "GitHub"]
        records = non_github + github[:max(0, args.target+500-len(non_github))]
    normalize_scores(records)
    records.sort(key=lambda record: (-record.normalized_commercial_score, -record.raw_commercial_score, record.platform, record.name.lower()))

    write_csv(records, args.out / "hardware_opportunities.csv")
    with (args.out / "hardware_opportunities.jsonl").open("w", encoding="utf-8") as handle:
        for record in records: handle.write(json.dumps(asdict(record), ensure_ascii=False)+"\n")
    with (args.out / "source_status.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["平台", "状态", "抓取条数", "耗时秒", "错误/备注"]); writer.writeheader(); writer.writerows(status_rows)
    summary = {"generated_at": NOW.isoformat(), "cutoff": CUTOFF.date().isoformat(), "records": len(records), "platforms": len(set(record.platform for record in records)), "platform_counts": Counter(record.platform for record in records), "category_counts": Counter(record.category for record in records), "quality_counts": Counter(record.data_quality for record in records), "score_mean": statistics.mean(record.normalized_commercial_score for record in records) if records else 0, "score_stdev": statistics.pstdev(record.normalized_commercial_score for record in records) if len(records)>1 else 0, "gte_8": sum(record.normalized_commercial_score >= 8 for record in records)}
    with (args.out / "summary.json").open("w", encoding="utf-8") as handle: json.dump(summary, handle, ensure_ascii=False, indent=2, default=dict)
    write_xlsx(records, status_rows, args.out / "开源硬件商业化机会库.xlsx")
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=dict))
    if len(records) < 3000:
        print(f"QUALITY GATE FAILED: only {len(records)} records (<3000)", file=sys.stderr); return 2
    if len(set(record.platform for record in records)) < 20:
        print(f"QUALITY GATE FAILED: only {len(set(record.platform for record in records))} platforms (<20)", file=sys.stderr); return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
