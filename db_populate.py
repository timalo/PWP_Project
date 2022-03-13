import importlib
import random
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from app import app, db, Game, Deck, Card, Playergamepair, Player


#app = Flask(__name__)
#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
#app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#db = SQLAlchemy(app)
#api = Api(app)

delete_player = False
delete_game = False
delete_deck = False
delete_card = False
delete_playergamepair = False


def main():
    try:
        os.remove("test.db")
    except Exception as e:
        print(e)
    db.create_all()
    game1 = Game(game_name="testGame1")
    game2 = Game(game_name="testGame2")
    db.session.add(game1)
    #db.session.commit()
    deck1 = Deck(game=game1)
    db.session.add(deck1)
    #db.session.commit()

    deck2 = Deck(game=game1)
    db.session.add(deck2)
    #db.session.commit()
    print(Deck.query.all())
    card1 = Card(value="2D", deck=deck1, is_still_in_deck=True, order_id=1)
    card2 = Card(value="Mee töihin!", deck=deck2, is_still_in_deck=True, order_id=1)
    card3 = Card(value="3D", deck=deck1, is_still_in_deck=True, order_id=1)
    db.session.add(card1)
    db.session.add(card2)
    db.session.add(card3)
    print(Card.query.all())
    playergamepair1=Playergamepair()
    playergamepair1.games.append(game1)
    playergamepair1.games.append(game2)
    player1 = Player(game=game1)
    player2 = Player(game=game1)

    db.session.add(player1)
    db.session.add(player2)
    card1.player = player1



    for card in Card.query.all():
        print(f"Card: {card.id}, Value: {card.value}, Deck ID: {card.deck_id}, Deck: {card.deck}, Player: {card.player}")
    print("Adding player1 to card2")
    card2.player = player1
    for card in Card.query.all():
        print(f"Card: {card.id}, Value: {card.value}, Deck ID: {card.deck_id}, Deck: {card.deck}, Player: {card.player}")
    db.session.commit()

    print()
    print("Games:")
    for game in Game.query.all():
        print(f"Game: {game}, Game_id: {game.id}, Game deck: {game.deck_id}, Game players: {game.players}")
    print("Decks:")
    for deck in Deck.query.all():
        print(f"Deck: {deck}, Game: {deck.game}, Cards: {deck.cards}")
    print("Players:")
    for player in Player.query.all():
        print(f"Player: {player}, Game: {player.game}")
    print("Cards:")
    for card in Card.query.all():
        print(f"Card: {card.id}, Value: {card.value}, Deck ID: {card.deck_id}, Deck: {card.deck}, Player: {card.player}")
    print()


    if delete_player:
        print("Deleting player1")
        db.session.commit()
        db.session.delete(player1)
        print("Games:")
        for game in Game.query.all():
            print(f"Game: {game}, Game_id: {game.id}, Game deck: {game.deck_id}, Game players: {game.players}")
        print("Decks:")
        for deck in Deck.query.all():
            print(f"Deck: {deck}, Game: {deck.game}, Cards: {deck.cards}")
        print("Players:")
        for player in Player.query.all():
            print(f"Player: {player}, Game: {player.game}")
        print("Cards:")
        for card in Card.query.all():
            print(f"Card: {card.id}, Value: {card.value}, Deck ID: {card.deck_id}, Deck: {card.deck}, Player: {card.player}")
        
    if delete_game:
        print("Deleting game1")
        db.session.delete(game1)
        db.session.commit()
        print("Games:")
        for game in Game.query.all():
            print(f"Game: {game}, Game_id: {game.id}, Game deck: {game.deck_id}, Game players: {game.players}")
        print("Decks:")
        for deck in Deck.query.all():
            print(f"Deck: {deck}, Game: {deck.game}, Cards: {deck.cards}")
        print("Players:")
        for player in Player.query.all():
            print(f"Player: {player}, Game: {player.game}")
        print("Cards:")
        for card in Card.query.all():
            print(f"Card: {card.id}, Value: {card.value}, Deck ID: {card.deck_id}, Deck: {card.deck}, Player: {card.player}")

    if delete_deck:
        print("Deleting deck1")
        db.session.delete(deck1)
        db.session.commit()
        print("Games:")
        for game in Game.query.all():
            print(f"Game: {game}, Game_id: {game.id}, Game deck: {game.deck_id}, Game players: {game.players}")
        print("Decks:")
        for deck in Deck.query.all():
            print(f"Deck: {deck}, Game: {deck.game}, Cards: {deck.cards}")
        print("Players:")
        for player in Player.query.all():
            print(f"Player: {player}, Game: {player.game}")
        print("Cards:")
        for card in Card.query.all():
            print(f"Card: {card.id}, Value: {card.value}, Deck ID: {card.deck_id}, Deck: {card.deck}, Player: {card.player}")

if __name__ == '__main__':
	main()