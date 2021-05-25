import discord, os, requests, json, Dealer
import CountBustExeption, EmptyLobbyException
from deck_of_cards import deck_of_cards

class Game:
    def __init__(self):
        self.deck = deck_of_cards.DeckOfCards()
        self.players = []
        self.player_i = 0
        self.curr_player = self.players[self.player_i]
        self.dealer = Dealer(self.deck)
        self.client = discord.Client()
        self.isOver = False

    @discord.client.event
    async def on_ready(self):
        print("We have logged in as {0.user}".format(self.client))

    @discord.client.event
    async def on_message(self, message):
        if message.author == self.client.user:
            return

        if message.content.startswith("$bj hit"):
            pass

    def dealer_turn(self):
        pass

    def player_turn(self):
        pass

    '''
    Send the game to the next turn. Could be either the dealer or the players turn
    '''
    def next_turn(self):
        if len(self.players) < 1:
            raise EmptyLobbyException()
        else:
            self.curr_player = self.players[self.player_i+1]
            self.player_i += 1

    def start(self):
        self.__init__()
        self.next_turn()

    '''
    Adds a Player object to the list of players
    '''
    def add_player(self, player):
        self.players.append(player)

    def remove_player(self, player):
        self.players.remove(player)