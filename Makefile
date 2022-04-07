help:
	@echo "Run \`make <target>'"
	@echo "Available targets:"
	@echo "  clean    - clean all"
	@echo "  help     - this text"

# убрать временные файлы
clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

