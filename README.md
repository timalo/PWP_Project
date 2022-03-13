# Party Game API, Programmable Web Project

This repository contains the project for Programmable Web course. The project is a party game API that allows the users to play card games with each other.

## Dependencies
* Flask v2.0.2

* Flask_SQLAlchemy v.2.5.1

* SQLAlchemy v1.4.31

* Pytest v7.0.0

These can be installed through pip and requirements.txt file using command:
pip install -r /path/to/requirements.txt

## Database

Database is built on SQLite using SQLAlchemy v.1.4.31.

Database can be setup and populated with a few sample games, decks and players by running the db_populate.py (python3 db_populate.py)

## Testing
Tests are in a single file: "resource_test.py"

Tests and coverage report can be run with the command: "pytest --cov-report term-missing --cov=app"

