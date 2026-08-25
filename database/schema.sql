-- database/schema.sql

DROP TABLE IF EXISTS accounts;
CREATE TABLE accounts (
    account_id TEXT PRIMARY KEY,
    account_name TEXT,
    plan TEXT,
    status TEXT,
    csm TEXT,
    contract_file TEXT,
    premium_support TEXT,
    notes TEXT
);

DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    account_id TEXT,
    carrier TEXT,
    status TEXT,
    booked_at TEXT,
    pickup_window_start TEXT,
    pickup_window_end TEXT,
    pickup_actual_at TEXT,
    shipment_fee_inr REAL,
    carrier_fault TEXT,
    customer_fault TEXT,
    cancellation_requested_at TEXT,
    notes TEXT,
    FOREIGN KEY(account_id) REFERENCES accounts(account_id)
);

DROP TABLE IF EXISTS tickets;
CREATE TABLE tickets (
    ticket_id TEXT PRIMARY KEY,
    account_id TEXT,
    created_at TEXT,
    status TEXT,
    subject TEXT,
    description TEXT,
    channel TEXT,
    assigned_to TEXT,
    last_customer_message_at TEXT,
    historical_resolution TEXT,
    FOREIGN KEY(account_id) REFERENCES accounts(account_id)
);

DROP TABLE IF EXISTS actions;
CREATE TABLE actions (
    action_id TEXT PRIMARY KEY,
    actor TEXT,
    created_at TEXT,
    action_type TEXT,
    target TEXT,
    reason TEXT,
    status TEXT -- 'pending_confirmation', 'confirmed', 'executed', 'cancelled'
);
