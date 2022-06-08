# Pxls-auth

A hacky way of authentifying `pxls.space` users while they set up OAuth. Works by challenging the user to join a predefined faction.

Will require a `pxls.space` bot account to run (the `/profile` page is protected behind auth), make sure to ask the admins for authorization.

## Installation
* Clone the repo.
* Build the docker image: `docker build -t pxls-auth:latest .`
* Copy `.env.dist` to `.env` and set the environment variables.
* Run the docker image: `docker run --env-file .env pxls-auth`