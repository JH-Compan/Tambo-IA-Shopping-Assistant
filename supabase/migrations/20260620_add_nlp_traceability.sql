do $$
begin
    alter table public.chat_messages
        add column if not exists intent_confidence numeric,
        add column if not exists nlp_method text,
        add column if not exists nlp_analysis jsonb not null default '{}'::jsonb,
        add column if not exists processing_status text not null default 'pending',
        add column if not exists processed_at timestamp without time zone;
exception
    when duplicate_column then null;
end $$;

do $$
begin
    if not exists (
        select 1
        from pg_constraint
        where conname = 'chat_messages_intent_confidence_range_chk'
    ) then
        alter table public.chat_messages
            add constraint chat_messages_intent_confidence_range_chk
            check (intent_confidence is null or (intent_confidence >= 0 and intent_confidence <= 1));
    end if;
end $$;

do $$
begin
    if not exists (
        select 1
        from pg_constraint
        where conname = 'chat_messages_processing_status_chk'
    ) then
        alter table public.chat_messages
            add constraint chat_messages_processing_status_chk
            check (processing_status in ('pending', 'processed', 'clarification', 'failed'));
    end if;
end $$;

do $$
begin
    alter table public.chat_conversations
        add column if not exists context_state jsonb not null default '{}'::jsonb,
        add column if not exists clarification_count integer not null default 0;
exception
    when duplicate_column then null;
end $$;

do $$
begin
    if not exists (
        select 1
        from pg_constraint
        where conname = 'chat_conversations_clarification_count_chk'
    ) then
        alter table public.chat_conversations
            add constraint chat_conversations_clarification_count_chk
            check (clarification_count >= 0);
    end if;
end $$;

create index if not exists idx_chat_messages_conversation_created_at
    on public.chat_messages (conversation_id, created_at);

create index if not exists idx_chat_messages_processing_status
    on public.chat_messages (processing_status);

create index if not exists idx_chat_conversations_user_status
    on public.chat_conversations (user_id, status);
