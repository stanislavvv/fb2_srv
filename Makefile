help:
	@echo "Run \`make <target>'"
	@echo "Available targets:"
	@echo "  clean    - clean all"
	@echo "  help     - this text"

# убрать временные файлы
clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

flakeall:
	find . -name '*.py' -print0 | xargs -0 -n 100 flake8
