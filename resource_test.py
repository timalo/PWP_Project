import json
import os
import pytest
import random
import tempfile
import time
from datetime import datetime
from jsonschema import validate
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

from app import app, db
from app import Game, Deck, Card, Playergamepair, Player


CARDS = ['AS', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', 'TS', 'JS', 'QS', 'KS',
         'AD', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', 'TD', 'JD', 'QD', 'KD',
         'AC', '2C', '3C', '4C', '5C', '6C', '7C', '8C', '9C', 'TC', 'JC', 'QC', 'KC',
         'AH', '2H', '3H', '4H', '5H', '6H', '7H', '8H', '9H', 'TH', 'JH', 'QH', 'KH']

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# based on http://flask.pocoo.org/docs/1.0/testing/
@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.config["TESTING"] = True

    db.create_all()
    _populate_db()

    yield app.test_client()

    db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)

def _populate_db():

    game1 = Game(game_name="testGame1")
    game2 = Game(game_name="testGame2")
    game3 = Game(game_name="testGame3")
    game4 = Game(game_name="testGame4")

    db.session.add(game1)
    db.session.add(game2)
    db.session.add(game3)
    db.session.add(game4)
    
    deck1 = Deck(game=game1)
    db.session.add(deck1)
    deck2 = Deck(game=game2)
    deck4 = Deck(game=game4)
    db.session.add(deck4)
    db.session.add(deck2)
    db.session.commit()


    for deck in range(1, 2):

        for i, j in enumerate(CARDS):
            new_card = Card(
                value = j,
                is_still_in_deck = True,
                deck_id = deck,
                order_id = i
            )
            db.session.add(new_card)
        db.session.commit()

    playergamepair1=Playergamepair()
    playergamepair1.games.append(game1)
    playergamepair1.games.append(game2)
    player1 = Player(game=game1)
    player2 = Player(game=game1)

    db.session.add(player1)
    db.session.add(player2)
    db.session.commit()


def _get_game_json(number=1):
    """
    Creates a valid sensor JSON object to be used for PUT and POST tests.
    """
    
    return {"game_name": "extra-game-{}".format(number)}

def _get_wrong_game_json(number=1):
    """
    Creates a JSON object that has incorrect data
    """
    return {"game:": "extra-game-{}".format(number)}

def _get_deck_json():
    """
    Creates an empty json object to be used for deck POST tests.
    """

    return {"": ""}

def _get_card_json():
    """
    Creates an empty json object to be used for card tests.
    """
    return {"": ""}

class TestGameCollection(object):
    """
    This class implements tests for each HTTP method in game collection
    resource. 
    """
    RESOURCE_URL = "/api/games/"
    WRONG_URL = "/api/game/"


    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)

        assert len(body) == 4
        assert body[0]["game_name"] == "testGame1"
        assert body[0]["id"] == 1

        """
        assert len(body["items"]) == 3
        for item in body["items"]:
            assert "name" in item
            assert "model" in item
        """
    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and 
        also checks that a valid request receives a 201 response with a 
        location header that leads into the newly created resource.
        """
        
        valid = _get_game_json()
        not_valid = _get_wrong_game_json()
        
        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415
        
        #test with wrong path
        resp = client.post(self.WRONG_URL, json=valid)
        assert resp.status_code == 404

        resp = client.post(self.RESOURCE_URL, json=not_valid)
        assert resp.status_code == 400

        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + "5" + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["id"] == 5
        assert body["game_name"] == "extra-game-1"
        
        # send same data again for 201
        # Sending same data is allowed since game names are not unique
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        
        # remove model field for 415
        valid.pop("game_name")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 415


    def test_put(self, client):
        """
        PUT method is not supported so it should result to 405
        """
        valid = _get_game_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 405

    def test_delete(self, client):
        """
        DELETE is not implemented for game collection resource so it should result to 405
        """
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 405

    def test_patch(self, client):
        """
        PATCH method is used to change the game_name value of game resource
        """
        resp = client.get(self.RESOURCE_URL)
        body = json.loads(resp.data)
        assert body[0]["game_name"] == "testGame1"

        resp = client.patch(f"{self.RESOURCE_URL}1/", json=_get_game_json(2))
        assert resp.status_code == 200

        resp = client.get(self.RESOURCE_URL)
        body = json.loads(resp.data)
        assert body[0]["game_name"] == "extra-game-2"



class TestGameItem(object):
    """
    This class implements tests for each HTTP method in game item
    resource. 
    """

    RESOURCE_URL = "/api/games/2/"
    WRONG_URL = "/api/game/2/"
    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)

        assert body["id"] == 2
        assert body["game_name"] == "testGame2"

        resp = client.get(self.WRONG_URL)
        assert resp.status_code == 404



    def test_post(self, client):
        """
        Post isn't implemented for game item resource, so it should return 405
        """
        resp = client.post(self.RESOURCE_URL, json="")
        assert resp.status_code == 405

    def test_delete(self, client):
        """
        tests the DELETE method. 
        """
        #1. check that game exists
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        #2. delete the game
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 200
        #3. check that the game is deleted
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404

        #delete with wrong URL
        resp = client.delete(self.WRONG_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        """
        PUT is not implemented so 405 is expected
        """
        resp = client.put(self.RESOURCE_URL, json=_get_game_json())
        assert resp.status_code == 405
        


class TestDeckCollection(object):
    """
    This class implements tests for each HTTP method in deck collection
    resource. 
    """
    RESOURCE_URL = "/api/games/3/decks/"
    WRONG_URL = "/api/games/3/deckss/"
    WRONG_URL2 = "/api/games/5/decks/"

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and 
        also checks that a valid request receives a 201 response with a 
        location header that leads into the newly created resource.
        """

        valid = _get_deck_json()

        #test with url that has typo
        resp = client.post(self.WRONG_URL, json=valid)
        assert resp.status_code == 404

        #test with a game that doesn't exist
        resp = client.post(self.WRONG_URL2, json=valid)
        assert resp.status_code == 404

        


        
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + "4" + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200

        #Trying to create a new deck for the same game
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        #invalid JSON will pass since the input is not used anywhere 
        #but the game already has a deck so 400 is expected
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 400



    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """
        valid = _get_deck_json()
        client.post(self.RESOURCE_URL, json=valid)
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)

        assert body[2]["game_id"] == 4
        assert body[2]["id"] == 3

    def test_put(self, client):
        """
        PUT is not implemented, should return 405
        """
        valid = _get_deck_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 405

    def test_delete(self, client):
        """
        DELETE is not implemented, should return 405
        """
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 405

class TestDeckItem(object):
    """
    This class implements tests for each HTTP method in deck item
    resource. 
    """
    RESOURCE_URL = "/api/games/2/decks/1/"
    WRONG_URL = "/api/games/2/deck/1/"
    WRONG_URL2 = "/api/games/2/deck/3/"


    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200

        body = json.loads(resp.data)

        assert body["id"] == 1
        assert body["game_id"] == 1

        assert len(body["cards"]) == 52

        resp = client.get(self.WRONG_URL)
        assert resp.status_code == 404

    def test_post(self, client):
        """
        POST is not implemented, should return 405
        """

        resp = client.post(self.RESOURCE_URL, json="")
        assert resp.status_code == 405

    def test_delete(self, client):
        """
        tests the DELETE method. 
        """
        #1. check that game exists
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        #2. delete the game
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 200
        #3. check that the game is deleted
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404

        #delete with wrong URL should return 404
        resp = client.delete(self.WRONG_URL)
        assert resp.status_code == 404

        #delete a object that doesn't exist
        resp = client.delete(self.WRONG_URL2)
        assert resp.status_code == 404

    def test_put(self, client):
        """
        PUT is not implemented, should return 405
        """

        resp = client.put(self.RESOURCE_URL, json="")
        assert resp.status_code == 405


class TestCardCollection(object):
    """
    This class implements tests for each HTTP method in card collection
    resource. 
    """

    RESOURCE_URL = "/api/decks/3/cards/"
    WRONG_URL = "/api/decks/3/card/"
    WRONG_URL2 = "/api/decks/3/cardss/"

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and 
        also checks that a valid request receives a 201 response with a 
        location header that leads into the newly created resource.
        """

        valid = _get_card_json()

        #test with url that has typo
        resp = client.post(self.WRONG_URL, json=valid)
        assert resp.status_code == 404

        #test with a game that doesn't exist
        resp = client.post(self.WRONG_URL2, json=valid)
        assert resp.status_code == 404


        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201

        #previous test again, should result to 415 since deck already has cards
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 415


        #assert resp.headers["Location"].endswith(self.RESOURCE_URL + "3" + "/")

        #resp = client.get(resp.headers["Location"])
        #assert resp.status_code == 200

    def test_get(self, client):
        """
        GET is not implemented, should return 405
        """

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 400

    def test_put(self, client):
        """
        PUT is not implemented, should return 405
        """
        valid = _get_card_json()
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 405

    def test_delete(self, client):
        """
        DELETE is not implemented, should return 405
        """
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 405


class TestCardItem(object):
    """
    This class implements tests for each HTTP method in card item resouce
    """
    RESOURCE_URL = "/api/decks/1/cards/1/"
    WRONG_URL = "/api/decks/1/card/1/"
    WRONG_URL2 = "/api/decks/1/cardss/1/"

    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls.
        """

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200

        body = json.loads(resp.data)

        assert body["deck_id"] == 1
        assert body["value"] == "2S"
        assert body["is_still_in_deck"] == True


        resp = client.get(self.WRONG_URL)
        assert resp.status_code == 404

    def test_post(self, client):
        """
        POST is not implemented, should return 405
        """

        resp = client.post(self.RESOURCE_URL, json="")
        assert resp.status_code == 405

    def test_delete(self, client):
        """
        tests the DELETE method. 
        """
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 405

    def test_put(self, client):
        """
        tests PUT method which should toggle "drawn" status for a single card
        """

        #1. check that the boolean "is_still_in_deck" is false
        resp = client.get("/api/decks/1/cards/1/")
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["is_still_in_deck"] == True

        #2. toggle the value and check that the boolean is now false
        resp = client.put(self.RESOURCE_URL, json="")
        assert resp.status_code == 200
        resp = client.get("/api/decks/1/cards/1/")
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["is_still_in_deck"] == False

        #3. toggle it again and check that it changes back to true
        resp = client.put(self.RESOURCE_URL, json="")
        assert resp.status_code == 200
        resp = client.get("/api/decks/1/cards/1/")
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["is_still_in_deck"] == True


@pytest.mark.skip(reason="Card handler has been removed from the API")
class TestCardHandler(object):
    """
    This class implements test for each HTTP method in card handler resource
    """

    RESOURCE_URL = "/api/decks/1/cards/1/handler/"
    def test_post(self, client):
        """
        POST not implemented, returns 405
        """
        resp = client.post(self.RESOURCE_URL, json="")
        assert resp.status_code == 405

    def test_get(self, client):
        """
        GET not implemented, returns 405
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 405

    def test_delete(self, client):
        """
        DELETE not implemented, return 405
        """
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 405

    def test_put(self, client):
        """
        tests PUT method which should toggle "drawn" status for a single card
        """

        #1. check that the boolean "is_still_in_deck" is false
        resp = client.get("/api/decks/1/cards/1/")
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["is_still_in_deck"] == True

        #2. toggle the value and check that the boolean is now false
        resp = client.put(self.RESOURCE_URL, json="")
        assert resp.status_code == 200
        resp = client.get("/api/decks/1/cards/1/")
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["is_still_in_deck"] == False

        #3. toggle it again and check that it changes back to true
        resp = client.put(self.RESOURCE_URL, json="")
        assert resp.status_code == 200
        resp = client.get("/api/decks/1/cards/1/")
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["is_still_in_deck"] == True
