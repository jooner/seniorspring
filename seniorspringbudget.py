#!/usr/bin/env python

import sys

from gsp import GSP
from util import argmax_index
from math import pi, cos
from random import randint

# aggressive factor for projection (overestimating other agents' bids)
AGG_FACT = float(1.001)

class seniorspringbudget:
    """Balanced bidding agent"""
    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget

    def initial_bid(self, reserve):
        return self.value / 2

    def click_calc(self, history, t):
        """
        Now we actually calculate the clicks per round instead of naively assuming
        it will remain constant
        """
        payment_record = history.round(t-1).slot_payments
        c1 = round(30 * cos(pi * t / 24) + 50)
        return [c1 * pow(0.75, y) for y in range (0, len(payment_record))]

    def bid_predictor(self, history, t):
        """
        Instead of naively assuming bids will remain constant, we estimate
        what their next move might be based on their cumulative history and budget
        """
        BUDGET = self.budget #since self.budget does not get updated, BUDGET is the same for all agents
        n_agents = history.n_agents
        others_budget = [BUDGET - history.agents_spent[i] for i in range(0, n_agents)]
        del others_budget[self.id]
        prev1 = filter(lambda (a_id, b): a_id != self.id, history.round(t-1).bids)
        if t > 1:
            projected_bid = []
            prev2 = filter(lambda (a_id, b): a_id != self.id, history.round(t-2).bids)
            for i in range(0, n_agents - 1):
                if others_budget[i] > 0:
                    # b1 is the most recent, b2 is the bid before
                    b1, b2 = prev1[i][1], prev2[i][1]
                    # If an agent's most recent 2 bids remain constant,
                    # we assume the bid will remain constant
                    if round(b1) == round(b2):
                        next_bid = b1
                    # if the bid increased, we project that it will increase again
                    else:
                        r = randint(0, 2)
                        if r == 0:
                            next_bid = b1
                        else:
                            next_bid = b1 * (1 + (b2 - b1) / b2)
                        #print("DIFF {} {}".format(next_bid, b1))
                else:
                    # Agents who have exhausted their budget will bid 0
                    next_bid = 0
                projected_bid.append((i + 1, next_bid))
        else:
            projected_bid = prev1
        #print("prev: {}".format(prev1))
        #print("proj: {}".format(projected_bid))
        return projected_bid


    def slot_info(self, t, history, reserve):
        """Compute the following for each slot, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns list of tuples [(slot_id, min_bid, max_bid)], where
        min_bid is the bid needed to tie the other-agent bid for that slot
        in the last round.  If slot_id = 0, max_bid is 2* min_bid.
        Otherwise, it's the next highest min_bid (so bidding between min_bid
        and max_bid would result in ending up in that slot)
        """
        other_bids = self.bid_predictor(history, t)
        clicks = self.click_calc(history, t)

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
        Figure out the expected total utility of bidding such that we win each
        slot for rest of the bidding day

        returns a tuple list of (total utilities of a slot, total cost of a slot)
        """
        
        info = self.slot_info(t, history, reserve)
        min_bids, utilities, costs = [], [], []
        for x in range(0, len(info)):
            min_bids.append(info[x][1])
        for x in range(t, 48):
            utilities_this_round, cost_this_round  = [], []
            clicks = self.click_calc(history, t)
            utilities_this_round = [(self.value - b) * c for b, c in zip(min_bids, clicks)]
            cost_this_round = [b * c for b,c in zip(min_bids, clicks)]
            utilities.append(utilities_this_round)
            costs.append(cost_this_round)
        utilities_total = [sum(x) for x in zip(*utilities)]
        cost_total = [sum(x) for x in zip(*costs)]
        
        return zip(utilities_total, cost_total)

    def target_slot(self, t, history, reserve):
        """Figure out the best slot to target, assuming that everyone else
        keeps their bids the same as this round. The best slot to target should be the one that maximizes the
        total utility over the entire period while not going over budget

        Returns (slot_id, min_bid, max_bid), where min_bid is the bid needed to tie
        the other-agent bid for that slot in the last round.  If slot_id = 0,
        max_bid is min_bid * 2
        """

        utilities_budget = self.expected_utils(t, history, reserve)
        sustainable_utilities = []
        for x in range(0, len(utilities_budget)):
            if utilities_budget[x][1] > (self.budget -  history.agents_spent[self.id]):
                sustainable_utilities.append(0)
            else:
                sustainable_utilities.append(utilities_budget[x][0])
        i =  argmax_index(sustainable_utilities)
        info = self.slot_info(t, history, reserve)
        #print self.budget-history.agents_spent[self.id]
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

        clicks = self.click_calc(history, t)
        (slot, min_bid, max_bid) = self.target_slot(t, history, reserve)
        if min_bid >= self.value or slot == 0 or clicks < 30:
            return self.value

        # not going for the top

        else:
            return self.value * AGG_FACT  - (float(clicks[slot]) / clicks[slot - 1]) * (self.value - min_bid)



    def __repr__(self):
        return "%s(id=%d, value=%d)" % (
            self.__class__.__name__, self.id, self.value)


