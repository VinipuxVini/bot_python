-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    full_name TEXT,
    username TEXT,
    role TEXT NOT NULL DEFAULT 'user',  -- 'user', 'moderator', 'admin'
    is_active BOOLEAN DEFAULT TRUE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Create logs (errors)
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(telegram_id) ON DELETE SET NULL,
    error_text TEXT NOT NULL,
    level TEXT DEFAULT 'error',  -- error, info, warning
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create groups table
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_groups_chat_id ON groups(chat_id);

-- Create file descriptions table
CREATE TABLE IF NOT EXISTS file_descriptions (
    id SERIAL PRIMARY KEY,
    file_id TEXT NOT NULL,
    file_name TEXT,
    description TEXT,
    uploaded_by BIGINT REFERENCES users(telegram_id) ON DELETE SET NULL,
    group_id BIGINT REFERENCES groups(chat_id) ON DELETE SET NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create reports table
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    week INTEGER NOT NULL,
    date_from DATE NOT NULL,
    date_to DATE NOT NULL,
    total_files INTEGER,
    success_files INTEGER,
    failed_files JSONB DEFAULT '[]',      -- массив объектов с ошибками
    sent_groups BIGINT[] DEFAULT '{}',    -- массив chat_id
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
