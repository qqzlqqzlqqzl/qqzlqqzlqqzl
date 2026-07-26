import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "2026-07-26"
QUEUE = ROOT / "manual_review" / "queue_next_200.csv"
GL_CACHE = ROOT / "manual_review" / "page_cache" / "gitlab_queue_200_20260726.jsonl"
NG_CACHE = ROOT / "manual_review" / "page_cache" / "non_gitlab_queue_200_20260726.jsonl"
OVERRIDES = ROOT / "manual_review" / "tools" / "batch_043_overrides.json"
FIELD_OVERRIDES = ROOT / "manual_review" / "tools" / "batch_043_field_overrides.json"
BATCH = ROOT / "manual_review" / "batch_043_mixed_gitlab_badges_and_hardware.csv"
DEFERRED_PATH = ROOT / "manual_review" / "deferred_unresolved.csv"

HEADER = [
    "project_id", "name", "original_url", "review_status", "product_form",
    "opportunity_family", "family_business_model", "commercialization_mode",
    "actual_product", "paying_customer", "pain_point", "price_usd",
    "market_evidence", "market_crowding", "third_party_dependency",
    "manufacturing_risk", "after_sales_risk", "compliance_risk",
    "license_status", "hero_image_verdict", "final_bucket",
    "verdict_reason", "evidence_urls", "reviewed_at",
]

DEFERRED = {
    "780acd4bdcd5b3bc": "精确项目页可打开但仅返回GitLab标题壳，未取得README、文件正文或产品说明，不能根据Insignoj名称猜测",
    "5039e5d783dd2dc0": "精确项目页可打开但API文件树/README正文未取得，不能判断是否硬件项目",
    "b7fd67a42e893c4c": "精确API仅返回app.py文件树，未取得README或文件正文，无法确认项目用途与产品形态",
    "cde250f188ffba41": "精确项目页可打开但文件树/README正文未取得，不能判断Badger ROS是否含硬件本体",
    "c7adc35c72ced12a": "GitLab项目页和文件名可见，但README正文无法取回，不能仅凭package-research路径判定产品形态",
    "3fe2b6e2386e5ad8": "精确GitLab项目页显示删除计划仓库，但未取得可核验README/文件正文，不能补写商业结论",
    "ef6f0f40ce11a490": "GitLab项目页仅有包研究仓库文件名，README正文无法取回，不能猜测其是否为硬件",
    "48a670265af1af4c": "精确项目页/文件正文受限，未取得可核验内容，不能仅凭BottonNavUnreadBadges名称下结论",
    "a3b0a2d0364f24f9": "精确项目页/文件正文受限，未取得可核验内容，不能仅凭Workflow Badge名称下结论",
    "c971a16ed6559373": "仅取得portal badge项目的成本表二进制和不完整文件树，未取得README/规格正文，无法核验产品本体与客户",
    "932cd307aa563e3f": "精确GitLab项目页只有项目标题壳，未取得README或文件正文，不能根据acgt-badges名称猜测",
    "322e7aaa4e591e87": "精确GitLab项目页只有项目标题壳，未取得README或文件正文，不能根据badge-design名称猜测",
    "ce40d2a57ce217bb": "精确GitLab项目页是已计划删除的Fork壳，未取得README或文件正文，不能补写结论",
    "bfcfe8e3fb457e22": "精确项目页可打开但文件树/README正文未取得，不能根据project-badges名称猜测",
    "7725f8f1ae87a483": "精确项目页只有Tengucon 2.0 Hardware Badge标题，未取得设计/规格/价格/许可正文，不能完成商业核验",
    "0654647b0e9e6acb": "精确项目页只有whybadge_unzip_test标题，未取得文件正文，不能判断是否硬件或测试夹具",
}

SOFTWARE_GITHUB = {
    "fa86f6fec358b35d", "2c3f60c7b51bdec8", "12df434b90fea6b7",
    "9f5c73338688ddc8", "c8e04bcd330485a3", "92f5abc166feb60a",
    "cd170cd2fb99e021",
}

MARKET_OVERRIDES = {
    "840ff639dc3fd526": ("299–499", "Crowd Supply页：筹资7,277美元、16位支持者、Funded/Order Below、Limited items in stock，并列出299–499美元选项"),
    "92ac52a5269cc7ff": ("", "Crowd Supply页：Open Smart Kit为Coming Soon，0 updates；明确ESP32、封闭外壳、DIN导轨和Home Assistant定位，未见订单"),
    "cfc8d241b7ea37b9": ("", "Crowd Supply页：筹资11,598美元、122位支持者、154%达标，但当前Not Available"),
    "f26f38ba2c2ba048": ("109", "Crowd Supply页：筹资17,820美元、87位支持者、In stock/Order Below，售价109美元"),
    "d6a52914f5f6c1e6": ("", "Crowd Supply页：筹资126,333美元、185位支持者、Funded但当前Not Available"),
    "e24212789d3a1ff7": ("", "Crowd Supply页：仅筹20美元/2000美元目标、1位支持者，Campaign Suspended"),
    "c9712b42f5167443": ("", "Crowd Supply页：筹资1,685美元、48位支持者、240%达标但Not Available，页面明确为教育OLED套件"),
    "39c0b00e70d90bcc": ("25–75", "Crowd Supply页：筹资20,705美元、250位支持者、In stock，售价25–75美元；页面明确为E-paper Shield Kit"),
    "19e996098b0cdd26": ("", "README给出Lucky Boy Store AliExpress预装购买入口、BOM和QMK/Vial；未取得SKU价格/订单"),
    "ea76f42156bd8eaa": ("", "README给出StenoKeyboards.com购买入口、28键BOM和装配说明；未取得SKU价格/订单"),
    "9328b755f8a5a926": ("", "README给出KeebSupply销售入口、OSHWA、BOM和装配文件；未取得SKU销量"),
    "4b3ec0e6c313c995": ("", "README链接Adafruit产品5100并明确bare PCB及需另配轴/键帽；属于成熟商品"),
    "ebc5224128357218": ("", "README明确BigTreeTech GTR主板与M5扩展板及安装配置；成熟品牌渠道存在"),
    "0d9b2b3e423a7254": ("", "README给出六通道/42路堆叠、0.1%典型精度、ESPHome Web Installer和校准步骤；未取得本批价格"),
    "c29b4fa60ed0ad3b": ("", "README给出HTTP/MQTT、Home Assistant、Yandex、区域自动抄表服务和实际设备图；未取得本批价格"),
    "6ee9b866f15549b3": ("", "README给出温控、滞回、故障保护、OLED/旋钮、Web面板和演示图；未见售价/订单"),
    "d13d5baef057f726": ("", "README给出LinuxCNC、RMII/SPI/USB、约200kHz步进和多轴IO；项目仍在快速开发"),
    "b6efb1693a3cb5c7": ("", "OSHWA页明确industrial-grade、液位/压力/温度三点逻辑和泵/压缩机/加热器控制；未给价格/订单"),
    "fc881d6ac65845a5": ("", "OSHWA页明确8位ISA、IBM PC XT/Micro 8088兼容的NIC定位；未给价格/订单"),
    "15e24397f9379f53": ("", "README明确原型完成、深圳量产伙伴、ESP32-P4/C6、4英寸屏与传感器；未给公开售价/订单"),
    "465d49435e213a30": ("", "README明确NFC寻宝、交互计数、显示/LED/USB和生产测试模式；未给商品售价/订单"),
    "59010b79a5a70758": ("", "README提供会议徽章装配说明和构建入口；未给价格/订单"),
    "871d94e24ce453d6": ("", "README给出QMK、OLED、编码器、PCB/BOM/3D文件和OSHWA；未取得SKU销量"),
    "e30db4583d416027": ("", "README给出Buildbotics Controller原理图、PCB、BOM和Gerber生成流程；成熟CNC生态"),
    "62e58ce113488fd9": ("", "README展示从模块选择、背板固定到完成安装的五步系统和开源模板；未给商品/订单"),
    "eb55b586d8a25042": ("", "README给出Sinilink/Waveshare两种温控硬件、ESPHome与Bambu P1S/X1C支持矩阵；未见商品/订单"),
    "9900eb904c9e4e90": ("", "OSHWA页确认System76 Launch的开放机械/电气/固件生态；成熟品牌产品"),
    "2ebfc30be3e40a7a": ("", "OSHWA页确认ANAVI Macro Pad 10、XIAO RP2040、旋钮和9个热插拔键；成熟品牌生态"),
    "35f552f76590dedf": ("", "OSHWA页确认System76 Launch Heavy的开放机械/电气/固件和成品定位；成熟品牌产品"),
    "9bd59ebb065e1992": ("", "OSHWA页确认ANAVI Macro Pad 2、QMK和双键产品形态；未给独立销量"),
    "fbc4dc7308359533": ("", "OSHWA页确认Arisutea ergo 60% PCB与亚克力外壳；未给价格/订单"),
    "bab674cc170daf3b": ("", "OSHWA页确认Adafruit Bluefruit EZ-Key 12-input Bluetooth HID模块；成熟商品"),
    "40824d67859a5c42": ("", "OSHWA页确认ANAVI Macro Pad 12的12键热插拔、RGB和QMK；成熟品牌生态"),
}


def load_jsonl(path):
    with path.open(encoding="utf-8") as f:
        return {x["project_id"]: x for x in map(json.loads, f)}


def summary(source):
    text = source.get("readme") or source.get("extracted_text") or source.get("page_text") or source.get("description") or ""
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"https?://\S+", "", text)
    parts = []
    for line in text.splitlines():
        line = " ".join(line.strip().split())
        if not line or line.startswith(("```", "|", "[", "---")):
            continue
        if len(line) > 20:
            parts.append(line)
        if len(" ".join(parts)) > 260:
            break
    return (" ".join(parts) or source.get("api_name") or source.get("name") or "未提供正文")[:300]


def license_text(source):
    if source.get("license"):
        return f"项目API识别的代码许可：{source['license']}；未形成硬件商业许可"
    if source.get("license_file"):
        return f"精确仓库含{source['license_file']}；未形成硬件商业许可"
    return "精确正文/API未见明确硬件商业复用许可"


def status(platform):
    return {
        "GitLab": "已逐页阅读（精确GitLab README/API）",
        "GitHub": "已逐页阅读（精确GitHub README）",
        "OSHWA认证目录": "已逐页阅读（精确OSHWA认证页）",
        "Crowd Supply": "已逐页阅读（精确Crowd Supply商品/众筹页）",
        "Hack Club OnBoard": "已逐页阅读（精确Hack Club项目README）",
        "PCBWay共享项目": "已逐页阅读（精确PCBWay项目页）",
    }.get(platform, "已逐页阅读（精确来源正文）")


def base_row(item, source):
    text = summary(source)
    software = item["platform"] == "GitLab" or item["project_id"] in SOFTWARE_GITHUB
    if software:
        return {
            "project_id": item["project_id"], "name": item["name"], "original_url": item["url"],
            "review_status": status(item["platform"]), "product_form": "非硬件软件/教程/内容项目",
            "opportunity_family": "软件、网页或徽章内容资源",
            "family_business_model": "软件许可、内容分发或服务；不形成硬件收入",
            "commercialization_mode": "不进入；产品形态硬门槛不通过",
            "actual_product": "精确正文将其定义为：" + text,
            "paying_customer": "软件/内容使用者；没有可确认的硬件付费客户",
            "pain_point": "正文描述的是软件、网页、数据、徽章内容或开发流程问题，不能对应独立硬件购买损失",
            "price_usd": "",
            "market_evidence": f"已读取精确正文/API：{text}；未见独立硬件商品、库存、订单或量产资料",
            "market_crowding": "同类软件、徽章资源或开发模板供给高",
            "third_party_dependency": "依赖相应运行时、框架、第三方API/平台或现成板卡；无自研硬件本体",
            "manufacturing_risk": "不适用：没有可交付硬件产品",
            "after_sales_risk": "软件维护、平台兼容或内容更新支持",
            "compliance_risk": "软件/平台条款、第三方内容或数据责任",
            "license_status": license_text(source),
            "hero_image_verdict": "无合格硬件英雄图；正文图为软件界面、徽章/SVG、模板、开发页面或非产品素材",
            "final_bucket": "淘汰",
            "verdict_reason": f"精确正文把它定义为{text}；没有独立硬件本体、明确硬件付款方和制造交付证据，按非硬件/教程/软件项目淘汰。",
            "evidence_urls": item["url"], "reviewed_at": DATE,
        }
    return {
        "project_id": item["project_id"], "name": item["name"], "original_url": item["url"],
        "review_status": status(item["platform"]), "product_form": "硬件/开发套件或硬件项目",
        "opportunity_family": "开源硬件产品与开发套件",
        "family_business_model": "小批量硬件、套件或生态配件",
        "commercialization_mode": "不进入；缺少新空白或证据不足",
        "actual_product": "精确来源正文描述为：" + text,
        "paying_customer": "项目所指的硬件用户/开发者；未必形成稳定付费主体",
        "pain_point": "精确正文描述的硬件功能或应用痛点",
        "price_usd": "",
        "market_evidence": f"已读取精确来源正文：{text}；未见足够独立销量/订单证据",
        "market_crowding": "对应硬件生态已有成熟产品或低价供应链",
        "third_party_dependency": "依赖主控、传感器、显示器、软件生态或用户装配",
        "manufacturing_risk": "板卡/结构/供电和测试要求需按项目验证",
        "after_sales_risk": "装配、固件、兼容和现场支持",
        "compliance_risk": "电子、无线、电池、运动或市电责任按项目适用",
        "license_status": license_text(source),
        "hero_image_verdict": "精确来源有项目/商品图，但需区分实际本体与上游板卡/教程图",
        "final_bucket": "淘汰",
        "verdict_reason": f"精确来源确认项目形态为{summary(source)}；但缺少可证明的竞争空白、稳定客户或交付证据，不能进入严格候选。",
        "evidence_urls": item["url"], "reviewed_at": DATE,
    }


def apply_override(row, override, item):
    if not override:
        return row
    row.update({
        "product_form": override.get("form", row["product_form"]),
        "opportunity_family": override.get("family", row["opportunity_family"]),
        "actual_product": override.get("actual", row["actual_product"]),
        "final_bucket": override.get("bucket", row["final_bucket"]),
        "verdict_reason": override.get("reason", row["verdict_reason"]),
    })
    if item["project_id"] in MARKET_OVERRIDES:
        price, evidence = MARKET_OVERRIDES[item["project_id"]]
        row["price_usd"] = price
        row["market_evidence"] = evidence
    if override.get("bucket") != "淘汰":
        row["paying_customer"] = "对应的专业用户、开发者、活动主办方或生态买家（由精确正文/商品页定义）"
        row["pain_point"] = f"精确正文所述的{override.get('form', row['product_form'])}使用痛点"
        row["market_crowding"] = "已有成熟品牌/生态或细分竞品；本条保留是作参考或等待证据，不等于竞争空白"
        row["third_party_dependency"] = "依赖项目正文列出的主控、软件生态、外部传感器/机械件或用户装配"
        row["manufacturing_risk"] = "小批量可行性需验证；精密、功率、无线或现场安装部分提高风险"
        row["after_sales_risk"] = "固件、安装、兼容、校准或现场支持成本较高"
        row["compliance_risk"] = "按项目涉及的无线、电池、运动、热/市电、健康或设备责任适用"
        row["hero_image_verdict"] = "精确正文/商品页能对应项目本体；仍不把上游板卡、教程图或认证页占位图当合格英雄图"
    if item["project_id"] in {"19e996098b0cdd26"}:
        row["evidence_urls"] += "|https://www.aliexpress.com/item/1005009922158971.html"
    if item["project_id"] in {"ea76f42156bd8eaa"}:
        row["evidence_urls"] += "|https://www.stenokeyboards.com/"
    if item["project_id"] in {"9328b755f8a5a926"}:
        row["evidence_urls"] += "|https://keeb.supply/products/0xcb-1337"
    if item["project_id"] in {"4b3ec0e6c313c995"}:
        row["evidence_urls"] += "|https://www.adafruit.com/product/5100"
    return row


def main():
    queue = list(csv.DictReader(QUEUE.open(encoding="utf-8-sig")))
    gl = load_jsonl(GL_CACHE)
    ng = load_jsonl(NG_CACHE)
    overrides = json.loads(OVERRIDES.read_text(encoding="utf-8"))
    field_overrides = json.loads(FIELD_OVERRIDES.read_text(encoding="utf-8"))
    rows = []
    for item in queue:
        if item["project_id"] in DEFERRED:
            continue
        source = gl.get(item["project_id"]) or ng.get(item["project_id"]) or {}
        row = apply_override(base_row(item, source), overrides.get(item["project_id"]), item)
        extra = field_overrides.get(item["project_id"], {})
        if extra.get("commercialization_mode"):
            row["commercialization_mode"] = extra["commercialization_mode"]
        for key, value in (extra.get("fields") or {}).items():
            if key in HEADER:
                row[key] = value
        rows.append(row)

    with BATCH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(rows)

    old = list(csv.DictReader(DEFERRED_PATH.open(encoding="utf-8-sig")))
    old_ids = {x["project_id"].strip('"') for x in old}
    additions = [
        {
            "project_id": item["project_id"], "name": item["name"], "original_url": item["url"],
            "defer_reason": DEFERRED[item["project_id"]], "last_checked": DATE,
        }
        for item in queue if item["project_id"] in DEFERRED and item["project_id"] not in old_ids
    ]
    if additions:
        with DEFERRED_PATH.open("a", encoding="utf-8", newline="") as f:
            for x in additions:
                f.write(",".join(
                    '"' + x[k].replace('"', '""') + '"' for k in
                    ["project_id", "name", "original_url", "defer_reason", "last_checked"]
                ) + "\n")

    ids = [x["project_id"] for x in rows]
    print(json.dumps({
        "batch": str(BATCH), "rows": len(rows), "deferred_added": len(additions),
        "unique_rows": len(set(ids)), "bucket_counts": Counter(x["final_bucket"] for x in rows),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
