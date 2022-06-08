debug:
    DEBUG=True; python -m src.main

build:
    docker build -t pxls-auth:latest .

run:
    docker run --rm --env-file .env --name pxls-auth -dp 8000:8000 pxls-auth:latest