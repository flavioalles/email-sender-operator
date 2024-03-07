.PHONY: help
help:
	@echo "Available targets are:"
	@echo ""
	@echo "install \t\t\t Installs python project dependencies."

.PHONY: install
install:
	@poetry install --with=dev
