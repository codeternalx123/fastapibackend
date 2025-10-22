-- Enable necessary extensions
create extension if not exists "uuid-ossp";
create extension if not exists "pgcrypto";

-- Users table (extends existing auth.users)
create table public.user_profiles (
    id uuid references auth.users not null primary key,
    full_name text,
    avatar_url text,
    health_conditions text[],
    dietary_restrictions text[],
    created_at timestamp with time zone default now(),
    updated_at timestamp with time zone default now()
);

-- Meals table
create table public.meals (
    id uuid default uuid_generate_v4() primary key,
    user_id uuid references public.user_profiles not null,
    name text not null,
    description text,
    meal_type text not null, -- 'breakfast', 'lunch', 'dinner', 'snack'
    calories integer,
    protein float,
    carbs float,
    fats float,
    nutrients jsonb,
    cancer_fighting_ingredients text[],
    consumed_at timestamp with time zone default now(),
    created_at timestamp with time zone default now()
);

-- Meal plans table
create table public.meal_plans (
    id uuid default uuid_generate_v4() primary key,
    user_id uuid references public.user_profiles not null,
    name text not null,
    description text,
    start_date date not null,
    end_date date not null,
    plan_type text not null, -- 'weekly', 'monthly'
    nutritional_goals jsonb,
    created_at timestamp with time zone default now(),
    updated_at timestamp with time zone default now()
);

-- Meal plan items table
create table public.meal_plan_items (
    id uuid default uuid_generate_v4() primary key,
    meal_plan_id uuid references public.meal_plans not null,
    meal_id uuid references public.meals,
    day_of_week integer, -- 0-6 for weekly plans
    week_number integer, -- 1-4 for monthly plans
    meal_type text not null,
    scheduled_time time,
    created_at timestamp with time zone default now()
);

-- Reminders table
create table public.reminders (
    id uuid default uuid_generate_v4() primary key,
    user_id uuid references public.user_profiles not null,
    title text not null,
    description text,
    reminder_type text not null, -- 'meal', 'medication', 'hydration'
    frequency text not null, -- 'daily', 'weekly', 'monthly'
    scheduled_time time not null,
    days_of_week integer[], -- Array of days (0-6)
    is_active boolean default true,
    created_at timestamp with time zone default now(),
    updated_at timestamp with time zone default now()
);

-- Analytics table
create table public.health_analytics (
    id uuid default uuid_generate_v4() primary key,
    user_id uuid references public.user_profiles not null,
    analysis_date date not null,
    period text not null, -- 'daily', 'weekly', 'monthly'
    metrics jsonb not null, -- Stores various health metrics
    nutritional_compliance float,
    meal_plan_adherence float,
    cancer_fighting_foods_consumed integer,
    created_at timestamp with time zone default now()
);

-- RLS Policies
alter table public.user_profiles enable row level security;
alter table public.meals enable row level security;
alter table public.meal_plans enable row level security;
alter table public.meal_plan_items enable row level security;
alter table public.reminders enable row level security;
alter table public.health_analytics enable row level security;

-- User profiles policy
create policy "Users can view their own profile"
    on public.user_profiles for select
    using (auth.uid() = id);

create policy "Users can update their own profile"
    on public.user_profiles for update
    using (auth.uid() = id);

-- Meals policy
create policy "Users can CRUD their own meals"
    on public.meals for all
    using (auth.uid() = user_id);

-- Meal plans policy
create policy "Users can CRUD their own meal plans"
    on public.meal_plans for all
    using (auth.uid() = user_id);

-- Meal plan items policy
create policy "Users can CRUD their own meal plan items"
    on public.meal_plan_items for all
    using (exists (
        select 1 from public.meal_plans mp
        where mp.id = meal_plan_items.meal_plan_id
        and mp.user_id = auth.uid()
    ));

-- Reminders policy
create policy "Users can CRUD their own reminders"
    on public.reminders for all
    using (auth.uid() = user_id);

-- Analytics policy
create policy "Users can view their own analytics"
    on public.health_analytics for select
    using (auth.uid() = user_id);

-- Indexes
create index idx_meals_user_id on public.meals(user_id);
create index idx_meals_consumed_at on public.meals(consumed_at);
create index idx_meal_plans_user_id on public.meal_plans(user_id);
create index idx_meal_plans_date_range on public.meal_plans(start_date, end_date);
create index idx_reminders_user_id on public.reminders(user_id);
create index idx_health_analytics_user_id_date on public.health_analytics(user_id, analysis_date);