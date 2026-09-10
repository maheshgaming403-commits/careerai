-- CareerAI Production Database Schema
-- Supabase Dashboard -> SQL Editor -> New query -> paste -> Run

create extension if not exists "uuid-ossp";

create table if not exists public.users (
  id uuid primary key default uuid_generate_v4(),
  email text unique not null,
  full_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.resumes (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references public.users(id) on delete cascade,
  file_name text not null,
  storage_path text,
  extracted_text text,
  created_at timestamptz not null default now()
);
create index if not exists resumes_user_id_idx on public.resumes(user_id);

create table if not exists public.resume_analysis (
  id uuid primary key default uuid_generate_v4(),
  resume_id uuid references public.resumes(id) on delete cascade,
  user_id uuid references public.users(id) on delete cascade,
  overall_score int check (overall_score between 0 and 100),
  strengths jsonb default '[]'::jsonb,
  weaknesses jsonb default '[]'::jsonb,
  recommended_roles jsonb default '[]'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.skills (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references public.users(id) on delete cascade,
  skill_name text not null,
  proficiency int check (proficiency between 1 and 5),
  created_at timestamptz not null default now(),
  unique (user_id, skill_name)
);

create table if not exists public.job_matches (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references public.users(id) on delete cascade,
  job_title text not null,
  match_score int check (match_score between 0 and 100),
  missing_skills jsonb default '[]'::jsonb,
  created_at timestamptz not null default now()
);
create index if not exists job_matches_user_id_idx on public.job_matches(user_id);

create table if not exists public.career_roadmaps (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references public.users(id) on delete cascade,
  target_role text not null,
  roadmap jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
create index if not exists career_roadmaps_user_id_idx on public.career_roadmaps(user_id);

create table if not exists public.roadmap_progress (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references public.users(id) on delete cascade,
  roadmap_id uuid not null references public.career_roadmaps(id) on delete cascade,
  step_index int not null,
  completed boolean not null default false,
  completed_at timestamptz,
  unique (roadmap_id, step_index)
);

create table if not exists public.interview_sessions (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references public.users(id) on delete cascade,
  role text not null,
  difficulty text default 'medium',
  status text default 'in_progress',
  overall_score int,
  created_at timestamptz not null default now(),
  completed_at timestamptz
);
create index if not exists interview_sessions_user_id_idx on public.interview_sessions(user_id);

create table if not exists public.interview_questions (
  id uuid primary key default uuid_generate_v4(),
  session_id uuid not null references public.interview_sessions(id) on delete cascade,
  question_index int not null,
  question text not null,
  created_at timestamptz not null default now(),
  unique (session_id, question_index)
);

create table if not exists public.interview_answers (
  id uuid primary key default uuid_generate_v4(),
  question_id uuid not null references public.interview_questions(id) on delete cascade,
  answer text not null,
  score int check (score between 0 and 100),
  feedback text,
  created_at timestamptz not null default now()
);
create index if not exists interview_answers_question_id_idx on public.interview_answers(question_id);

create table if not exists public.project_recommendations (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references public.users(id) on delete cascade,
  skill_gap text not null,
  project_title text not null,
  description text,
  difficulty text default 'beginner',
  created_at timestamptz not null default now()
);
create index if not exists project_recs_user_id_idx on public.project_recommendations(user_id);

-- Row Level Security: users can only access their own data
alter table public.users enable row level security;
alter table public.resumes enable row level security;
alter table public.resume_analysis enable row level security;
alter table public.skills enable row level security;
alter table public.job_matches enable row level security;
alter table public.career_roadmaps enable row level security;
alter table public.roadmap_progress enable row level security;
alter table public.interview_sessions enable row level security;
alter table public.interview_questions enable row level security;
alter table public.interview_answers enable row level security;
alter table public.project_recommendations enable row level security;

create policy "own users" on public.users for all using (auth.uid() = id) with check (auth.uid() = id);
create policy "own resumes" on public.resumes for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own analysis" on public.resume_analysis for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own skills" on public.skills for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own matches" on public.job_matches for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own roadmaps" on public.career_roadmaps for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own progress" on public.roadmap_progress for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own sessions" on public.interview_sessions for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own questions" on public.interview_questions for all using (
  exists (select 1 from public.interview_sessions s where s.id = session_id and s.user_id = auth.uid()));
create policy "own answers" on public.interview_answers for all using (
  exists (select 1 from public.interview_questions q join public.interview_sessions s on s.id = q.session_id
          where q.id = question_id and s.user_id = auth.uid()));
create policy "own projects" on public.project_recommendations for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
