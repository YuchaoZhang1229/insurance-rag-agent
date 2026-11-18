-- auto-generated definition
create table chat_threads
(
    id         uuid                                                         not null,
    user_id    bigint                                                       not null,
    title      varchar(200)             default '新会话'::character varying not null,
    created_at timestamp with time zone default CURRENT_TIMESTAMP           not null,
    updated_at timestamp with time zone default CURRENT_TIMESTAMP           not null,
    primary key ()
);

comment on table chat_threads is '用户与智能客服的会话元数据，消息正文由 LangGraph Checkpointer 保存';

comment on column chat_threads.id is '会话主键，同时作为 LangGraph thread_id';

comment on column chat_threads.user_id is 'JWT 中解析出的业务用户主键';

comment on column chat_threads.title is '会话列表展示标题';

comment on column chat_threads.created_at is '会话创建时间';

comment on column chat_threads.updated_at is '最后一次对话或修改标题的时间';

alter table chat_threads
    owner to insurance;

create unique index chat_threads_pkey
    on chat_threads (id);

create index idx_chat_threads_user_updated
    on chat_threads (user_id asc, updated_at desc);

