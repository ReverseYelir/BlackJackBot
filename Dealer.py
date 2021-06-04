from deck_of_cards import deck_of_cards
class Dealer:
    def __init__(self, deck):
        self.deck = deck
        self.cards = [deck.give_random_card(), deck.give_random_card()]  # first index is the "hidden" card
        self.count = 0
        self.hidden = True

    def __str__(self):
        if self.hidden:
            return "[*, {}]".format(str(self.cards[1].value))
        else:
            retStr = "The Dealer - ["
            for card in self.cards:
                retStr += (str(card.value) + ", ")
            return retStr.rstrip(", ") + "]"

    '''
    Clears the dealears hand
    '''
    def clear_hand(self):
        self.cards = []
        self.count = 0

    '''
        Deals a new hand to each player in a linked list
        
        :param head - The first player at the table
    '''
    def deal(self, head):
        if self.deck.__sizeof__() < 2:
            self.deck = deck_of_cards.DeckOfCards()
            self.deck.shuffle_deck()
        curr = head
        while curr:
            curr.clear_cards()
            try:
                curr.add_card(self.deck.give_random_card())
                curr.add_card(self.deck.give_random_card())
            except IndexError:
                self.deck = deck_of_cards.DeckOfCards()
                self.deck.shuffle_deck()
                curr.add_card(self.deck.give_random_card())
                curr.add_card(self.deck.give_random_card())
            curr = curr.next
        self.new_hand()

    '''
    Draws a card. Grabs a new shuffled deck if no cards remain in the current deck
    
    :return deck_of_cards.Card drawn from deck
    '''
    def draw_card(self):
        if len(self.deck.deck) < 1:
            self.deck = deck_of_cards.DeckOfCards()
            self.deck.shuffle_deck()
        return self.deck.give_random_card()

    '''
    Adds a card to the a player's hand
    
    :param player - The player to "hit"
    '''
    def hit(self, player):
        if len(self.deck.deck) < 1:
            self.deck = deck_of_cards.DeckOfCards()
            self.deck.shuffle_deck()
        return player.add_card(self.deck.give_random_card())

    '''
    Creates a new hand for the dealer. Used at the start of a game or round
    '''
    def new_hand(self):
        self.cards = []
        self.count = 0
        for i in range(2):
            self.cards.append(self.deck.give_random_card())

    '''
    Draws a single card FOR the dealer
    '''
    def self_draw(self):
        card = self.draw_card()
        self.cards.append(card)
        if card.value > 10:
            self.count += 10
        else:
            self.count += card.value
