FLAKE8_ARGS=--max-line-length=120
export FLASK_ENV=prod

help:
	@echo "Run \`make <target>'"
	@echo "Available targets:"
	@echo "  clean    - clean all"
	@echo "  flakeall - check all .py by flake8"
	@echo "  newdb    - [re]create database"
	@echo "  fillnew  - fill new data"
	@echo "  fillall  - refill all data"
	@echo "  listfill - refill all data from .lists"
	@echo "  help     - this text"

# убрать временные файлы
clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

flakeall:
	find . -name '*.py' -print0 | xargs -0 -n 100 flake8 $(FLAKE8_ARGS)

newdb:
	./managedb.py newdb

fillnew:
	./managedb.py fillnew

fillall:
	./managedb.py refillall

listfill:
	./managedb.py fill_lists
