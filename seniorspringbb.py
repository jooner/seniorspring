#!/usr/bin/env python

import sys

from gsp import GSP
import math
from math import pi
from util import argmax_index

class seniorspringbb:
    """Balanced bidding agent"""
    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget

    def initial_bid(self, reserve):
        return self.value / 2
        """ Why is the intial bid self.value / 2? """


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


    def expected_utils(self, t, history, reserve):
        """
        Figure out the expected utility of bidding such that we win each
        slot, assuming that everyone else keeps their bids constant from
        the previous round.

        returns a list of utilities per slot.
        """
        # TODO: Fill this in
        prev_round = history.round(t-1)
        c1 = round(30*math.cos(pi*t/24)+50)  # Number of clicks for the top position)


        info = self.slot_info(t, history, reserve)

        min_bids = []
        slot_ids = []

        for x in range(0, len(info)):
            min_bids.append(info[x][1])
            slot_ids.append(info[x][0])

        """calculate position factors = p"""
    
        """For some reason we don't calculate the number of clicks by ourself?
        but instead take the number of clicks from last round? Makes no sense to me.

        clicks = [] #Number of clicks for each spot positions

        for i in range(0, len(slot_ids)):
            clicks.append(round(c1*pow(0.75, i))) 
            """

        clicks = prev_round.clicks

        #calculate utilities = [value per click - (min_bid per click)]*number of clicks


        utilities = [(self.value-b)*c for b,c in zip(min_bids, clicks)]
    
        return utilities

    def target_slot(self, t, history, reserve):
        """Figure out the best slot to target, assuming that everyone else
        keeps their bids constant from the previous rounds.

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
        
        """ epsilon is added because if the bid equals exactly the min_bid, 
        the winner is determined randomly. Epsilon ensures that agent wins the 
        slot"""

        epsilon = 0.0000000000000000000000000000000000000001

        # TODO: Fill this in.
        #If going for the top:

        #top slot_id = 0

        if slot == 0: 
            return self.value
        #If not expecting to win (p_k* > w_i), then bid w_i in this period
        elif min_bid + epsilon > self.value: 
            return self.value

        else: 
            bid = self.value - epsilon - int(0.75*(self.value - min_bid)) # change this
        
    
        return bid

    def __repr__(self):
        return "%s(id=%d, value=%d)" % (
            self.__class__.__name__, self.id, self.value)


