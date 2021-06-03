import os, deck_of_cards, Player, Dealer
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
ADMIN_ROLE = "Guy Who Owns The Server"


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
def game_reset():
    global head, deck
    head = None
    deck = deck_of_cards.DeckOfCards().shuffle_deck()


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
def add_player(player_obj):
    global head
    if head is None:
        head = player_obj
    elif find_player(player_obj.disc_username) is None:
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


def find_player(disc_username):
    curr = head
    while curr:
        if curr.disc_username == disc_username or curr.username == disc_username:
            return curr
        curr = curr.next
    return None


'''
Begin differs from start as it is used to begin a round. This is used at the very beginning of the
game OR when someone joins the table via "-join". Begin must be used once everyone is done joining the
table. Being is only neccesary when > 1 person/people join the table.
'''
@bot.command(name='begin')
async def begin(message):
    game_begin()
    await message.channel.send("Starting the game:\n{}".format(to_str()))
    await message.channel.send("{}, it is your turn!".format(str(curr_player)))


@bot.command(name='fund')
async def fund(message):
    for role in message.author.roles:
        print(str(role))
        if str(role) == ADMIN_ROLE:
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


def comp_dealer():
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
    player.bet(amount)
    await message.channel.send("{} has bet ${}".format(str(find_player(str(message.author))), str(amount)))

@bot.command(name='hand')
async def hand(message):
    player = find_player(str(message.author))
    if player is not None:
        await message.channel.send("{}'s hand is {}".format(player.username, player.cards_str()))

@bot.command(name='hit')
async def hit(message):
    global curr_player
    player = curr_player
    await message.channel.send("{}, it is your turn!".format(str(curr_player.username)))
    if player.disc_username.strip() != str(message.author).strip():
        #await message.channel.send("{}, it is {}'s turn!".format(message.author, str(player.disc_username)))
        return
    if not game_hit(message):
        await message.channel.send("{} bust with {}!".format(str(message.author), player.count))
        if curr_player.next is not None:
            await message.channel.send("{}, it is your turn!".format(str(player.next)))
            curr_player = curr_player.next
        else:
            if dealer_turn(message) > 21:
                await message.channel.send("The Dealer busted with {}".format(str(dealer.count)))
            else:
                await message.channel.send("The Dealer ended with {}\n\n".format(str(dealer.count)))
            results = comp_dealer()
            resultStr = "\nWinners:\n"
            for winner in results[0]:
                resultStr += ("\t{}\n".format(winner.username))
            resultStr += "Ties:\n"
            for tie in results[1]:
                resultStr += ("\t{}\n".format(tie.username))
            resultStr += "Losers:\n"
            for loser in results[2]:
                resultStr += ("\t{}\n".format(loser.username))
            new_round()
            await message.channel.send("{}\n{}, it is your turn!".format(resultStr, str(curr_player)))
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
            if dealer_turn(message) > 21:
                await message.channel.send("The Dealer busted with {}".format(str(dealer.count)))
            else:
                await message.channel.send("The Dealer ended with {}\n".format(str(dealer.count)))
            results = comp_dealer()
            resultStr = ">>> Winners:\n"
            for winner in results[0]:
                resultStr += ("\t{}\n".format(winner.username))
            resultStr += "Ties:\n"
            for tie in results[1]:
                resultStr += ("\t{}\n".format(tie.username))
            resultStr += "Losers:\n"
            for loser in results[2]:
                resultStr += ("\t{}\n".format(loser.username))
            new_round()
            await message.channel.send("{}".format(resultStr))
            await message.channel.send("{}, it is your turn!".format(str(curr_player)))


def remove_player(disc_username):
    global head
    curr = head
    if curr.disc_username.strip() == disc_username.strip():
        head = curr.next
        return
    else:
        while curr.next:
            if curr.next.disc_username.strip() == disc_username.strip():
                curr.next = curr.next.next
                return
            curr = curr.next


@bot.command(name='leave')
async def leave(message):
    remove_player(str(message.author))
    await message.channel.send("{} has left the table. Thanks for Playing!".format(message.author))


@bot.command(name='table')
async def table(message):
    await message.channel.send(to_str())


bot.run(TOKEN)
