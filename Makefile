ifeq (,$(wildcard .env))
${error .env file is missing at . Please create one}
endif

include .env

build-kubrick:
	docker compse build

start-kubric:
	docker compose up --build -d

stop-kubric: 
	docker compose stop


build-kubrick-dev:
	docker compose -f docker-compose.dev.yml build

start-kubrick-dev:
	docker compose -f docker-compose.dev.yml up --build -d

stop-kubrick-dev: 
	docker compose -f docker-compose.dev.yml stop