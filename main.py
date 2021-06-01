import discord, os, dotenv, deck_of_cards, Player, Dealer, Game, EmptyLobbyException
from Player import Player
from discord.ext.commands import Bot
from dotenv import load_dotenv
from deck_of_cards import deck_of_cards

# Discord Auth/Bot Logistics
bot = Bot(command_prefix="-")
load_dotenv(".env")
TOKEN = os.getenv("TOKEN")

# game fields
game = None
deck = deck_of_cards.DeckOfCards()
dealer = Dealer.Dealer(deck)
head = None
curr_player = None


def to_str():
    retStr = "\t\t\t\t\t\tThe Table - {}\n\n".format(str(dealer))
    curr = head
    while curr:
        retStr += ("\t\t\t\t\t\t" + str(curr) + "\n")
        curr = curr.next
    return "```" + retStr + "```"

@bot.command(name='test')
async def test_command(message):
    await message.channel.send("Test Received! BlackJackBot is Online!")

# STARTS A NEW BLACKJACK GAME
'''
Resets a game by initializng the game with an empty lobby and a new deck
'''
def game_reset(head, deck):
    head = None
    deck = deck_of_cards.DeckOfCards()

@bot.command(name='start')
async def start(message):
    game_reset(head,deck)
    await message.channel.send("Welcome to BlackJack! Use -join to have a seat at the table!")

@bot.command(name='turn')
async def turn(message):
    await message.channel.send("It is {}'s turn.".format(str(curr_player)))

'''
Adds a newly created player object to the linked list representing the players at the table.
Labeled as "head"
'''
def add_player(player_obj):
    global head
    if head is None:
        head = player_obj
    else:
        curr = head
        while curr:
            if curr.next == None:
                curr.next = player_obj
                return
            curr = curr.next

@bot.command(name='join')
async def join(message):
    add_player(Player(str(message.author)))
    await message.channel.send("{} has joined the table! \
    Use -begin once all players have joined.\n{}".format(message.author, to_str()))

'''
Begin differs from start as it is used to begin a round. This is used at the very beginning of the
game OR when someone joins the table via "-join". Begin must be used once everyone is done joining the
table. Being is only neccesary when > 1 person/people join the table.
'''

def game_begin():
    global curr_player, dealer
    curr_player = head
    # place bets
    dealer.deal(head)
    # hit || double || stand

def new_round():
    global curr_player, head
    curr_player = head
    dealer.hidden = True
    dealer.deal(head)

@bot.command(name='begin')
async def begin(message):
    game_begin()
    await message.channel.send("Starting the game:\n{}".format(to_str()))
    await message.channel.send("{}, it is your turn!".format(str(curr_player.username)))


def game_hit(message):
    return dealer.hit(curr_player)

def dealer_turn(message):
    print("in dealer_turn")
    dealer.hidden = False
    while dealer.count < 17:
        dealer.self_draw()
    if dealer.count > 21:
        return True
    else:
        print("Dealer Count: {}".format(str(dealer.count)))
        print(to_str())
        return False


@bot.command(name='hit')
async def hit(message):
    global curr_player
    player = curr_player
    await message.channel.send("{}, it is your turn!".format(str(curr_player.username)))
    if player.disc_username.strip() != str(message.author).strip():
        await message.channel.send("{}, it is {}'s turn!".format(message.author, str(player.disc_username)))
        return
    if not game_hit(message):
        await message.channel.send("{} bust with {}!".format(str(message.author), player.count))
        if curr_player.next is not None:
            await message.channel.send("{}, it is your turn!".format(str(player.next)))
            curr_player = curr_player.next
        else:
            if dealer_turn(message):
                message.channel.send("The Dealer busted with {}".format(str(dealer.count)))
            else:
                message.channel.send("The Dealer ended with {}".format(str(dealer.count)))
            new_round()
            await message.channel.send("{}, it is your turn!".format(str(curr_player.username)))
    else:
        await message.channel.send("{}, your new hand is {} for a total of {}. Would you like to hit or stand?".format(player.get_username(), player.cards_str(), str(player.count)))

@bot.command(name='stand')
async def stand(message):
    global curr_player
    player = curr_player
    if player.disc_username.strip() != str(message.author).strip():
        await message.channel.send("{}, it is {}'s turn!".format(message.author, str(player.disc_username)))
    else:
        if player.next is not None:
            await message.channel.send("{}, it is your turn!".format(str(player.next)))
            curr_player = player.next
        else:
            if dealer_turn(message):
                await message.channel.send("The Dealer busted with {}".format(str(dealer.count)))
            else:
                await message.channel.send("The Dealer ended with {}".format(str(dealer.count)))
            new_round()
            await message.channel.send("{}, it is your turn!".format(str(curr_player.username)))


@bot.command(name='leave')
async def leave(message):
    game.remove_player(str(message.author))
    await message.channel.send("{} has left the table. Thanks for Playing!".format(message.author))

@bot.command(name='table')
async def table(message):
    await message.channel.send("{}".format(str(game)))

print(TOKEN)
bot.run(TOKEN)