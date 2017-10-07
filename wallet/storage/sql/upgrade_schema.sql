-- SET ROLE 'passport';

BEGIN;

CREATE SEQUENCE IF NOT EXISTS accounts_pk START WITH 1;

CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY default nextval('accounts_pk'),
    name VARCHAR(255) NOT NULL,
    amount NUMERIC(20, 2) DEFAULT 0.0,
    original NUMERIC(20, 2) DEFAULT 0.0,
    enabled BOOLEAN DEFAULT TRUE,
    owner_id INTEGER,
    created_on TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS accounts_name_idx ON accounts (name, enabled, owner_id);


CREATE SEQUENCE IF NOT EXISTS tags_pk START WITH 1;

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY default nextval('tags_pk'),
    name VARCHAR(255) NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    owner_id INTEGER,
    created_on TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS tags_name_idx ON tags (name, enabled, owner_id);


CREATE SEQUENCE IF NOT EXISTS operations_pk START WITH 1;

CREATE TYPE operation_type AS ENUM ('income', 'expense', 'transfer');

CREATE TABLE IF NOT EXISTS operations (
    id INTEGER PRIMARY KEY default nextval('operations_pk'),
    type operation_type NOT NULL,
    description VARCHAR(500) NOT NULL,
    amount NUMERIC(20, 2) NOT NULL,
    account_id INTEGER NOT NULL REFERENCES accounts (id) ON DELETE CASCADE,
    enabled BOOLEAN DEFAULT TRUE,
    created_on TIMESTAMP WITHOUT TIME ZONE NOT NULL
);


CREATE TABLE IF NOT EXISTS operation_tags (
    operation_id INTEGER REFERENCES operations (id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags (id) ON DELETE CASCADE,
    CONSTRAINT operation_tags_pk PRIMARY KEY (operation_id, tag_id)
);


CREATE SEQUENCE IF NOT EXISTS operation_details_pk START WITH 1;

CREATE TABLE IF NOT EXISTS operation_details (
    id INTEGER PRIMARY KEY default nextval('operation_details_pk'),
    name VARCHAR(255) NOT NULL,
    price_per_unit NUMERIC(20, 2) CONSTRAINT positive_price_per_unit CHECK (price_per_unit > 0),
    count NUMERIC(10, 3) CONSTRAINT positive_count CHECK (count > 0),
    total NUMERIC(20, 2) CONSTRAINT positive_total CHECK (total > 0),
    enabled BOOLEAN DEFAULT TRUE,
    created_on TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    operation_id INTEGER NOT NULL REFERENCES operations (id)
);


CREATE SEQUENCE IF NOT EXISTS balance_pk START WITH 1;

CREATE TABLE IF NOT EXISTS balance (
    id INTEGER PRIMARY KEY default nextval('balance_pk'),
    income NUMERIC(20, 2) CONSTRAINT positive_income CHECK (income > 0),
    expense NUMERIC(20, 2) CONSTRAINT positive_expense CHECK (expense > 0),
    remain NUMERIC(20, 2) NOT NULL,
    account_id INTEGER REFERENCES accounts (id) ON DELETE CASCADE,
    owner_id INTEGER NOT NULL,
    date DATE NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS balance_account_idx ON balance (account_id, date);

COMMIT;
