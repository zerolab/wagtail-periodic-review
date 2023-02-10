.PHONY: help install lint test clean package-setup package

help:  ## ⁉️  - Display help comments for each make command
	@grep -E '^[0-9a-zA-Z_-]+:.*? .*$$'  \
		$(MAKEFILE_LIST)  \
		| awk 'BEGIN { FS=":.*?## " }; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'  \
		| sort

install:  ## ⚙️  - Install with testing dependencies, and pre-commit
	@echo "⚙️ - Running install in editable mode with testing dependencies"
	python -m pip install -e ".[testing]"
	python -m pip install -U pre-commit
	pre-commit install

lint:  ## 🧹  - Lint and format
	@echo "🧹 - Running pre-commit to lint and format"
	git ls-files --others --cached --exclude-standard | xargs pre-commit run --files

test:  ## 🧪  - Run tests
	@echo "🧪 - Running test suite"
	tox

clean:	## 🗑️  - Remove __pycache__ and test artifacts
	@echo "🗑️ - Removing __pycache__ and test artifacts"
	find . -name ".tox" -prune -o -type d -name  "__pycache__" -exec rm -r {} +

package-setup:
	@echo "📦 - Packaging for PyPI"
	flit build

package: clean package-setup  ## 📦 - Package for PyPI
