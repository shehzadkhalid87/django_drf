# Makefile for Docker Compose

# Define your services
SERVICES = web db

# Define the docker-compose file
COMPOSE_FILE = docker-compose.yml

# Define the Docker Compose command
DOCKER_COMPOSE = docker-compose -f $(COMPOSE_FILE)

.PHONY: up down logs build

# Start services in the background
up:
	@echo "Starting services in the background..."
	$(DOCKER_COMPOSE) up -d $(SERVICES)

# Stop services
down:
	@echo "Stopping services..."
	$(DOCKER_COMPOSE) down

# View logs for services
logs:
	@echo "Viewing logs for services..."
	$(DOCKER_COMPOSE) logs -f

# Build services (optional)
build:
	@echo "Building services..."
	$(DOCKER_COMPOSE) build

# Restart services
restart: down up
	@echo "Restarting services..."
