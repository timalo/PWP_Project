from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


delete_player = False
delete_game = True
delete_deck = False
delete_card = False
delete_playergamepair = False


playergamepairs = db.Table("playergamepairs",
    db.Column("playergamepair_id", db.Integer, db.ForeignKey("playergamepair.id"), primary_key=True),
    db.Column("game_id", db.Integer, db.ForeignKey("game.id"), primary_key=True)
)

class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("game.id", ondelete="CASCADE"))

    
    cards = db.relationship("Card", cascade="all", back_populates="deck")
    game = db.relationship("Game", back_populates="deck_id")

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(128), nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey("deck.id", ondelete="CASCADE"))
    player_id = db.Column(db.Integer, db.ForeignKey("player.id"))


    deck = db.relationship("Deck", back_populates="cards")
    player = db.relationship("Player", back_populates="cards")
   

    #task_id = db.relationship("Task", back_populates="card")

class Playergamepair(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    games = db.relationship("Game", secondary=playergamepairs, back_populates="playergamepairs")


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    deck_id = db.relationship("Deck", cascade="all", back_populates="game", uselist=False)
    players = db.relationship("Player", back_populates="game")
    playergamepairs = db.relationship("Playergamepair", secondary=playergamepairs, back_populates="games")


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("game.id", ondelete="SET NULL"))


    game = db.relationship("Game", back_populates="players")
    cards = db.relationship("Card", back_populates="player")




def main():
    try:
        os.remove("test.db")
    except Exception as e:
        print(e)
    db.create_all()
    game1 = Game()
    game2 = Game()
    db.session.add(game1)
    deck1 = Deck(game=game1)
    db.session.add(deck1)
    db.session.commit()

    deck2 = Deck(game=game1)
    db.session.add(deck2)
    db.session.commit()
    print(Deck.query.all())
    card1 = Card(value="2D", deck=deck1)
    card2 = Card(value="Mee töihin!", deck=deck2)
    card3 = Card(value="3D", deck=deck1)
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

#Product.query.filter_by(handle=product).first()



if __name__ == '__main__':
    main()