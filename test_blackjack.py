#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import unittest

from blackjack import *


class CardTestCase(unittest.TestCase):
    """Unit tests for Blackjack Card class"""

    def test_card_validity(self):
        """Only valid cards can be created"""
        card = Card("3","♡")
        with self.assertRaises(AssertionError):
            card = Card("13","♡")
        with self.assertRaises(AssertionError):
            card = Card("A", "x")

    def test_card_representation(self):
        """Is card representation correct?"""
        card = Card("A", "♡")
        self.assertEqual(str(card), " A♡")
        card = Card("10", "♡")
        self.assertEqual(str(card), "10♡")

    def test_value_of_card(self):
        """Does card return correct value?"""
        card = Card("5", "♡")
        self.assertEqual(card.value(), 5)
        card = Card("A", "♡")
        self.assertEqual(card.value(), 11)
        card = Card("J", "♡")
        self.assertEqual(card.value(), 10)

    def test_card_is_ace(self):
        """Is an Ace recognised correctly?"""
        card = Card("A", "♡")
        self.assertTrue(card.ace())
        card = Card("8", "♡")
        self.assertFalse(card.ace())


class DeckTestCase(unittest.TestCase):
    """Unit tests for Blackjack Deck class"""

    def test_size_of_deck(self):
        """Are there 52 cards in the deck?"""
        deck = Deck()
        self.assertEqual(len(deck.cards), 52)

    def test_shuffle_randomizes_deck(self):
        """Does the deck get shuffled?"""
        deck_one = Deck()
        deck_one.shuffle()
        deck_two = Deck()
        deck_two.shuffle()
        self.assertNotEqual(str(deck_one), str(deck_two))

    def test_deal_removes_a_card(self):
        """Does a deal remove one card from the deck?"""
        deck = Deck()
        num_before = len(deck.cards)
        deck.deal()
        num_after = len(deck.cards)
        self.assertEqual(num_before, num_after + 1)

    def test_deal_returns_a_card(self):
        """Does calling deal return a card?"""
        deck = Deck()
        self.assertIsInstance(deck.deal(), Card)

    def test_empty_deck_refills(self):
        """Does an empty deck get refilled?"""
        deck = Deck()
        deck.cards = []
        deck.deal()
        self.assertEqual(len(deck.cards), 51)


class HandTestCase(unittest.TestCase):
    """Unit tests for Blackjack Hand class"""

    def test_hand_representation(self):
        """Is hand representation correct?"""
        hand = Hand()
        hand.add_card(Card("A", "♡"))
        hand.add_card(Card("5", "♡"))
        self.assertEqual(str(hand), " A♡   5♡")

    def test_does_a_new_card_get_added(self):
        """Does a new dealt card end up in the hand?"""
        hand = Hand()
        card = Card("A", "♡")
        num_before = len(hand.cards)
        hand.add_card(card)
        num_after = len(hand.cards)
        self.assertEqual(num_after, num_before + 1)
        self.assertIs(hand.cards[-1], card)

    def test_calculates_points_correctly(self):
        """Does the value of the hand calculate correctly?"""
        hand = Hand()
        hand.add_card(Card("A", "♡"))
        hand.add_card(Card("5", "♡"))
        self.assertEqual(hand.value(), 16)
        hand.add_card(Card("A", "♡"))
        self.assertEqual(hand.value(), 17)
        hand.add_card(Card("7", "♡"))
        self.assertEqual(hand.value(), 14)

    def test_blackjack_detected(self):
        """Does 'blackjack' get detected correctly?"""
        hand = Hand()
        hand.add_card(Card("A", "♡"))
        hand.add_card(Card("J", "♡"))
        self.assertTrue(hand.blackjack())
        hand.add_card(Card("10", "♡"))
        self.assertFalse(hand.blackjack())

    def test_twenty_one_detected(self):
        """Does 'twenty one' get detected correctly?"""
        hand = Hand()
        hand.add_card(Card("A", "♡"))
        hand.add_card(Card("5", "♡"))
        self.assertFalse(hand.twenty_one())
        hand.add_card(Card("5", "♡"))
        self.assertTrue(hand.twenty_one())

    def test_bust_detected(self):
        """Does a 'bust' get detected correctly?"""
        hand = Hand()
        hand.add_card(Card("J", "♡"))
        hand.add_card(Card("5", "♡"))
        self.assertFalse(hand.bust())
        hand.add_card(Card("10", "♡"))
        self.assertTrue(hand.bust())

    def test_split_hand(self):
        """Does a split work for splittable hand?"""
        card = Card("J", "♡")
        hand_one = Hand()
        hand_one.add_card(card)
        hand_one.add_card(card)
        hand_one.add_card(Card("5", "♢"))
        with self.assertRaises(AssertionError):
            hand_one.split()
        hand_one.cards.pop()
        hand_two = hand_one.split()
        self.assertIsInstance(hand_two, Hand)
        self.assertTrue(str(hand_one) == str(hand_two))


class PlayerTestCase(unittest.TestCase):
    """Unit tests for the Blackjack Player class"""

    def test_player_has_chips(self):
        """Does the player report chips left correctly?"""
        player = Player("Wazza", 100)
        self.assertTrue(player.has_chips())
        self.assertFalse(player.has_chips(150))
        player.chips = 0
        self.assertFalse(player.has_chips())

    def test_player_can_bet(self):
        """Is the player able to record a bet?"""
        player = Player("Wazza", 100)
        bet = player.bet(10)
        self.assertEqual(bet, 10)
        self.assertEqual(player.chips, 90)

    def test_player_is_able_to_double_down(self):
        """Does the player report double down is possible correctly?"""
        player = Player("Wazza", 100)
        hand = Hand(50)
        hand.add_card(Card("5", "♢"))
        hand.add_card(Card("2", "♢"))
        self.assertTrue(player.can_double_down(hand))
        player.chips = 0
        self.assertFalse(player.can_double_down(hand))
        player.chips = 100
        hand.add_card(Card("2", "♢"))
        self.assertTrue(player.can_double_down(hand))
        hand.add_card(Card("5", "♢"))
        self.assertFalse(player.can_double_down(hand))

    def test_player_can_split_hand(self):
        """Is a splitting a  hand possible?"""
        player = Player("Wazza", 100)
        hand = Hand(50)
        hand.add_card(Card("J", "♡"))
        hand.add_card(Card("5", "♢"))
        self.assertFalse(player.can_split(hand))
        hand.add_card(Card("J", "♡"))
        self.assertFalse(player.can_split(hand))
        hand.cards.pop()
        hand.cards.pop()
        hand.add_card(Card("J", "♡"))
        self.assertTrue(player.can_split(hand))
        player.chips = 0
        self.assertFalse(player.can_split(hand))

    def test_player_wins_bet(self):
        """Does the player record wins correctly?"""
        player = Player("Wazza", 100)
        player.win(10, 1.5)
        self.assertTrue(player.chips, 115)
        self.assertTrue(player.results['wins'], 1)

    def test_player_loses_bet(self):
        """Does the player record losses correctly?"""
        player = Player("Wazza", 100)
        player.loss()
        self.assertTrue(player.chips, 100)
        self.assertTrue(player.results['losses'], 1)

    def test_player_pushes_bet(self):
        """Does the player record pushes correctly?"""
        player = Player("Wazza", 100)
        player.push(10)
        self.assertTrue(player.chips, 110)
        self.assertTrue(player.results['ties'], 1)


if __name__ == '__main__':
    unittest.main()
