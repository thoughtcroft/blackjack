#!/usr/bin/env python
# -*- coding: utf-8 -*-
#pylint: disable=redefined-builtin

"""Black Jack Game

"""

# python2 and python3 portability
from __future__ import print_function
from builtins import input
import random
import sys

CARD_RANK = ("A", "K", "Q", "J", "10", "9", "8", "7", "6", "5", "4", "3", "2")
CARD_SUIT = ("H", "D", "C", "S")

class Card(object):
    """Represents an individual playing card"""

    def __init__(self, rank, suit):
        assert rank in CARD_RANK
        self.rank = rank
        assert suit in CARD_SUIT
        self.suit = suit

    def __repr__(self):
        return "{}-{}".format(self.rank, self.suit)

    def value(self):
        try:
            if self.rank == "A":
                return 11
            else:
                return int(self.rank)
        except ValueError:
            return 10


class Deck(object):
    """Represents deck of 52 cards to be dealt to the player and dealer"""

    def __init__(self):
        self.cards = list(Card(r, s) for r in CARD_RANK for s in CARD_SUIT)

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()


class Hand(object):
    """Represents the cards held by the player or the dealer"""

    def __init__(self):
        self.cards = []

    def __repr__(self):
        return " ".join(str(card) for card in self.cards)

    def add_card(self, card):
        self.cards.append(card)

    def blackjack(self):
        return len(self.cards) == 2 and self.value() == 21

    def natural(self):
        return self.value() == 21

    def bust(self):
        return self.value() > 21

    def show(self):
        print("-> hand {}: {}".format(self.value(), self))


    def value(self):
        aces = sum(1 for c in self.cards if c.rank == "A")
        value = sum(c.value() for c in self.cards)
        while value > 21 and aces > 0:
            aces -= 1
            value -= 10
        return value


class Play(object):
    """Controls the flow of the game"""

    def __init__(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.results = {'wins': 0, 'ties': 0, 'losses': 0}
        self.playing = False

    def __deal_card(self, hand, announce_move=True):
        card = self.deck.deal()
        hand.add_card(card)
        if announce_move:
            print("-> card {}".format(card))

    def setup(self):
        self.player = Hand()
        self.dealer = Hand()
        for _ in range(2):
            self.__deal_card(self.player, False)
            self.__deal_card(self.dealer, False)
        print("Player initial deal: ", str(self.player))
        print("Dealer face-up card: ", self.dealer.cards[0])

        if not(self.player.blackjack() or self.dealer.blackjack()):
            # no-one has won initially, so play the game
            self.playing = True
        elif self.player.blackjack():
            if self.dealer.blackjack():
                print("Both hands are blackjack - it's a tie")
                self.results['ties'] += 1
            else:
                print("Player wins with blackjack!")
                self.results['wins'] += 1
        elif self.dealer.blackjack():
                print("Dealer wins with blackjack!")
                self.results['losses'] += 1

    def games(self):
        return sum(results.values())

    def hit(self):
        self.__deal_card(self.player)
        if self.player.natural():
            print("Player scored 21! :)")
            self.stand()
        elif self.player.bust():
            print("Player busted! :(")
            self.results['losses'] += 1
            playing = False

    def stand(self):
        print("Dealer's turn...")
        while True:
            if self.dealer.bust():
                print("Dealer busted - player wins! :(")
                self.results['wins'] += 1
                break
            elif self.dealer.value() > self.player.value():
                print("Dealer wins :(")
                self.results['losses'] += 1
                break
            elif self.dealer.value() == self.player.value():
                print("Dealer has same value as Player - it's a tie")
                self.results['ties'] += 1
                break
            else:
                self.__deal_card(self.dealer)
        playing = False


def main():
    """Run the main game loop"""

    print("""
    Welcome to Black Jack!
    ----------------------

    These are some instructions...
    """)

    play = Play()

    while True:
        play.setup()

        while play.playing:
            print("Player: would you like to 'hit'?")
            if input('> ').lower == 'y':
                play.hit()
            else:
                play.stand()

        print("Would you like to keep playing?")
        if input('> ').lower != 'y':
            break

    print("Thanks for playing. Your results were: {}".format(play.results))

if __name__ == '__main__':
    main()
