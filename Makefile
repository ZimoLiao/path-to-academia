.PHONY: test compile validate release-check clean

test:
	python3 -m pytest

compile:
	python3 -m py_compile $$(find src scripts -name '*.py')

validate:
	python3 "$${CODEX_HOME:-$$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/path-to-academia
	python3 "$${CODEX_HOME:-$$HOME/.codex}/skills/.system/plugin-creator/scripts/validate_plugin.py" .

release-check:
	python3 scripts/check_release.py

clean:
	rm -rf build dist src/path_to_academia.egg-info .pytest_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

