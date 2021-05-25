import discord, os, requests, json, Dealer, CountBustExeption
from deck_of_cards import deck_of_cards

class Player:
    def __init__(self, username):
        self.disc_username = username
        self.count = 0
        self.cards = []  # contains the card objects

    def hit(self):
        pass

    def stand(self):
        pass

    def get_hand(self):
        return self.cards

    def get_count(self):
        return self.count

    def bet(self):
        pass

    def raise_bet(self):
        pass

    def add_card(self, card):
        self.count += card.rank
        if self.count > 21:
            print("Busted GiGgItYgIgGtTyGiGgItY")
            raise CountBustExeption
        self.cards.append(card)