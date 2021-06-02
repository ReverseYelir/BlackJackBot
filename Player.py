import discord, os, requests, json, Dealer, CountBustExeption
from deck_of_cards import deck_of_cards

class Player:
    def __init__(self, username, next=None):
        self.disc_username = username
        self.username = self.disc_username.split("#")[0]
        self.count = 0
        self.cards = []  # contains the card objects
        self.next = next
        self.bank = 0
        self.bet = 0

    def cards_str(self):
        ret = "["
        for card in self.cards:
            if card.value > 10:
                ret += (str(10) + ", ")
            else:
                ret += (str(card.value) + ", ")
        ret = ret.strip(", ")
        return ret + "]"

    def __str__(self):
        return "{} - {}".format(self.username, self.cards_str())

    def fund(self, n):
        self.bank += n

    def get_hand(self):
        return self.cards

    def get_count(self):
        return self.count

    def bet(self, n):
        self.bet = n
        self.bank -= n

    def raise_bet(self):
        pass

    def add_card(self, card):
        self.cards.append(card)
        if card.rank > 10:
            self.count += 10
        else:
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

