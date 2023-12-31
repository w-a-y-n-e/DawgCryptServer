DROP TABLE IF EXISTS devices;

CREATE TABLE devices (
    uuid PRIMARY KEY,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    key TEXT NOT NULL,
    ip TEXT NOT NULL,
    decrypt_authorized INT NOT NULL DEFAULT 0
);