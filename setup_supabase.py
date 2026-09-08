#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键搭建 Supabase：建项目 -> 建表 -> 关邮箱确认 -> 取密钥 -> 写入 index.html
用法：SUPABASE_PAT=sbp_xxx python3 setup_supabase.py
     （令牌通过环境变量传入，不写入任何文件）
"""
import sys, os, json, time, re, secrets, string, urllib.request, urllib.error

API = "https://api.supabase.com"
PAT = os.environ.get("SUPABASE_PAT") or (sys.argv[1] if len(sys.argv) > 1 else "")
REGION = os.environ.get("REGION", "ap-southeast-1")      # 新加坡
PROJECT_NAME = os.environ.get("PROJECT_NAME", "signin")
DB_PASS = secrets.token_urlsafe(16) + "A1"               # 随机数据库密码

if not PAT:
    print("用法: SUPABASE_PAT=sbp_xxx python3 setup_supabase.py"); sys.exit(1)

def req(method, path, body=None, raw=False):
    url = API + path
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header("Authorization", "Bearer " + PAT)
    r.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    r.add_header("Accept", "application/json")
    if body is not None:
        r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r) as resp:
            txt = resp.read().decode()
            return (txt if raw else (json.loads(txt) if txt else None)), resp.status
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        raise RuntimeError(f"{method} {path} -> HTTP {e.code}: {err[:500]}")

def find_anon(keys):
    if isinstance(keys, dict):
        return keys.get("anon") or keys.get("anon_key")
    for k in keys:
        if isinstance(k, dict) and "service" not in (k.get("name") or ""):
            return k.get("api_key") or k.get("anon")
    return None

def main():
    # 1) 找组织（没有就自动建一个）
    orgs, _ = req("GET", "/v1/organizations")
    if not orgs:
        print("[1/6] 账号下暂无组织，自动创建一个…")
        try:
            created, _ = req("POST", "/v1/organizations", {"name": "signin-org"})
        except RuntimeError as e:
            raise RuntimeError("自动建组织失败，请到 supabase.com 控制台随便建一个组织（名字任意、免费计划）后重试：" + str(e))
        orgs = created if isinstance(created, list) else [created]
    org = orgs[0]
    org_id = org.get("id")
    print(f"[1/6] 组织: {org.get('name')} ({org_id})")

    # 2) 创建项目
    body = {"name": PROJECT_NAME, "region": REGION, "db_pass": DB_PASS}
    if org_id:
        body["organization_id"] = org_id
    proj, _ = req("POST", "/v1/projects", body)
    ref = proj.get("id") or proj.get("ref")
    if not ref:
        raise RuntimeError("创建项目失败，返回: " + json.dumps(proj, ensure_ascii=False)[:500])
    print(f"[2/6] 项目已创建，ref={ref}")

    # 3) 等待就绪
    print("[3/6] 等待数据库就绪…", end="", flush=True)
    ok = False
    for _ in range(60):
        p, _ = req("GET", f"/v1/projects/{ref}")
        st = p.get("status", "")
        print(".", end="", flush=True)
        if st in ("ACTIVE_HEALTHY", "ACTIVE"):
            ok = True; break
        time.sleep(6)
    print()
    if not ok:
        raise RuntimeError("项目长时间未就绪，请到 supabase.com 控制台查看")

    # 4) 建表
    schema = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql"),
                  encoding="utf-8").read()
    req("POST", f"/v1/projects/{ref}/database/query", {"query": schema})
    print("[4/6] 建表完成（people / sessions / records）")

    # 5) 关闭邮箱确认、允许注册
    cfg, _ = req("GET", f"/v1/projects/{ref}/config/auth")
    print(f"[5/6] 当前 auth: mailer_autoconfirm={cfg.get('mailer_autoconfirm')}, disable_signup={cfg.get('disable_signup')}")
    try:
        req("PATCH", f"/v1/projects/{ref}/config/auth",
            {"mailer_autoconfirm": True, "disable_signup": False})
    except RuntimeError:
        # 部分版本要求提交完整配置，退回合并后再提交
        cfg.update({"mailer_autoconfirm": True, "disable_signup": False})
        req("PATCH", f"/v1/projects/{ref}/config/auth", cfg)
    cfg2, _ = req("GET", f"/v1/projects/{ref}/config/auth")
    print(f"      改后 auth: mailer_autoconfirm={cfg2.get('mailer_autoconfirm')}, disable_signup={cfg2.get('disable_signup')}")

    # 6) 取 anon key 并写入 index.html
    keys, _ = req("GET", f"/v1/projects/{ref}/api-keys")
    anon_key = find_anon(keys)
    if not anon_key:
        raise RuntimeError("未找到 anon key，返回: " + json.dumps(keys, ensure_ascii=False)[:500])
    url = f"https://{ref}.supabase.co"

    idx = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    html = open(idx, encoding="utf-8").read()
    html = html.replace('const SUPABASE_URL = "";', f'const SUPABASE_URL = "{url}";')
    html = html.replace('const SUPABASE_ANON_KEY = "";', f'const SUPABASE_ANON_KEY = "{anon_key}";')
    open(idx, "w", encoding="utf-8").write(html)

    print("[6/6] 完成 ✅")
    print("=" * 50)
    print("Project URL :", url)
    print("Anon key    :", anon_key[:24] + "…" + anon_key[-6:])
    print("数据库密码  :", DB_PASS, "（仅需直连数据库时用，一般用不到）")
    print("已自动写入 index.html 的 SUPABASE_URL / SUPABASE_ANON_KEY")
    print("=" * 50)

if __name__ == "__main__":
    main()
