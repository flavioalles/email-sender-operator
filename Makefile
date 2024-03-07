.PHONY: help
help:
	@echo "email-sender-operator"
	@echo "---------------------"
	@echo "Available targets are:"
	@echo
	@echo "Operation:"
	@echo "\t run             \t\t Starts operator."
	@echo
	@echo "Development & testing:"
	@echo "\t install         \t\t Installs python project dependencies."

.PHONY: install
install:
	@poetry install --with=dev

.PHONY: run
run:
	@kopf run src/main.py
