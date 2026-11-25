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

    # 页脚电话（带国际区号的展示格式）
    "footer_phone": "0086 000 00000000",
}

# 列表分页条数（与原站一致：产品 4 列 × 8 行）
PRODUCTS_PER_PAGE = 32
NEWS_PER_PAGE = 20
JOBS_PER_PAGE = 10
