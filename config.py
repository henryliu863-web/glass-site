# -*- coding: utf-8 -*-
"""站点配置：公司信息、联系方式等都在这里改。

下面的公司名称、Logo 文字、电话、地址都是占位内容，上线前请替换成你自己的。
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---- Flask ----
SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-to-a-long-random-string")
DATABASE = os.environ.get("DATABASE", os.path.join(BASE_DIR, "data", "site.db"))
UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.join(BASE_DIR, "data", "uploads"))
MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 上传图片上限 8MB
ALLOWED_IMAGE_EXT = {"jpg", "jpeg", "png", "gif", "webp"}  # 不允许上传 SVG，防止脚本注入

# ---- 后台管理员（首次运行 init 时写入数据库，之后可在后台修改密码）----
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

# ---- 公司信息（占位，请替换）----
SITE = {
    "brand": "LOGO",                              # 页头 / 页脚的大号品牌字
    "company": "某某五金工具有限公司",              # 公司中文名
    "company_en": "YOUR COMPANY HARDWARE TOOLS CO.,LTD",  # Logo 下方英文小字
    "title": "某某五金工具有限公司/玻璃切割工具厂家/玻璃五金产品",  # 浏览器标题
    "keywords": "玻璃刀,玻璃工具,玻璃五金,地弹簧,玻璃门夹",
    "description": "专业生产玻璃切割工具、玻璃五金产品的企业。",
    "copyright_years": "2016-2026",

    # 联系方式
    "contact_person": "王先生",
    "tel": "0000-00000000",
    "fax": "0000-00000000",
    "mobile": "13800000000",
    "mobiles": [("13800000000", "王先生"), ("13900000000", "孙小姐")],
    "email": "sales@example.com",
    "address": "某省某市国际商贸城二期 G 区 2 楼 2 街 00000 商位",
    "business_hours": "9:00-18:00",

    "wechat": "123456",                           # 转人工用的微信号

    # 页脚电话（带国际区号的展示格式）
    "footer_phone": "0086 000 00000000",
}

# 列表分页条数（与原站一致：产品 4 列 × 8 行）
PRODUCTS_PER_PAGE = 32
NEWS_PER_PAGE = 20
JOBS_PER_PAGE = 10

# ---- 智能客服 ----
# API Key 只从环境变量读取（在 Railway 的 Variables 里设置 ANTHROPIC_API_KEY），不要写进代码
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
CHAT_MODEL = os.environ.get("CHAT_MODEL", "claude-haiku-5-5")
CHAT_MAX_TOKENS = 800
CHAT_HISTORY_TURNS = 10          # 带给模型的最近对话轮数
CHAT_LIMIT_PER_IP_DAY = int(os.environ.get("CHAT_LIMIT_PER_IP_DAY", 40))     # 每个访客每天最多提问次数
CHAT_LIMIT_TOTAL_DAY = int(os.environ.get("CHAT_LIMIT_TOTAL_DAY", 1500))     # 全站每天最多提问次数（控制费用）
CHAT_MAX_INPUT_CHARS = 500
CHAT_WELCOME = "您好！我是在线客服小助手，可以为您介绍产品、解答下单和发货等问题。请问有什么可以帮您？"
CHAT_QUICK_QUESTIONS = ["玻璃刀怎么选？", "地弹簧承重多少？", "怎么下单？", "起订量和发货时间"]
