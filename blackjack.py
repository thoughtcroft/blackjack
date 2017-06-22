#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=redefined-builtin

"""Blackjack Game

The playing card gambling game also known as 21.
For one or many players against the computer dealer.
"""

# python2 and python3 portability
from __future__ import print_function
from builtins import input

import random
import time
from termcolor import colored, COLORS

CARD_RANK = ("A", "K", "Q", "J", "10", "9", "8", "7", "6", "5", "4", "3", "2")
CARD_SUIT = ("♡", "♢", "♧", "♤")
SYSTEM_COLORS = ['grey', 'white']
PLAYER_COLORS = list(c for c in COLORS.keys() if c not in SYSTEM_COLORS)
MAX_PLAYERS = len(PLAYER_COLORS)


class Card(object):
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
        if self.ace():
            value = 11
        else:
            try:
                value = int(self.rank)
            except ValueError:
                value = 10
        return value

    def ace(self):
        """Is this card an ace?"""
        return self.rank == "A"

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
        """Deal from the end of the deck - if the deck is empty, start a new one"""
        if not self.cards:
            self.__new_deck()
            self.shuffle()
        return self.cards.pop()


class Hand(object):
    """Represents the cards held by the player or the dealer"""

    def __init__(self, stake=0):
        self.cards = []
        self.stake = stake
        self.active = True

    def __repr__(self):
        return "  ".join(str(card) for card in self.cards)

    def first(self):
        """Returns the first card in the hand"""
        assert self.cards
        return self.cards[0]

    def last(self):
        """Returns the last card in the hand"""
        assert self.cards
        return self.cards[-1]

    def add_card(self, card):
        """Add the instance of card to the hand"""
        self.cards.append(card)

    def value(self):
        """Calculate the value of the hand, taking into account Aces can be 11 or 1"""
        aces = sum(1 for c in self.cards if c.ace())
        value = sum(c.value() for c in self.cards)
        while value > 21 and aces > 0:
            aces -= 1
            value -= 10
        return value

    def blackjack(self):
        """Determine if the hand is 'blackjack'"""
        return len(self.cards) == 2 and self.value() == 21

    def twenty_one(self):
        """Determine if the hand is worth 21"""
        return self.value() == 21

    def bust(self):
        """Determine if the hand is worth more than 21, known as a 'bust'"""
        return self.value() > 21

    def pair(self):
        """Determine if the hand is two cards the same"""
        return len(self.cards) == 2 and self.first().rank == self.last().rank

    def split(self):
        """Split this hand into two hands if it can be split"""
        assert self.pair()
        card = self.cards.pop()
        hand = Hand(self.stake)
        hand.add_card(card)
        return hand


class Player(object):
    """Represents a player or the dealer in the game"""

    def __init__(self, name, chips, color='green'):
        assert chips > 0
        assert color in PLAYER_COLORS
        self.chips = chips
        self.hands = []
        self.insurance = 0
        self.name = name
        self.color = color
        self.results = {'wins': 0, 'ties': 0, 'losses': 0}

    def can_double_down(self, hand):
        """Is the player entitled to double down?"""
        return (self.has_chips(hand.stake) and
                (len(hand.cards) == 2 or
                 hand.value() in (9, 10, 11)))

    def active_hands(self):
        """Generator of hands still active in this round"""
        for hand in self.hands:
            if hand.active:
                yield hand

    def has_active_hands(self):
        """Does the player have any active hands?"""
        return list(h for h in self.hands if h.active)

    def can_split(self, hand):
        """Is the player entitled to split their hand?"""
        return self.has_chips(hand.stake) and hand.pair()

    def has_chips(self, amount=0):
        """Does the player have sufficient chips left?"""
        assert amount >= 0
        if amount == 0:
            return self.chips > 0
        return self.chips >= amount

    def push(self, bet):
        """Player bet is preserved"""
        assert bet > 0
        self.chips += bet
        self.results['ties'] += 1

    def win(self, bet, odds=1):
        """Player wins at the odds provided"""
        assert bet > 0
        assert odds >= 1
        self.chips += int(bet * (odds + 1))
        self.results['wins'] += 1

    def loss(self):
        """Player loses their bet"""
        self.results['losses'] += 1

    def bet(self, bet):
        """Player places a bet"""
        assert bet > 0
        assert self.has_chips(bet)
        self.chips -= bet
        return bet


class Game(object):
    """Controls the actions of the game"""

    def __init__(self, names, chips):
        self.deck = Deck()
        self.deck.shuffle()
        self.colors = list(PLAYER_COLORS)
        self.players = list(Player(name, chips, self.__get_color()) for name in names)
        self.max_name_len = max(max(len(name) for name in names), len("Dealer"))
        self.playing = False
        self.dealer = None
        self.insurance = False

    def __get_color(self):
        """Obtain a random color from available termcolors"""
        assert self.colors
        colors = self.colors
        color = random.choice(colors)
        colors.remove(color)
        return color

    def __deal_card(self, name, hand, color="white", announce=True):
        """Take the next available card from deck and add to hand"""
        card = self.deck.deal()
        hand.add_card(card)
        if announce:
            time.sleep(1)
            prompt = "dealt {}  {:>2} : {}".format(card, hand.value(), hand)
            print(self.format_text(name, prompt, color))

    def __get_bet(self, player, question, minimum, multiple):
        """Ask player for their bet and check constraints on answer"""
        print()
        print(self.format_text(player.name, question.lower(), player.color))
        prompt = "{} available, {} minimum, multiples of {} only".format(
            player.chips, minimum, multiple)
        print(self.format_text(player.name, prompt, player.color))
        bet = -1
        while bet < minimum or bet > player.chips or bet % multiple != 0:
            bet = input(self.format_text(
                player.name, "enter amount ({}): ".format(minimum), player.color))
            if bet == '':
                bet = minimum
            else:
                try:
                    bet = int(bet)
                except ValueError:
                    pass
        return bet

    def format_text(self, name, text, color="white"):
        """Prefix output with player's name and colorize"""
        name = name.rjust(self.max_name_len)
        return colored("{} > {}".format(name, text), color)

    def players_with_chips(self, min=0):
        """Returns a list of players with chips remaining"""
        return list(p for p in self.players if p.has_chips(min))

    def active_players(self):
        """Generator of layers with active hands"""
        for player in self.players:
            if player.has_active_hands():
                yield player

    def has_active_hands(self):
        """Are there any active hands remaining?"""
        return list(p for p in self.players if p.has_active_hands())

    def setup(self):
        """Obtain bets and deal two cards to the player and the dealer"""
        hands = []
        self.playing = True
        min_bet = 10
        random.shuffle(self.players)
        players = self.players_with_chips(min_bet)
        if not players:
            return
        for player in players:
            bet = self.__get_bet(player, "How much would you like to bet?", min_bet, 2)
            hand = Hand(bet)
            hands.append(hand)
            player.bet(bet)
            player.hands = [hand]
        dealer = Hand(0)
        for _ in range(2):
            for hand in hands:
                self.__deal_card(_, hand, announce=False)
            self.__deal_card(_, dealer, announce=False)
        print()
        for player in players:
            hand = player.hands[0]
            prompt = "hand dealt {:>2} : {}".format(hand.value(), hand)
            print(self.format_text(player.name, prompt, player.color))
        print(self.format_text("Dealer", "face up card  : {}".format(dealer.first())))
        self.dealer = dealer

    def offer_insurance(self):
        """Offer insurance if applicable"""
        if self.dealer.first().ace():
            players = self.players_with_chips()
            for player in players:
                bet = self.__get_bet(player, "would you like to take insurance?", 0, 2)
                if bet > 0:
                    player.insurance = player.bet(bet)
                else:
                    player.insurance = 0

    def check_for_dealer_blackjack(self):
        """Check if dealer has blackjack and settle bets accordingly"""
        dealer = self.dealer
        players = self.active_players()
        if dealer.blackjack():
            self.playing = False
            print()
            print(self.format_text("Dealer", "scored blackjack : {}".format(dealer)))
            for player in players:
                for hand in player.active_hands():
                    if player.insurance:
                        print(self.format_text(
                            player.name, "you won your insurance bet!", player.color))
                        player.win(player.insurance, odds=2)
                    self.settle_outcome(dealer, player, hand)
        elif dealer.first().ace():
            print()
            print(self.format_text("Dealer", "did not score blackjack"))
            for player in players:
                if player.insurance:
                    print(self.format_text(
                        player.name, "you lost your insurance bet!", player.color))
                    player.loss()

    def check_for_player_blackjack(self):
        """Check if any player has blackjack and settle bets accordingly"""
        dealer = self.dealer
        players = self.active_players()
        for player in players:
            for hand in player.active_hands():
                if hand.blackjack():
                    print(self.format_text(player.name, "you scored blackjack!", player.color))
                    self.settle_outcome(dealer, player, hand)

    def settle_outcome(self, dealer, player, hand):
        """Decide the outcome of the player's hand compared to the dealer"""
        hand.active = False
        if hand.value() > dealer.value() or dealer.bust():
            outcome = "you beat the dealer! :)"
            if hand.blackjack():
                odds = 1.5
            else:
                odds = 1
            player.win(hand.stake, odds)
        elif hand.value() == dealer.value():
            outcome = "you tied with the dealer :|"
            player.push(hand.stake)
        else:
            outcome = "you lost to the dealer :("
            player.loss()
        print(self.format_text(player.name, outcome, player.color))

    def split_hand(self, player, hand):
        """Split player's hand if possible"""
        if hand.pair() and player.has_chips(hand.stake):
            prompt = "would you like to split your pair? (Y/n): "
            prompt = self.format_text(player.name, prompt, player.color)
            resp = get_response(prompt, ("Y", "N"), "Y")
            if resp == "Y":
                new_hand = hand.split()
                player.bet(hand.stake)
                self.__deal_card(player.name, hand, player.color)
                self.__deal_card(player.name, new_hand, player.color)
                player.hands.append(new_hand)
                self.show_hand(player.name, hand, player.color)

    def hit(self, player, hand):
        """Draw another card for player hand and determine outcome if possible"""
        self.__deal_card(player.name, hand, player.color)

    def bust(self, player, hand):
        """Handle a player's hand that has busted"""
        print(self.format_text(player.name, "busted! :(", player.color))
        player.loss()
        hand.active = False

    def double_down(self, player, hand):
        """Player wishes to double their bet and receive one more card"""
        player.bet(hand.stake)
        hand.stake += hand.stake
        self.__deal_card(player.name, hand, player.color)
        if hand.bust():
            self.bust(player, hand)


    def dealer_turn(self):
        """Controls the dealer's turn and determines the outcome of the game"""
        dealer = self.dealer
        print()
        prompt = "turns {}  {:>2} : {}".format(
            dealer.last(),
            dealer.value(),
            dealer)
        print(self.format_text("Dealer", prompt))
        while dealer.value() < 17:
            self.__deal_card("Dealer", dealer)
        if dealer.bust():
            print(self.format_text("Dealer", "busted!"))
        for player in self.active_players():
            for hand in player.active_hands():
                self.settle_outcome(dealer, player, hand)

    def results(self):
        """Print player statistics"""
        print()
        players = sorted(self.players, key=lambda x: x.chips, reverse=True)
        for player in players:
            results = ",  ".join("{}: {:>2}".format(k, v) for k, v in player.results.items())
            prompt = "chips: {:>3},  {}".format(player.chips, results)
            print(self.format_text(player.name, prompt, player.color))

    def show_hand(self, name, hand, color="white"):
        """Print player's current hand"""
        print()
        prompt = "hand value {:>2} : {}".format(hand.value(), hand)
        print(self.format_text(name, prompt, color))

    def play_hand(self, player, hand):
        """Play the hand until finished"""
        self.show_hand(player.name, hand, player.color)
        if player.can_split(hand):
            self.split_hand(player, hand)

        while hand.active:
            if hand.twenty_one():
                print(self.format_text(player.name, "scored 21! :)", player.color))
                break
            if hand.bust():
                self.bust(player, hand)
                break
            if player.can_double_down(hand):
                question = "would you like to hit, stand or double down? (H/s/d): "
                answers = ('H', 'S', 'D')
            else:
                question = "would you like to hit or stand? (H/s): "
                answers = ('H', 'S')

            prompt = self.format_text(player.name, question, player.color)
            resp = get_response(prompt, answers, default='H')
            if resp == 'H':
                if self.hit(player, hand):
                    break
            elif resp == 'S':
                break
            elif resp == 'D':
                self.double_down(player, hand)
                break
            else:
                # should never get here!
                raise ValueError

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
where you and others can play against the
computer dealer.

There is one 52 pack of cards in the deck
and the rules are documented here*. Purely
for fun, the game tracks your results and
and reports them at the conclusion.

* https://en.wikipedia.org/wiki/Blackjack
    """)

    # collect names of the players and their starting chip balance
    # then cycle through game process:
    # - deal initial cards
    # - offer insurance if dealer up card is A
    # - check dealer blackjack and announce results if true
    # - then for each player:
    #   - for each hand
    #       - offer split, double down, hit or stand as appropriate
    #       - if player busts, mark as finished and move to next
    # - then dealer plays until busts or stands
    # - show results and settle bets
    # -> repeat
    # when game is complete show results for each player

    # collect names of the players and their starting chip balance
    print()
    while True:
        prompt = "Enter up to {} player names or return for single player game: ".format(MAX_PLAYERS)
        names = input(prompt)
        if names == '':
            names = ["Player"]
        else:
            names = names.split(' ')
        if len(names) > MAX_PLAYERS:
            print("Maximum of {} players only please!".format(MAX_PLAYERS))
        else:
            break

    print()
    chips = input("Enter starting number of chips (100): ")
    if chips == '':
        chips = 100
    else:
        chips = int(chips)
    game = Game(names, chips)

    # then cycle through game process:
    try:
        while True:
            print()
            input("Hit enter to continue - ctrl-c to exit: ")
            clear_screen()
            if not game.players_with_chips(10):
                print("No one with any chips remaining - game over")
                break

            # - collect initial bets and deal cards
            game.setup()

            # - offer insurance if dealer up card is an Ace
            game.offer_insurance()

            # - if anyone has blackjack announce results
            game.check_for_dealer_blackjack()
            game.check_for_player_blackjack()
            if game.playing:

                # - then for each player's hand:
                for player in game.active_players():
                    for hand in player.active_hands():
                        game.play_hand(player, hand)

                # - then dealer plays until busts or stands
                if game.has_active_hands():
                    game.dealer_turn()

    except KeyboardInterrupt:
        print()
    finally:
        game.results()
        print()
        print("Thanks for playing.")
        print()


if __name__ == '__main__':
    main()
