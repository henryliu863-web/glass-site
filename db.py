# -*- coding: utf-8 -*-
"""SQLite 数据库：建表、连接、初始化示例数据。"""
import json
import os
import sqlite3

from flask import current_app, g
from werkzeug.security import generate_password_hash

SCHEMA = """
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

-- 关于我们 / 招商加盟 等单页
CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL DEFAULT '',
    in_about_menu INTEGER NOT NULL DEFAULT 1,
    sort INTEGER NOT NULL DEFAULT 0
);

-- 产品分类：parent_id 为空的是大类（如“玻璃工具系列”），否则是小类
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    sort INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    model TEXT NOT NULL,            -- 型号，列表里显示的就是它
    name TEXT NOT NULL DEFAULT '',
    image TEXT NOT NULL DEFAULT '',
    specs TEXT NOT NULL DEFAULT '', -- JSON: {"headers": [...], "rows": [[...], ...]}
    description TEXT NOT NULL DEFAULT '',
    sort INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    body TEXT NOT NULL DEFAULT '',
    hits INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position TEXT NOT NULL,        -- 招聘对象
    headcount TEXT NOT NULL DEFAULT '',  -- 招聘人数
    location TEXT NOT NULL DEFAULT '',   -- 工作地点
    salary TEXT NOT NULL DEFAULT '面议', -- 工资待遇
    valid_days INTEGER NOT NULL DEFAULT 30, -- 有效期限（天）
    requirement TEXT NOT NULL DEFAULT '',   -- 招聘要求
    created_at TEXT NOT NULL DEFAULT (date('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS job_applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER REFERENCES jobs(id) ON DELETE SET NULL,
    position TEXT NOT NULL DEFAULT '',
    name TEXT NOT NULL,
    gender TEXT NOT NULL DEFAULT '',
    age TEXT NOT NULL DEFAULT '',
    education TEXT NOT NULL DEFAULT '',
    phone TEXT NOT NULL,
    email TEXT NOT NULL DEFAULT '',
    resume TEXT NOT NULL DEFAULT '',
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    contact TEXT NOT NULL,
    company TEXT NOT NULL,
    tel TEXT NOT NULL,
    email TEXT NOT NULL,
    address TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact TEXT NOT NULL,
    company TEXT NOT NULL DEFAULT '',
    company_address TEXT NOT NULL DEFAULT '',
    tel TEXT NOT NULL,
    email TEXT NOT NULL DEFAULT '',
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    reply TEXT NOT NULL DEFAULT '',
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- 智能客服
CREATE TABLE IF NOT EXISTS faqs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    sort INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS chat_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT UNIQUE NOT NULL,
    ip TEXT NOT NULL DEFAULT '',
    first_question TEXT NOT NULL DEFAULT '',
    messages INTEGER NOT NULL DEFAULT 0,
    has_lead INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL,            -- user / assistant
    content TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER REFERENCES members(id) ON DELETE SET NULL,
    products TEXT NOT NULL,        -- 您想购的产品
    description TEXT NOT NULL DEFAULT '', -- 购买说明
    name TEXT NOT NULL,
    tel TEXT NOT NULL,
    fax TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    address TEXT NOT NULL,         -- 发货地址
    status TEXT NOT NULL DEFAULT '未处理',
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);
"""


def get_db():
    if "db" not in g:
        path = current_app.config["DATABASE"]
        os.makedirs(os.path.dirname(path), exist_ok=True)
        g.db = sqlite3.connect(path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query(sql, args=(), one=False):
    cur = get_db().execute(sql, args)
    rows = cur.fetchall()
    cur.close()
    return (rows[0] if rows else None) if one else rows


def execute(sql, args=()):
    db = get_db()
    cur = db.execute(sql, args)
    db.commit()
    return cur.lastrowid


def init_db(seed=True):
    db = get_db()
    db.execute("PRAGMA busy_timeout = 10000")
    db.executescript(SCHEMA)
    cfg = current_app.config
    # gunicorn 多个进程会同时启动：先拿写锁，再检查、写入，避免重复初始化
    db.execute("BEGIN IMMEDIATE")
    try:
        db.execute(
            "INSERT OR IGNORE INTO admins (username, password_hash) "
            "SELECT ?, ? WHERE NOT EXISTS (SELECT 1 FROM admins)",
            (cfg["ADMIN_USERNAME"], generate_password_hash(cfg["ADMIN_PASSWORD"])),
        )
        if seed and not db.execute("SELECT 1 FROM categories").fetchone():
            _seed(db)
        if seed and not db.execute("SELECT 1 FROM faqs").fetchone():
            for i, (q, a) in enumerate(SEED_FAQS, 1):
                db.execute("INSERT INTO faqs (question, answer, sort) VALUES (?,?,?)", (q, a, i))
        db.commit()
    except Exception:
        db.rollback()
        raise


# --------------------------------------------------------------------------
# 示例数据：分类名称与原站一致，产品只保留每个小类 3 个
# --------------------------------------------------------------------------
CUTTER_HEAD = ["型号", "刀轮代号", "切割厚度(MM)", "包装数量(把)", "净重(KG)", "外箱尺寸(CM)"]
GENERIC_HEAD = ["型号", "材质", "规格", "表面处理", "包装"]

SEED_CATEGORIES = [
    ("玻璃工具系列", [
        ("玻璃刀系列", "cutter", "GC", [
            ("黄色塑柄玻璃刀", "0.3-2|2-6|6-12|12-19", "360", "22.5", "42x21x38"),
            ("蓝色塑柄玻璃刀", "0.3-2|2-6|6-12|12-19", "360", "22.5", "42x21x38"),
            ("铜头加油玻璃刀", "2-6|6-12|12-19", "240", "18.0", "40x20x30"),
        ]),
        ("玻璃切割刀轮系列", "wheel", "GW", [
            ("硬质合金刀轮 3mm", "硬质合金", "Φ3.0 × 0.65", "本色", "10 个/盒"),
            ("硬质合金刀轮 5.5mm", "硬质合金", "Φ5.5 × 1.1", "本色", "10 个/盒"),
            ("瓷砖切割刀轮 22mm", "钨钢", "Φ22 × 6", "镀钛", "1 个/卡"),
        ]),
        ("玻璃吸盘系列", "sucker", "GS", [
            ("单爪铝合金吸盘", "铝合金 + 橡胶", "Φ120 / 承重 40KG", "阳极氧化", "1 个/盒"),
            ("双爪铝合金吸盘", "铝合金 + 橡胶", "Φ120 / 承重 80KG", "阳极氧化", "1 个/盒"),
            ("三爪铝合金吸盘", "铝合金 + 橡胶", "Φ120 / 承重 120KG", "阳极氧化", "1 个/盒"),
        ]),
        ("玻璃钻头系列", "drill", "GD", [
            ("金刚石开孔钻 6mm", "金刚石 + 碳钢", "Φ6", "电镀", "10 支/盒"),
            ("金刚石开孔钻 12mm", "金刚石 + 碳钢", "Φ12", "电镀", "10 支/盒"),
            ("玻璃瓷砖三角钻", "钨钢", "Φ3-12 套装", "镀铬", "7 支/套"),
        ]),
    ]),
    ("玻璃门控系列", [
        ("地弹簧系列", "spring", "FS", [
            ("重型地弹簧", "钢 + 铝合金", "承重 150KG", "拉丝", "1 套/箱"),
            ("中型地弹簧", "钢 + 铝合金", "承重 100KG", "拉丝", "1 套/箱"),
            ("无框门地弹簧", "钢 + 铝合金", "承重 80KG", "拉丝", "1 套/箱"),
        ]),
        ("玻璃门夹系列", "clip", "DC", [
            ("上门夹", "304 不锈钢", "适用 10-12mm 玻璃", "镜光 / 拉丝", "1 个/盒"),
            ("下门夹", "304 不锈钢", "适用 10-12mm 玻璃", "镜光 / 拉丝", "1 个/盒"),
            ("L 型门夹", "304 不锈钢", "适用 10-12mm 玻璃", "镜光 / 拉丝", "1 个/盒"),
        ]),
        ("玻璃门锁系列", "lock", "DL", [
            ("单门中心锁", "锌合金", "适用 10-12mm 玻璃", "镀铬", "1 套/盒"),
            ("双门中心锁", "锌合金", "适用 10-12mm 玻璃", "镀铬", "1 套/盒"),
            ("地锁", "304 不锈钢", "适用 10-12mm 玻璃", "拉丝", "1 套/盒"),
        ]),
        ("闭门器系列", "closer", "DCL", [
            ("液压闭门器 45KG", "铝合金", "门重 25-45KG", "喷涂", "1 套/盒"),
            ("液压闭门器 65KG", "铝合金", "门重 45-65KG", "喷涂", "1 套/盒"),
            ("液压闭门器 85KG", "铝合金", "门重 65-85KG", "喷涂", "1 套/盒"),
        ]),
    ]),
]

SEED_PAGES = [
    ("profile", "公司简介", 1, 1, """<p>　　本公司是一家专业生产玻璃切割工具、玻璃五金产品的企业，产品远销东南亚、中东及欧美等多个国家和地区。自成立以来，一直致力于为客户提供高品质的玻璃五金。</p>
<p>　　公司依靠成熟的生产工艺和持续的研发投入，在产品功能上不断改进，外观设计简洁现代，兼顾实用与美观。</p>
<p>　　品质、服务、诚信是我们一贯坚持的经营宗旨。我们坚持“质量是企业生存之本”，真诚欢迎新老客户携手合作，共同发展。</p>
<p class="note">（以上为示例文字，请在后台“单页管理”中修改。）</p>"""),
    ("culture", "企业文化", 1, 2, """<p><b>企业使命：</b>为客户提供好用、耐用的玻璃工具与五金配件。</p>
<p><b>经营理念：</b>品质第一，客户至上，诚信经营。</p>
<p><b>团队精神：</b>务实、协作、进取。</p>"""),
    ("honor", "公司荣誉", 1, 3, "<p>在此展示公司获得的资质证书、荣誉奖项（可在后台上传图片）。</p>"),
    ("organization", "组织机构", 1, 4, """<p>总经理<br>├─ 销售部（国内 / 外贸）<br>├─ 生产部<br>├─ 品质部<br>├─ 仓储物流部<br>└─ 财务部</p>"""),
    ("join", "招商加盟", 0, 5, """<p>招商加盟</p>
<p>我们面向全国诚招各地区经销商、代理商。加盟可享受出厂价格、区域保护和完善的售后支持。</p>
<p>有意者请通过“在线留言”或“联系我们”页面与我们取得联系。</p>"""),
]

SEED_NEWS = [
    ("玻璃刀的保养方法？", """<p>1. 每次使用后用干布擦去刀轮上的玻璃碎屑。</p>
<p>2. 加油式玻璃刀请定期补充切割油，保持刀轮润滑。</p>
<p>3. 不用时将刀头朝上存放，避免刀轮磕碰。</p>
<p>4. 刀轮磨损后应及时更换，切割效果会明显改善。</p>""", "2014-04-12 10:00:00"),
    ("如何选择合适的玻璃刀轮", "<p>切割薄玻璃宜选用小角度刀轮，厚玻璃宜选用大角度刀轮。具体可参考产品详情页中的“刀轮代号 / 切割厚度”对照表。</p>", "2014-04-12 09:30:00"),
    ("地弹簧安装注意事项", "<p>安装前请确认门重与地弹簧承重等级相符，并保证地面开槽水平，安装后调节关门速度至合适范围。</p>", "2014-04-12 09:00:00"),
    ("网站正式上线", "<p>公司新网站正式上线，欢迎广大客户浏览产品、在线留言及下单。</p>", "2014-04-12 08:00:00"),
]

SEED_JOBS = [
    ("仓库管理  财务  记账文员  电子商务", "15", "公司所在地", "面议", 90,
     "对工作认真负责，有责任心，年龄 20-35 岁，愿意学习专业知识，上班准时，能长期稳定工作者优先。", "2014-11-13"),
    ("外贸业务员", "5", "公司所在地", "面议", 10, "英语读写流利，有五金类产品外贸经验者优先。", "2014-04-12"),
    ("玻璃工具销售员", "2", "公司所在地", "面议", 30, "面议", "2014-04-12"),
]


# 智能客服常见问题（示例，请在后台“常见问题”里改成真实情况）
SEED_FAQS = [
    ("起订量是多少？", "常规产品一般 1 箱起订，样品可单独购买；具体以业务员报价为准。"),
    ("多久发货？", "现货产品一般付款后 1-3 个工作日内发货；定制或大批量订单交期另行确认。"),
    ("支持哪些付款方式？", "支持银行转账、对公账户付款；外贸订单支持 T/T，具体可与业务员确认。"),
    ("可以定制或贴牌（OEM）吗？", "可以。支持定制包装、贴牌，需要提供数量和要求，由业务员评估后报价。"),
    ("可以寄样品吗？", "可以提供样品，样品费和运费需客户承担，正式下单后可协商抵扣。"),
    ("产品有质量问题怎么办？", "收货后如发现质量问题，请拍照并联系我们，核实后给予退换。"),
    ("怎么下单？", "可以在网站“在线定单”页面填写想购买的产品和联系方式，也可以直接电话或微信联系业务员。"),
]


def _seed(db):
    for p in SEED_PAGES:
        db.execute("INSERT INTO pages (slug, title, in_about_menu, sort, body) VALUES (?,?,?,?,?)", p)

    for big_sort, (big_name, subs) in enumerate(SEED_CATEGORIES, 1):
        big_id = db.execute("INSERT INTO categories (parent_id, name, sort) VALUES (NULL, ?, ?)",
                            (big_name, big_sort)).lastrowid
        for sub_sort, (sub_name, kind, prefix, items) in enumerate(subs, 1):
            sub_id = db.execute("INSERT INTO categories (parent_id, name, sort) VALUES (?, ?, ?)",
                                (big_id, sub_name, sub_sort)).lastrowid
            for i, item in enumerate(items, 1):
                model = f"{prefix}-{i:03d}"
                if kind == "cutter":
                    name, thick, qty, nw, box = item
                    codes = ["A", "M", "T", "S"][: len(thick.split("|"))]
                    rows = [[model if j == 0 else "", c, t, qty if j == 0 else "", nw if j == 0 else "",
                             box if j == 0 else ""] for j, (c, t) in enumerate(zip(codes, thick.split("|")))]
                    specs = {"headers": CUTTER_HEAD, "rows": rows, "merge": [0, 3, 4, 5]}
                else:
                    name, material, size, finish, pack = item
                    specs = {"headers": GENERIC_HEAD, "rows": [[model, material, size, finish, pack]]}
                db.execute(
                    "INSERT INTO products (category_id, model, name, image, specs, description, sort) "
                    "VALUES (?,?,?,?,?,?,?)",
                    (sub_id, model, name, f"/static/img/products/{kind}-{i}.svg",
                     json.dumps(specs, ensure_ascii=False), "", i),
                )

    for title, body, ts in SEED_NEWS:
        db.execute("INSERT INTO news (title, body, created_at) VALUES (?,?,?)", (title, body, ts))
    for job in SEED_JOBS:
        db.execute("INSERT INTO jobs (position, headcount, location, salary, valid_days, requirement, created_at) "
                   "VALUES (?,?,?,?,?,?,?)", job)
