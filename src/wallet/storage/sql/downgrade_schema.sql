BEGIN;

DROP TABLE operation_details;
DROP SEQUENCE operation_details_pk;

DROP TABLE operation_tags;

DROP TABLE operations;
DROP TYPE operation_type;
DROP SEQUENCE operations_pk;

DROP INDEX categories_name_idx;
DROP TABLE categories;
DROP SEQUENCE operation_details_pk;

DROP INDEX tags_name_idx;
DROP TABLE tags;
DROP SEQUENCE tags_pk;

DROP INDEX balance_month_idx;
DROP TABLE balance;
DROP SEQUENCE balance_pk;

DROP INDEX accounts_name_idx;
DROP TABLE accounts;
DROP SEQUENCE accounts_pk;

COMMIT;
