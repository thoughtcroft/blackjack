# -*- coding: utf-8 -*-

from __future__ import print_function
import unittest
import sys
from blackjack import Card
from blackjack import Deck
from blackjack import Hand
from blackjack import Play

class CardTestCase(unittest.TestCase):
    """Unit tests for Blackjack Card class"""

    def test_card_representation(self):
        """Is card representation correct?"""
        card = Card("A", "♡")
        self.assertEqual(str(card), "A♡")

    def test_value_of_card(self):
        """Does card return correct value?"""
        card = Card("5", "♡")
        self.assertEqual(card.value(), 5)
        card = Card("A", "♡")
        self.assertEqual(card.value(), 11)
        card = Card("J", "♡")
        self.assertEqual(card.value(), 10)


class DeckTestCase(unittest.TestCase):
    """Unit tests for Blackjack Deck class"""

    def test_size_of_deck(self):
        """Are there 52 cards in the deck?"""
        deck = Deck()
        self.assertEqual(len(deck.cards), 52)

    def test_shuffle_randomizes_deck(self):
        """Does the deck get shuffled?"""
        deck = Deck()
        card1 = deck.cards[0]
        deck.shuffle()
        card2 = deck.cards[0]
        self.assertIsNot(card1, card2)

    def test_deal_removes_a_card(self):
        """Does a deal remove one card from the deck?"""
        deck = Deck()
        num_before = len(deck.cards)
        deck.deal()
        num_after = len(deck.cards)
        self.assertEqual(num_before, num_after + 1)


class HandTestCase(unittest.TestCase):
    """Unit tests for Blackjack Hand class"""

    def test_hand_representation(self):
        """Is hand representation correct?"""
        hand = Hand()
        hand.add_card(Card("A", "♡"))
        hand.add_card(Card("5", "♡"))
        self.assertEqual(str(hand), "A♡  5♡")

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

    def test_bust_detected(self):
        """Does a 'bust' get detected correctly?"""
        hand = Hand()
        hand.add_card(Card("J", "♡"))
        hand.add_card(Card("5", "♡"))
        self.assertFalse(hand.bust())
        hand.add_card(Card("10", "♡"))
        self.assertTrue(hand.bust())


if __name__ == '__main__':
    unittest.main()
