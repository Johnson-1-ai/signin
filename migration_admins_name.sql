-- 给管理员账号加姓名字段
-- 在 Supabase SQL Editor 运行，或给 Claude 一个 PAT 自动跑
alter table admins add column if not exists name text;
