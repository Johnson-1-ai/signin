# 签到系统 📋

电脑、手机互通的签到网页应用（PWA，可安装到桌面/主屏幕）。数据存云端（Supabase 免费版），管理员和学生在任意设备上都能实时看到同一份数据。

## 文件清单

| 文件 | 作用 |
|------|------|
| `index.html` | 应用本体（单文件，含全部界面与逻辑） |
| `schema.sql` | 建表脚本（在 Supabase 里运行一次） |
| `manifest.json` | PWA 描述（用于「添加到主屏幕」安装） |
| `sw.js` | 离线缓存（让应用可安装、断网也能打开外壳） |
| `icon-192.png` / `icon-512.png` | 应用图标 |

---

## 一、一次性配置（约 10 分钟）

### 第 1 步：注册 Supabase 并建项目

1. 打开 <https://supabase.com>，用邮箱/GitHub 注册登录。
2. 点 **New project**，起个名字（如 `signin`），设置数据库密码（自己记好），地区选离你近的（如 `Singapore`/`Tokyo`）。
3. 等 1–2 分钟项目初始化完成。

### 第 2 步：建表

1. 进入项目，左侧菜单点 **SQL Editor** → **New query**。
2. 把本目录 `schema.sql` 的**全部内容**粘贴进去，点 **Run**。
3. 左侧 **Table Editor** 里应能看到 `people`、`sessions`、`records` 三张表。

### 第 3 步：配置账号登录（关键）

1. 左侧 **Authentication** → **Sign In / Providers** → 找到 **Email**。
2. 保证 **Email** 是开启的。
3. 把 **Confirm email** 关掉（否则学生注册后要收确认邮件才能登录，很麻烦）。
4. **Allow new users to sign up**（允许新用户注册）保持开启。

> 这一步让「学生自助注册邮箱账号」立即可用，无需你手动帮每个人建号。

### 第 4 步：拿两个密钥

左侧 **Settings** → **API**，复制两个值：

- **Project URL**，形如 `https://xxxx.supabase.co`
- **anon public** key，形如 `eyJhbGciOi...`

### 第 5 步：填入 index.html

用记事本/编辑器打开 `index.html`，找到最上方这段：

```js
const SUPABASE_URL = "";        // 填 Project URL
const SUPABASE_ANON_KEY = "";   // 填 anon public key
const ADMIN_EMAILS = "";        // 填你的邮箱（管理员）
```

- `SUPABASE_URL`：填第 4 步的 Project URL
- `SUPABASE_ANON_KEY`：填 anon public key
- `ADMIN_EMAILS`：填**你自己的邮箱**（登录后拥有管理权限）。多个管理员用英文逗号分隔，如 `a@x.com,b@x.com`

保存即可。

---

## 二、让手机和电脑都能用（选一种）

数据在云端，所以**打开同一个 `index.html` 就行**。区别在于怎么把这个文件给到手机、以及能不能「安装成快捷方式」。

### 方式 A：免费托管（推荐，可安装快捷方式）

把 `signin` 整个文件夹上传到任意免费静态托管，得到一个 HTTPS 网址：

- **GitHub Pages**：建仓库 → Settings → Pages → 选分支，得到 `https://用户名.github.io/xxx/`
- **Vercel / Netlify / Cloudflare Pages**：导入文件夹即可，得到 `https://xxx.vercel.app`

然后在手机/电脑浏览器打开该网址：

- **手机**：浏览器菜单 → **添加到主屏幕**（安卓 Chrome）/ **添加到主屏幕**（iPhone Safari 分享 → 添加到主屏幕）
- **电脑**：Chrome/Edge 地址栏右侧会出现 **安装** 图标，点击即装成桌面应用

> 只有 HTTPS 才能安装成快捷方式（PWA），这也是推荐托管的原因。

### 方式 B：局域网（临时用，不能安装）

同一 WiFi 下，在电脑上 `signin` 目录里运行：

```bash
python3 -m http.server 8000
```

手机浏览器访问 `http://电脑局域网IP:8000`（电脑 IP 用 `ipconfig`/`ifconfig` 查）。能用，但非 HTTPS，不能「添加到主屏幕」。

### 方式 C：直接发文件（不推荐）

把 `index.html` 通过微信/QQ 发给手机打开。部分浏览器对 `file://` 有限制，可能登录异常，仅作应急。

---

## 三、使用说明

### 管理员（你）

1. **人员**页：整段粘贴名单，每行一人：
   ```
   张三 2023001 zhang@example.com
   李四 2023002 li@example.com
   王五 2023003
   ```
   姓名和学号用空格/逗号分隔，**邮箱选填**（填了的学生才能登录看自己的记录）。点「解析预览」→「保存到名单」。
2. **签到**页：选日期 + 上午/下午，点「开始签到」。
3. **逐人签到**：一人一屏，姓名学号居中；左下「未到」、右下「已到」，下方备注框可填。点完自动跳到下一个人；可「上一个」回退；右上「结果」随时查看。
4. **结果/未到名单**：签到结束自动进入。**未到名单可逐一点击改成「已到」**；下方可「复制名单」或「下载 CSV」。
5. **记录**页：按日期查询，点某条查看该次完整名单、未到名单、删除该次签到。

### 学生（每人独立账号）

1. 打开同一网址 → 用邮箱**注册** → 登录。
2. 登录后只能看到**自己的**历次签到状态与备注（只读）。
3. 若提示「未找到你的信息」，说明管理员还没把你的邮箱加进名单，联系管理员即可。

> 学生注册的邮箱，必须与管理员在名单里填的邮箱一致，才会自动关联。

---

## 四、常见问题

- **国内打开 Supabase 慢/打不开**：可挂代理，或把项目地区选得更近；仍不行可考虑换 LeanCloud 等国内 BaaS（需改动数据层，可再让我适配）。
- **学生登录提示邮箱未确认**：是你第 3 步没关掉 Confirm email，去 Authentication → Sign In/Providers 关掉即可。
- **数据安全说明**：本工具把 anon key 直接内嵌在前端、且数据表对匿名角色开放读写，适合**班级/内部小范围使用**，请勿存放敏感信息。
- **修改管理员**：改 `index.html` 顶部的 `ADMIN_EMAILS` 后重新部署即可。
- **改了 schema 想重来**：`schema.sql` 用了 `if not exists`，重复运行安全；要彻底重置可在 SQL Editor 里 `drop table records, sessions, people;` 后再运行一次。
