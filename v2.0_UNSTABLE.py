import sys
import numpy as np
import copy

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
min_turn_strength = 4
max_turn_strength = 26
curve = {2: 6, 3: 4, 4: 4, 5: 3, 6: 3, 7: 4}
cost_strength = 5
over_cost_punish_threshold = 2
over_cost_punish_strength = 1
draw_target = 7
draw_strength = 2
spells_target = 6
spells_strength = 3
duplicate_strength = 8
cost_advantage = 22

def draft_score(card, deck):
    card_type = card['type']
    turn_strength = 0
    if turn >= min_turn_strength - 1:
        turn_strength = min((turn - min_turn_strength + 1) / (max_turn_strength - min_turn_strength), 1)

    cost = card['cost']
    cost_bonus = 0
    if card_type == 0:
        cost_reached = 0
        cost_target = 0
        this_cost_strength = cost_strength
        if cost_reached >= cost_target * turn / 30 + over_cost_punish_threshold:
            this_cost_strength += cost_strength * over_cost_punish_strength * (cost_reached - cost_target * turn / 30 - over_cost_punish_threshold)
        if cost >= 7:
            cost_reached = len([c for c in deck if c['cost'] >= 7 and c['type'] == 0])
            cost_target = curve[7]
        elif cost <= 2:
            cost_reached = len([c for c in deck if c['cost'] <= 2 and c['type'] == 0])
            cost_target = curve[2]
        else:
            cost_reached = len([c for c in deck if c['cost'] == cost and c['type'] == 0])
            cost_target = curve[cost]
        cost_bonus = this_cost_strength * turn_strength * (cost_target * turn / 30 - cost_reached)

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
    return val + cost_bonus + draw_bonus + spell_bonus + duplicate_bonus

def play_score(card, mana, my_board, op_board):
    card_score = draft_vals[card['id']]
    cost = card['cost']
    card_type = card['type']

    if cost < mana:
        card_score -= cost_advantage * (mana - cost)

    target = 0
    if card_type == 1:
        target_pos = np.argmax([c['atk'] for c in my_board])
        target = my_board[target_pos]['instance']

    elif card_type == 2:
        target_pos = np.argmax([c['atk'] for c in op_board])
        target = op_board[target_pos]['instance']

    elif card_type == 3:
        if op_board:
            target_pos = np.argmax([c['atk'] for c in op_board])
            target = op_board[target_pos]['instance']
        else:
            target = -1

    return card_score, target

def compute_plays_before(my_hand, my_board, op_board, can_attack, mana):
    can_play = True
    plays = []
    targets = []

    while can_play:
        # only charge minions before attacking
        playable_0 = [card for card in my_hand if card['cost'] <= mana and card['type'] == 0 and 'C' in card['abilities']]
        if len(my_board) == 6:
            playable_0 = []
        playable_1 = [card for card in my_hand if card['cost'] <= mana and card['type'] == 1]
        if not my_board:
            playable_1 = []
        playable_2 = [card for card in my_hand if card['cost'] <= mana and card['type'] == 2]
        if not op_board:
            playable_2 = []
        playable_3 = [card for card in my_hand if card['cost'] <= mana and card['type'] == 3]
        playable = copy.deepcopy(playable_0 + playable_1 + playable_2 + playable_3)

        if not playable:
            can_play = False
        else:
            round_scores, round_targets = zip(*[play_score(card, mana, my_board, op_board) for card in playable])
            round_play_pos = np.argmax(round_scores)
            round_play_card = playable[round_play_pos]
            round_play = round_play_card['instance']
            cost = round_play_card['cost']
            card_type = round_play_card['type']
            round_target = round_targets[round_play_pos]

            hand_pos = np.argwhere(np.array([c['instance'] for c in my_hand]) == round_play)[0][0]
            my_hand.pop(hand_pos)
            if card_type == 0:
                my_board.append(copy.deepcopy(round_play_card))
            elif card_type > 1 and round_target != -1:
                target_pos = np.argwhere(np.array([c['instance'] for c in op_board]) == round_target)[0][0]
                target_card = op_board[target_pos]
                if 'W' in target_card['abilities']:
                    target_card['abilities'] = target_card['abilities'].replace('W', '-')
                else:
                    target_card['hp'] += round_play_card['hp']
                if target_card['hp'] <= 0:
                    op_board.pop(target_pos)
            mana -= cost
    
            plays.append(round_play)
            targets.append(round_target)

    return plays, targets

def compute_plays_after(my_hand, my_board, op_board, can_attack, mana):
    can_play = True
    summons = []

    while can_play:
        playable = copy.deepcopy([card for card in my_hand if card['cost'] <= mana and card['type'] == 0])
        if len(my_board) == 6:
            playable = []

        if not playable:
            can_play = False
        else:
            round_scores, round_targets = zip(*[play_score(card, mana, my_board, op_board) for card in playable])
            round_play_pos = np.argmax(round_scores)
            round_play_card = playable[round_play_pos]
            round_play = round_play_card['instance']
            cost = round_play_card['cost']

            hand_pos = np.argwhere(np.array([c['instance'] for c in my_hand]) == round_play)[0][0]
            my_hand.pop(hand_pos)
            my_board.append(copy.deepcopy(round_play_card))
            mana -= cost
    
            summons.append(round_play)

    return summons

def compute_attacks(can_attack, op_board):
    attackers = []
    targets = []
    for card in can_attack:
        attacker = card['instance']
        attackers.append(attacker)
        if card['atk'] > 0:
            guard = False
            guard_pos = 0
            for i, op_card in enumerate(op_board):
                if 'G' in op_card['abilities']:
                    guard = True
                    guard_pos = i
            if not guard:
                targets.append(-1)
            else:
                op_card = op_board[guard_pos]
                attacked = op_card['instance']
                targets.append(attacked)
                if 'W' in op_card['abilities']:
                    op_card['abilities'] = op_card['abilities'].replace('W', '-')
                else:
                    if 'L' in card['abilities']:
                        op_card['hp'] = 0
                    else:
                        op_card['hp'] -= card['atk']
                    if op_card['hp'] <= 0:
                        op_board.pop(guard_pos)

    return attackers, targets

    # attackers, targets = compute_attacks # compute variables
    # for i, attacker in enumerate(attackers):
    #     target = targets[i]
    #     actions.append('ATTACK ' + str(attacker) + ' ' + str(target))

    #       attacker_pos = np.argwhere(np.array([c['instance'] for c in can_attack]) == attacker)[0][0]
    #     attacker_card = can_attack[attacker_pos]
    #     if target == -1:
    #         atk = attacker_card['atk']
    #         op_hp -= atk
    #         if 'D' in attacker_card['abilities']:
    #             my_hp += atk

    #       else:
    #         target_pos = np.argwhere(np.array([c['instance'] for c in op_board]) == target)[0][0]
    #         target_card = op_board[target_pos]
    #         attacker_abilities = attacker_card['abilities']
    #         target_abilities = target_card['abilities']
    #         if 'W' in attacker_abilities and 'W' in target_abilities:
    #             attacker_card['abilities'] = attacker_abilities.replace('W', '-') # 0 atk?
    #             target_card['abilities'] = target_abilities.replace('W', '-')

    #           elif 'W' in attacker_abilities:

# compute my_hp, my_mana, my_rune?, op_hp, op_rune?, my_board, op_board, my_hand, can_attack

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
    can_attack = copy.deepcopy(my_board)

    if turn < 30: # draft phase
        scores = [draft_score(card, my_deck) for card in my_hand]
        pick = np.argmax(scores)
        print('PICK ' + str(pick))
        my_deck.append(my_hand[pick])

    else: # battle phase
        actions = []
        played = False

        plays, targets = compute_plays_before(copy.deepcopy(my_hand), copy.deepcopy(my_board), copy.deepcopy(op_board), copy.deepcopy(can_attack), my_mana) # before-attack play phase
        print('before-attack', plays, targets, file=sys.stderr)
        for i in range(len(plays)):
            play = plays[i]
            target = targets[i]
            play_pos = np.argwhere(np.array([c['instance'] for c in my_hand]) == play)[0][0]
            card = my_hand[play_pos]
            card_type = card['type']

            if card_type == 0:
                actions.append('SUMMON ' + str(play))
            else:
                actions.append('USE ' + str(play) + ' ' + str(target))

            my_hp += card['my_hp_change']
            my_mana -= card['cost']
            op_hp += card['op_hp_change']
            my_hand.pop(play_pos)

            if card_type == 0:
                my_board.append(copy.deepcopy(card))
                if 'C' in card['abilities']:
                    can_attack.append(copy.deepcopy(card))

            elif card_type == 1:
                for board in [can_attack, my_board]:
                    try:
                        target_pos = np.argwhere(np.array([c['instance'] for c in board]) == target)[0][0]
                        target_card = board[target_pos]
                        target_card['atk'] += card['atk']
                        target_card['hp'] += card['hp']
                        for i, v in enumerate(card['abilities']):
                            if v != '-':
                                target_card['abilities'] = target_card['abilities'][:i] + v + target_card['abilities'][i+1:]
                        if 'C' in target_card['abilities'] and target not in [c['instance'] for c in can_attack]:
                            can_attack.append(copy.deepcopy(target_card))
                    except IndexError:
                        pass

            elif card_type == 2:
                target_pos = np.argwhere(np.array([c['instance'] for c in op_board]) == target)[0][0]
                target_card = op_board[target_pos]
                target_card['atk'] += card['atk']
                for i, v in enumerate(card['abilities']):
                    if v != '-':
                        target_card['abilities'] = target_card['abilities'].replace(v, '-')
                if 'W' in target_card['abilities']:
                    target_card['abilities'] = target_card['abilities'].replace('W', '-')
                else:
                    target_card['hp'] += card['hp']
                if target_card['hp'] <= 0:
                    op_board.pop(target_pos)

            else:
                if target != -1:
                    target_pos = np.argwhere(np.array([c['instance'] for c in op_board]) == target)[0][0]
                    target_card = op_board[target_pos]
                    if 'W' in target_card['abilities']:
                        target_card['abilities'] = target_card['abilities'].replace('W', '-')
                    else:
                        target_card['hp'] += card['hp']
                    if target_card['hp'] <= 0:
                        op_board.pop(target_pos)
                else:
                    op_hp += card['hp']

            played = True

        attacked = False
        attackers, targets = compute_attacks(copy.deepcopy(can_attack), copy.deepcopy(op_board)) # attack phase
        print('attack', attackers, targets, file=sys.stderr)
        for i in range(len(attackers)):
            attacker = attackers[i]
            target = targets[i]

            actions.append('ATTACK ' + str(attacker) + ' ' + str(target))

            if target == -1:
                attacker_pos = np.argwhere(np.array([c['instance'] for c in my_board]) == attacker)[0][0]
                attacker_card = my_board[attacker_pos]
                attacker_atk = attacker_card['atk']
                op_hp -= attacker_atk
                if 'D' in attacker_card['abilities']:
                    my_hp += attacker_atk

            else:
                target_pos = np.argwhere(np.array([c['instance'] for c in op_board]) == target)[0][0]
                target_card = op_board[target_pos]
                target_atk = target_card['atk']
                attacker_pos = np.argwhere(np.array([c['instance'] for c in my_board]) == attacker)[0][0]
                attacker_card = my_board[attacker_pos]
                attacker_atk = attacker_card['atk']
    
                if target_atk > 0:
                    if 'W' in attacker_card['abilities']:
                        attacker_card['abilities'] = attacker_card['abilities'].replace('W', '-')
                    elif 'L' in target_card['abilities']:
                        attacker_card['hp'] = 0
                    else:
                        attacker_card['hp'] -= target_atk
                if attacker_atk > 0:
                    if 'W' in target_card['abilities']:
                        target_card['abilities'] = target_card['abilities'].replace('W', '-')
                    elif 'L' in attacker_card['abilities']:
                        target_card['hp'] = min(target_card['hp'] - attacker_atk, 0)
                        if 'D' in attacker_card['abilities']:
                            my_hp += attacker_atk
                    else:
                        target_card['hp'] -= attacker_atk
                        if 'D' in attacker_card['abilities']:
                            my_hp += attacker_atk
                can_attack_pos = np.argwhere(np.array([c['instance'] for c in can_attack]) == attacker)[0][0]
                can_attack[can_attack_pos] = copy.deepcopy(attacker_card)
    
                if target_card['hp'] <= 0:
                    op_board.pop(target_pos)
                    if 'B' in attacker_card['abilities']:
                        op_hp += target_card['hp']
                if attacker_card['hp'] <= 0:
                    my_board.pop(attacker_pos)
                    can_attack.pop(can_attack_pos)

            attacked = True

        summons = compute_plays_after(copy.deepcopy(my_hand), copy.deepcopy(my_board), copy.deepcopy(op_board), copy.deepcopy(can_attack), my_mana) # after-attack play phase
        print('after-attack', summons, file=sys.stderr)
        for i in range(len(summons)):
            summon = summons[i]

            actions.append('SUMMON ' + str(summon))

            play_pos = np.argwhere(np.array([c['instance'] for c in my_hand]) == summon)[0][0]
            card = my_hand[play_pos]
            if 'C' in card['abilities']:
                guard = False
                for op_card in op_board:
                    if 'G' in op_card['abilities']:
                        guard = True
                if not guard:
                    actions.append('ATTACK ' + str(summon) + ' -1') # can be done better

            played = True

        if not played and not attacked:
            actions = ['PASS']
        print(';'.join(actions))

    turn += 1
