CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE product (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id            TEXT NOT NULL,
    env                  TEXT NOT NULL,
    external_product_id  TEXT NOT NULL,
    title                TEXT NOT NULL,
    description          TEXT NOT NULL,
    category             TEXT,
    gender               TEXT,
    image_url            TEXT,
    attributes           JSONB NOT NULL DEFAULT '{}'::jsonb,
    embedding            VECTOR(1024),
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, env, external_product_id)
);

CREATE INDEX idx_product_tenant_env ON product (tenant_id, env);
CREATE INDEX idx_product_embedding_hnsw ON product
    USING hnsw (embedding vector_cosine_ops);

CREATE TABLE items (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id        UUID NOT NULL REFERENCES product (id) ON DELETE CASCADE,
    tenant_id         TEXT NOT NULL,
    env               TEXT NOT NULL,
    external_item_id  TEXT NOT NULL,
    size              TEXT,
    color             TEXT,
    price             NUMERIC(10, 2),
    stock             INTEGER NOT NULL DEFAULT 0,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, env, external_item_id)
);

CREATE INDEX idx_items_tenant_env_product ON items (tenant_id, env, product_id);
CREATE INDEX idx_items_tenant_env_size_color ON items (tenant_id, env, size, color);
