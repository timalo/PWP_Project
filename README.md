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
Tests are located in a single file: "resource_test.py"

Tests and coverage report can be run with the command: "pytest --cov-report term-missing --cov=app"

## Guide

1. First create new empty database by accessing Python terminal and entering the following commands

> from app import db
> 
> db.create_all()
> 
> (alternatively run the db_populate.py file)

2. Now start the server by typing

> flask run

3. API tester plugin is recommended for ease of use (e.g. Talend API Tester)

* Create a game: POST request to the ~api/games/ that contains JSON content: {"game_name":"**enter-your-game-name-here**"}
* Create a deck for a game: POST request to the url ~api/games/**enter-your-game-id**/decks/ that contains empty JSON: {}
* Create cards for a deck: POST request ot the url ~api/decks/**enter-your-deck-id-here**/cards/ that contains empty JSON: {}

* Get list of active games: GET request to the url ~api/games/
* Get list of decks in a game: Get request to the url ~api/games/**enter-your-game-id**/decks/
* Get a specific card in a deck: Get request to the url ~api/decks/**enter-your-deck-id-here**/cards/**enter-your-card-id-here**/

* Toggle cards *is_still_in_deck* parameter: PUT request to the url ~api/decks/**enter-your-deck-id-here**/cards/**enter-your-card-id-here**/
* Change name of a game: PATCH request to the url ~api/games/**enter-your-game-id**/ that contains JSON content: {"game_name":"**enter-new-game-name-here**"}
* Delete a game: DELETE request to the url ~api/games/**enter-your-game-id**/
* Delete a deck: DELETE request to the url ~api/games/**enter-your-game-id**/decks/**enter-your-deck-id**/
