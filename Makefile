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

logs:
	tmux new-session -d -s kubrick-logs && \
	tmux split-window -h && \
	tmux select-pane -t 0 && \
	tmux send-keys "docker compose logs -f kubrick-mcp" C-m && \
	tmux select-pane -t 1 && \
	tmux send-keys "docker compose logs -f kubrick-api" C-m && \
	tmux attach-session -t kubrick-logs