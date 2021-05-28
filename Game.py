import discord, os, requests, json, Dealer, dotenv
import CountBustExeption, EmptyLobbyException
from deck_of_cards import deck_of_cards
from dotenv import load_dotenv

class Game():
    def __init__(self, bot):
        self.bot = bot
        self.deck = deck_of_cards.DeckOfCards()
        self.dealer = Dealer.Dealer(self.deck)
        self.players = []
        self.player_i = -1
        self.curr_player = None
        self.next_player = None
        self.isOver = False
        self.dealerTurn = False

    def __str__(self):
        retStr = "```\t\t\t\t\t\tThe Table - {}\n\n".format(str(self.dealer))
        for player in self.players:
            playerStr = ""
            retStr += ("\t\t\t\t\t\t" + str(player) + "\n")
        return retStr + "```"

    def dealer_turn(self, message):
        pass

    def player_turn(self, message):
        message.channel.send("player turn")

    '''
    Send the game to the next turn. Could be either the dealer or the players turn
    '''
    def next_turn(self, message):
        self.player_i += 1
        if len(self.players) < 1:
                print("Empty Table")
        elif self.player_i == len(self.players):
            self.dealer_turn(message)
        else:
            self.player_turn(message)

    def start(self):
        self.deck = deck_of_cards.DeckOfCards()
        self.dealer = Dealer.Dealer(self.deck)
        self.players = []
        self.player_i = -1
        self.curr_player = None
        self.isOver = False
        self.dealerTurn = False
        self.dealer.new_hand()

    def begin(self, message):
        self.dealer.deal(self.players)
        self.curr_player = self.players[self.player_i]
        self.next_turn(message)
    '''
    Adds a Player object to the list of players
    '''
    def add_player(self, player):
        for curr in self.players:
            if str(curr) == str(player):
                return
        self.players.append(player)

    def remove_player(self, player):
        for i in range(len(self.players)):
            curr = self.players[i]
            if str(curr) == str(player):
                self.players.pop(i)

    def hit(self, message):
        return self.dealer.hit(self.curr_player)

    def stand(self):
        pass

    def get_next_player(self):
        if self.player_i == len(self.players):
            self.next_player = self.players[0]
        else:
            self.next_player = self.players[self.player_i+1]
        return self.next_player

    def deal(self, playerList):
        self.dealer.deal(playerList)