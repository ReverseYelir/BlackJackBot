import discord, os, requests, json, Dealer
from deck_of_cards import deck_of_cards

'''
Models a player at a blackjack table.
Manages:
    1. The player's discord name and nickname
    2. The cards in a player's hand
    3. A card total(count)
    4. Number of chips
    5. A reference to the next player at the table
    6. The player's current bet
'''


class Player:
    def __init__(self, username, next=None):
        self.disc_username = username
        self.username = self.disc_username.split("#")[0]
        self.count = 0
        self.cards = []
        self.next = next
        self.bank = 0
        self.curr_bet = 0

    '''
        Adds a cards to the player's hand

    :param card - the deck_of_cards.Card instance to add
    :return boolean - True if the cards was added, False if adding causes the player to bust
    '''
    def add_card(self, card):
        self.cards.append(card)
        if card.rank > 10:
            self.count += 10
        else:
            self.count += card.rank
        if self.count > 21:
            return False
        return True

    '''
    Sets the current bet of the player

    :param n - The amount to bet
    '''
    def bet(self, n):
        self.curr_bet = int(n)
        self.bank -= n

    '''
    :return ret - A String representing the users cards
    ex: [2, 10]
    '''
    def cards_str(self):
        ret = "["
        for card in self.cards:
            if card.value > 10:
                ret += (str(10) + ", ")
            else:
                ret += (str(card.value) + ", ")
        ret = ret.strip(", ")
        return ret + "]"

    '''
    Clears a player's hand
    '''
    def clear_cards(self):
        self.cards = []
        self.count = 0

    '''
    Gives the player n chips

    :param n - The number of chips to add
    '''
    def fund(self, n):
        self.bank += n

    def get_count(self):
        return self.count

    def get_disc_name(self):
        return self.disc_username

    def get_hand(self):
        return self.cards

    def get_username(self):
        return self.username

    def __str__(self):
        return "{} {} ${}".format(self.cards_str(), self.username, str(self.bank))
