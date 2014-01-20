all: pytest flake8 pep257

NC=\x1b[0m
OK=\x1b[32;01m

pytest:
	@echo "\n\n$(OK)### py.test and coverage ###$(NC)\n"
	@coverage erase
	@echo "$(OK)✓ deleted existing coverage reports$(NC)\n"
	@coverage run \
		--source analog \
		--omit="analog/tests/*" \
		-m py.test
	@echo "$(OK)✓ ran tests and collected coverage$(NC)\n"
	@coverage report
	@coverage html --title="analog coverage report" -d docs/_coverage/
	@echo "$(OK)✓ created coverage reports in docs/_coverage/$(NC)\n"

flake8:
	@echo "\n\n$(OK)### flake8 (pyflakes, pep8, mccabe) ###$(NC)\n"
	@flake8 \
		--max-line-length=80 \
		--statistics \
		--count \
		--exclude=.hg,__pycache__,node_modules \
		analog ./*.py
	@echo "$(OK)✓ flake8 report complete$(NC)\n"

pep257:
	@echo "\n\n$(OK)### pep257 ###$(NC)\n"
	@pep257 analog
	@echo "$(OK)✓ pep257 report complete$(NC)\n"

docs:
	@echo "\n\n$(OK)### documentation ###$(NC)\n"
	@cd docs && make clean && make html
	@echo "$(OK)✓ built docs.$(NC)\n"

.PHONY: all pytest flake8 pep257 docs
