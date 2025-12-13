-- Pipeline Runs
create table if not exists pipeline_runs (
    id uuid primary key default gen_random_uuid(),
    bill_id text not null,
    jurisdiction text,
    models jsonb,
    status text default 'running' check (status in ('running', 'completed', 'failed')),
    error text,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- Pipeline Steps
create table if not exists pipeline_steps (
    id uuid primary key default gen_random_uuid(),
    run_id uuid references pipeline_runs(id) on delete cascade not null,
    step_name text not null,
    model text,
    data jsonb,
    created_at timestamptz default now()
);

-- Indexes
create index if not exists idx_pipeline_runs_bill on pipeline_runs(bill_id);
create index if not exists idx_pipeline_steps_run on pipeline_steps(run_id);
