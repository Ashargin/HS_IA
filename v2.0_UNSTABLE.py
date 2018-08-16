import sys
import numpy as np

turn = 0
my_deck = []
draft_vals = {1: 60, 2: 50, 3: 55, 4: 55, 5: 50, 6: 55, 7: 65, 8: 60, 9: 65, 10: 50, 11: 58, 
12: 62, 13: 55, 14: 30, 15: 68, 16: 40, 17: 68, 18: 71, 19: 65, 20: 35, 21: 62, 
22: 55, 23: 70, 24: 55, 25: 50, 26: 60, 27: 62, 28: 65, 29: 68, 30: 60, 31: 45, 
32: 70, 33: 72, 34: 62, 35: 53, 36: 78, 37: 75, 38: 65, 39: 62, 40: 55, 41: 55, 
42: 48, 43: 60, 44: 85, 45: 55, 46: 55, 47: 62, 48: 68, 49: 82, 50: 58, 51: 88, 
52: 60, 53: 70, 54: 58, 55: 30, 56: 58, 57: 42, 58: 58, 59: 63, 60: 50, 61: 68, 
62: 100, 63: 20, 64: 55, 65: 70, 66: 72, 67: 80, 68: 85, 69: 80, 70: 57, 71: 50,
 72: 52, 73: 75, 74: 60, 75: 65, 76: 60, 77: 63, 78: 62, 79: 65, 80: 93, 81: 60,
 82: 77, 83: 40, 84: 55, 85: 53, 86: 40, 87: 45, 88: 52, 89: 53, 90: 42, 91: 40,
 92: 30, 93: 58, 94: 57, 95: 67, 96: 61, 97: 69, 98: 58, 99: 68, 100: 53, 101: 52,
 102: 50, 103: 70, 104: 62, 105: 67, 106: 64, 107: 54, 108: 45, 109: 67, 110: 
20, 111: 68, 112: 64, 113: 30, 114: 71, 115: 65, 116: 140, 117: 48, 118: 49, 119
: 53, 120: 86, 121: 88, 122: 85, 123: 81, 124: 45, 125: 47, 126: 65, 127: 75, 128:
 76, 129: 72, 130: 81, 131: 49, 132: 45, 133: 85, 134: 69, 135: 63, 136: 42, 137:
 76, 138: 59, 139: 82, 140: 48, 141: 39, 142: 35, 143: 5, 144: 45, 145: 47, 146:
 42, 147: 45, 148: 55, 149: 48, 150: 60, 151: 81, 152: 87, 153: 44, 154: 51, 
155: 51, 156: 44, 157: 35, 158: 63, 159: 58, 160: 39}
min_turn_strength = 8
max_turn_strength = 20
curve = {2: 6, 3: 4, 4: 4, 5: 3, 6: 3, 7: 4}
cost_strength = 5
draw_target = 7
draw_strength = 2
spells_target = 6
spells_strength = 3
duplicate_strength = 8
cost_advantage = 22

def draft_score(card, deck): # update score : abilities, items
    #atk = card['atk']
    #cost = card['cost']
    #card_type = card['type']
    #if card_type == 0:
        #return 10 * (atk - 1.5 * cost)
        # return 50 + 10 * (atk + hp - 2 * cost) + 3 * (hp - atk)
    #else:
        #return -1000

    card_type = card['type']
    turn_strength = 0
    if turn >= min_turn_strength - 1:
        turn_strength = min((turn - min_turn_strength + 1) / (max_turn_strength - min_turn_strength), 1)
    cost = card['cost']
    cost_bonus = 0
    if cost > 1 and card_type == 0:
        cost_reached = 0
        cost_target = 0
        if cost >= 7:
            cost_reached = len([c for c in deck if c['cost'] >= 7 and c['type'] == 0])
            cost_target = curve[7]
        else:
            cost_reached = len([c for c in deck if c['cost'] == cost and c['type'] == 0])
            cost_target = curve[cost]
        cost_bonus = cost_strength * turn_strength * (cost_target * turn / 30 - cost_reached)
    draw = card['draw']
    draw_reached = sum([c['draw'] for c in deck])
    draw_bonus = draw_strength * turn_strength * draw * (draw_target * turn / 30 - draw_reached)
    spell_bonus = 0
    if card_type > 0:
        spells_reached = len([c for c in deck if c['type'] > 0])
        spell_bonus = spells_strength * turn_strength * (spells_target * turn / 30 - spells_reached)
    duplicate_bonus = 0
    if card_type > 0:
        card_id = card['id']
        duplicates = len([c for c in deck if c['id'] == card_id])
        duplicate_bonus = -duplicate_strength * duplicates
    val = draft_vals[card['id']]
    print('val', val, file=sys.stderr)
    print('cost', cost_bonus, file=sys.stderr)
    print('draw', draw_bonus, file=sys.stderr)
    print('spell', spell_bonus, file=sys.stderr)
    print('duplicates', duplicate_bonus, file=sys.stderr)
    return val + cost_bonus + draw_bonus + spell_bonus + duplicate_bonus

def battle_score(card, mana): # update score : abilities, items
    card_score = draft_vals[card['id']]
    cost = card['cost']
    # card_score = 50 + 10 * (atk + hp - 2 * cost) + 3 * (hp - atk)
    if cost < mana:
        card_score -= cost_advantage * (mana - cost)
    elif cost > mana:
        card_score -= 1000
    return card_score

# def compute_plays

# def compute_attacks

while True: # update my_rune, op_rune?

    # inputs
    my_hp, my_mana, my_deck_count, my_rune = [int(j) for j in input().split()]
    op_hp, op_mana, op_deck_count, op_rune = [int(j) for j in input().split()]
    op_hand_count = int(input())
    card_count = int(input())
    my_board = []
    op_board = []
    my_hand = []
    for i in range(card_count):
        card_number, instance_id, location, card_type, cost, attack, defense, abilities, my_health_change, opponent_health_change, card_draw = input().split()
        card = {}
        card['id'] = int(card_number)
        card['instance'] = int(instance_id)
        card['type'] = int(card_type)
        card['cost'] = int(cost)
        card['atk'] = int(attack)
        card['hp'] = int(defense)
        card['abilities'] = abilities
        card['my_hp_change'] = int(my_health_change)
        card['op_hp_change'] = int(opponent_health_change)
        card['draw'] = int(card_draw)
        loc = int(location)
        if loc == 0:
            my_hand.append(card)
        elif loc == 1:
            my_board.append(card)
        else:
            op_board.append(card)

    if turn < 30: # draft phase
        scores = [draft_score(card, my_deck) for card in my_hand]
        print(scores, file=sys.stderr)
        pick = np.argmax(scores)
        print('PICK ' + str(pick))
        my_deck.append(my_hand[pick])

    else: # battle phase
        actions = []
        can_play = True #play phase
        played = False
        my_board_count = len(my_board)
        while can_play:
            playable = [card for card in my_hand if card['cost'] <= my_mana and card['type'] == 0]
            if playable and my_board_count < 6:
                scores = [battle_score(card, my_mana) for card in my_hand]
                play = np.argmax(scores)
                card = my_hand[play]
                actions.append('SUMMON ' + str(card['instance']))
                my_hp += card['my_hp_change']
                my_mana -= card['cost']
                op_hp += card['op_hp_change']
                if 'C' in card['abilities']:
                    my_board.append(card)
                my_board_count += 1
                my_hand.pop(play)
                played = True
            else:
                can_play = False

        attacked = False
        # attacks = compute_attacks
        for my_card in my_board: # attack phase # compute variables
            if my_card['atk'] > 0:
                attacked = True
                guard = False
                guard_pos = 0
                for i, op_card in enumerate(op_board):
                    if 'G' in op_card['abilities']:
                        guard = True
                        guard_pos = i
                if not guard:
                    actions.append('ATTACK ' + str(my_card['instance']) + ' -1')
                else:
                    op_card = op_board[guard_pos]
                    actions.append('ATTACK ' + str(my_card['instance']) + ' ' + str(op_card['instance']))
                    if 'W' in op_card['abilities']:
                        op_card['abilities'] = op_card['abilities'].replace('W', '-')
                    else:
                        if 'L' in my_card['abilities']:
                            op_card['hp'] = 0
                        else:
                            op_card['hp'] -= my_card['atk']
                        if op_card['hp'] <= 0:
                            op_board.pop(guard_pos)

        if not played and not attacked:
            actions = ['PASS']
        print(';'.join(actions))

    turn += 1