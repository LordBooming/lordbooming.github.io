-- WorldForge RPG: mundos privados por conta para hospedagem estática (GitHub Pages).
-- Execute uma vez no SQL Editor do projeto Supabase.

create table if not exists public.worldforge_worlds (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  local_id text not null check (char_length(local_id) between 1 and 120),
  name text not null check (char_length(name) between 1 and 160),
  world jsonb not null check (jsonb_typeof(world) = 'object'),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (owner_id, local_id)
);

create index if not exists worldforge_worlds_owner_updated_idx
  on public.worldforge_worlds (owner_id, updated_at desc);

alter table public.worldforge_worlds enable row level security;

revoke all on table public.worldforge_worlds from anon, authenticated;
grant select, insert, update, delete on table public.worldforge_worlds to authenticated;

drop policy if exists "Users can read their own worlds" on public.worldforge_worlds;
create policy "Users can read their own worlds"
  on public.worldforge_worlds for select to authenticated
  using ((select auth.uid()) = owner_id);

drop policy if exists "Users can add their own worlds" on public.worldforge_worlds;
create policy "Users can add their own worlds"
  on public.worldforge_worlds for insert to authenticated
  with check ((select auth.uid()) = owner_id);

drop policy if exists "Users can update their own worlds" on public.worldforge_worlds;
create policy "Users can update their own worlds"
  on public.worldforge_worlds for update to authenticated
  using ((select auth.uid()) = owner_id)
  with check ((select auth.uid()) = owner_id);

drop policy if exists "Users can delete their own worlds" on public.worldforge_worlds;
create policy "Users can delete their own worlds"
  on public.worldforge_worlds for delete to authenticated
  using ((select auth.uid()) = owner_id);
