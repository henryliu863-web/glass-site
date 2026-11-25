# 玻璃工具 / 玻璃五金企业网站（中文版）

按一个老式 ASP 企业站的前台布局和功能，用 Python Flask + SQLite 重新实现：页面结构、配色、栏目和表单都与原站对应，另外补了一个管理后台。

## 快速开始

```bash
pip install -r requirements.txt
python app.py
```

打开 http://127.0.0.1:5000 。首次运行时会自动建库（`data/site.db`），并写入示例分类、产品、新闻和招聘信息。

- 后台地址：http://127.0.0.1:5000/admin
- 默认账号：`admin` / `admin123`（**上线前一定要改**：后台右上角“修改密码”，或启动前设置环境变量 `ADMIN_PASSWORD`）

正式部署时（需另外 `pip install gunicorn`）请设置随机的 `SECRET_KEY` 环境变量，并用 gunicorn / waitress 启动，例如：

```bash
SECRET_KEY=$(python -c "import secrets;print(secrets.token_hex(32))") gunicorn -w 2 -b 0.0.0.0:8000 app:app
```

## 先改这些

| 要改的内容 | 位置 |
|---|---|
| 公司名、Logo 文字、电话、传真、手机、邮箱、地址、营业时间 | `config.py` 里的 `SITE` |
| Banner、公司简介图、生产设备图、广告条、二维码、客服头像 | 覆盖 `static/img/` 下的同名文件（也可以换成 .jpg，同时改模板里的文件名） |
| 产品、分类、新闻、招聘、公司简介 / 企业文化 / 荣誉 / 组织机构 / 招商加盟 | 后台对应菜单 |

现在的公司信息和图片都是占位内容。`python scripts/make_images.py` 可以重新生成这些占位图。

## 页面对照

| 原站 | 新站 | 说明 |
|---|---|---|
| cnindex.asp | `/` | 网站首页：轮播、产品分类、公司简介、生产设备轮播、广告条 |
| about.asp?id= | `/about?id=profile` 等 | 公司简介 / 企业文化 / 公司荣誉 / 组织机构 |
| product.asp?bigid=&smallid= | `/product?bigid=` / `?smallid=` | 产品列表，4 列 × 8 行分页 |
| productshow.asp | `/productshow?id=` | 产品详情：图片、规格表、上一个 / 下一个、在线定购 |
| news.asp / news_list.asp | `/news`、`/news_show?id=` | 新闻中心 |
| member.asp | `/member` | 会员注册、登录；登录后可看到“我的定单” |
| feedback.asp | `/feedback` | 在线留言 |
| join.asp | `/join` | 招商加盟 |
| order.asp | `/order` | 在线定单（会员登录后自动带出联系方式） |
| job.asp / job_list.asp | `/job`、`/job_apply?id=` | 人才招聘、应聘此岗位 |
| contact.asp | `/contact` | 联系我们 |

旧的 `.asp` 地址会 301 跳转到新地址，方便保留原来的外链和搜索收录。

## 后台功能

- 产品管理（可上传图片、编辑规格表）、产品分类（大类 / 小类）
- 新闻管理、单页管理、招聘管理
- 留言管理、定单管理（可改处理状态）、应聘简历、会员管理；未读数量显示在菜单上

## 智能客服

右侧“在线客服”是接入 Claude 的 AI 客服（`chat.py`）：

- 知识来源：`config.py` 里的公司信息 + 后台“常见问题” + 产品目录（实时读取，后台改了马上生效）
- 推荐产品时附带详情页链接；不编造价格、库存
- 客户留下称呼和电话后自动登记到后台“留言管理”，标题为“【智能客服】客户询盘”
- 窗口右上角“转人工”显示电话、手机、微信（在 `config.py` 的 `SITE` 里改）
- 后台“客服对话”可查看所有对话记录

需要在 Railway 的 Variables 里设置 `ANTHROPIC_API_KEY`。未设置或接口出错时，客服会自动回复人工联系方式。
可选变量：`CHAT_MODEL`（默认 claude-haiku-5-5）、`CHAT_LIMIT_PER_IP_DAY`（每个访客每天提问上限，默认 40）、
`CHAT_LIMIT_TOTAL_DAY`（全站每天上限，默认 1500）。

## 产品规格表格式

产品的“规格表(JSON)”字段示例：

```json
{
  "headers": ["型号", "刀轮代号", "切割厚度(MM)", "包装数量(把)"],
  "rows": [["GC-001", "A", "0.3-2", "360"], ["", "M", "2-6", ""]],
  "merge": [0, 3]
}
```

`merge` 中列出的列会在详情页合并成一个单元格（例如型号、包装数量）。

## 目录结构

```
app.py            前台路由（含旧 .asp 地址跳转）
admin.py          管理后台
db.py             建表与示例数据
config.py         站点配置（公司信息在这里改）
templates/        页面模板（base / layout 为公共框架，admin/ 为后台）
static/css        style.css 前台样式，admin.css 后台样式
static/js         轮播、在线客服浮窗
static/img        占位图片
static/uploads    后台上传的图片
scripts/          占位图片生成脚本
```
