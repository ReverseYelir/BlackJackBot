import discord, os, deck_of_cards, Player, Dealer, time, random
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
deck.shuffle_deck()
dealer = Dealer.Dealer(deck)
head = None
curr_player = None
ADMIN_ROLE = "Captain Dumbass"
have_bet = []
num_players = 0
has_started = False

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
prev_gif = ""
DEALER_COMP_TIME = 4.0
'''
TODO:
    Add help and brief keyword arguments to command decorators
'''


def to_str():
    retStr = "The Dealer - {}\n\n".format(str(dealer))
    curr = head
    while curr:
        retStr += ("\t\t" + str(curr) + "\n")
        curr = curr.next
    return "\n>>> " + retStr


@bot.command(name='test', brief="THis is a tEsT")
async def test_command(message):
    await message.channel.send("Test Received! BlackJackBot is Online!")


@bot.command(name='mybet', brief="Tells the user their current bet")
async def bet_inquiry(message):
    player = find_player(str(message.author))
    await message.channel.send("{}, your current bet is ${}".format(player.username, player.curr_bet))


@bot.command(name='double', brief="Doubles the users current bet")
async def bet_inquiry(message):
    player = find_player(str(message.author))
    player.bank -= player.curr_bet
    player.curr_bet *= 2
    await message.channel.send("{}, you doubled down for ${}".format(player.username, player.curr_bet))


# STARTS A NEW BLACKJACK GAME
'''
Resets a game by initializng the game with an empty lobby and a new deck
'''


def game_reset():
    global head, deck, num_players, has_started
    head = None
    deck = deck_of_cards.DeckOfCards()
    deck.shuffle_deck()
    num_players = 0
    has_started = False


@bot.command(name='start')
async def start(message):
    game_reset()
    await message.channel.send("Welcome to BlackJack! Use -join to have a seat at the table!")


@bot.command(name='turn')
async def turn(message):
    await message.channel.send("It is {}'s turn.".format(str(curr_player)))


'''
Adds a newly created player object to the linked list representing the players at the table.
Labeled as "head"
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


@bot.command(name='join')
async def join(message):
    player = Player(str(message.author))
    await add_player(player)
    await message.channel.send("{} has joined the table! \
Use -begin once all players have joined.\n{}".format(message.author, to_str()))


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
    # hit || double || stand


async def new_round():
    global curr_player, head
    curr_player = head
    dealer.hidden = True
    dealer.deal(head)


def find_player(disc_username):
    curr = head
    while curr:
        if curr.disc_username == disc_username or curr.username == disc_username:
            return curr
        curr = curr.next
    return None


async def get_bets(message):
    if not await all_bet():
        await message.channel.send("Place your bets.")


async def all_bet():
    global curr_player, head
    curr = head
    while curr:
        if curr.curr_bet == 0:
            print("all_bet returned false")
            return False
        curr = curr.next
    return True
    '''if num_players == len(have_bet):
        print("all_bet returned true")
        return True
    else:
        print("all_bet returned false")
        return False'''


'''
Begin differs from start as it is used to begin a round. This is used at the very beginning of the
game OR when someone joins the table via "-join". Begin must be used once everyone is done joining the
table. Being is only neccesary when > 1 person/people join the table.
'''


@bot.command(name='begin')
async def begin(message):
    await game_begin(message)
    await get_bets(message)
    '''curr = head
    while curr:
        if curr not in have_bet:
            await message.channel.send("{}, you still need to bet. \
Use -begin once everyone has bet.".format(curr.username))
        else:
            await message.channel.send("Starting the game:\n{}\n{}, it is your turn!".format(to_str(), str(curr_player)))
        curr = curr.next'''


@bot.command(name='fund')
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


@bot.command(name="fundall")
async def fund_all(message):
    isAdmin = False
    amount = 0
    '''for role in message.author.roles:
        if str(role) == ADMIN_ROLE:
            isAdmin = True
            break'''
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


def game_hit(message):
    return dealer.hit(curr_player)


@bot.command(name="gif")
async def get_gif(message):
    embed = discord.Embed(
        title="This is a gif.",
        color=discord.Colour.purple()
    )
    embed.set_image(url=THINKING_GIFS[random.randint(0, len(THINKING_GIFS) - 1)])
    await message.channel.send(embed=embed)


async def comp_dealer(message):
    global have_bet, prev_gif, TITLES
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
    return results


def dealer_turn(message):
    dealer.hidden = False
    while dealer.count < 17:
        dealer.self_draw()
    return dealer.count


@bot.command(name='bet')
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


@bot.command(name='hand')
async def hand(message):
    player = find_player(str(message.author))
    if player is not None:
        await message.channel.send("{}'s hand is {}".format(player.username, player.cards_str()))


'''
DEBUGGER
'''


@bot.command(name='have-bet')
async def hand(message):
    await message.channel.send("{} have bet".format(str(have_bet)))


'''
DEBUGGER
'''


@bot.command(name='size')
async def hand(message):
    await message.channel.send("{} players at the table".format(str(num_players)))


async def notify_to_bet(message):
    curr = head
    while curr:
        if curr not in have_bet:
            await message.channel.send("{}, you need to bet.".format(curr.username))
        curr = curr.next


@bot.command(name='hit')
async def hit(message):
    global curr_player
    print("{} curr at start of hit".format(curr_player))
    if not await all_bet():
        await notify_to_bet(message)
        return
    # await message.channel.send("{}, it is your turn!".format(str(curr_player.username)))
    if curr_player.disc_username.strip() != str(message.author).strip():
        await message.channel.send("{}, it is {}'s turn!".format(message.author, str(curr_player.disc_username)))
        return
    if not game_hit(message):  # on bust
        await message.channel.send("{} bust with {}!".format(str(message.author), curr_player.count))
        if curr_player.next is not None:
            await message.channel.send("{}, it is your turn!".format(str(curr_player.next)))
            curr_player = curr_player.next
        else:
            if dealer_turn(message) > 21:
                await message.channel.send("The Dealer busted with {}".format(str(dealer.count)))
            else:
                await message.channel.send("The Dealer ended with {}\n\n".format(str(dealer.count)))
            results = await comp_dealer(message)
            resultStr = ">>> \nWinners:\n"
            for winner in results[0]:
                resultStr += ("\t{}\n".format(winner.username))
            resultStr += "Ties:\n"
            for tie in results[1]:
                resultStr += ("\t{}\n".format(tie.username))
            resultStr += "Losers:\n"
            for loser in results[2]:
                resultStr += ("\t{}\n".format(loser.username))
            await new_round()
            await message.channel.send("{}\n{}, it is your turn!".format(resultStr, str(curr_player)))
    else:  # didn't bust
        await message.channel.send(
            "{}, your new hand is {} for a total of {}. Would you like to hit or stand?".format(
                curr_player.get_username(),
                curr_player.cards_str(),
                str(curr_player.count)))


@bot.command(name='stand')
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
            if dealer_turn(message) > 21:
                await message.channel.send("The Dealer busted with {}".format(str(dealer.count)))
            else:
                await message.channel.send("The Dealer ended with {}\n".format(str(dealer.count)))
            results = await comp_dealer(message)
            resultStr = ">>> Winners:\n"
            for winner in results[0]:
                resultStr += ("\t{}\n".format(winner.username))
            resultStr += "Ties:\n"
            for tie in results[1]:
                resultStr += ("\t{}\n".format(tie.username))
            resultStr += "Losers:\n"
            for loser in results[2]:
                resultStr += ("\t{}\n".format(loser.username))
            await new_round()
            await message.channel.send("{}".format(resultStr))
            await message.channel.send("{}, it is your turn!".format(str(curr_player)))


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


@bot.command(name='leave')
async def leave(message):
    await remove_player(str(message.author))
    await message.channel.send("{} has left the table. Thanks for Playing!".format(message.author))


@bot.command(name='table')
async def table(message):
    await message.channel.send(to_str())


bot.run(TOKEN)
