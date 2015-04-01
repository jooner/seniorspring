#!/usr/bin/env python

import sys

from gsp import GSP
from util import argmax_index
import math
import pi from math

class seniorspringbudget:
    """Balanced bidding agent"""
    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget

    def initial_bid(self, reserve):
        return self.value / 2


    def slot_info(self, t, history, reserve):
        """Compute the following for each slot, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns list of tuples [(slot_id, min_bid, max_bid)], where
        min_bid is the bid needed to tie the other-agent bid for that slot
        in the last round.  If slot_id = 0, max_bid is 2* min_bid.
        Otherwise, it's the next highest min_bid (so bidding between min_bid
        and max_bid would result in ending up in that slot)
        """
        prev_round = history.round(t-1)

        other_bids = filter(lambda (a_id, b): a_id != self.id, prev_round.bids)

        clicks = prev_round.clicks
        def compute(s):
            (min, max) = GSP.bid_range_for_slot(s, clicks, reserve, other_bids)
            if max == None:
                max = 2 * min
            return (s, min, max)
            
        info = map(compute, range(len(clicks)))
#        sys.stdout.write("slot info: %s\n" % info)
        return info

    def expected_utils(self, t, bid, reserve):
        
        """take as input a list of projected bids for next round and calculate 
        total utility of each slot given budget constraint assuming bids will stay constant"""

        """
        Figure out the expected utility of bidding such that we win each
        slot, assuming that everyone else keeps their bids constant from
        the previous round.

        returns a list of utilities per slot.
        """
        
        min_bids, clicks_topspot, clicks = [], [], []

        for i in range(t, 48):
            clicks_topspot.append(round(30*math.cos(pi*t/24)+50))

        info = self.slot_info(t, history, reserve)

        for x in range(0, len(info))
            min_bids.append(info[x][1])
            clicks.append(round(clicks_topspot[t]*pow(0.75, x)))

        #utilities_this_round =  [(self.value - b) * c for b, c in zip(min_bids, clicks)]
        
        utilites_total = [0 in range(0, len(info))]

        cost_total = [0 in range(0, len(info))]

        for x in range(t, 48):
            clicks = []
            utilities_this_round = []
            cost_this_round = []

            for y in range(0, len(info)):
                clicks.append(round(clicks_topspot[t]*pow(0.75, y)))
            
            utilities_this_round = [(self.value - b) * c for b, c in zip(min_bids, clicks)]
            cost_this_round = [b*c for b,c in zip(min_bids, clicks)]

            utilities_total = [a+b for a, b in zip(utilities_total, utilites_this_round)]
            cost_total = [a+b for a, b in zip(cost_total, cost_this_round)]

        return zip(utilities_total, cost_total)

    def target_slot(self, t, history, reserve):
        """Figure out the best slot to target, assuming that everyone else
        keeps their bids the same as this round. The best slot to target should be the one that maximizes the
        total utility over the entire period while not going over budget

        Returns (slot_id, min_bid, max_bid), where min_bid is the bid needed to tie
        the other-agent bid for that slot in the last round.  If slot_id = 0,
        max_bid is min_bid * 2
        """
        i =  argmax_index(self.expected_utils(t, history, reserve))
        info = self.slot_info(t, history, reserve)
        return info[i]

    def bid(self, t, history, reserve):
        # The Balanced bidding strategy (BB) is the strategy for a player j that, given
        # bids b_{-j},
        # - targets the slot s*_j which maximizes his utility, that is,
        # s*_j = argmax_s {clicks_s (v_j - p_s(j))}.
        # - chooses his bid b' for the next round so as to
        # satisfy the following equation:
        # clicks_{s*_j} (v_j - p_{s*_j}(j)) = clicks_{s*_j-1}(v_j - b')
        # (p_x is the price/click in slot x)
        # If s*_j is the top slot, bid the value v_j

        prev_round = history.round(t-1)
        (slot, min_bid, max_bid) = self.target_slot(t, history, reserve)

        # TODO: Fill this in.
        bid = 0  # change this
        if min_bid >= self.value or slot == 0:
            return self.value
        # not going for the top
        else:
            return self.value - (float(clicks[slot]) / clicks[slot - 1]) * (self.value - min_bid)


    def __repr__(self):
        return "%s(id=%d, value=%d)" % (
            self.__class__.__name__, self.id, self.value)


