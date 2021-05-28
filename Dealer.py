from deck_of_cards import deck_of_cards
class Dealer:
    def __init__(self, deck):
        self.deck = deck
        self.cards = []  # first index is the "hidden" card
        self.count = 0

    def __str__(self):
        return "[*, {}]".format(str(self.cards[1].value))

    def get_card(self):
        if len(self.deck.deck) < 1:
            self.deck = deck_of_cards.DeckOfCards()
            self.deck.shuffle_deck()
        return self.deck.give_random_card()

    def deal(self, playerList):
        if self.deck.__sizeof__() < 2:
            self.deck = deck_of_cards.DeckOfCards()
            self.deck.shuffle_deck()
        for player in playerList:
            player.clear_cards()
            player.add_card(self.deck.give_random_card())
            player.add_card(self.deck.give_random_card())

    def hit(self, player):
        if len(self.deck.deck) < 1:
            self.deck = deck_of_cards.DeckOfCards()
            self.deck.shuffle_deck()
        return player.add_card(self.deck.give_random_card())

    def clear_hand(self):
        self.cards = []
        self.count = 0

    def new_hand(self):
        for i in range(2):
            self.cards.append(self.deck.give_random_card())