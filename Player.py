import discord, os, requests, json, Dealer, CountBustExeption
from deck_of_cards import deck_of_cards

class Player:
    def __init__(self, username, next=None):
        self.disc_username = username
        self.username = self.disc_username.split("#")[0]
        self.count = 0
        self.cards = []  # contains the card objects
        self.next = next

    def __str__(self):
        if len(self.cards) < 1:
            return "{} - []".format(self.username)
        else:
            retStr = "{} - [".format(self.username)
            for card in self.cards:
                retStr += (str(card.value) + ", ")
            return retStr.rstrip(", ") + "]"

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
        self.cards.append(card)
        self.count += card.rank
        if self.count > 21:
            return False
        return True

    def clear_cards(self):
        self.cards = []
        self.count = 0

    def get_username(self):
        return self.username

    def get_disc_name(self):
        return self.disc_username

    def cards_str(self):
        ret = "["
        for card in self.cards:
            ret += (str(card.value) + ", ")
        ret = ret.strip(", ")
        return ret + "]"