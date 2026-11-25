# -*- coding: utf-8 -*-
"""管理后台：/admin

用一份 RESOURCES 配置驱动通用的“列表 / 新增 / 编辑 / 查看 / 删除”页面，
对应原 ASP 站后台的产品、新闻、单页、招聘、留言、定单、会员管理。
"""
import os
import secrets
from functools import wraps

from flask import (Blueprint, abort, current_app, flash, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from db import execute, query

bp = Blueprint("admin", __name__, url_prefix="/admin")


def _cat_options(only_sub=True):
    rows = query("SELECT s.id, b.name || ' / ' || s.name AS label FROM categories s "
                 "JOIN categories b ON b.id=s.parent_id ORDER BY b.sort, s.sort")
    return [(r["id"], r["label"]) for r in rows]


def _big_options():
    return [("", "（无，作为大类）")] + [(r["id"], r["name"]) for r in
                                   query("SELECT id, name FROM categories WHERE parent_id IS NULL ORDER BY sort")]


# 字段：(列名, 中文名, 类型, 是否必填)；类型：text / textarea / html / number / select / image / json / bool
RESOURCES = {
    "products": {
        "title": "产品管理", "table": "products", "order": "p.category_id, p.sort, p.id",
        "list": [("id", "ID"), ("model", "型号"), ("name", "名称"), ("cat", "分类"), ("price", "价格"),
                 ("image", "图片")],
        "list_sql": "SELECT p.*, c.name AS cat FROM products p LEFT JOIN categories c ON c.id=p.category_id",
        "fields": [("category_id", "所属分类", "select", True), ("model", "型号", "text", True),
                   ("name", "名称", "text", False), ("image", "产品图片", "image", False),
                   ("price", "价格", "textarea", False), ("show_price", "在产品详情页公开显示价格", "bool", False),
                   ("specs", "规格表(JSON)", "json", False), ("description", "详细介绍", "html", False),
                   ("sort", "排序", "number", False)],
        "options": {"category_id": _cat_options},
        "help": {"price": "留空 = 智能客服不报价、引导客户留联系方式。可写阶梯价，例如：\n1-99 把：¥12/把\n100 把以上：¥10/把（含税，不含运费）",
                 "show_price": "不勾选时，价格只给智能客服使用，网页上不显示"},
        "search": ["p.model", "p.name"],
    },
    "categories": {
        "title": "产品分类", "table": "categories", "order": "COALESCE(c.parent_id, c.id), c.parent_id IS NOT NULL, c.sort",
        "list": [("id", "ID"), ("parent", "上级大类"), ("name", "分类名称"), ("sort", "排序")],
        "list_sql": "SELECT c.*, b.name AS parent FROM categories c LEFT JOIN categories b ON b.id=c.parent_id",
        "fields": [("parent_id", "上级大类", "select", False), ("name", "分类名称", "text", True),
                   ("sort", "排序", "number", False)],
        "options": {"parent_id": _big_options},
    },
    "news": {
        "title": "新闻管理", "table": "news", "order": "created_at DESC, id DESC",
        "list": [("id", "ID"), ("title", "标题"), ("hits", "点击"), ("created_at", "发布时间")],
        "fields": [("title", "标题", "text", True), ("body", "内容", "html", False),
                   ("created_at", "发布时间", "text", False)],
        "search": ["title"],
    },
    "pages": {
        "title": "单页管理", "table": "pages", "order": "sort, id",
        "list": [("id", "ID"), ("slug", "标识"), ("title", "标题"), ("in_about_menu", "显示在关于我们")],
        "fields": [("slug", "标识(英文)", "text", True), ("title", "标题", "text", True),
                   ("body", "内容", "html", False), ("in_about_menu", "显示在关于我们菜单", "bool", False),
                   ("sort", "排序", "number", False)],
    },
    "jobs": {
        "title": "招聘管理", "table": "jobs", "order": "created_at DESC, id DESC",
        "list": [("id", "ID"), ("position", "招聘对象"), ("headcount", "人数"), ("created_at", "发布时间")],
        "fields": [("position", "招聘对象", "text", True), ("headcount", "招聘人数", "text", False),
                   ("location", "工作地点", "text", False), ("salary", "工资待遇", "text", False),
                   ("valid_days", "有效期限(天)", "number", False), ("requirement", "招聘要求", "textarea", False),
                   ("created_at", "发布时间", "text", False)],
    },
    "job_applications": {
        "title": "应聘简历", "table": "job_applications", "order": "id DESC", "readonly": True,
        "list": [("id", "ID"), ("position", "应聘岗位"), ("name", "姓名"), ("phone", "电话"),
                 ("is_read", "已读"), ("created_at", "时间")],
        "fields": [("position", "应聘岗位", "text", False), ("name", "姓名", "text", False),
                   ("gender", "性别", "text", False), ("age", "年龄", "text", False),
                   ("education", "学历", "text", False), ("phone", "电话", "text", False),
                   ("email", "邮箱", "text", False), ("resume", "个人简历", "textarea", False),
                   ("created_at", "时间", "text", False)],
    },
    "feedback": {
        "title": "留言管理", "table": "feedback", "order": "id DESC", "readonly": True,
        "list": [("id", "ID"), ("title", "标题"), ("contact", "联系人"), ("tel", "电话"),
                 ("is_read", "已读"), ("created_at", "时间")],
        "fields": [("contact", "联系人", "text", False), ("company", "公司名称", "text", False),
                   ("company_address", "公司地址", "text", False), ("tel", "联系电话", "text", False),
                   ("email", "电子邮箱", "text", False), ("title", "留言标题", "text", False),
                   ("content", "留言内容", "textarea", False), ("created_at", "时间", "text", False)],
        "editable": [("reply", "回复备注", "textarea", False)],
    },
    "orders": {
        "title": "定单管理", "table": "orders", "order": "id DESC", "readonly": True,
        "list": [("id", "ID"), ("products", "产品"), ("name", "姓名"), ("tel", "电话"), ("status", "状态"),
                 ("created_at", "时间")],
        "fields": [("products", "您想购的产品", "textarea", False), ("description", "购买说明", "textarea", False),
                   ("name", "姓名", "text", False), ("tel", "电话号码", "text", False),
                   ("fax", "传真号码", "text", False), ("email", "电子邮箱", "text", False),
                   ("address", "发货地址", "text", False), ("member_id", "会员ID", "text", False),
                   ("created_at", "时间", "text", False)],
        "editable": [("status", "处理状态", "select", True)],
        "options": {"status": lambda: [(s, s) for s in ("未处理", "已联系", "已发货", "已完成", "已取消")]},
    },
    "faqs": {
        "title": "常见问题", "table": "faqs", "order": "sort, id",
        "list": [("id", "ID"), ("question", "问题"), ("answer", "回答"), ("sort", "排序")],
        "fields": [("question", "问题", "text", True), ("answer", "回答", "textarea", True),
                   ("sort", "排序", "number", False)],
        "search": ["question", "answer"],
    },
    "chat_sessions": {
        "title": "客服对话", "table": "chat_sessions", "order": "updated_at DESC, id DESC", "readonly": True,
        "list": [("id", "ID"), ("first_question", "首个问题"), ("messages", "轮数"), ("has_lead", "已留资"),
                 ("ip", "IP"), ("updated_at", "最后时间")],
        "fields": [],
        "search": ["first_question"],
    },
    "members": {
        "title": "会员管理", "table": "members", "order": "id DESC", "readonly": True,
        "list": [("id", "ID"), ("username", "用户名"), ("contact", "联系人"), ("company", "公司"),
                 ("tel", "电话"), ("created_at", "注册时间")],
        "fields": [("username", "用户名", "text", False), ("contact", "联系人", "text", False),
                   ("company", "公司名称", "text", False), ("tel", "联系电话", "text", False),
                   ("email", "电子邮箱", "text", False), ("address", "联系地址", "text", False),
                   ("created_at", "注册时间", "text", False)],
    },
}

MENU = [("products", "categories"), ("news", "pages", "jobs"), ("chat_sessions", "faqs"),
        ("feedback", "orders", "job_applications", "members")]


def login_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if not session.get("admin_id"):
            return redirect(url_for("admin.login", next=request.path))
        return view(*a, **kw)
    return wrapped


def _check_csrf():
    if request.form.get("_csrf") != session.get("_csrf"):
        abort(400, "表单已过期，请刷新页面后重试。")


@bp.context_processor
def admin_ctx():
    unread = {
        "feedback": query("SELECT COUNT(*) FROM feedback WHERE is_read=0", one=True)[0],
        "orders": query("SELECT COUNT(*) FROM orders WHERE status='未处理'", one=True)[0],
        "job_applications": query("SELECT COUNT(*) FROM job_applications WHERE is_read=0", one=True)[0],
    } if session.get("admin_id") else {}
    return {"RES": RESOURCES, "MENU": MENU, "unread": unread}


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        _check_csrf()
        a = query("SELECT * FROM admins WHERE username=?", (request.form.get("username", ""),), one=True)
        if a and check_password_hash(a["password_hash"], request.form.get("password", "")):
            session["admin_id"] = a["id"]
            nxt = request.args.get("next", "")
            return redirect(nxt if nxt.startswith("/admin") else url_for("admin.dashboard"))
        flash("用户名或密码错误", "error")
    return render_template("admin/login.html")


@bp.route("/logout")
def logout():
    session.pop("admin_id", None)
    return redirect(url_for("admin.login"))


@bp.route("/")
@login_required
def dashboard():
    counts = {k: query(f"SELECT COUNT(*) FROM {v['table']}", one=True)[0] for k, v in RESOURCES.items()}
    latest_feedback = query("SELECT * FROM feedback ORDER BY id DESC LIMIT 5")
    latest_orders = query("SELECT * FROM orders ORDER BY id DESC LIMIT 5")
    return render_template("admin/dashboard.html", counts=counts, latest_feedback=latest_feedback,
                           latest_orders=latest_orders)


@bp.route("/password", methods=["GET", "POST"])
@login_required
def password():
    if request.method == "POST":
        _check_csrf()
        a = query("SELECT * FROM admins WHERE id=?", (session["admin_id"],), one=True)
        f = request.form
        if not check_password_hash(a["password_hash"], f.get("old", "")):
            flash("原密码错误", "error")
        elif len(f.get("new", "")) < 6 or f.get("new") != f.get("new2"):
            flash("新密码至少 6 位，且两次输入一致", "error")
        else:
            execute("UPDATE admins SET password_hash=? WHERE id=?", (generate_password_hash(f["new"]), a["id"]))
            flash("密码已修改", "ok")
            return redirect(url_for("admin.dashboard"))
    return render_template("admin/password.html")


def _res(name):
    res = RESOURCES.get(name) or abort(404)
    return res


def _options(res):
    return {k: fn() for k, fn in res.get("options", {}).items()}


@bp.route("/<name>/")
@login_required
def listing(name):
    res = _res(name)
    q = request.args.get("q", "").strip()
    sql = res.get("list_sql", f"SELECT * FROM {res['table']}")
    args = []
    if q and res.get("search"):
        sql += " WHERE " + " OR ".join(f"{c} LIKE ?" for c in res["search"])
        args = [f"%{q}%"] * len(res["search"])
    order = res["order"]
    rows = query(f"{sql} ORDER BY {order}", args)
    return render_template("admin/list.html", name=name, res=res, rows=rows, q=q)


def _save_image(file):
    if not file or not file.filename:
        return None
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in current_app.config["ALLOWED_IMAGE_EXT"]:
        flash("图片格式不支持", "error")
        return None
    os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
    fname = secrets.token_hex(8) + "_" + secure_filename(file.filename)
    file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], fname))
    return "/uploads/" + fname


def _collect(res, fields, row=None):
    import json
    values, errors = {}, []
    for col, label, typ, req in fields:
        if typ == "image":
            uploaded = _save_image(request.files.get(col))
            values[col] = uploaded or request.form.get(col, "").strip() or (row[col] if row else "")
            continue
        if typ == "bool":
            values[col] = 1 if request.form.get(col) else 0
            continue
        val = request.form.get(col, "").strip()
        if typ == "number":
            val = int(val) if val.lstrip("-").isdigit() else 0
        if typ == "select" and val == "":
            val = None
        if typ == "json" and val:
            try:
                json.loads(val)
            except ValueError:
                errors.append(f"{label} 不是有效的 JSON")
        if req and val in ("", None):
            errors.append(f"请填写 {label}")
        if col == "created_at" and not val:
            continue  # 留空则用数据库默认时间
        values[col] = val
    return values, errors


@bp.route("/<name>/new", methods=["GET", "POST"])
@login_required
def create(name):
    res = _res(name)
    if res.get("readonly"):
        abort(404)
    if request.method == "POST":
        _check_csrf()
        values, errors = _collect(res, res["fields"])
        if errors:
            for e in errors:
                flash(e, "error")
        else:
            cols = ", ".join(values)
            execute(f"INSERT INTO {res['table']} ({cols}) VALUES ({', '.join('?' * len(values))})",
                    tuple(values.values()))
            flash("已添加", "ok")
            return redirect(url_for("admin.listing", name=name))
    return render_template("admin/form.html", name=name, res=res, row=request.form or None,
                           fields=res["fields"], options=_options(res), mode="new")


@bp.route("/<name>/<int:rid>", methods=["GET", "POST"])
@login_required
def edit(name, rid):
    res = _res(name)
    row = query(f"SELECT * FROM {res['table']} WHERE id=?", (rid,), one=True) or abort(404)
    readonly = res.get("readonly")
    if name == "chat_sessions":
        msgs = query("SELECT * FROM chat_messages WHERE session_id=? ORDER BY id", (rid,))
        return render_template("admin/chat_view.html", name=name, res=res, row=row, msgs=msgs)
    fields = res.get("editable", []) if readonly else res["fields"]
    if readonly and "is_read" in row.keys() and not row["is_read"]:
        execute(f"UPDATE {res['table']} SET is_read=1 WHERE id=?", (rid,))
    if request.method == "POST":
        _check_csrf()
        if not fields:
            abort(400)
        values, errors = _collect(res, fields, row)
        if errors:
            for e in errors:
                flash(e, "error")
        else:
            sets = ", ".join(f"{c}=?" for c in values)
            execute(f"UPDATE {res['table']} SET {sets} WHERE id=?", tuple(values.values()) + (rid,))
            flash("已保存", "ok")
            return redirect(url_for("admin.listing", name=name))
    return render_template("admin/form.html", name=name, res=res, row=row, fields=fields,
                           options=_options(res), mode="view" if readonly else "edit")


@bp.route("/<name>/<int:rid>/delete", methods=["POST"])
@login_required
def delete(name, rid):
    _check_csrf()
    res = _res(name)
    execute(f"DELETE FROM {res['table']} WHERE id=?", (rid,))
    flash("已删除", "ok")
    return redirect(url_for("admin.listing", name=name))
