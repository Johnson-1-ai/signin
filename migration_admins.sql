-- 账号表（终极管理员 / 管理员）
-- 在 Supabase SQL Editor 里运行本脚本，或给 Claude 一个 PAT 让它自动跑
create table if not exists admins (
  id         uuid primary key default gen_random_uuid(),
  sid        text not null unique,          -- 账号学号
  role       text not null default 'admin', -- 'super' 终极管理员 / 'admin' 管理员
  created_at timestamptz not null default now()
);

grant select, insert, update, delete on admins to anon, authenticated;
alter table admins enable row level security;
create policy "admins_all" on admins for all to anon using (true) with check (true);

-- 播种：把当前 admin 账号设为首个终极管理员
insert into admins (sid, role) values ('admin', 'super') on conflict (sid) do nothing;
