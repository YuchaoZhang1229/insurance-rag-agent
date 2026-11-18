-- auto-generated definition
create table products
(
    id           bigserial,
    name         varchar(200)                                                 not null,
    clause_name  varchar(300)                                                 not null,
    category     varchar(50)                                                  not null
        constraint chk_products_category
            check ((category)::text = ANY
                   ((ARRAY ['medical'::character varying, 'critical_illness'::character varying, 'accident'::character varying, 'life'::character varying])::text[])),
    insurer      varchar(120)                                                 not null,
    image_url    text,
    description  text,
    min_premium  numeric(14, 2),
    max_premium  numeric(14, 2),
    target_group varchar(300),
    highlights   text[],
    status       varchar(30)              default 'active'::character varying not null,
    created_at   timestamp with time zone default CURRENT_TIMESTAMP           not null,
    updated_at   timestamp with time zone default CURRENT_TIMESTAMP           not null,
    primary key ()
);

comment on table products is '保险商城在售及历史保险产品';

comment on column products.id is '产品主键';

comment on column products.name is '商城展示名称';

comment on column products.clause_name is '主条款文件名，包含 .pdf 后缀';

comment on column products.category is '险种分类：医疗、重疾、意外或寿险';

comment on column products.insurer is '承保保险公司';

comment on column products.image_url is '产品展示图片地址';

comment on column products.description is '产品简介';

comment on column products.min_premium is '产品公开的最低年缴保费参考';

comment on column products.max_premium is '产品公开的最高保费参考，可为空';

comment on column products.target_group is '适用人群说明';

comment on column products.highlights is '产品亮点列表';

comment on column products.status is '产品状态';

comment on column products.created_at is '创建时间';

comment on column products.updated_at is '最后更新时间';

alter table products
    owner to insurance;

create unique index products_pkey
    on products (id);

create index idx_products_category
    on products (category);

create index idx_products_status
    on products (status);

