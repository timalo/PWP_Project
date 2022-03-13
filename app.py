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

CARDS = ['AS', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', 'TS', 'JS', 'QS', 'KS',
         'AD', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', 'TD', 'JD', 'QD', 'KD',
         'AC', '2C', '3C', '4C', '5C', '6C', '7C', '8C', '9C', 'TC', 'JC', 'QC', 'KC',
         'AH', '2H', '3H', '4H', '5H', '6H', '7H', '8H', '9H', 'TH', 'JH', 'QH', 'KH']

playergamepairs = db.Table("playergamepairs",
    db.Column("playergamepair_id", db.Integer, db.ForeignKey("playergamepair.id"), primary_key=True),
    db.Column("game_id", db.Integer, db.ForeignKey("game.id"), primary_key=True)
)

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
class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("game.id", ondelete="CASCADE"))

    cards = db.relationship("Card", cascade="all", back_populates="deck")
    game = db.relationship("Game", back_populates="deck_id")

    def serialize(self):
        card_list = []
        for i in self.cards:
            card_list.append((i.value, i.order_id, i.is_still_in_deck))
        return {
            "id": self.id,
            "game_id": self.game_id,
            "cards": card_list
        }

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(12), nullable=False)
    is_still_in_deck = db.Column(db.Boolean, nullable=False)
    order_id = db.Column(db.Integer, nullable=False)
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


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("game.id", ondelete="SET NULL"))

    game = db.relationship("Game", back_populates="players")
    cards = db.relationship("Card", back_populates="player")

class DeckItem(Resource):
    """
    DeckItem resource that resembles a single deck. 
    Get function returns information of the deck. The values are id, game_id, and card_list
    Delete function removes the deck. 
    """
    def get(self, game, deck):
        return deck.serialize()

    def delete(self, deck, game):
        try:
            db.session.delete(deck)
            db.session.commit()
            return "Deck removed.", 200
        except Exception as e:
            print(e)
    
class CardItem(Resource):
    """
    resource for a singular card item. Get function returns the deck_id and card value.
    Input values card and deck are given in the URL "/api/decks/<deck_id>/cards/<order_id>" 
    where order_id is an integer resembling the position of the card in the deck.
    """
    def get(self, card, deck):
        print(deck)
        return deck.cards[card.id].serialize()

class CardCollection(Resource):
    """
    Resource for handling the creation of the cards in the deck.
    Only allows post function, which creates all the cards in the given deck.
    Does not return location for the URLs of the individual cards.
    Cards are created in URLs "/api/decks/<deck_Id>/cards/order_id/" where order_id is an integer from 1-52
    """
    def get(self, deck):
       return Response("only post request allowed", status=400)
    
    def post(card, deck):
        try:
            for i, j in enumerate(CARDS):
                new_card = Card(
                    value = j,
                    is_still_in_deck = True,
                    deck_id = deck.id,
                    order_id = i
                )
                db.session.add(new_card)
                db.session.commit()

                card_url = api.url_for(CardItem, deck=deck, card=new_card)
            
            return "cards created :)", 201

        except IntegrityError:
            db.session.rollback()
            print("something borke")

class DeckCollection(Resource):
    """
    Resource for handling decks.
    Get function returns a list of all decks in every game.
    Post request creates a new deck in the given game. The deck is initially empty and needs to be filled with cards.
    """
    def get(self, game):
        print("printing game")
        print(game)
        deck_list = []
        for i in range(len(Deck.query.all())):
            deck = {
                "id": Deck.query.get(i+1).id,
                "game_id": Deck.query.get(i+1).game_id
            }
            deck_list.append(deck)
        return deck_list

    def post(deck, game):
        try:
            print("trying to create new deck...")
            if (game.deck_id != None):
                return "Game already has a deck. Don't create a new one :(", 400
            newDeck = Deck(
                game_id = game.id
            )
            db.session.add(newDeck)
            db.session.commit()
            print("deck in DB")
            deck_url = api.url_for(DeckItem, deck=newDeck, game=game)
            print("deck url is: " + deck_url)
            
            return Response(headers={'Location': deck_url}, status=201)
        except KeyError:
            return "something borke", 400
        except ValidationError as e:
            raise BadRequest(description=str(e))
        except IntegrityError:
            return "Something wrong with adding the deck to the database.", 400

class GameItem(Resource):
    """
    A resource holding a single game item. Only has functions for getting the game info, and for deleting a single game.
    Inputs are given through the resource URL
    """
    def get(self, game):
        return game.serialize()

    def delete(self, game):
        try:
            print("deleting game: " + game.game_name)
            db.session.delete(game)
            db.session.commit()
            return "Game removed.", 200
        except Exception as e:
            print(e)

class GameCollection(Resource):
    """
    Resource that takes in new games in the post function. New games are created from the URL "/api/games/" 
    POST function takes in the game name as a json object.
    Get function return a list of games
    """
#----------------------------------------------------
    def get(self):
        game_list = []
        for i in range(len(Game.query.all())):
            game = {
                "id": Game.query.get(i+1).id,
                "game_name": Game.query.get(i+1).game_name
            }
            game_list.append(game)
        return game_list
#------------------------------------------------------
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

    
class CardHandler(Resource):
    """
    CardHandler resource that is responsible for performing actions on the deck.
    Put function picks a given card from the deck and marks it as drawn/discarded
    """
    def get():
        pass
    def post():
        pass
    def put(self, deck, card):
        deck.cards[card.id].is_still_in_deck = False
        db.session.commit()


#Converters
class DeckConverter(BaseConverter):
    #Converter for getting the url for a deck from database object
    def to_python(self, id):
        db_deck = Deck.query.filter_by(id=id).first()
        if db_deck is None:
            raise NotFound
        return db_deck
    
    def to_url(self, db_deck):
        return str(db_deck.id)

class CardConverter(BaseConverter):
    def to_python(self, id):
        db_card = Card.query.filter_by(id=id).first()
        if db_card is None:
            raise NotFound
        return db_card

    def to_url(self, db_card):
        return str(db_card.order_id)

class GameConverter(BaseConverter):
    def to_python(self, id):
        db_game = Game.query.filter_by(id=id).first()
        if db_game is None:
            raise NotFound
        return db_game

    def to_url(self, db_game):
        return str(db_game.id)



app.url_map.converters["game"] = GameConverter
api.add_resource(GameCollection, "/api/games/")
api.add_resource(GameItem, "/api/games/<game:game>/")

app.url_map.converters["deck"] = DeckConverter
api.add_resource(DeckCollection, "/api/games/<game:game>/decks/")
api.add_resource(DeckItem, "/api/games/<game:game>/decks/<deck:deck>/")

app.url_map.converters["card"] = CardConverter
api.add_resource(CardHandler, "/api/decks/<deck:deck>/cards/<card:card>/handler/")
api.add_resource(CardCollection, "/api/decks/<deck:deck>/cards/")
api.add_resource(CardItem, "/api/decks/<deck:deck>/cards/<card:card>/")
