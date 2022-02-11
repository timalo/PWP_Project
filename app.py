from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    card_id = db.relationship("Card", back_populates="deck")
    game = db.relationship("Game", back_populates="deck_id")
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"))

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(128), nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey("deck.id"))

    deck = db.relationship("Deck", back_populates="card_id")

    player = db.relationship("Player", back_populates="card_id")
    player_id = db.Column(db.Integer, db.ForeignKey("player.id"))

    #task_id = db.relationship("Task", back_populates="card")

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    deck_id = db.relationship("Deck", back_populates="game", uselist=False)
    player_id = db.relationship("Player", back_populates="game")

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    game = db.relationship("Game", back_populates="player_id")
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"))

    card_id = db.relationship("Card", back_populates="player")


def main():
    os.remove("test.db")
    db.create_all()
    game1 = Game()
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

    print()
    for game in Game.query.all():
        print(f"Game: {game}, Game_id: {game.id}, Game deck: {game.deck_id}, Game players: {game.player_id}")
    db.session.commit()

#Product.query.filter_by(handle=product).first()



if __name__ == '__main__':
    main()