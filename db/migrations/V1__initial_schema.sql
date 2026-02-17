-- V1__initial_schema.sql
-- Initial schema for Windsong blog system
-- Equivalent to GORM AutoMigrate for Post, Photo, GoldAnalysis models

-- Posts table
CREATE TABLE IF NOT EXISTS posts (
    id          BIGSERIAL PRIMARY KEY,
    slug        TEXT NOT NULL,
    title       TEXT,
    date        TIMESTAMPTZ,
    tags        TEXT[],
    content     TEXT,
    content_hash VARCHAR(64),
    is_published BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ,
    updated_at  TIMESTAMPTZ
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_posts_slug ON posts (slug);
CREATE INDEX IF NOT EXISTS idx_posts_date ON posts (date);
CREATE INDEX IF NOT EXISTS idx_posts_is_published ON posts (is_published);

-- Photos table
CREATE TABLE IF NOT EXISTS photos (
    id          BIGSERIAL PRIMARY KEY,
    url         TEXT NOT NULL,
    thumbnail   TEXT,
    title       TEXT NOT NULL,
    description TEXT,
    date        TIMESTAMPTZ,
    location    TEXT,
    city        TEXT,
    country     TEXT,
    tags        TEXT,
    aspect_ratio TEXT,
    created_at  TIMESTAMPTZ,
    updated_at  TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_photos_date ON photos (date);
CREATE INDEX IF NOT EXISTS idx_photos_location ON photos (location);

-- Gold analyses table
CREATE TABLE IF NOT EXISTS gold_analyses (
    id             BIGSERIAL PRIMARY KEY,
    analysis_date  TIMESTAMPTZ NOT NULL,
    content        TEXT NOT NULL,
    model_used     VARCHAR(50),
    prompt_hash    VARCHAR(64),
    created_at     TIMESTAMPTZ,
    updated_at     TIMESTAMPTZ
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_gold_analyses_analysis_date ON gold_analyses (analysis_date);
