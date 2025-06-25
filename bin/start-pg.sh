docker run -d \
    -p 5433:5432 \
    -e POSTGRES_USER=apigent \
    -e POSTGRES_PASSWORD=xyz-password \
    -e POSTGRES_DB=apigent \
    --name pgv \
    pgvector/pgvector:pg17