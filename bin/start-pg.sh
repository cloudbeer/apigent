docker run -d \
    -p 5433:5432 \
    -e POSTGRES_USER=abigent \
    -e POSTGRES_PASSWORD=xyz-password \
    -e POSTGRES_DB=abigent \
    --name pgv \
    pgvector/pgvector:pg17