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

CARDS = ['AS', '2S', '3S', '4S', '5S', '6S', '7S', '8S', '9S', 'TS', 'JS', 'QS', 'KS',
         'AD', '2D', '3D', '4D', '5D', '6D', '7D', '8D', '9D', 'TD', 'JD', 'QD', 'KD',
         'AC', '2C', '3C', '4C', '5C', '6C', '7C', '8C', '9C', 'TC', 'JC', 'QC', 'KC',
         'AH', '2H', '3H', '4H', '5H', '6H', '7H', '8H', '9H', 'TH', 'JH', 'QH', 'KH']


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
    Card.query.first().player = player1



    for card in Card.query.all():
        print(f"Card: {card.id}, Value: {card.value}, Deck ID: {card.deck_id}, Deck: {card.deck}, Player: {card.player}")
    print("Adding player1 to card2")
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