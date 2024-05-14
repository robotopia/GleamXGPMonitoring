#! /usr/bin/env bash
docker compose exec db bash -c 'psql -d ${POSTGRES_DB} -U ${POSTGRES_USER} -c "CREATE EXTENSION q3c;CREATE INDEX ON candidate_app_candidate (q3c_ang2ipix(ra_deg, dec_deg));"'
