CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ups_name TEXT NOT NULL UNIQUE,
    station TEXT NOT NULL,
    location_code TEXT NOT NULL,
    vendor TEXT NOT NULL,
    model TEXT NOT NULL,
    capacity_kva TEXT NOT NULL,
    ip_address TEXT NOT NULL UNIQUE,
    snmp_version TEXT NOT NULL,
    snmp_port INTEGER NOT NULL DEFAULT 161,
    community_or_username TEXT,
    auth_protocol TEXT,
    priv_protocol TEXT,
    web_url TEXT,
    serial_number TEXT,
    install_date TEXT,
    monitoring_enabled INTEGER NOT NULL DEFAULT 1,
    notes TEXT,
    oid_profile_name TEXT NOT NULL DEFAULT 'generic_ups',
    current_status TEXT NOT NULL DEFAULT 'unknown',
    last_poll_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS device_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    sampled_at TEXT NOT NULL,
    battery_status TEXT,
    battery_capacity REAL,
    runtime_remaining_minutes REAL,
    load_percentage REAL,
    temperature_c REAL,
    input_voltage REAL,
    output_voltage REAL,
    communication_status TEXT,
    on_battery INTEGER NOT NULL DEFAULT 0,
    overload INTEGER NOT NULL DEFAULT 0,
    battery_disconnected INTEGER NOT NULL DEFAULT 0,
    replace_battery INTEGER NOT NULL DEFAULT 0,
    general_alarm INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    occurrences INTEGER NOT NULL DEFAULT 1,
    acknowledged INTEGER NOT NULL DEFAULT 0,
    acknowledged_by TEXT,
    acknowledged_at TEXT,
    comment TEXT,
    UNIQUE(device_id, alert_type, active),
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER,
    event_type TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
