from xml.dom import ValidationErr
from flask import Flask, request, Response, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from jsonschema import ValidationError
from sqlalchemy.engine import Engine
from sqlalchemy import event
from flask_restful import Api, Resource
from werkzeug.exceptions import NotFound
from werkzeug.routing import BaseConverter
from werkzeug.exceptions import NotFound, Conflict, BadRequest, UnsupportedMediaType

import os
import random

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
api = Api(app)

delete_player = False
delete_game = True
delete_deck = False
delete_card = False
delete_playergamepair = False

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

CARDS = ['AS', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', '0S', 'JS', 'QS', 'KS',
         'AD', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', '0D', 'JD', 'QD', 'KD',
         'AC', '2C', '3C', '4C', '5C', '6C', '7C', '8C', '9C', '0C', 'JC', 'QC', 'KC',
         'AH', '2H', '3H', '4H', '5H', '6H', '7H', '8H', '9H', '0H', 'JH', 'QH', 'KH']

playergamepairs = db.Table("playergamepairs",
    db.Column("playergamepair_id", db.Integer, db.ForeignKey("playergamepair.id"), primary_key=True),
    db.Column("game_id", db.Integer, db.ForeignKey("game.id"), primary_key=True)
)

class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    cards = db.relationship("Card", back_populates="deck")

    game_id = db.Column(db.Integer, db.ForeignKey("game.id", ondelete="CASCADE"))

    cards = db.relationship("Card", cascade="all", back_populates="deck")
    game = db.relationship("Game", back_populates="deck_id")


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(12), nullable=False)
    is_still_in_deck = db.Column(db.Boolean(), nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey("deck.id"), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey("player.id"))


    deck = db.relationship("Deck", back_populates="cards")
    
    player = db.relationship("Player", back_populates="cards")
    

    def serialize(self):
        return {
            "deck_id": self.deck_id,
            "value": self.value
        }

class Playergamepair(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    games = db.relationship("Game", secondary=playergamepairs, back_populates="playergamepairs")


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(128), nullable=False) 

    deck_id = db.relationship("Deck", cascade="all", back_populates="game", uselist=False)
    players = db.relationship("Player", back_populates="game")
    playergamepairs = db.relationship("Playergamepair", secondary=playergamepairs, back_populates="games")

    def serialize(self):
        doc = {
            "id": self.id,
            "game_name": self.game_name
        }
        return doc
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("game.id", ondelete="SET NULL"))

    game = db.relationship("Game", back_populates="players")
    cards = db.relationship("Card", back_populates="player")

class DeckItem(Resource):
    def get(self):
        pass

    def post(self):
        pass
    
class CardItem(Resource):
    def get(self, card):
        #returns the value of the card.
        return card.serialize()

class CardCollection(Resource):
    def get(self):
        return Response(headers={"content": "none"}, status=400)
    
    def post(self, deck):
        if not request.content_type.startswith('application/json'):
            return Response(headers={"msg": "Unsupported media type. Only JSON accepted"}, status=415)
        try:
            for i in CARDS:
                new_card = Card(
                    value = i,
                    is_still_in_deck = True,
                    deck = deck
                )
                print("adding new card with value: " + new_card.value)
                db.session.add(new_card)
                db.session.commit()

        except IntegrityError:
            db.session.rollback()
            print("something borke")

class DeckCollection(Resource):
    def get(self):
        deck_list = []
        for i in range(len(Deck.query.all())):
            deck = {
                "id": Deck.query.get(i+1).id
            }
            deck_list.append(deck)
        return deck_list

    def post(deck):
        if not request.json:
            return Response("not json", status=415)
        try:
            newDeck = Deck(
                name = request.json["name"]
            )
            db.session.add(newDeck)
            db.session.commit()
            deck_url = api.url_for(DeckItem, deck=deck)
            print(deck_url)
            
            return Response(headers={'Location': deck_url}, status=201)
        except KeyError:
            return "something borke", 400
        except ValidationError as e:
            raise BadRequest(description=str(e))
        except IntegrityError:
            return "Something wrong with adding the deck to the database.", 400

class GameItem(Resource):
    def get(self, game):
        return game.serialize()


class GameCollection(Resource):
    def get(self):
        return "get works", 200

    def post(game):
        if not request.json:
            return Response("not json", status=415)
        try:
            print("trying to create new game")
            newGame = Game(
                game_name = request.json["game_name"]
            )
            print("Game name is: " + newGame.game_name)
            db.session.add(newGame)
            db.session.commit()
            print("added game to db")
            game_url = api.url_for(GameItem, game=newGame)
            print("game url: " + game_url)
            
            return Response(headers={'Location': game_url}, status=201)
        except KeyError:
            return "something borke", 400
        except ValidationError as e:
            raise BadRequest(description=str(e))
        except IntegrityError:
            return "Something wrong with adding the game to the database.", 400

class DeckConverter(BaseConverter):

    #Converter for getting the url for a deck from database object

    def to_python(self, id):
        db_deck = Deck.query.filter_by(id=id).first()
        if db_deck is None:
            raise NotFound
        return db_deck
    
    def to_url(self, db_deck):
        return db_deck.id

class CardConverter(BaseConverter):
    def to_python(self, id):
        db_card = Card.query.filter_by(id=id).first()
        if db_card is None:
            raise NotFound
        return db_card

    def to_url(self, db_card):
        return db_card.id 

class GameConverter(BaseConverter):
    def to_python(self, id):
        db_game = Game.query.filter_by(id=id).first()
        if db_game is None:
            raise NotFound
        return db_game

    def to_url(self, db_game):
        print(db_game)
        return str(db_game.id)

app.url_map.converters["deck"] = DeckConverter
app.url_map.converters["card"] = CardConverter
app.url_map.converters["game"] = GameConverter

api.add_resource(GameCollection, "/api/games/")
api.add_resource(GameItem, "/api/games/<game:game>/")

api.add_resource(DeckCollection, "/api/decks/")

api.add_resource(DeckItem, "/api/decks/<deck:deck>/")

api.add_resource(CardCollection, "/api/decks/<deck:deck>/cards/")

api.add_resource(CardItem, "/api/decks/<deck:deck>/cards/<card:card>/")

try:
    os.remove("test.db")
except Exception as e:
    print(e)
db.create_all()