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


class Bank(object):
    """Represents the player's betting pool of money"""

    def __init__(self, chips=100):
        self.chips = chips
        self.wager = 0
        self.insurance = 0

    def bet(self, amount, insurance=False):
        """Place a bet, must have this many chips remaining or raises ValueError exception"""
        if amount > self.chips:
            raise ValueError("""
            You can't bet {}. You only have {} chips remaining!
            """.format(amount, self.chips))
        self.chips -= amount
        if insurance:
            self.insurance += amount
        else:
            self.wager += amount

    def win(self, odds=1, insurance=False):
        """Succcessful bet: increments chips by wager at odds"""
        if insurance:
            self.chips += int(self.insurance * (1 + odds))
            self.insurance = 0
        else:
            self.chips += int(self.wager * (1 + odds))
            self.wager = 0

    def loss(self, insurance=False):
        """Unsuccessful bet: set wager to zero"""
        if insurance:
            self.insurance = 0
        else:
            self.wager = 0

    def push(self):
        """Bet is nullified, return chips to the bank"""
        self.chips += self.wager
        self.wager = 0

    def double_down(self):
        """Player can double their existing bet"""
        self.bet(self.wager)


class Play(object):
    """Controls the flow of the game"""

    def __init__(self):
        self.bank = Bank()
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
            print("> dealt {}  for {:>2} : {}".format(card, hand.value(), hand))

    def push(self):
        """Player bet is preserved"""
        self.bank.push()
        self.results['ties'] += 1

    def win(self, odds=1):
        "Player wins at the odds provided"""
        self.bank.win(odds)
        self.results['wins'] += 1

    def loss(self):
        """Player loses their bet"""
        self.bank.loss()
        self.results['losses'] += 1

    def insolvent(self):
        """Does the player have any chips left?"""
        return self.bank.chips <= 0

    def double_down_available(self):
        """Player is entitled to double down their initial bet"""
        return self.bank.chips >= self.bank.wager and len(self.player.cards) == 2

    def setup(self):
        """Deal two cards to the player and the dealer and check for blackjack"""
        bet = 0
        while bet <= 0 or bet > self.bank.chips or bet % 2 != 0:
            print("You have {} chips available".format(self.bank.chips))
            bet = input("How much do you want to bet (even numbers only)? (10): ")
            if bet == '':
                bet = 10
            else:
                bet = int(bet)
        self.bank.bet(bet)
        self.player = Hand()
        self.dealer = Hand()
        for _ in range(2):
            self.__deal_card(self.player, False)
            self.__deal_card(self.dealer, False)
        print()
        print("Player was dealt {:>2} : {}".format(self.player.value(), self.player))
        print("Dealer's first card : {}   ??".format(self.dealer.cards[0]))

        if self.dealer.cards[0].rank == "A":
            print()
            while True:
                try:
                    bet = input("How much do you want to bet on insurance? (0): ")
                    if bet == '':
                        bet = 0
                    else:
                        bet = int(bet)
                    break
                except ValueError:
                    pass

            if bet > 0:
                self.bank.bet(bet, insurance=True)

        if not(self.player.blackjack() or self.dealer.blackjack()):
            # no-one has won initially
            self.playing = True
        elif self.player.blackjack():
            if self.dealer.blackjack():
                print("Dealer checks card  : {}".format(self.dealer))
                print()
                print("Both hands are blackjack - it's a tie")
                self.push()
            else:
                print()
                print("Player wins with blackjack!")
                self.win(1.5)
        elif self.dealer.blackjack():
            print("Dealer checks card  : {}".format(self.dealer))
            print()
            print("Dealer wins with blackjack!")
            self.loss()

        if self.bank.insurance > 0:
            print()
            if self.dealer.blackjack():
                print("Insurance pays out!")
                self.bank.win(ratio=2, insurance=True)
            else:
                print("Insurance did not pay out")
                self.bank.loss(insurance=True)

    def hit(self, stand=False):
        """Draw another card for the player and determine the outcome if possible"""
        self.__deal_card(self.player)
        if self.player.twenty_one():
            print()
            print("Player scored 21! :)")
            self.stand()
        elif self.player.bust():
            print()
            print("Player busted! :(")
            self.loss()
            self.playing = False
        elif stand:
            print()
            self.stand()

    def stand(self):
        """Controls the dealer's turn and determines the outcome of the game"""
        print("Dealer's turn...")
        print()
        print("> turns {}  for {:>2} : {}".format(
            self.dealer.cards[-1],
            self.dealer.value(),
            self.dealer))
        while self.dealer.value() < 17:
            self.__deal_card(self.dealer)

        dealer_value = self.dealer.value()
        player_value = self.player.value()
        print()
        if self.dealer.bust():
            print("Dealer busted - player wins :)")
            self.win()
        elif dealer_value < player_value:
            print("Player wins :)")
            self.win()
        elif dealer_value == player_value:
            print("Dealer has same value as Player - it's a tie")
            self.push()
        elif dealer_value > player_value:
            print("Dealer wins :(")
            self.loss()
        self.playing = False

    def double_down(self):
        """The player doubles their bet and draws one more card"""
        self.bank.double_down()
        self.hit(stand=True)

def clear_screen():
    """Clear the screen before starting a new round"""
    print("\033[H\033[J")

def get_response(question, accepted, default):
    """Get input that matches the accepted answers"""
    while True:
        resp = input(question).upper()
        if resp == '':
            resp = default
        if resp in accepted:
            break
    return resp

def main():
    """Run the main game loop"""
    clear_screen()
    print("""
          Welcome to Blackjack!
          ---------------------

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
            if play.insolvent():
                break
            input("Hit enter to continue - ctrl-c to exit: ")
            clear_screen()
            play.setup()

            while play.playing:
                print()
                if play.double_down_available():
                    question = "Would you like to hit, stand or double down? (H/s/d): "
                    answers = ('H', 'S', 'D')
                else:
                    question = "Would you like to hit or stand? (H/s): "
                    answers = ('H', 'S')
                resp = get_response(question, answers, default='H')
                print()
                if resp == 'H':
                    play.hit()
                elif resp == 'S':
                    play.stand()
                elif resp == 'D':
                    play.double_down()
                else:
                    raise ValueError
            print()

    except KeyboardInterrupt:
        print()
    finally:
        print("Your bank balance: {}".format(play.bank.chips))
        print()
        print("Your results were: {}".format(play.results))
        print()
        print("Thanks for playing.")
        print()

if __name__ == '__main__':
    main()
