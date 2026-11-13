-- Read-only database role for the public demo API (OPS-001, line C).
-- Line A turns this into a migration. Idempotent: running it again changes nothing.
--
-- The tables keep row level security without policies for anon/authenticated (D-197), so the
-- Supabase Data API stays closed. This role gets SELECT plus one explicit read policy per table
-- the API reads; a table without a policy would look empty to it, not fail.
--
-- No password here. Set it out of band (ALTER ROLE vf_api_ro PASSWORD ...) and use it only in
-- the hosting provider's DATABASE_URL. Through the Supabase pooler the user is
-- vf_api_ro.<project_ref>.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'vf_api_ro') THEN
        CREATE ROLE vf_api_ro LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
    END IF;
END
$$;

ALTER ROLE vf_api_ro SET default_transaction_read_only = on;
ALTER ROLE vf_api_ro SET statement_timeout = '15s';
ALTER ROLE vf_api_ro SET search_path = public, extensions;

GRANT USAGE ON SCHEMA public, extensions TO vf_api_ro;

-- Keep in sync with the tables the API queries (tests/unit/api/test_readonly_role.py checks it).
DO $$
DECLARE
    api_table text;
BEGIN
    FOREACH api_table IN ARRAY ARRAY[
        'dataset_registry',
        'dataset_version',
        'feature_registry',
        'feature_value',
        'geo_admin_unit',
        'place_master',
        'source_registry',
        'transit_hub',
        'commute_time'
    ]
    LOOP
        EXECUTE format('GRANT SELECT ON public.%I TO vf_api_ro', api_table);
        EXECUTE format('DROP POLICY IF EXISTS vf_api_ro_read ON public.%I', api_table);
        EXECUTE format(
            'CREATE POLICY vf_api_ro_read ON public.%I FOR SELECT TO vf_api_ro USING (true)',
            api_table
        );
    END LOOP;
END
$$;
