#! /usr/bin/env bash
docker-compose exec db bash -c 'psql -d ${POSTGRES_DB} -U ${POSTGRES_USER} -c "CREATE EXTENSION q3c;"'