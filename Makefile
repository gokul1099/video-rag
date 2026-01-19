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