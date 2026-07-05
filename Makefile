# ==========================================================
# RoomLoop Makefile
# ==========================================================

-include .env
export

# ==========================================================
# Variables
# ==========================================================

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
MYSQL := mysql

# ==========================================================
# PHONY Targets
# ==========================================================

.PHONY: \
	help \
	init \
	venv \
	install \
	setup \
	run \
	test \
	test-unit \
	db-create \
	db-schema \
	db-seed \
	db-init \
	db-reset \
	clean

# ==========================================================
# Environment
# ==========================================================

init:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env from .env.example"; \
	else \
		echo ".env already exists"; \
	fi

venv:
	@if [ ! -d "$(VENV)" ]; then \
		python3 -m venv $(VENV); \
		echo "Virtual environment created."; \
	else \
		echo "Virtual environment already exists."; \
	fi

# ==========================================================
# Python
# ==========================================================

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) run.py

# ==========================================================
# Testing
# ==========================================================

test:
	$(PYTEST) -v

test-unit:
	$(PYTEST) tests/ -v

# ==========================================================
# Database
# ==========================================================

db-create:
	$(MYSQL) \
		-h $(DATABASE_HOST) \
		-P $(DATABASE_PORT) \
		-u $(DATABASE_USER) \
		-e "CREATE DATABASE IF NOT EXISTS $(DATABASE_NAME);"

db-schema:
	$(MYSQL) \
		-h $(DATABASE_HOST) \
		-P $(DATABASE_PORT) \
		-u $(DATABASE_USER) \
		$(DATABASE_NAME) < database/schema.sql

db-seed:
	$(MYSQL) \
		-h $(DATABASE_HOST) \
		-P $(DATABASE_PORT) \
		-u $(DATABASE_USER) \
		$(DATABASE_NAME) < database/seed.sql

db-init: db-create db-schema db-seed

db-reset:
	$(MYSQL) \
		-h $(DATABASE_HOST) \
		-P $(DATABASE_PORT) \
		-u $(DATABASE_USER) \
		-e "DROP DATABASE IF EXISTS $(DATABASE_NAME);"

	$(MYSQL) \
		-h $(DATABASE_HOST) \
		-P $(DATABASE_PORT) \
		-u $(DATABASE_USER) \
		-e "CREATE DATABASE $(DATABASE_NAME);"

	$(MYSQL) \
		-h $(DATABASE_HOST) \
		-P $(DATABASE_PORT) \
		-u $(DATABASE_USER) \
		$(DATABASE_NAME) < database/schema.sql

	$(MYSQL) \
		-h $(DATABASE_HOST) \
		-P $(DATABASE_PORT) \
		-u $(DATABASE_USER) \
		$(DATABASE_NAME) < database/seed.sql

# ==========================================================
# Complete Project Setup
# ==========================================================

setup: init install db-init
	@echo ""
	@echo "======================================="
	@echo " RoomLoop setup completed successfully."
	@echo "======================================="
	@echo ""
	@echo "Run the application:"
	@echo "    make run"
	@echo ""
	@echo "Run all tests:"
	@echo "    make test"
	@echo ""

# ==========================================================
# Cleanup
# ==========================================================

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# ==========================================================
# Help
# ==========================================================

help:
	@echo ""
	@echo "RoomLoop Make Commands"
	@echo "-----------------------------------------------------"
	@echo "make init         Create .env from .env.example"
	@echo "make venv         Create Python virtual environment"
	@echo "make install      Install Python dependencies"
	@echo "make setup        Complete project setup"
	@echo ""
	@echo "make run          Run FastAPI application"
	@echo ""
	@echo "make test         Run all tests"
	@echo "make test-unit    Run unit tests"
	@echo ""
	@echo "make db-create    Create database"
	@echo "make db-schema    Apply schema.sql"
	@echo "make db-seed      Apply seed.sql"
	@echo "make db-init      Create DB + Apply schema + Seed data"
	@echo "make db-reset     Recreate database from scratch"
	@echo ""
	@echo "make clean        Remove cache files"
	@echo ""