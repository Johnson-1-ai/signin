-- ============================================================
-- 签到系统 · Supabase 建表脚本
-- 使用方法：登录 Supabase 控制台 → 你的项目 → SQL Editor → 新建查询
--           → 把下面整段粘贴进去 → 点 Run
-- ============================================================

-- 1) 人员表（名单主表）
create table if not exists people (
  id         uuid primary key default gen_random_uuid(),
  name       text not null,                 -- 姓名
  sid        text not null,                 -- 学号
  email      text,                          -- 登录邮箱（关联账号，选填；填了才能登录看自己记录）
  ord        int  not null default 0,       -- 显示顺序（按录入顺序）
  created_at timestamptz not null default now()
);

-- 2) 签到活动表（每次「日期 + 上午/下午」对应一条）
create table if not exists sessions (
  id         uuid primary key default gen_random_uuid(),
  sdate      text not null,                 -- 日期，如 2026-09-08
  period     text not null,                 -- 时段：上午 / 下午
  created_at timestamptz not null default now(),
  unique (sdate, period)                    -- 同一天同一时段只允许一次签到
);

-- 3) 签到记录表（某次签到中，每个人的状态快照）
create table if not exists records (
  id         uuid primary key default gen_random_uuid(),
  session_id uuid not null references sessions(id) on delete cascade,
  person_id  uuid not null,                 -- 对应人员 id（无外键，删人员不影响历史）
  name       text not null,                 -- 姓名快照
  sid        text not null,                 -- 学号快照
  ord        int  not null default 0,       -- 该次签到内的顺序
  status     text not null default '未到',  -- 已到 / 未到
  note       text not null default '',      -- 备注
  updated_at timestamptz not null default now()
);

-- 4) 授权：让匿名(anon)角色可读写这三张表
--    （本工具把 anon key 直接内嵌在前端，适合班级/内部使用；
--      对公网恶意者而言 key 可见，请勿存放敏感数据）
grant usage on schema public to anon, authenticated;
grant select, insert, update, delete on people, sessions, records to anon, authenticated;

-- 5) 行级安全策略：允许 anon 全量读写（简单工具，不做多用户隔离）
alter table people   enable row level security;
alter table sessions enable row level security;
alter table records  enable row level security;

create policy "people_all"   on people   for all to anon using (true) with check (true);
create policy "sessions_all" on sessions for all to anon using (true) with check (true);
create policy "records_all"  on records  for all to anon using (true) with check (true);

-- 完成。现在到 项目设置 → API，复制 Project URL 与 anon public key 即可。
