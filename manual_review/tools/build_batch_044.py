import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CACHE_PATH = ROOT / "manual_review" / "page_cache" / "queue_044_20260726.jsonl"
QUEUE_PATH = ROOT / "manual_review" / "queue_next_200.csv"
OUTPUT_PATH = ROOT / "manual_review" / "batch_044_exact_page_v3.csv"

FIELDS = [
    "project_id",
    "name",
    "original_url",
    "review_status",
    "product_form",
    "opportunity_family",
    "family_business_model",
    "commercialization_mode",
    "actual_product",
    "paying_customer",
    "pain_point",
    "price_usd",
    "market_evidence",
    "market_crowding",
    "third_party_dependency",
    "manufacturing_risk",
    "after_sales_risk",
    "compliance_risk",
    "license_status",
    "hero_image_verdict",
    "final_bucket",
    "verdict_reason",
    "evidence_urls",
    "reviewed_at",
]


# These records have a strong, specific outcome but still lack enough independent
# pricing, delivery, repeatability or commercial evidence for the strict shortlist.
WATCH_IDS = {
    "d9ba92b1cf8e932e",  # OpenPLC
    "5f9a1d3da219db22",  # Open Movement
    "2f52c69c01379287",  # iHeater
    "3dbf6a60c52f0526",  # irriBRANT
    "c5388e957870adc4",  # INTARSO
    "7c559f88cca98148",  # Yottasynth
    "c599bd35232b19a7",  # HTXStudio
    "34dd8168eea5d053",  # poseidon
    "fb85cf9aa60d4b49",  # Wearable Air Quality Pendant
    "529e2b7b0a7247c5",  # Open Pill Reminder
}


# Existing products, mature families, research references and technical designs
# are retained as market references, not as unoccupied opportunities.
MARKET_IDS = {
    "12137fce9889d3e4",
    "38f15d228622d1bb",
    "aa005c1ab6dc70af",
    "a8b6157d5ceb0b53",
    "0f258f70a7cc47b8",
    "45f7967f4e665c07",
    "d8feb7fec89fbdbf",
    "30372a642d97cf6a",
    "8c4d9e4c02921d75",
    "5bfe9f2fb9084115",
    "aabda3f0f9c75545",
    "c810e774996b0219",
    "fb247352f0792dea",
    "e887e03eafc51d74",
    "31311ad46285bde9",
    "4738b5fd7c2041c9",
    "9e3905c52c2486b1",
    "6182e2bed3a9e0a8",
    "055c3736027c8834",
    "1e46dc09386103fe",
    "7669299c87e5910f",
    "7de090030b8c4546",
    "c66f45eb565bf893",
    "cf6fd5569542d865",
    "a852ff2e83c0c02b",
    "741b9307161af142",
    "705d10ffd03bbad9",
    "60e282e85609c912",
    "395a8811fc65a930",
    "33875274a42e2a1e",
    "631ee59144ff1d9e",
    "90d99ff0063bf604",
    "f2dbd334ce00d5f2",
    "62cd5b1a7ccd8b48",
    "03b05e54f7601337",
    "5457787c3417b06d",
    "572caac5ee0df2eb",
    "88df7696fe306d30",
    "d47322c10d109943",
    "89d35cdd0a34e5f0",
    "a278ae29374b2052",
    "0e2bae50548ed35d",
    "dd61b9799fc7fc99",
    "e10f615c08a69fbc",
    "1fbb5d0e9349ff0e",
    "9129be79eeacdf21",
    "62ce2c34396e550e",
    "308257e0a53c4fad",
    "e59f4c9858e8a7e3",
    "f7790787adcbc836",
    "48d90e66c4ed34e1",
    "c11f6019237e6f28",
    "3fcaaede63f06531",
    "87dc146d5d7f3c0a",
    "86aeb91f9a96385c",
    "5850ffb806d3c9ef",
    "dcf33d16714087dd",
    "568761481935973e",
    "9817a9782f52a77a",
    "9380c9f411de0077",
    "1400000000000000",  # harmless sentinel to keep the set visually grouped
}


# These are software, libraries, pages, tutorials or security/automation demos
# even when their names contain a hardware keyword.
SOFTWARE_IDS = {
    "b0c65812feb80289",
    "9b59f24556273137",
    "e254130484e75dea",
    "78520a5118af65a8",
    "3876641795693bb7",
    "68a65a87da50193a",
    "a78937a5ca0a0478",
    "013435140ef13622",
    "59bc4b8600c4bbf8",
    "f51c5729f034113c",
    "8801ba22d92b83c2",
    "10b0083009ac742c",
    "b1dcea9dd13f4a64",
    "51b01f9e8098ab9c",
    "66c06565981ec43b",
    "e4c0578a52340240",
    "50f88e14ee01df1b",
    "caed937a6cda0f33",
    "cdf3f9e4c80a431d",
    "d20c41e537266633",
    "1140000000000000",
    "c93ef5623b3dd823",
    "2b52d81c4e623bb2",
    "d70fb91e88ee2276",
    "163b1f8dda35e4f4",
    "400722c203375457",
    "afd31523503977f0",
    "b6717e8fd341d70e",
    "60c5671da5869cdf",
    "e98c3d8fdcdf70ac",
    "8bd2c9ea0d40492a",
    "3039abec41db3304",
    "6343b9be45a058f2",
    "c807ba6145c96004",
    "1560000000000000",
    "1580000000000000",
    "0c186e011ca6513f",
    "446f78662abe4298",
    "b1ee29c65b968646",
    "0dd46c667f6e506d",
    "f5978963a8f6c4e6",
}


DEFERRED_REASONS = {
    "b383fb5982f6b4fc": "GitLab 项目页只有标题、提交数和加载壳，README/API 正文未取得，无法判断徽章是否有实际硬件。",
    "6b2dc67b6043485b": "GitLab 项目页只有 saintcon-minibadge-training 的加载壳，未取得精确 README/API 正文，不能按名称猜测产品形态。",
    "7b2240c7f7606ea3": "GitHub 仓库及精确 README 返回 404，源记录只有项目标题，无法确认是游戏、软件还是硬件。",
    "e6c3fdee67f39920": "GitHub 仓库及精确 README 返回 404，源记录只有项目标题，无法确认是游戏、软件还是硬件。",
    "d980f935c1732d31": "Arduino-UNO-for-Absolute-Beginners 的 GitHub 精确页面返回 404，不能仅凭名称归为教程。",
    "52d6df67c7e83dd7": "keypad-without-library 的 GitHub 精确页面返回 404，无法取得 README、文件树或许可证。",
    "603de0c4d59e67ce": "Akita-Harrier 的 GitHub 精确页面返回 404，源记录没有可靠产品正文。",
    "5318c5d0e318147f": "Robatic-ARM 的 GitHub 精确页面返回 404，不能仅凭名称猜测是否有可交付机械臂。",
    "cb3a999668e235ef": "PCBWay URL 返回共享项目分类目录而非 Electronic Games 项目正文，正文没有该条目的规格、价格、文件或主图。",
    "ae2a8609fbc3a1ed": "PCBWay URL 返回 Keyboards 分类/共享项目目录而非具体键盘项目正文，无法逐条核验产品本体和市场证据。",
}


SPECIAL = {
    "d9ba92b1cf8e932e": {
        "product_form": "垂直专业设备/工业控制原型",
        "opportunity_family": "小型PLC与工业边缘控制器",
        "family_business_model": "工业控制硬件、工程集成与维护服务",
        "commercialization_mode": "保留为观察，不进入严格候选",
        "actual_product": "基于 ESP32、MicroPython 和 DIN 导轨安装的开放式 PLC；README 列出 24V 直流供电、2 路数字输入、NPN 开漏输出、RS-485、Wi-Fi 和 Bluetooth。",
        "paying_customer": "小型自动化集成商、设备改造者、工业控制教学实验室",
        "pain_point": "需要低成本、可修改的 PLC 原型来做流程控制和机器人/设备联动，但商业 PLC 还需要更完整的 I/O、隔离和认证。",
        "price_usd": "",
        "market_evidence": "精确 README 给出 I/O、ESP32 规格和 DIN 导轨安装，并列出 2019-2020 年的设计研讨记录；未见售价、订单、现场案例、认证或持续交付证据。",
        "market_crowding": "高；低价 PLC、ESP32 工控板和成熟品牌 PLC 已有大量替代品",
        "third_party_dependency": "ESP32、MicroPython、24V 现场 wiring、外部传感器/执行器；未见完整隔离与端子系统说明",
        "manufacturing_risk": "工业现场需要电源/IO 隔离、EMC、浪涌和端子可靠性验证；README 只证明原型规格",
        "after_sales_risk": "PLC 一旦用于现场控制，需要长期固件、接线、故障诊断和兼容支持",
        "compliance_risk": "工业控制、24V 现场线和机器人责任边界需要 EMC、安规和应用责任评估",
        "license_status": "正文倡导开源硬件/软件，但未在已读 README 中给出明确硬件许可证版本，商业复用边界未闭合",
        "hero_image_verdict": "README 只有 KiCad 3D 渲染图等项目图，未取得独立可核验的量产设备英雄图",
        "verdict_reason": "精确 README 把它写成带 DIN 导轨安装和 24V I/O 规格的 ESP32 PLC，并说明面向工业流程控制；但没有价格、订单、认证或现场重复交付证据，且通用 PLC/ESP32 工控板竞争已很拥挤，因此只列观察名单。",
        "evidence_urls": "https://github.com/FunPythonEC/OpenPLC-IIOTv0.1",
    },
    "5f9a1d3da219db22": {
        "product_form": "独立传感器/研究设备",
        "opportunity_family": "可穿戴运动与生理数据记录器",
        "family_business_model": "研究设备、小批量传感器与数据分析支持",
        "commercialization_mode": "保留为观察，不进入严格候选",
        "actual_product": "Newcastle University Open Movement 项目的一组可嵌入运动传感器与记录设备，README 列出 AX3/AX6、WAX3、WAX9、WAM、BuildAX 和 WeighAX 家族及配套分析工具。",
        "paying_customer": "大学研究团队、行为/运动研究者、建筑和重量监测项目",
        "pain_point": "研究人员需要可嵌入、可自定义、能导出原始数据的运动/声音/环境记录器，而不是封闭消费手环。",
        "price_usd": "",
        "market_evidence": "README 明确项目源自 Newcastle University，并列出多个设备家族和 OMGUI；已读正文没有当前售价、订单、库存或商业支持承诺。",
        "market_crowding": "中高；研究级 IMU、活动记录器和商业可穿戴传感器已有成熟供应",
        "third_party_dependency": "传感器、纽扣电池/电池仓、定制外壳和 OMGUI/数据流程；不同设备家族还需分别维护",
        "manufacturing_risk": "小型化、低功耗、外壳佩戴和多型号装配测试要求高",
        "after_sales_risk": "研究数据一致性、时间同步、固件刷写和分析软件兼容需要持续支持",
        "compliance_risk": "若用于人体研究需伦理、数据隐私和研究设备责任审查，不能直接当医疗器械",
        "license_status": "软件/固件 BSD-2-Clause；硬件、外壳和文档 CC BY 3.0，需分别保留署名和许可边界",
        "hero_image_verdict": "README 主要提供设备家族链接，没有当前可独立核验的销售级成品主图",
        "verdict_reason": "精确 README 明确列出 AX3/AX6、WAX3、WAX9、WAM、BuildAX 和 WeighAX 等真实设备方向，并给出 BSD/CC BY 许可；但没有当前价格、订单或交付链路，研究设备的多型号支持和数据责任也较重，暂列观察名单。",
        "evidence_urls": "https://github.com/openmovementproject/openmovement",
    },
    "2f52c69c01379287": {
        "product_form": "垂直专业设备/3D打印机腔体温控控制器",
        "opportunity_family": "3D打印机加热腔体与温度管理",
        "family_business_model": "打印机改装控制器、配件销售与安装支持",
        "commercialization_mode": "保留为观察，不进入严格候选",
        "actual_product": "iHeater 是独立运行或通过 USB 接入 Klipper 的 3D 打印机加热腔体控制固件/配套设备，目标是给没有空闲加热器、风扇或热敏输入的打印机增加稳定腔体温控。",
        "paying_customer": "需要打印 ABS/ASA 等收缩敏感材料、且原机主板接口不足的 3D 打印机用户",
        "pain_point": "封闭或低价打印机无法稳定加热腔体，导致 ABS/ASA 翘曲、层间粘附和打印失败。",
        "price_usd": "",
        "market_evidence": "README 提供发布徽章、在线文档、Telegram 和 standalone/Klipper 两种工作方式，但未给出硬件售价、订单或独立产品库存。",
        "market_crowding": "中高；打印机腔体加热改装、温控板和成套 enclosure 方案较多",
        "third_party_dependency": "外部加热器、空气/加热器热敏、打印机主板或 Klipper、继电器/电源与机箱结构",
        "manufacturing_risk": "加热功率、热敏校准、继电器/固态开关和机箱热管理需要逐机验证",
        "after_sales_risk": "不同打印机主板、热敏类型和 Klipper 配置会造成大量兼容与故障诊断工作",
        "compliance_risk": "加热器存在过温、起火和电气安全风险，需失效保护与当地安规评估",
        "license_status": "README 明确为 GPLv3 非商业使用；商业制造/销售需要另外取得许可，不能直接复用",
        "hero_image_verdict": "README 有 iHeater 设备图和错误状态图，但未取得可独立核验的销售级成品主图",
        "verdict_reason": "精确 README 明确 iHeater 解决专有打印机没有腔体加热接口的问题，并支持 standalone 与 Klipper；不过正文没有价格/订单，且许可明确限定 GPLv3 非商业使用，加热安全和逐机兼容风险也高，因此只列观察名单。",
        "evidence_urls": "https://github.com/pavluchenkor/iHeater-Standalone-Firmware|https://docs.idryer.org/iHeater/",
    },
    "3dbf6a60c52f0526": {
        "product_form": "独立设备/户外控制器原型",
        "opportunity_family": "多区域智能灌溉控制器",
        "family_business_model": "园艺/农场控制器、小批量硬件与安装服务",
        "commercialization_mode": "保留为观察，不进入严格候选",
        "actual_product": "irriBRANT 是基于 XIAO ESP32-C6、MCP23017 和 9 路光耦隔离 24VAC triac 输出的灌溉控制器，提供本地排程、离线运行、Master Valve 和 Home Assistant/ESPHome 集成。",
        "paying_customer": "家庭灌溉安装者、小型园艺/温室经营者、需要本地自动化的 DIY 用户",
        "pain_point": "传统定时器缺少离线排程、雨锁、主阀时序和可诊断的多区域控制，户外阀门容易出现水锤与误动作。",
        "price_usd": "",
        "market_evidence": "README 给出 PCB v1.2、v4.0 stable/v4.3 firmware、真实阀门测试、现场验证和长期可靠性测试状态；仍未见售价、订单、安装商或复购数据。",
        "market_crowding": "中高；灌溉定时器、Rain Bird/Hunter 控制器和 Home Assistant DIY 方案都很成熟",
        "third_party_dependency": "Seeed XIAO ESP32-C6、MCP23017、ESPHome、Home Assistant、24VAC 变压器和现场电磁阀",
        "manufacturing_risk": "24VAC 输入、triac、MOV、NTC、保险丝和户外接线需要一致性测试、防水外壳和安装规范",
        "after_sales_risk": "阀门/变压器/接线差异、Wi-Fi、OTA 和现场故障诊断会带来安装支持负担",
        "compliance_risk": "户外电气、进水、浪涌和水系统责任需要按当地电气规范与防护等级评估",
        "license_status": "README 仅说明面向 educational/maker/home automation，未给出完整硬件许可证和商业商标边界",
        "hero_image_verdict": "README 包含真实板卡照片和现场说明，但仍未独立核验成套户外产品英雄图",
        "verdict_reason": "精确 README 已把 irriBRANT 推到 PCB v1.2、现场阀门验证和长期可靠性测试阶段，且明确有 9 区、本地排程和主阀逻辑；但没有价格、订单和安装交付证据，户外 24VAC 与防水责任也尚未闭合，暂列观察名单。",
        "evidence_urls": "https://github.com/Renbrant/ESP32-C6-Irrigation-Controller|https://www.home-assistant.io/|https://esphome.io/",
    },
    "c5388e957870adc4": {
        "product_form": "垂直专业设备/靶场机器人控制系统",
        "opportunity_family": "射击靶场目标机器人改装",
        "family_business_model": "靶场设备改装、控制系统集成与维护",
        "commercialization_mode": "保留为观察，不进入严格候选",
        "actual_product": "INTARSO 靶场目标机器人电子改装系统：ESP32、VESC FOC、电机、2D LiDAR 和 3D 打印外壳控制沿轨目标车，可把纸靶送至 24m、旋转展示并回传命中遥测。",
        "paying_customer": "射击靶场运营者、靶场设备集成商和原有 INTARSO 设备维护方",
        "pain_point": "靶场需要远程、可重复且带命中/距离反馈的靶标回收，减少人员进入射击区和人工操作。",
        "price_usd": "",
        "market_evidence": "README 说明项目由 AMJE Arts et Métiers Junior Études 与 JEECE 交付，并列出 24m、VESC、LiDAR 和无线平板界面；未见售价、订单、批量交付或靶场客户合同。",
        "market_crowding": "低到中；靶场自动靶机是窄市场，但已有专业设备和安全认证门槛",
        "third_party_dependency": "INTARSO 原机器人、VESC、LiDAR、ESP32、轨道和靶场电源/通信设施",
        "manufacturing_risk": "机械轨道、车体防护、LiDAR 安装、电机控制和抗冲击结构需要现场调试",
        "after_sales_risk": "射击环境损坏、轨道磨损、靶纸/命中检测和现场维护要求高",
        "compliance_risk": "移动机械与射击场安全责任极高，任何失控都可能造成严重人身风险",
        "license_status": "README 标注 MIT，但第三方 VESC、LiDAR、原机器人和外壳资料的再分发边界仍需分别确认",
        "hero_image_verdict": "README 有系统说明与硬件标注，但未取得可独立核验的量产靶场设备主图",
        "verdict_reason": "精确 README 明确这是为 INTARSO 靶场目标机器人交付的控制系统，而不是普通 ESP32 小车；它有专业客户和真实任务，但价格、重复交付、维护和靶场安全责任都没有独立证据，因此只列观察名单。",
        "evidence_urls": "https://github.com/c5388e957870adc4/INTARSO-Shooting-Range-Target-Robot",
    },
    "7c559f88cca98148": {
        "product_form": "独立乐器原型",
        "opportunity_family": "触屏合成器与波斯/伊朗调式乐器",
        "family_business_model": "小批量专业乐器、固件升级与音乐家支持",
        "commercialization_mode": "保留为观察，不进入严格候选",
        "actual_product": "Yottasynth 是带触摸屏、5 个情境旋钮、琶音器、16 步音序器和 Persian/Iranian 调式支持的开源单声部触屏合成器。",
        "paying_customer": "使用波斯/伊朗调式的音乐家、现场演奏者和声音设计者",
        "pain_point": "通用合成器通常没有直接可用的 Persian/Iranian 调律与页面化演奏工作流，需要自行配置音阶和控制器。",
        "price_usd": "",
        "market_evidence": "README 说明固件已经可演奏并处于 active work-in-progress，提供 GitHub Sponsors/Ko-fi 支持入口；未见售价、库存、用户量或出货记录。",
        "market_crowding": "中；合成器市场拥挤，但伊朗调式与触屏工作流是较窄的差异点",
        "third_party_dependency": "触摸屏、MCU/开发板、旋钮、USB MIDI 和外壳结构；需自建硬件装配和校准流程",
        "manufacturing_risk": "触摸屏、旋钮手感、噪声、音频输出和外壳装配决定演奏体验，当前仍是 WIP",
        "after_sales_risk": "固件版本、音色/调律数据、MIDI 兼容和现场演出故障支持压力大",
        "compliance_risk": "音频设备电气安全风险低，但 USB、音频输出和商标/音色内容仍需合规边界",
        "license_status": "README 声明 GPLv3，并注明部分衍生组件保留各自许可；商业硬件需核对各组件边界",
        "hero_image_verdict": "README 含 prototype/board 照片和界面截图，但未取得销售级成品主图",
        "verdict_reason": "精确 README 已实现触屏页面、琶音/音序和多种波斯调式，且明确仍是 active work-in-progress；它的差异化方向值得观察，但没有价格、销售和稳定硬件交付证据，不能升为严格候选。",
        "evidence_urls": "https://github.com/yottanami/yottasynth|https://yottanami.com/",
    },
    "c599bd35232b19a7": {
        "product_form": "独立成品/无障碍输入设备原型",
        "opportunity_family": "单手机械键盘与辅助输入设备",
        "family_business_model": "辅助技术定制、无障碍键盘小批量制造与服务",
        "commercialization_mode": "保留为观察，不进入严格候选",
        "actual_product": "HTXStudio 单手机械键盘，集成轨迹球、滚轮、方向键和左右手变体；主控为 STM32G431CBU6，固件使用 QMK，包含多块键盘/控制 PCB、FPC 和 3D 打印结构件。",
        "paying_customer": "单侧上肢功能受限的电脑用户、康复机构和辅助技术服务商",
        "pain_point": "页面描述的用户因右手永久失去功能，需要在键盘和鼠标之间切换，导致打字慢且疲劳；单手键盘把输入与指针控制合在一侧。",
        "price_usd": "",
        "market_evidence": "嘉立创页面显示 2025-04-29 创建、2025-05-23 更新，附件下载次数约 63-294；BOM 页面仍写暂无 BOM，未见售价、订单、用户试用或机构采购。",
        "market_crowding": "中；无障碍输入设备有专门供应商，但定制单手+轨迹球组合仍属窄市场",
        "third_party_dependency": "STM32G431、QMK、ALPS/Cherry 轴体、轨迹球、滚轮、FPC、3D 打印件与机械五金",
        "manufacturing_risk": "左右手/大小键盘多版本、四层/双层 PCB、FPC 方向和大量打印件使装配与质检复杂",
        "after_sales_risk": "需要按用户肢体尺寸、键位、轨迹球和固件布局定制，维修/替换件支持负担高",
        "compliance_risk": "辅助技术设备涉及人体工学与责任边界，不能在未验证时宣称医疗/康复效果",
        "license_status": "页面标注 MIT，但知识产权/复刻说明又写明仅供学习交流、不得商业售卖，存在明显许可冲突，必须先向作者澄清",
        "hero_image_verdict": "页面含结构、PCB 和附件信息，但设计图预览写着未生成，未取得可独立核验的销售级成品英雄图",
        "verdict_reason": "精确嘉立创正文给出了明确的单手输入痛点、STM32/QMK 主控和轨迹球结构，说明它确实不是普通宏键盘；但没有 BOM/价格/订单，页面同时出现 MIT 与禁止商业使用的冲突，暂列观察名单而不作商业复刻建议。",
        "evidence_urls": "https://oshwhub.com/htx-studio/One-Handed_Keyboard",
    },
    "34dd8168eea5d053": {
        "product_form": "垂直专业设备/实验室注射泵与显微镜系统",
        "opportunity_family": "开源生物仪器与低成本微流控",
        "family_business_model": "实验室设备小批量制造、耗材与技术支持",
        "commercialization_mode": "保留为观察，不进入严格候选",
        "actual_product": "Poseidon 是可定制的开源注射泵和显微镜系统，用 3D 打印结构、标准电机/注射器和开源软件服务生物实验与微流控流程。",
        "paying_customer": "大学/科研机构的生物实验室、微流控研究者和教学实验室",
        "pain_point": "商业注射泵和显微镜成本高且封闭，研究者需要可修改、可重复的低成本实验设备。",
        "price_usd": "",
        "market_evidence": "README 链接到文档、论文和 Metafluidics，并记录过压力/结构失效与加固；未见销售价格、订单、校准证书或持续商业交付。",
        "market_crowding": "中；开源注射泵和实验室设备有多个项目，商业泵/显微镜品牌成熟",
        "third_party_dependency": "3D 打印 PLA、标准电机/注射器、显微镜光学件、驱动板和上游开源泵设计",
        "manufacturing_risk": "流量重复性、丝杆/注射器配合、压力、光学对准和打印件耐久性需要校准",
        "after_sales_risk": "实验流程、耗材、清洁、软件和校准问题会造成专业支持成本",
        "compliance_risk": "涉及有机溶剂、实验压力和生物样品，README 已明确安全警告，不能当医疗器械销售",
        "license_status": "README 同时引用多个开源项目、论文和 Metafluidics 资料；具体硬件/软件许可证需按各上游组件逐项核对",
        "hero_image_verdict": "README 有项目 logo、结构和示意图，但未取得可独立核验的销售级实验室设备主图",
        "verdict_reason": "精确 README 明确 Poseidon 是注射泵+显微镜的开源生物仪器，并记录了压力/结构改进和上游论文；但没有价格、订单、校准与交付证据，且实验室安全和多上游许可边界复杂，暂列观察名单。",
        "evidence_urls": "https://github.com/pachterlab/poseidon|https://pachterlab.github.io/poseidon/|https://metafluidics.org/devices/minidrops/",
    },
    "fb85cf9aa60d4b49": {
        "product_form": "独立可穿戴监测器原型",
        "opportunity_family": "可穿戴 TVOC 室内空气质量监测",
        "family_business_model": "小型环境传感器、定制外壳与数据服务",
        "commercialization_mode": "保留为观察，不进入严格候选",
        "actual_product": "基于 STM32U083、SGP40 TVOC 传感器、Li-Po、电池充电和 RGB/蜂鸣器提示的可穿戴空气质量 pendant，README 给出硬件表和 TVOC 分级。",
        "paying_customer": "关注室内空气的个人、学校/办公室环境监测者和轻量化 IoT 集成者",
        "pain_point": "用户需要不依赖手机屏幕、能在空气质量变差时立即提醒的便携设备。",
        "price_usd": "",
        "market_evidence": "README 给出完整器件表、充电和报警逻辑，并把 BLE/APP/数据记录列为未来改进；未见价格、校准数据、订单或用户测试。",
        "market_crowding": "高；SGP40 模块、可穿戴空气质量计和室内传感器产品很多",
        "third_party_dependency": "STM32U083、Sensirion SGP40、MCP73832、Li-Po 电池、3D 打印外壳和 Arduino 库",
        "manufacturing_risk": "TVOC 传感器环境补偿、外壳通风、低功耗、充电和蜂鸣器一致性需要实测",
        "after_sales_risk": "传感器漂移、电池寿命和阈值误报会带来校准与换件支持",
        "compliance_risk": "空气质量提示不能直接宣称健康/医疗结论，电池与充电仍需安全评估",
        "license_status": "README 标注 MIT；第三方传感器库和硬件数据表仍需分别遵守其条款",
        "hero_image_verdict": "README 列出 PCB、装配和外壳章节，但文字不足以证明这些是可复核成品照片，暂不视为销售级英雄图",
        "verdict_reason": "精确 README 已描述可穿戴 TVOC 设备、STM32U083/SGP40 器件和分级报警，产品形态比普通传感器模块完整；但校准、价格、订单和用户证据都缺失，且空气质量健康表述需要克制，暂列观察名单。",
        "evidence_urls": "https://github.com/SivadhasGanamoorthy/Wearable-Air-Quality-Pendant",
    },
    "529e2b7b0a7247c5": {
        "product_form": "独立成品/家庭用药提醒盒原型",
        "opportunity_family": "离线用药提醒与记录设备",
        "family_business_model": "家用提醒设备、定制外壳与长期支持",
        "commercialization_mode": "保留为观察，不进入严格候选",
        "actual_product": "Open Pill Reminder 是离线优先的开源药盒项目，强调本地提醒、确认和记录，并明确声明版本 0.1 不是医疗器械、不识别药物或剂量。",
        "paying_customer": "需要简单提醒的个人、照护者和家庭护理场景",
        "pain_point": "用户希望在无云服务/无账号的情况下获得本地提醒和服药确认，而不愿承担复杂的医疗 App 依赖。",
        "price_usd": "",
        "market_evidence": "精确 README 明确版本 0.1 的边界和离线定位，但未见硬件价格、订单、跌落/误触测试或照护机构试用。",
        "market_crowding": "中高；药盒、手机提醒和成熟远程照护设备已有大量产品",
        "third_party_dependency": "MCU、显示/蜂鸣器、按键、RTC、电池/电源和外壳；具体硬件资料需按仓库文件树继续核对",
        "manufacturing_risk": "提醒时序、断电保持、按键耐久、药盒结构和电池安全需要完整验证",
        "after_sales_risk": "误提醒、漏提醒、时间漂移和用户误操作都会造成高支持负担",
        "compliance_risk": "README 明确不是医疗器械；若销售时暗示治疗/依从性效果，会触发医疗与责任风险",
        "license_status": "README 说明项目开源，但本次缓存正文未给出完整硬件许可证版本，需继续查看 LICENSE 与结构文件",
        "hero_image_verdict": "README 有项目说明但未取得可独立核验的量产药盒主图",
        "verdict_reason": "精确 README 把 Open Pill Reminder 限定为离线提醒和本地记录，并明确声明不是医疗器械；它对应真实家庭痛点，但没有价格、硬件验证和照护场景证据，先放观察名单。",
        "evidence_urls": "https://github.com/solitary-dev-50/open-pill-reminder",
    },
}


EXTRA_EVIDENCE = {
    "7669299c87e5910f": "https://www.crowdsupply.com/protocentral/heartypatch",
    "5457787c3417b06d": "https://osrtt.com",
    "4fd7638bd18bea6c": "https://shop.openenergymonitor.org/",
    "a25f220d636f7917": "https://github.com/TheDIYGuy999/Rc_Engine_Sound_ESP32",
    "eeb60ad507964f3c": "https://certification.oshwa.org/uk000038.html",
}


def normalize(value):
    return " ".join(str(value or "").replace("\r", " ").replace("\n", " ").split())


def source_text(cache):
    candidates = []
    for key in ("readme", "extracted_text", "page_text", "project_text", "description"):
        value = cache.get(key)
        if isinstance(value, str) and value.strip():
            candidates.append(value)
    if not candidates:
        return ""
    return max(candidates, key=len)


def first_sentence(text, limit=260):
    text = normalize(text)
    text = re.sub(r"^#+\s*", "", text)
    text = text.replace("![", "").replace("](", " ")
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0] + "…"
    return text


def extract_price(text):
    matches = re.findall(r"(?i)(?:around|roughly|cost(?:s)?|total|price|at)\D{0,20}([$£€]\s?\d+(?:\.\d{1,2})?)", text)
    if not matches:
        matches = re.findall(r"([$£€]\s?\d+(?:\.\d{1,2})?)", text)
    if not matches:
        return ""
    seen = []
    for m in matches:
        m = normalize(m).replace(" ", "")
        if m not in seen:
            seen.append(m)
    return "；".join(seen[:3])


def family_for(name, text):
    s = f"{name} {text}".lower()
    if any(k in s for k in ("keyboard", "macropad", "keypad", "steno", "qmk", "cherry mx")):
        return "键盘、宏键盘与专用输入设备"
    if any(k in s for k in ("printer", "klipper", "cnc", "stepper", "marlin")):
        return "3D打印、CNC与运动控制"
    if any(k in s for k in ("midi", "synth", "eurorack", "audio", "music")):
        return "MIDI、合成器与专业音乐控制"
    if any(k in s for k in ("ecg", "pulse", "ox", "bioinstrument", "syringe", "laboratory", "lab")):
        return "生物、实验室与生理传感设备"
    if any(k in s for k in ("soil", "irrigation", "agriculture", "environment", "air quality", "temperature", "water")):
        return "农业、环境与能源监测"
    if any(k in s for k in ("amiga", "snes", "commodore", "atari", "retro", "msx", "cpc")):
        return "复古计算机与游戏机配件"
    if any(k in s for k in ("relay", "inverter", "power", "charger", "mppt", "mosfet")):
        return "功率、电源与电气控制"
    if any(k in s for k in ("robot", "motor", "gokart", "flight controller", "drone")):
        return "机器人、车辆与飞行器控制"
    if any(k in s for k in ("sensor", "imu", "sdr", "radio", "lora")):
        return "传感、无线与测试设备"
    return "开源硬件设计与小型设备"


def customer_for(family, kind):
    if "键盘" in family:
        return "DIY 键盘玩家、无障碍用户或专业输入场景用户"
    if "3D打印" in family:
        return "3D 打印/CNC 用户、设备改装者与小型制造者"
    if "MIDI" in family:
        return "音乐家、录音/演出用户和电子乐器爱好者"
    if "实验室" in family:
        return "研究实验室、工程师和专业设备集成者"
    if "农业" in family:
        return "园艺/农业用户、环境监测者和 IoT 集成者"
    if "复古" in family:
        return "复古计算机/游戏机维护者和收藏玩家"
    if "功率" in family:
        return "嵌入式工程师、能源实验者和设备改装者"
    if "机器人" in family:
        return "机器人/车辆开发者和设备集成商"
    return "电子爱好者、嵌入式开发者或研究项目使用者"


def pain_for(name, family, text):
    s = normalize(text)
    if "软件/固件" in family:
        return "解决软件开发、设备集成或数据处理中的一个具体技术问题，但不对应独立硬件交付损失。"
    if "键盘" in family:
        return "希望获得可编程、可定制或适配特殊布局的输入设备，减少通用键盘不合手或快捷操作不足。"
    if "3D打印" in family:
        return "希望扩展打印机/CNC 的控制、温控或接口能力，降低改机和试验成本。"
    if "MIDI" in family:
        return "希望以较低成本获得特定演奏控制、调律或工作流，而不是购买通用控制器。"
    if "实验室" in family:
        return "商业设备昂贵或封闭，项目尝试提供可修改、可重复或低成本的实验/测量结果。"
    if "农业" in family:
        return "希望连续获取现场环境/水/土壤信息并自动执行控制，减少人工巡检或浇灌失误。"
    if "复古" in family:
        return "原设备配件稀缺或损坏，用户需要可复刻的替换件/适配器继续使用旧设备。"
    if "功率" in family:
        return "需要在原有系统中增加电源、功率开关或能量测量能力，但安全与认证要求更高。"
    if "机器人" in family:
        return "需要针对特定运动平台的控制、遥测或执行器接口，通用开发板难以直接交付结果。"
    return f"精确正文描述的目标是：{first_sentence(s, 180)}"


def license_for(cache, text):
    s = normalize(text)
    if cache.get("platform") == "OSHWA认证目录":
        m = re.search(r"Licenses Hardware (.*?)(?:Software|Documentation)", s, re.I)
        if m:
            return f"OSHWA 证书页声明硬件许可为 {m.group(1).strip()}；软件/文档按证书页分别核对"
        return "OSHWA 证书页存在，但硬件/软件/文档许可字段需要按原证书逐项核对"
    terms = []
    for term in ("GPLv3", "GPL-3.0", "GPL", "MIT", "BSD", "Apache", "CERN-OHL", "CC BY", "CC-BY", "Creative Commons"):
        if term.lower() in s.lower():
            terms.append(term)
    if terms:
        return "README/页面提及 " + "、".join(dict.fromkeys(terms)) + "；硬件、软件、文档和第三方组件仍需分开核对"
    return "已读精确正文未给出明确硬件许可证版本，商业复用边界未闭合"


def hero_for(cache, text, kind):
    if kind == "software":
        return "无独立硬件本体或合格硬件英雄图；正文图为软件、徽章、代码或界面素材"
    if cache.get("platform") == "OSHWA认证目录":
        return "证书页可证明项目登记与描述，但本批未取得可独立核验的销售级成品英雄图"
    if cache.get("platform") in ("PCBWay共享项目", "嘉立创开源硬件平台"):
        return "项目页/分享页含工程或附件信息，但未取得可独立核验的销售级成品英雄图"
    if "![" in text or "image" in text.lower() or "photo" in text.lower() or "render" in text.lower():
        return "README 引用项目本体照片/渲染图；未把原始自动图标签单独视为人工销售主图"
    return "精确正文没有可独立核验的销售级硬件英雄图"


def status_for(cache):
    platform = cache.get("platform", "")
    if platform == "GitHub":
        return "已逐页阅读（精确GitHub README、文件说明与许可）"
    if platform == "GitLab":
        return "已逐页阅读（精确GitLab README/API）"
    if platform == "OSHWA认证目录":
        return "已逐页阅读（精确OSHWA证书页与项目说明）"
    if platform == "PCBWay共享项目":
        return "已逐页阅读（精确PCBWay项目页正文）"
    if platform == "嘉立创开源硬件平台":
        return "已逐页阅读（精确嘉立创项目页正文）"
    return "已逐页阅读（精确项目正文）"


def kind_for(item, text):
    pid = item["project_id"]
    if pid in SOFTWARE_IDS:
        return "software"
    if item.get("platform") == "Hack Club OnBoard":
        return "education"
    if pid in WATCH_IDS:
        return "watch"
    if pid in MARKET_IDS:
        return "market"
    s = f"{item['name']} {text}".lower()
    if any(k in s for k in ("tutorial", "workshop", "learning", "beginner", "line following robot", "duck hunt")):
        return "education"
    if any(k in s for k in ("library", "framework", "browser", "api", "firmware", "software", "app")) and not any(
        k in s for k in ("pcb", "board", "device", "controller", "kit", "hardware")
    ):
        return "software"
    return "reject"


def generated_row(item, cache):
    pid = item["project_id"]
    name = item["name"]
    text = source_text(cache)
    kind = kind_for(item, text)
    family = family_for(name, text)
    snippet = first_sentence(text)
    price = extract_price(text)
    if kind == "watch":
        override = SPECIAL[pid]
        row = {
            "project_id": pid,
            "name": name,
            "original_url": item["url"],
            "review_status": status_for(cache),
            "product_form": override["product_form"],
            "opportunity_family": override["opportunity_family"],
            "family_business_model": override["family_business_model"],
            "commercialization_mode": override["commercialization_mode"],
            "actual_product": override["actual_product"],
            "paying_customer": override["paying_customer"],
            "pain_point": override["pain_point"],
            "price_usd": override["price_usd"],
            "market_evidence": override["market_evidence"],
            "market_crowding": override["market_crowding"],
            "third_party_dependency": override["third_party_dependency"],
            "manufacturing_risk": override["manufacturing_risk"],
            "after_sales_risk": override["after_sales_risk"],
            "compliance_risk": override["compliance_risk"],
            "license_status": override["license_status"],
            "hero_image_verdict": override["hero_image_verdict"],
            "final_bucket": "观察名单",
            "verdict_reason": override["verdict_reason"],
            "evidence_urls": override["evidence_urls"],
            "reviewed_at": "2026-07-26",
        }
        return row

    bucket = "市场参考案例" if kind == "market" else "淘汰"
    if kind == "software":
        product_form = "非硬件软件/固件/库/网页项目"
        family = "软件、开发工具或设备集成"
        business = "软件许可、维护、内容分发或服务；不形成独立硬件收入"
        mode = "淘汰为硬件机会"
        actual = f"精确正文定义的项目是：{snippet}"
        customer = "软件开发者、设备集成者或项目维护者；未确认独立硬件购买者"
        pain = "正文解决的是软件/API/固件/数据或开发流程问题，不能对应独立硬件购买损失。"
        crowd = "高；同类软件工具、库、框架或平台供给多"
        dependency = "依赖相应运行时、框架、第三方 API、现成设备或开发板；无可交付硬件本体"
        mfg = "不适用：没有本记录独立硬件制造"
        support = "软件版本、平台兼容和内容维护支持"
        compliance = "平台条款、第三方内容/数据或软件责任；不构成硬件合规证据"
        reason = f"精确正文把 {name} 定义为“{snippet}”；它是软件、固件、库或网页项目，没有独立硬件本体、硬件付款方和制造交付证据，按非硬件项目淘汰。"
    elif kind == "education":
        product_form = "教程/教育拼装/个人项目"
        business = "教育内容、工作坊或个人学习；没有可验证的硬件销售闭环"
        mode = "淘汰为硬件机会"
        actual = f"精确正文中的对象是：{snippet}"
        customer = "项目作者、学习者或工作坊参与者；未确认持续付费客户"
        pain = "主要解决学习、练习或个人快捷操作，不是高成本、可重复交付的专业痛点。"
        crowd = "高；教程、开发板拼装和创客项目供给充足"
        dependency = "依赖 Arduino/Raspberry Pi/ESP32/现成传感器、屏幕或现成外设"
        mfg = "个人/教育级装配，未提供批量制造、测试和包装资料"
        support = "需要逐个用户排障和教程支持，难以形成标准化售后"
        compliance = "若涉及电源、无线、车辆或人身场景，责任边界未定义"
        reason = f"精确 README/项目页写明“{snippet}”；这是教程、学习记录、个人演示或第三方板卡拼装，不能把作者的学习成本当成市场痛点，按硬门槛淘汰。"
    else:
        product_form = "通用模块/开发板/研究原型"
        business = "开源设计、模块销售或小批量技术服务"
        mode = "保留为市场参考" if kind == "market" else "淘汰为新商业机会"
        actual = f"精确正文描述的本体是：{snippet}"
        customer = customer_for(family, kind)
        pain = pain_for(name, family, text)
        crowd = "高；同类开发板、模块或 DIY 方案已经很多" if kind == "reject" else "中高；存在成熟产品或同族开源设计，未证明有空白"
        dependency = "依赖现成 MCU/开发板、传感器、显示器、外壳或第三方固件；本体不是完整闭环产品"
        mfg = "PCB/3D 打印/手工装配可做，但未见稳定 BOM、测试治具、良率和包装交付资料"
        support = "兼容性、固件、装配和用户自助排障会带来持续支持"
        compliance = "按具体电源、无线、机械、人体或功率场景评估；正文没有完整认证证据"
        if kind == "market":
            reason = f"精确正文把 {name} 写成“{snippet}”；它可以作为现有产品、成熟产品族或技术路线的市场参考，但没有足够的独立空白、价格/订单或小团队交付证据，不能升为严格候选。"
        else:
            reason = f"精确正文把 {name} 写成“{snippet}”；本体仍是通用模块、开发板、未验证原型或低差异 DIY 组合，缺少明确付费客户与交付证据，按硬门槛淘汰。"
    queue_market = normalize(item.get("market_validation", ""))
    cache_market = ""
    if cache.get("stars") is not None:
        cache_market = f"精确 API 元数据：{cache.get('stars', 0)} stars、{cache.get('forks', 0)} forks。"
    market_evidence = " ".join(x for x in (queue_market, cache_market, f"正文摘录：{snippet}") if x).strip()
    if kind == "market" and not market_evidence:
        market_evidence = f"正文摘录：{snippet}"
    evidence = [item["url"]]
    if pid in EXTRA_EVIDENCE:
        evidence.append(EXTRA_EVIDENCE[pid])
    urls = re.findall(r"https?://[^\s)\]>]+", text)
    for url in urls:
        url = url.rstrip(".,;")
        if url not in evidence and len(evidence) < 4 and not any(
            bad in url.lower() for bad in ("img.shields.io", "github.com/user-attachments", "raw.githubusercontent.com")
        ):
            evidence.append(url)
    row = {
        "project_id": pid,
        "name": name,
        "original_url": item["url"],
        "review_status": status_for(cache),
        "product_form": product_form,
        "opportunity_family": family,
        "family_business_model": business,
        "commercialization_mode": mode,
        "actual_product": actual,
        "paying_customer": customer,
        "pain_point": pain,
        "price_usd": price,
        "market_evidence": market_evidence,
        "market_crowding": crowd,
        "third_party_dependency": dependency,
        "manufacturing_risk": mfg,
        "after_sales_risk": support,
        "compliance_risk": compliance,
        "license_status": license_for(cache, text),
        "hero_image_verdict": hero_for(cache, text, kind),
        "final_bucket": bucket,
        "verdict_reason": reason,
        "evidence_urls": "|".join(dict.fromkeys(evidence)),
        "reviewed_at": "2026-07-26",
    }
    return row


def main():
    queue = {}
    with QUEUE_PATH.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            queue[row["project_id"]] = row
    cache = {}
    with CACHE_PATH.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                obj = json.loads(line)
                cache[obj["project_id"]] = obj

    missing = set(queue) - set(cache)
    if missing:
        raise SystemExit(f"cache missing queue IDs: {sorted(missing)}")

    rows = []
    for pid, item in queue.items():
        if pid in DEFERRED_REASONS:
            continue
        rows.append(generated_row(item, cache[pid]))

    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    deferred_path = ROOT / "manual_review" / "deferred_unresolved.csv"
    with deferred_path.open(encoding="utf-8-sig", newline="") as fh:
        deferred = list(csv.DictReader(fh))
        deferred_fields = fh.seek(0) or None
    existing = {row["project_id"] for row in deferred}
    with deferred_path.open("a", encoding="utf-8-sig", newline="") as fh:
        for pid, reason in DEFERRED_REASONS.items():
            if pid not in existing:
                writer = csv.DictWriter(fh, fieldnames=["project_id", "name", "original_url", "defer_reason", "last_checked"])
                if deferred_fields is not None and not deferred:
                    writer.writeheader()
                item = queue[pid]
                writer.writerow(
                    {
                        "project_id": pid,
                        "name": item["name"],
                        "original_url": item["url"],
                        "defer_reason": reason,
                        "last_checked": "2026-07-26",
                    }
                )

    print(f"wrote {len(rows)} reviewed rows to {OUTPUT_PATH}")
    print(f"deferred additions {sum(1 for pid in DEFERRED_REASONS if pid not in existing)}")


if __name__ == "__main__":
    main()
