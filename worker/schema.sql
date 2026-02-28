-- Snapchat Organizer License API - D1 Database Schema
-- Apply with: wrangler d1 execute snapchat-organizer-license --file=schema.sql

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    stripe_customer_id TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_stripe_customer ON users(stripe_customer_id);

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    device_id TEXT,
    is_valid INTEGER NOT NULL DEFAULT 1,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);

-- Licenses table
CREATE TABLE IF NOT EXISTS licenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    license_key TEXT NOT NULL UNIQUE,
    tier TEXT NOT NULL DEFAULT 'free' CHECK(tier IN ('free', 'pro', 'premium')),
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'expired', 'replaced', 'revoked')),
    is_trial INTEGER NOT NULL DEFAULT 0,
    expires_at TEXT,
    max_devices INTEGER NOT NULL DEFAULT 1,
    stripe_subscription_id TEXT,
    activated_at TEXT DEFAULT (datetime('now')),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_licenses_user ON licenses(user_id);
CREATE INDEX IF NOT EXISTS idx_licenses_key ON licenses(license_key);
CREATE INDEX IF NOT EXISTS idx_licenses_stripe_sub ON licenses(stripe_subscription_id);

-- Device activations table
CREATE TABLE IF NOT EXISTS device_activations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    license_id INTEGER NOT NULL REFERENCES licenses(id) ON DELETE CASCADE,
    device_id TEXT NOT NULL,
    device_name TEXT DEFAULT 'Unknown',
    platform TEXT DEFAULT 'Unknown',
    is_active INTEGER NOT NULL DEFAULT 1,
    activated_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_seen_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_device_license ON device_activations(license_id);
CREATE INDEX IF NOT EXISTS idx_device_device_id ON device_activations(device_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_device_unique ON device_activations(license_id, device_id);
