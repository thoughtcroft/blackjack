#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=redefined-builtin

"""Blackjack Game

The playing card gambling game also known as 21.
For one player against the computer dealer.
"""

# python2 and python3 portability
from __future__ import print_function
from builtins import input

import random
import time

CARD_RANK = ("A", "K", "Q", "J", "10", "9", "8", "7", "6", "5", "4", "3", "2")
CARD_SUIT = ("♡", "♢", "♧", "♤")

class Card(object):  # pylint: disable=too-few-public-methods
    """Represents an individual playing card"""

    def __init__(self, rank, suit):
        assert rank in CARD_RANK
        self.rank = rank
        assert suit in CARD_SUIT
        self.suit = suit

    def __repr__(self):
        return "{:>2}{}".format(self.rank, self.suit)

    def value(self):
        """Computes the value of a card according to Blackjack rules"""
        try:
            if self.rank == "A":
                value = 11
            else:
                value = int(self.rank)
        except ValueError:
            value = 10
        return value


class Deck(object):
    """Represents deck of 52 cards to be dealt to the player and dealer"""

    def __init__(self):
        self.__new_deck()

    def __new_deck(self):
        """Create a new deck of 52 cards"""
        self.cards = list(Card(r, s) for r in CARD_RANK for s in CARD_SUIT)

    def shuffle(self):
        """Randomly shuffle the deck of cards"""
        random.shuffle(self.cards)

    def deal(self):
        """Deal from the end of the deck - if it's the last card, start a new deck"""
        while True:
            try:
                card = self.cards.pop()
                break
            except IndexError:
                self.__new_deck()
                self.shuffle()
        return card


class Hand(object):
    """Represents the cards held by the player or the dealer"""

    def __init__(self):
        self.cards = []

    def __repr__(self):
        return "  ".join(str(card) for card in self.cards)

    def add_card(self, card):
        """Add the instance of card to the hand"""
        self.cards.append(card)

    def blackjack(self):
        """Determine if the hand is 'blackjack'"""
        return len(self.cards) == 2 and self.value() == 21

    def twenty_one(self):
        """Determine if the hand is worth 21"""
        return self.value() == 21

    def bust(self):
        """Determine if the hand is worth more than 21, known as a 'bust'"""
        return self.value() > 21

    def value(self):
        """Calculate the value of the hand, taking into account Aces can be 11 or 1"""
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
        self.player = None
        self.dealer = None

    def __deal_card(self, hand, announce_move=True):
        card = self.deck.deal()
        hand.add_card(card)
        if announce_move:
            time.sleep(1)
            print("> dealt {}  for {:>2}: {}".format(card, hand.value(), hand))

    def setup(self):
        """Deal two cards to the player and the dealer and check for blackjack"""
        self.player = Hand()
        self.dealer = Hand()
        for _ in range(2):
            self.__deal_card(self.player, False)
            self.__deal_card(self.dealer, False)
        print()
        print("Player initial deal: {}".format(self.player))
        print("Dealer initial deal: {}   ??".format(self.dealer.cards[0]))

        if not(self.player.blackjack() or self.dealer.blackjack()):
            # no-one has won initially, so play the game
            self.playing = True
        elif self.player.blackjack():
            if self.dealer.blackjack():
                print("Dealer checks cards: {}".format(self.dealer))
                print("Both hands are blackjack - it's a tie")
                self.results['ties'] += 1
            else:
                print("Player wins with blackjack!")
                self.results['wins'] += 1
        elif self.dealer.blackjack():
            print("Dealer checks cards: {}".format(self.dealer))
            print("Dealer wins with blackjack!")
            self.results['losses'] += 1

    def hit(self):
        """Draw another card for the player and determine the outcome if possible"""
        self.__deal_card(self.player)
        if self.player.twenty_one():
            print("> Player scored 21! :)")
            self.stand()
        elif self.player.bust():
            print("> Player busted! :(")
            self.results['losses'] += 1
            self.playing = False

    def stand(self):
        """Controls the dealer's turn and determines the outcome of the game"""
        print("Dealer's turn...")
        print("> turns {}  for {:>2}: {}".format(
            self.dealer.cards[-1],
            self.dealer.value(),
            self.dealer))
        while self.dealer.value() < 17:
            self.__deal_card(self.dealer)

        dealer_value = self.dealer.value()
        player_value = self.player.value()
        if self.dealer.bust():
            print("> Dealer busted - player wins :)")
            self.results['wins'] += 1
        elif dealer_value < player_value:
            print("> Player wins :)")
            self.results['wins'] += 1
        elif dealer_value == player_value:
            print("> Dealer has same value as Player - it's a tie")
            self.results['ties'] += 1
        elif dealer_value > player_value:
            print("> Dealer wins :(")
            self.results['losses'] += 1
        self.playing = False


def clear_screen():
    """Clear the screen before starting a new round"""
    print("\033[H\033[J")

def main():
    """Run the main game loop"""

    print("""
    Welcome to Blackjack!
    ----------------------

    This is the gambling game also known as 21
    where you play against the computer dealer.

    There is one 52 pack of cards in the deck
    and the rules are documented here*. Purely
    for fun, the game tracks your results and
    and reports them at the conclusion.

    * https://en.wikipedia.org/wiki/Blackjack
    """)

    play = Play()

    try:
        while True:
            input("Hit any key to continue")
            clear_screen()
            print("<--- new round, ctrl-c to exit --->")
            play.setup()

            while play.playing:
                print()
                resp = input("Player would you like to 'hit'? (Y/n): ").upper()
                print()
                if resp in ('Y', ''):
                    play.hit()
                else:
                    play.stand()
            print()

    except KeyboardInterrupt:
        print()
    finally:
        print()
        print("Your results were: {}".format(play.results))
        print()
        print("Thanks for playing.")
        print()

if __name__ == '__main__':
    main()
