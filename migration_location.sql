-- 定位签到：加签到范围 + 签到位置字段
-- 在 Supabase SQL Editor 运行，或给 Claude 一个 PAT 自动跑
alter table sessions add column if not exists center_lat double precision;
alter table sessions add column if not exists center_lng double precision;
alter table sessions add column if not exists radius double precision;

alter table records add column if not exists lat double precision;
alter table records add column if not exists lng double precision;
