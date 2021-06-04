import discord, os, deck_of_cards, Player, Dealer, time, random
from Player import Player
from discord.ext.commands import Bot
from dotenv import load_dotenv
from deck_of_cards import deck_of_cards

'''
Author: Riley Simpson

Description: This scripts purpose is the simulate the card game "Blackjack" via
    a discord bot using the module discord.py. The script interacts with player object(s)
    and a dealer object. The Player class models a player at a blackjack table, keeping track
    of their cards, chips, bets, etc. The Dealer class models the dealer at a blackjack table,
    keeping track of the games deck and managing players cards/chips. Custom commands are defined
    here and are activated via a discord channel with a - prefix. For example: -hit or -stand.

Basic Game Outline:
    1. Use -start to start a game
    2. Players use -join to join the game
    3. Use -begin to signal all players are done joining and are ready to play
    4. Each player must use -bet amount in order to start the round
    5. The dealer deals and the round starts
    6. Each players takes their turn (hit, double, stand)
    7. Dealer goes
    8. Players win/lose money and steps repeat at 4
'''
# Discord Auth/Bot Logistics
bot = Bot(command_prefix="-")
load_dotenv(".env")
TOKEN = os.getenv("TOKEN")

'''
-----------------------------------------------------------
   ____                        _____ _      _     _     
  / ___| __ _ _ __ ___   ___  |  ___(_) ___| | __| |___ 
 | |  _ / _` | '_ ` _ \ / _ \ | |_  | |/ _ \ |/ _` / __|
 | |_| | (_| | | | | | |  __/ |  _| | |  __/ | (_| \__ \
  \____|\__,_|_| |_| |_|\___| |_|   |_|\___|_|\__,_|___/

-----------------------------------------------------------                                                      
'''
deck = deck_of_cards.DeckOfCards()
deck.shuffle_deck()
dealer = Dealer.Dealer(deck)
head = None
curr_player = None
have_bet = []
num_players = 0
has_started = False
prev_gif = ""

'''
--------------------------------------------------
   ____                _              _       
  / ___|___  _ __  ___| |_ __ _ _ __ | |_ ___ 
 | |   / _ \| '_ \/ __| __/ _` | '_ \| __/ __|
 | |__| (_) | | | \__ \ || (_| | | | | |_\__ \
  \____\___/|_| |_|___/\__\__,_|_| |_|\__|___/

--------------------------------------------------
'''
TITLES = ["Grabbing the calculator...",
          "Beep Boop Bopping",
          "Definitely not changing the dealers cards...",
          "Is it your lucky day?"
          ]

THINKING_GIFS = [
    "https://media.giphy.com/media/lKXEBR8m1jWso/giphy.gif",
    "https://media.giphy.com/media/lKXEBR8m1jWso/giphy.gif",
    "https://media.giphy.com/media/dgK22exekwOLm/giphy.gif",
    "https://media.giphy.com/media/WRQBXSCnEFJIuxktnw/giphy.gif",
    "https://media.giphy.com/media/hv53DaYcXWe3nRbR1A/giphy.gif",
    "https://media.giphy.com/media/DfSXiR60W9MVq/giphy.gif",
    "https://media.giphy.com/media/BBkKEBJkmFbTG/giphy.gif",
    "https://media.giphy.com/media/KzPhDm4lBUPDQ1c7du/giphy.gif",
    "https://media.giphy.com/media/MayGBc8GBkJLlsGp73/giphy.gif",
    "https://media.giphy.com/media/RLE2Q5ajPa6GgUxe1z/giphy.gif",
    "https://media.giphy.com/media/l41YtZOb9EUABnuqA/giphy.gif",
    "https://media.giphy.com/media/l1JoiJuevIG4wuTgQ/giphy.gif",
    "https://media.giphy.com/media/3ofSByJTa2LzP82d68/giphy.gif",
    "https://media.giphy.com/media/2bYewTk7K2No1NvcuK/giphy.gif"
]
DEALER_COMP_TIME = 4.0
ADMIN_ROLE = "Captain Dumbass"


''''
---------------------------------------------------------
   _____                                          _     
  / ____|                                        | |    
 | |     ___  _ __ ___  _ __ ___   __ _ _ __   __| |___ 
 | |    / _ \| '_ ` _ \| '_ ` _ \ / _` | '_ \ / _` / __|
 | |___| (_) | | | | | | | | | | | (_| | | | | (_| \__ \
  \_____\___/|_| |_| |_|_| |_| |_|\__,_|_| |_|\__,_|___/

------------------------------------------------------------  
'''

'''
Begin differs from start as it is used to begin a round. This is used at the very beginning of the
game OR when someone joins the table via "-join". Begin must be used once everyone is done joining the
table. Being is only neccesary when > 1 person/people join the table.
'''
@bot.command(name='begin', brief="Flags players are done joining for the round")
async def begin(message):
    await game_begin(message)
    await get_bets(message)


@bot.command(name='bet', brief="Place a bet of x chips", help="Usage: -bet amount")
async def bet(message):
    player = find_player(str(message.author))
    amount = 0
    try:
        amount = int(message.message.content.split()[1])
    except IndexError:
        await message.channel.send("Incorrect use. Ex: -bet 50")
        return
    try:
        player.bet(amount)
    except AttributeError:
        await message.channel.send("Make sure you have joined the table!")
        return
    if player is not None:
        have_bet.append(player)
    await message.channel.send("{} has bet ${}".format(player.username, str(amount)))
    if await all_bet():
        print("All Have Bet.")
        await new_round()
        await message.channel.send("{}, it is your turn".format(str(curr_player)))
    else:
        curr = head
        while curr:
            if curr not in have_bet:
                await message.channel.send(
                    "{}, you still need to bet. You have ${}".format(curr.username, str(curr.bank)))
            curr = curr.next


@bot.command(name='double', brief="Doubles the users current bet")
async def double(message):
    player = find_player(str(message.author))
    player.bank -= player.curr_bet
    player.curr_bet *= 2
    await message.channel.send("{}, you doubled down for ${}".format(player.username, player.curr_bet))


@bot.command(name='fund', brief="An admin can add chips to a player",
             help="Usage: -fund playerName amount OR -fund amount (funds oneself)")
async def fund(message):
    if message.author.top_role.permissions.administrator is True:
        content = message.message.content.split()
        if len(content) == 2 and content[1].isnumeric():
            player = find_player(str(message.author))
            if player is not None:
                player.fund(int(content[1]))
            await message.channel.send("{} received {} chips".format(str(message.author), content[1]))
        elif len(content) == 2 and not content[1].isnumeric():
            await message.channel.send("The correct usage is: -fund playerName amount")
        elif len(content) == 3 and content[2].isnumeric():
            player = find_player(content[1].lower())
            if player is not None:
                player.fund(int(content[2]))
            await message.channel.send("{} received {} chips".format(content[1], content[2]))

        else:
            await message.channel.send("Invalid use of fund.")


@bot.command(name="fundall", ief="Adds chips to all players. Requires administrative permissions",
             help="Usage: -fundall amount")
async def fund_all(message):
    amount = 0
    if message.author.top_role.permissions.administrator is True:
        content = message.message.content.split()
        if len(content) == 2 and content[1].isnumeric():
            amount = int(content[1])
    curr = head
    while curr:
        curr.fund(amount)
        curr = curr.next
    if amount > 0:
        await message.channel.send("Everyone received {} chips! \
Thank You {}, you truly are the coolest.".format(str(amount), ADMIN_ROLE))


@bot.command(name="gif", brief="Sends a random thinking gif for funzies")
async def get_gif(message):
    embed = discord.Embed(
        title="This is a gif.",
        color=discord.Colour.purple()
    )
    embed.set_image(url=THINKING_GIFS[random.randint(0, len(THINKING_GIFS) - 1)])
    await message.channel.send(embed=embed)


@bot.command(name='hand', brief="Responds with the player's hand")
async def hand(message):
    player = find_player(str(message.author))
    if player is not None:
        await message.channel.send("{}'s hand is {}".format(player.username, player.cards_str()))


@bot.command(name='have-bet', brief="Lets a user know if they have bet")
async def hand(message):
    await message.channel.send("{} have bet".format(str(have_bet)))


@bot.command(name='hit', brief="Gives the user another card")
async def hit(message):
    global curr_player
    print("{} curr at start of hit".format(curr_player))
    if not await all_bet():
        await notify_to_bet(message)
        return
    if curr_player.disc_username.strip() != str(message.author).strip():
        await message.channel.send("{}, it is {}'s turn!".format(message.author, str(curr_player.disc_username)))
        return
    if not game_hit(message):  # on bust
        await message.channel.send("{} bust with {}!".format(str(message.author), curr_player.count))
        if curr_player.next is not None:
            await message.channel.send("{}, it is your turn!".format(str(curr_player.next)))
            curr_player = curr_player.next
        else:
            if dealer_turn() > 21:
                await message.channel.send("The Dealer busted with {}".format(str(dealer.count)))
            else:
                await message.channel.send("The Dealer ended with {}\n\n".format(str(dealer.count)))
            result_str = await comp_dealer(message)
            await new_round()
            await message.channel.send("{}\n{}, it is your turn!".format(result_str, str(curr_player)))
    else:  # didn't bust
        await message.channel.send(
            "{}, your new hand is {} for a total of {}. Would you like to hit or stand?".format(
                curr_player.get_username(),
                curr_player.cards_str(),
                str(curr_player.count)))


@bot.command(name='join', brief="Adds a player to the game")
async def join(message):
    player = Player(str(message.author))
    await add_player(player)
    await message.channel.send("{} has joined the table! \
Use -begin once all players have joined.\n{}".format(message.author, to_str()))


@bot.command(name='leave', brief="Used to leave the table")
async def leave(message):
    await remove_player(str(message.author))
    await message.channel.send("{} has left the table. Thanks for Playing!".format(message.author))


@bot.command(name='my-bet', brief="Tells the user their current bet")
async def bet_inquiry(message):
    player = find_player(str(message.author))
    await message.channel.send("{}, your current bet is ${}".format(player.username, player.curr_bet))


@bot.command(name='size', brief="The number of players at the table")
async def hand(message):
    await message.channel.send("{} players at the table".format(str(num_players)))


@bot.command(name='stand', brief="Keep your current hand")
async def stand(message):
    global curr_player
    if not await all_bet():
        await notify_to_bet(message)
        return
    if curr_player.disc_username.strip() != str(message.author).strip():
        await message.channel.send("{}, it is {}'s turn!".format(message.author, str(curr_player.disc_username)))
    else:
        if curr_player.next is not None:  # another player has a turn
            await message.channel.send("{}, it is your turn!".format(str(curr_player.next)))
            curr_player = curr_player.next
            print("curr player: {}".format(str(curr_player)))
        else:
            if dealer_turn() > 21:
                await message.channel.send("The Dealer busted with {}".format(str(dealer.count)))
            else:
                await message.channel.send("The Dealer ended with {}\n".format(str(dealer.count)))
            result_str = await comp_dealer(message)
            await new_round()
            await message.channel.send("{}".format(result_str))
            await message.channel.send("{}, it is your turn!".format(str(curr_player)))


@bot.command(name='start', brief='Starts a game (also functions as reset)')
async def start(message):
    game_reset()
    await message.channel.send("Welcome to BlackJack! Use -join to have a seat at the table!")


@bot.command(name='table', brief="Shows the current state of the table")
async def table(message):
    await message.channel.send(to_str())


@bot.command(name='test', brief="Tests if the bot is responsive")
async def test_command(message):
    await message.channel.send("Test Received! BlackJackBot is Online!")


@bot.command(name='turn', brief="Reports the current player's turn")
async def turn(message):
    await message.channel.send("It is {}'s turn.".format(str(curr_player)))


'''
-----------------------------------------------------------------
  _____                 _   _                 
 |  ___|   _ _ __   ___| |_(_) ___  _ __  ___ 
 | |_ | | | | '_ \ / __| __| |/ _ \| '_ \/ __|
 |  _|| |_| | | | | (__| |_| | (_) | | | \__ \
 |_|   \__,_|_| |_|\___|\__|_|\___/|_| |_|___/

-----------------------------------------------------------------
'''

'''
Adds a newly created player object to the linked list representing the players at the table.

:param player_obj - The player to be added to the table
'''
async def add_player(player_obj):
    global head, num_players
    if head is None:
        head = player_obj
        num_players += 1
    elif find_player(player_obj.disc_username) is None:
        curr = head
        while curr:
            if curr.next is None:
                curr.next = player_obj
                num_players += 1
                return
            curr = curr.next


'''
Ensure all players have bet

:return True if all players have bet, False otherwise
'''
async def all_bet():
    global curr_player, head
    curr = head
    while curr:
        if curr.curr_bet == 0:
            print("all_bet returned false")
            return False
        curr = curr.next
    return True


'''
Calculates the winners/ties/loser of the round and sends feedback to the users

:param message - The discord.Message instance sent by the client
:return results - a 2d list containing the [[winners], [ties], [losers]]
'''
async def comp_dealer(message):
    global have_bet, prev_gif, TITLES
    await send_dealer_feedback(message)
    results = [[], [], []]  # [winners, ties, losers]
    curr = head
    while curr:
        if dealer.count > 21 and curr.count <= 21:
            results[0].append(curr)
            curr.fund(curr.curr_bet * 2)
        elif dealer.count < curr.count <= 21:
            results[0].append(curr)
            curr.fund(curr.curr_bet * 2)
        elif curr.count == dealer.count:
            results[1].append(curr)
            curr.fund(curr.curr_bet)
        else:
            results[2].append(curr)
        curr.curr_bet = 0
        curr = curr.next
    have_bet = []
    result_str = ">>> \nWinners:\n"
    for winner in results[0]:
        result_str += ("\t{}\n".format(winner.username))
    result_str += "Ties:\n"
    for tie in results[1]:
        result_str += ("\t{}\n".format(tie.username))
    result_str += "Losers:\n"
    for loser in results[2]:
        result_str += ("\t{}\n".format(loser.username))
    return result_str


'''
Executes the dealer's turn by drawing cards until a bust or a hand of at least 17
'''
def dealer_turn():
    dealer.hidden = False
    while dealer.count < 17:
        dealer.self_draw()
    return dealer.count


'''
Attempts to find a player at the table via discord username or nickname

:param disc_username - String representing a discord username or nickname
:return Player object, None if not at the table
'''
def find_player(disc_username):
    curr = head
    while curr:
        if curr.disc_username == disc_username or curr.username == disc_username:
            return curr
        curr = curr.next
    return None


'''
Begins the game ONCE ALL PLAYERS HAVE BET or -begin is called

:param message - The discord.Message instance sent via the client
'''
async def game_begin(message):
    global curr_player, dealer, has_started, have_bet
    have_bet = []
    curr_player = head
    # place bets
    if await all_bet():
        has_started = True
        dealer.deal(head)
        await message.channel.send("{}, it is your turn".format(str(curr_player)))
    elif not await all_bet() and has_started:
        await message.channel.send("Players still need to bet.")


'''
Executes the hit action by having the dealer hit a player
'''
def game_hit(message):
    return dealer.hit(curr_player)


'''
Resets a game with a newly shuffled deck and an empty table
'''
def game_reset():
    global head, deck, num_players, has_started
    head = None
    deck = deck_of_cards.DeckOfCards()
    deck.shuffle_deck()
    num_players = 0
    has_started = False


'''
Prompts and collects bets from players

:param message - The discord.Message instance sent via the client
'''
async def get_bets(message):
    if not await all_bet():
        await message.channel.send("Place your bets.")


'''
Begins a new round by resetting everyone's bets and hands
'''
async def new_round():
    global curr_player, head
    curr_player = head
    dealer.hidden = True
    dealer.deal(head)


'''
Tells the users who still need to bet before the round can being

:param message - The discord.Message instance sent via the client
'''
async def notify_to_bet(message):
    curr = head
    while curr:
        if curr not in have_bet:
            await message.channel.send("{}, you need to bet.".format(curr.username))
        curr = curr.next



'''
Removes a player with a given discord username or nickname from the table

:param disc_username - String of a player's discord username (include #) or their nickname
'''
async def remove_player(disc_username):
    global head, num_players
    curr = head
    if curr.disc_username.strip() == disc_username.strip():
        head = curr.next
        num_players -= 1
    else:
        while curr.next:
            if curr.next.disc_username.strip() == disc_username.strip():
                curr.next = curr.next.next
                num_players -= 1
                return
            curr = curr.next


'''
Send the gif blockquote to the server before calculating who won/tied/lost the round.
Used to add delay at the end of the round. This also delays the dealers turn so turns
do not feel instantaneous and short.

@:param message - The discord message object send by the server
'''
async def send_dealer_feedback(message):
    global prev_gif
    title = TITLES[random.randint(0, len(TITLES) - 1)]
    embed = discord.Embed(
        title=title,
        color=discord.Colour.purple()
    )
    link = THINKING_GIFS[random.randint(0, len(THINKING_GIFS) - 1)]
    while link == prev_gif:
        link = THINKING_GIFS[random.randint(0, len(THINKING_GIFS) - 1)]
        prev_gif = link
    embed.set_image(url=link)
    if not dealer.count > 21:
        await message.channel.send(embed=embed)
        time.sleep(DEALER_COMP_TIME)


'''
Returns a string representation of the table, which contains info on the dealer and players

:return retStr - String representing the table
    ex: 
        "The Dealer - [*, 1]\n\n\t\t[] Yelír $0"
'''
def to_str():
    retStr = "The Dealer - {}\n\n".format(str(dealer))
    curr = head
    while curr:
        retStr += ("\t\t" + str(curr) + "\n")
        curr = curr.next
    return "\n>>> " + retStr


bot.run(TOKEN)
