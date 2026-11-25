# -*- coding: utf-8 -*-
"""前台路由。URL 结构与原 ASP 站对应：
    /                       网站首页      (cnindex.asp)
    /about?id=profile       关于我们      (about.asp?id=)
    /product?bigid=&smallid= 产品展示     (product.asp)
    /productshow?id=        产品详情      (productshow.asp)
    /news, /news_show?id=   新闻中心      (news.asp / news_list.asp)
    /member                 会员中心      (member.asp)
    /feedback               在线留言      (feedback.asp)
    /join                   招商加盟      (join.asp)
    /order                  在线定单      (order.asp)
    /job, /job_apply?id=    人才招聘      (job.asp / job_list.asp)
    /contact                联系我们      (contact.asp)
旧的 .asp 地址会 301 跳到新地址，方便保留外链和收录。
"""
import json
import math
import re
import secrets

import click
from flask import (Flask, abort, flash, g, redirect, render_template, request,
                   send_from_directory, session, url_for)
from werkzeug.middleware.proxy_fix import ProxyFix
from markupsafe import Markup
from werkzeug.security import check_password_hash, generate_password_hash

import config
from db import close_db, execute, init_db, query

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.teardown_appcontext(close_db)

    from admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    register_helpers(app)
    register_routes(app)

    @app.cli.command("init-db")
    @click.option("--no-seed", is_flag=True, help="只建表，不写入示例数据")
    def init_db_cmd(no_seed):
        """建表并写入示例数据。"""
        init_db(seed=not no_seed)
        click.echo("数据库已初始化：" + app.config["DATABASE"])

    with app.app_context():
        init_db()
    return app


# --------------------------------------------------------------------------
# 公共工具
# --------------------------------------------------------------------------
class Pager:
    """分页，样式对应原站的“首页 <上一页 1 2 3 下一页> 尾页 共 x 页 共 y 条信息”。"""

    def __init__(self, total, per_page, page):
        self.total = total
        self.per_page = per_page
        self.pages = max(1, math.ceil(total / per_page))
        self.page = min(max(1, page), self.pages)
        self.offset = (self.page - 1) * per_page

    def url(self, n):
        args = request.args.to_dict()
        args["page"] = n
        return url_for(request.endpoint, **args)


def get_page_arg():
    try:
        return int(request.args.get("page", 1))
    except ValueError:
        return 1


def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_hex(16)
    return session["_csrf"]


def check_csrf():
    if request.form.get("_csrf") != session.get("_csrf"):
        abort(400, "表单已过期，请刷新页面后重试。")


def required(form, fields):
    """返回缺失的必填项名称列表。fields: [(字段名, 中文名)]"""
    return [label for name, label in fields if not form.get(name, "").strip()]


def category_tree():
    bigs = query("SELECT * FROM categories WHERE parent_id IS NULL ORDER BY sort, id")
    subs = query("SELECT * FROM categories WHERE parent_id IS NOT NULL ORDER BY sort, id")
    tree = []
    for b in bigs:
        tree.append({"big": b, "subs": [s for s in subs if s["parent_id"] == b["id"]]})
    return tree


def register_helpers(app):
    @app.context_processor
    def inject():
        return {
            "site": config.SITE,
            "csrf_token": csrf_token,
            "nav_items": NAV_ITEMS,
            "about_menu": lambda: query("SELECT slug, title FROM pages WHERE in_about_menu=1 ORDER BY sort, id"),
            "cat_tree": category_tree,
            "current_member": g.get("member"),
        }

    @app.template_filter("specs")
    def specs_filter(raw):
        try:
            return json.loads(raw) if raw else None
        except ValueError:
            return None

    @app.template_filter("nl2br")
    def nl2br(text):
        from markupsafe import escape
        return Markup("<br>".join(escape(text or "").split("\n")))

    @app.before_request
    def load_member():
        mid = session.get("member_id")
        g.member = query("SELECT * FROM members WHERE id=?", (mid,), one=True) if mid else None


# 导航：(端点, 显示名, 对应原站页面)
NAV_ITEMS = [
    ("index", "网站首页"),
    ("about", "关于我们"),
    ("product", "产品展示"),
    ("news", "新闻中心"),
    ("member", "会员中心"),
    ("feedback", "在线留言"),
    ("join", "招商加盟"),
    ("order", "在线定单"),
    ("job", "人才招聘"),
    ("contact", "联系我们"),
]

# 旧 ASP 地址 -> 新端点
LEGACY = {
    "cnindex.asp": "index", "index.asp": "index", "about.asp": "about", "contact.asp": "contact",
    "product.asp": "product", "productshow.asp": "productshow", "news.asp": "news",
    "news_list.asp": "news_show", "member.asp": "member", "feedback.asp": "feedback",
    "join.asp": "join", "order.asp": "order", "job.asp": "job", "job_list.asp": "job_apply",
}
LEGACY_ABOUT_IDS = {"2": "profile", "24": "culture", "25": "honor", "26": "organization"}


# --------------------------------------------------------------------------
# 路由
# --------------------------------------------------------------------------
def register_routes(app):

    @app.route("/")
    def index():
        about = query("SELECT * FROM pages WHERE slug='profile'", one=True)
        return render_template("index.html", about=about)

    @app.route("/uploads/<path:filename>")
    def uploads(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    @app.route("/healthz")
    def healthz():
        return "ok"

    @app.route("/<path:name>.asp")
    def legacy(name):
        endpoint = LEGACY.get(name.split("/")[-1] + ".asp")
        if not endpoint:
            abort(404)
        args = request.args.to_dict()
        if endpoint == "about" and args.get("id") in LEGACY_ABOUT_IDS:
            args["id"] = LEGACY_ABOUT_IDS[args["id"]]
        if "Page" in args:
            args["page"] = args.pop("Page")
        return redirect(url_for(endpoint, **args), 301)

    # ---------- 关于我们 ----------
    @app.route("/about")
    def about():
        slug = request.args.get("id", "profile")
        page = query("SELECT * FROM pages WHERE slug=?", (slug,), one=True) or abort(404)
        crumbs = [("关于我们", url_for("about")), (page["title"], None)]
        return render_template("page.html", page=page, crumbs=crumbs, sidebar="about")

    @app.route("/contact")
    def contact():
        crumbs = [("关于我们", url_for("about")), ("联系我们", None)]
        return render_template("contact.html", crumbs=crumbs, sidebar="about")

    @app.route("/join")
    def join():
        page = query("SELECT * FROM pages WHERE slug='join'", one=True) or abort(404)
        return render_template("page.html", page=page, crumbs=[("招商加盟", None)])

    # ---------- 产品 ----------
    @app.route("/product")
    def product():
        bigid = request.args.get("bigid", type=int)
        smallid = request.args.get("smallid", type=int)
        keyword = request.args.get("q", "").strip()
        crumbs = [("产品展示", url_for("product"))]
        where, args = [], []
        if smallid:
            cat = query("SELECT * FROM categories WHERE id=?", (smallid,), one=True) or abort(404)
            big = query("SELECT * FROM categories WHERE id=?", (cat["parent_id"],), one=True)
            crumbs += [(big["name"], url_for("product", bigid=big["id"])), (cat["name"], None)]
            where.append("p.category_id=?")
            args.append(smallid)
        elif bigid:
            big = query("SELECT * FROM categories WHERE id=?", (bigid,), one=True) or abort(404)
            crumbs.append((big["name"], None))
            where.append("c.parent_id=?")
            args.append(bigid)
        if keyword:
            where.append("(p.model LIKE ? OR p.name LIKE ?)")
            args += [f"%{keyword}%"] * 2
            crumbs.append((f"搜索：{keyword}", None))
        sql_where = ("WHERE " + " AND ".join(where)) if where else ""
        base = f"FROM products p JOIN categories c ON c.id=p.category_id {sql_where}"
        total = query(f"SELECT COUNT(*) {base}", args, one=True)[0]
        pager = Pager(total, config.PRODUCTS_PER_PAGE, get_page_arg())
        items = query(f"SELECT p.* {base} ORDER BY c.parent_id, c.sort, p.sort, p.id LIMIT ? OFFSET ?",
                      args + [pager.per_page, pager.offset])
        return render_template("product_list.html", items=items, pager=pager, crumbs=crumbs,
                               active_cat=smallid)

    @app.route("/productshow")
    def productshow():
        pid = request.args.get("id", type=int)
        p = query("SELECT p.*, c.name AS cat_name, c.parent_id FROM products p "
                  "JOIN categories c ON c.id=p.category_id WHERE p.id=?", (pid,), one=True) or abort(404)
        order_sql = "FROM products WHERE category_id=? AND (sort, id) {op} (?, ?) ORDER BY sort {d}, id {d} LIMIT 1"
        prev = query("SELECT id, model " + order_sql.format(op="<", d="DESC"),
                     (p["category_id"], p["sort"], p["id"]), one=True)
        nxt = query("SELECT id, model " + order_sql.format(op=">", d="ASC"),
                    (p["category_id"], p["sort"], p["id"]), one=True)
        crumbs = [("产品展示", url_for("product")), (p["cat_name"], url_for("product", smallid=p["category_id"])),
                  (p["model"], None)]
        return render_template("product_show.html", p=p, prev=prev, nxt=nxt, crumbs=crumbs,
                               active_cat=p["category_id"])

    # ---------- 新闻 ----------
    @app.route("/news")
    def news():
        total = query("SELECT COUNT(*) FROM news", one=True)[0]
        pager = Pager(total, config.NEWS_PER_PAGE, get_page_arg())
        items = query("SELECT * FROM news ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?",
                      (pager.per_page, pager.offset))
        return render_template("news_list.html", items=items, pager=pager, crumbs=[("新闻中心", None)])

    @app.route("/news_show")
    def news_show():
        nid = request.args.get("id", type=int)
        item = query("SELECT * FROM news WHERE id=?", (nid,), one=True) or abort(404)
        execute("UPDATE news SET hits=hits+1 WHERE id=?", (nid,))
        crumbs = [("新闻中心", url_for("news")), (item["title"], None)]
        return render_template("news_show.html", item=item, crumbs=crumbs)

    # ---------- 会员中心 ----------
    @app.route("/member", methods=["GET", "POST"])
    def member():
        crumbs = [("会员中心", None)]
        if g.member:
            orders = query("SELECT * FROM orders WHERE member_id=? ORDER BY id DESC", (g.member["id"],))
            return render_template("member_center.html", crumbs=crumbs, orders=orders)
        form = request.form
        if request.method == "POST":
            check_csrf()
            missing = required(form, [("username", "用户名"), ("password", "密码"), ("password2", "密码确认"),
                                      ("contact", "联系人"), ("company", "公司名称"), ("tel", "联系电话"),
                                      ("email", "电子邮箱"), ("address", "联系地址")])
            error = None
            if missing:
                error = "请填写：" + "、".join(missing)
            elif not re.fullmatch(r"[A-Za-z0-9_]{3,20}", form["username"]):
                error = "用户名为 3-20 位字母、数字或下划线"
            elif len(form["password"]) < 6:
                error = "密码至少 6 位"
            elif form["password"] != form["password2"]:
                error = "两次输入的密码不一致"
            elif not EMAIL_RE.match(form["email"]):
                error = "电子邮箱格式不正确"
            elif query("SELECT 1 FROM members WHERE username=?", (form["username"],), one=True):
                error = "该用户名已被注册"
            if error:
                flash(error, "error")
            else:
                mid = execute(
                    "INSERT INTO members (username, password_hash, contact, company, tel, email, address) "
                    "VALUES (?,?,?,?,?,?,?)",
                    (form["username"], generate_password_hash(form["password"]), form["contact"].strip(),
                     form["company"].strip(), form["tel"].strip(), form["email"].strip(), form["address"].strip()))
                session["member_id"] = mid
                flash("注册成功，已为您自动登录。", "ok")
                return redirect(url_for("member"))
        return render_template("member.html", crumbs=crumbs, form=form)

    @app.route("/member/login", methods=["POST"])
    def member_login():
        check_csrf()
        m = query("SELECT * FROM members WHERE username=?", (request.form.get("username", ""),), one=True)
        if m and check_password_hash(m["password_hash"], request.form.get("password", "")):
            session["member_id"] = m["id"]
            flash("登录成功。", "ok")
        else:
            flash("用户名或密码错误。", "error")
        return redirect(request.form.get("next") or url_for("member"))

    @app.route("/member/logout")
    def member_logout():
        session.pop("member_id", None)
        return redirect(url_for("member"))

    # ---------- 在线留言 ----------
    @app.route("/feedback", methods=["GET", "POST"])
    def feedback():
        form = request.form
        if request.method == "POST":
            check_csrf()
            missing = required(form, [("contact", "联系人"), ("tel", "联系电话"), ("title", "留言标题"),
                                      ("content", "留言内容")])
            if missing:
                flash("请填写：" + "、".join(missing), "error")
            elif form.get("email") and not EMAIL_RE.match(form["email"]):
                flash("电子邮箱格式不正确", "error")
            else:
                execute("INSERT INTO feedback (contact, company, company_address, tel, email, title, content) "
                        "VALUES (?,?,?,?,?,?,?)",
                        tuple(form.get(k, "").strip() for k in
                              ("contact", "company", "company_address", "tel", "email", "title", "content")))
                flash("留言成功，我们会尽快与您联系！", "ok")
                return redirect(url_for("feedback"))
        return render_template("feedback.html", crumbs=[("在线留言", None)], form=form)

    # ---------- 在线定单 ----------
    @app.route("/order", methods=["GET", "POST"])
    def order():
        form = request.form
        prefill = {}
        if request.method == "GET" and g.member:
            m = g.member
            prefill = {"name": m["contact"], "tel": m["tel"], "email": m["email"], "address": m["address"]}
        if request.method == "GET" and request.args.get("product"):
            prefill["products"] = request.args["product"]
        if request.method == "POST":
            check_csrf()
            missing = required(form, [("products", "您想购的产品"), ("name", "姓名"), ("tel", "电话号码"),
                                      ("address", "发货地址")])
            if missing:
                flash("请填写：" + "、".join(missing), "error")
            elif form.get("email") and not EMAIL_RE.match(form["email"]):
                flash("电子邮箱格式不正确", "error")
            else:
                execute("INSERT INTO orders (member_id, products, description, name, tel, fax, email, address) "
                        "VALUES (?,?,?,?,?,?,?,?)",
                        (g.member["id"] if g.member else None,) +
                        tuple(form.get(k, "").strip() for k in
                              ("products", "description", "name", "tel", "fax", "email", "address")))
                flash("定单已提交，我们会尽快与您确认！", "ok")
                return redirect(url_for("order"))
        return render_template("order.html", crumbs=[("在线定单", None)], form=form or prefill)

    # ---------- 人才招聘 ----------
    @app.route("/job")
    def job():
        total = query("SELECT COUNT(*) FROM jobs", one=True)[0]
        pager = Pager(total, config.JOBS_PER_PAGE, get_page_arg())
        items = query("SELECT * FROM jobs ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?",
                      (pager.per_page, pager.offset))
        return render_template("job_list.html", items=items, pager=pager, crumbs=[("人才招聘", None)])

    @app.route("/job_apply", methods=["GET", "POST"])
    def job_apply():
        jid = request.args.get("id", type=int)
        j = query("SELECT * FROM jobs WHERE id=?", (jid,), one=True) or abort(404)
        form = request.form
        if request.method == "POST":
            check_csrf()
            missing = required(form, [("name", "姓名"), ("phone", "联系电话"), ("resume", "个人简历")])
            if missing:
                flash("请填写：" + "、".join(missing), "error")
            elif form.get("email") and not EMAIL_RE.match(form["email"]):
                flash("电子邮箱格式不正确", "error")
            else:
                execute("INSERT INTO job_applications (job_id, position, name, gender, age, education, phone, email,"
                        " resume) VALUES (?,?,?,?,?,?,?,?,?)",
                        (j["id"], j["position"]) + tuple(form.get(k, "").strip() for k in
                                                         ("name", "gender", "age", "education", "phone", "email",
                                                          "resume")))
                flash("简历已提交，感谢您的关注！", "ok")
                return redirect(url_for("job"))
        crumbs = [("人才招聘", url_for("job")), ("应聘此岗位", None)]
        return render_template("job_apply.html", j=j, crumbs=crumbs, form=form)

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("message.html", crumbs=[("页面不存在", None)],
                               message="您访问的页面不存在或已被删除。"), 404

    @app.errorhandler(400)
    def bad_request(e):
        return render_template("message.html", crumbs=[("提示", None)], message=e.description), 400


app = create_app()

if __name__ == "__main__":
    import os
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", host="127.0.0.1", port=int(os.environ.get("PORT", 5000)))
