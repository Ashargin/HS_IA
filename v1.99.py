import sys
import numpy as np
import copy

turn = 0
my_deck = []
draft_vals = {1: 61.0, 2: 55, 3: 66, 4: 60.9, 5: 53, 6: 64.4, 7: 83, 8: 67.8, 9: 65.9, 10: 52
, 11: 56, 12: 73.0, 13: 62.4, 14: 41, 15: 70.3, 16: 46, 17: 71.5, 18: 78, 19: 71.5,
 20: 45, 21: 70, 22: 59, 23: 72.8, 24: 48, 25: 53, 26: 65, 27: 57, 28: 75.2, 
29: 74.0, 30: 62, 31: 45, 32: 75.3, 33: 65.3, 34: 59.5, 35: 49, 36: 63.2, 37: 82
, 38: 67.3, 39: 57, 40: 57.6, 41: 63.4, 42: 46, 43: 64, 44: 80.5, 45: 59.4, 46: 
54, 47: 67.7, 48: 76, 49: 73, 50: 61.0, 51: 83, 52: 80.5, 53: 75.3, 54: 65.3, 55
: 42, 56: 59.5, 57: 51, 58: 60, 59: 71, 60: 53.0, 61: 63.4, 62: 62.3, 63: 47, 64
: 61.0, 65: 80.5, 66: 75.3, 67: 74.0, 68: 82, 69: 74.0, 70: 59, 71: 53, 72: 59.7
, 73: 71.5, 74: 63.3, 75: 71.5, 76: 60.4, 77: 60.8, 78: 51, 79: 65, 80: 80.2, 81
: 64.5, 82: 75.1, 83: 53.7, 84: 63.4, 85: 61.0, 86: 45, 87: 46, 88: 71.7, 89: 61.0,
 90: 42, 91: 59.5, 92: 38, 93: 67.1, 94: 56, 95: 72.7, 96: 67.9, 97: 66, 98: 
66.6, 99: 69.2, 100: 57.0, 101: 59, 102: 48.6, 103: 75.2, 104: 64.4, 105: 73.1, 
106: 66.5, 107: 53, 108: 50, 109: 75, 110: 44, 111: 60.8, 112: 67, 113: 48, 114:
 67.7, 115: 71.6, 116: 100, 117: 52.5, 118: 63.3, 119: 62.4, 120: 69.0, 121: 71.6,
 122: 63.4, 123: 67.0, 124: 53, 125: 52, 126: 60, 127: 60.8, 128: 70.8, 129: 73.0,
 130: 65.3, 131: 51, 132: 52.5, 133: 67.0, 134: 56.7, 135: 67.1, 136: 54, 137:
 53.7, 138: 52, 139: 87, 140: 50, 141: 54, 142: 51, 143: 40, 144: 65, 145: 64.4,
 146: 56, 147: 54, 148: 69.0, 149: 47, 150: 68.3, 151: 83.2, 152: 73.8, 153: 44,
 154: 47, 155: 63.4, 156: 45, 157: 53.0, 158: 73.1, 159: 56, 160: 42}
min_turn_strength = 4
max_turn_strength = 26
curve = {2: 7, 3: 5, 4: 4, 5: 3, 6: 2, 7: 3}
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

    if [1 for c in my_hand if c['type'] == 0 and c['cost'] <= mana]:
        max_cost_creature = max([c['cost'] for c in my_hand if c['type'] == 0 and c['cost'] <= mana])
        if not [1 for c in my_hand if c['cost'] == max_cost_creature and c['type'] == 0 and 'C' in c['abilities']]:
            mana -= max_cost_creature

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

def compute_attacks(can_attack, op_board, op_hp=1000, guards=False):
    attackers = []
    targets = []
    save = []
    if guards:
        save = copy.deepcopy([c for c in op_board if 'G' not in c['abilities']])
        op_board = copy.deepcopy([c for c in op_board if 'G' in c['abilities']])

    if not guards and sum([c['atk'] for c in can_attack]) >= op_hp:
        return can_attack, save + op_board, [c['instance'] for c in can_attack], [-1 for i in range(len(can_attack))]

    clearing_wards = True
    enemy_wards = copy.deepcopy([c for c in op_board if 'W' in c['abilities']])
    while clearing_wards and enemy_wards:
        candidates = copy.deepcopy([c for c in can_attack if 'L' not in c['abilities'] and c['atk'] > 0])
        if not candidates:
            clearing_wards = False
        else:
            target_pos = np.argmax([c['atk'] for c in enemy_wards])
            target_card = enemy_wards[target_pos]
            enemy_wards.pop(target_pos)
            finding_candidate = True
            while finding_candidate and candidates:
                lowest_atk = min([c['atk'] for c in candidates])
                lowest_atks = [c for c in candidates if c['atk'] == lowest_atk]
                higher_hps = [c for c in lowest_atks if c['hp'] > target_card['atk']]
                attacker_card = None
                if higher_hps:
                    attacker_card = higher_hps[np.argmax([c['hp'] for c in higher_hps])]
                else:
                    attacker_card = lowest_atks[np.argmin([c['hp'] for c in lowest_atks])]
                if attacker_card['atk'] <= 3 and (attacker_card['hp'] > target_card['atk'] or attacker_card['hp'] <= target_card['atk'] - 2):
                    finding_candidate = False
                    attacker = attacker_card['instance']
                    target = target_card['instance']
    
                    attackers.append(attacker)
                    targets.append(target)
    
                    target_pos = np.argwhere(np.array([c['instance'] for c in op_board]) == target)[0][0]
                    target_card = op_board[target_pos]
                    target_card['abilities'] = target_card['abilities'].replace('W', '-')
                    attacker_pos = np.argwhere(np.array([c['instance'] for c in can_attack]) == attacker)[0][0]
                    can_attack.pop(attacker_pos)
                else:
                    attacker = attacker_card['instance']
                    candidate_pos = np.argwhere(np.array([c['instance'] for c in candidates]) == attacker)[0][0]
                    candidates.pop(candidate_pos)

    wards = copy.deepcopy([c for c in can_attack if 'W' in c['abilities'] and c['atk'] > 0])
    while wards:
        if guards and not [1 for c in op_board if 'G' in c['abilities']]:
            return can_attack, save + op_board, attackers, targets

        attacker_card = wards[np.argmax([c['atk'] for c in wards])]
        if [1 for c in wards if 'L' in c['abilities']]:
            attacker_card = [c for c in wards if 'L' in c['abilities']][0]
        attacker = attacker_card['instance']
        ward_pos = np.argwhere(np.array([c['instance'] for c in wards]) == attacker)[0][0]
        wards.pop(ward_pos)
        ward_targets = copy.deepcopy([c for c in op_board if c['hp'] <= attacker_card['atk'] and 'W' not in c['abilities']])
        if 'L' in attacker_card['abilities']:
            ward_targets = copy.deepcopy([c for c in op_board if 'W' not in c['abilities']])
        target_card = None
        if ward_targets:
            max_atk = max([c['atk'] for c in ward_targets])
            max_atks = [c for c in ward_targets if c['atk'] == max_atk]
            lethal_enemies = [c for c in ward_targets if 'L' in c['abilities']]
            if lethal_enemies:
                max_atks = lethal_enemies
            target_card = max_atks[np.argmax([c['hp'] for c in max_atks])]
        elif [1 for c in op_board if 'W' not in c['abilities']] and attacker_card['atk'] > 2:
            ward_targets = copy.deepcopy([c for c in op_board if 'W' not in c['abilities']])
            max_atk = max([c['atk'] for c in ward_targets])
            max_atks = [c for c in ward_targets if c['atk'] == max_atk]
            lethal_enemies = [c for c in ward_targets if 'L' in c['abilities']]
            if lethal_enemies:
                max_atks = lethal_enemies
            target_card = max_atks[np.argmax([c['hp'] for c in max_atks])]

        if target_card is not None:
            target = target_card['instance']
            attackers.append(attacker)
            targets.append(target)
            target_pos = np.argwhere(np.array([c['instance'] for c in op_board]) == target)[0][0]
            target_card = op_board[target_pos]
            if 'L' in attacker_card['abilities']:
                target_card['hp'] = 0
            else:
                target_card['hp'] -= attacker_card['atk']
            if target_card['hp'] <= 0:
                op_board.pop(target_pos)
            attacker_pos = np.argwhere(np.array([c['instance'] for c in can_attack]) == attacker)[0][0]
            can_attack.pop(attacker_pos)
        elif not guards:
            attackers.append(attacker)
            targets.append(-1)
            attacker_pos = np.argwhere(np.array([c['instance'] for c in can_attack]) == attacker)[0][0]
            can_attack.pop(attacker_pos)

    lethals = copy.deepcopy([c for c in can_attack if 'L' in c['abilities'] and c['atk'] > 0])
    while lethals:
        if guards and not [1 for c in op_board if 'G' in c['abilities']]:
            return can_attack, save + op_board, attackers, targets

        attacker_card = lethals[np.argmin([c['hp'] for c in lethals])]
        attacker = attacker_card['instance']
        lethal_pos = np.argwhere(np.array([c['instance'] for c in lethals]) == attacker)[0][0]
        lethals.pop(lethal_pos)
        lethal_targets = copy.deepcopy([c for c in op_board if c['atk'] < attacker_card['hp'] and 'W' not in c['abilities']])
        target_card = None
        if lethal_targets:
            max_hp = max([c['hp'] for c in lethal_targets])
            max_hps = [c for c in lethal_targets if c['hp'] == max_hp]
            target_card = max_hps[np.argmax([c['atk'] for c in max_hps])]
        elif [1 for c in op_board if 'W' not in c['abilities']]:
            lethal_targets = copy.deepcopy([c for c in op_board if 'W' not in c['abilities']])
            max_hp = max([c['hp'] for c in lethal_targets])
            max_hps = [c for c in lethal_targets if c['hp'] == max_hp]
            target_card = max_hps[np.argmax([c['atk'] for c in max_hps])]

        if target_card is not None:
            target = target_card['instance']
            attackers.append(attacker)
            targets.append(target)
            target_pos = np.argwhere(np.array([c['instance'] for c in op_board]) == target)[0][0]
            op_board.pop(target_pos)
            attacker_pos = np.argwhere(np.array([c['instance'] for c in can_attack]) == attacker)[0][0]
            can_attack.pop(attacker_pos)
        elif not guards:
            attackers.append(attacker)
            targets.append(-1)
            attacker_pos = np.argwhere(np.array([c['instance'] for c in can_attack]) == attacker)[0][0]
            can_attack.pop(attacker_pos)

    enemy_lethals = copy.deepcopy([c for c in op_board if 'L' in c['abilities'] and 'W' not in c['abilities']])
    while enemy_lethals:
        if guards and not [1 for c in op_board if 'G' in c['abilities']]:
            return can_attack, save + op_board, attackers, targets

        target_pos = np.argmin([c['hp'] for c in enemy_lethals])
        target_card = enemy_lethals[target_pos]
        enemy_lethals.pop(target_pos)
        candidates = copy.deepcopy([c for c in can_attack if c['atk'] >= target_card['hp']])
        if guards and can_attack and not candidates:
            max_atk = max([c['atk'] for c in can_attack])
            candidates = copy.deepcopy([c for c in can_attack if c['atk'] == max_atk])

        if candidates:
            attacker_card = candidates[np.argmin([c['hp'] for c in candidates])]
            attacker = attacker_card['instance']
            target = target_card['instance']
    
            attackers.append(attacker)
            targets.append(target)
    
            target_pos = np.argwhere(np.array([c['instance'] for c in op_board]) == target)[0][0]
            target_card = op_board[target_pos]
            if 'L' in attacker_card['abilities']:
                target_card['hp'] = 0
            else:
                target_card['hp'] -= attacker_card['atk']
            if target_card['hp'] <= 0:
                op_board.pop(target_pos)
            attacker_pos = np.argwhere(np.array([c['instance'] for c in can_attack]) == attacker)[0][0]
            can_attack.pop(attacker_pos)

    while can_attack:
        if guards and not [1 for c in op_board if 'G' in c['abilities']]:
            return can_attack, save + op_board, attackers, targets

        enemies = copy.deepcopy([c for c in op_board if 'W' not in c['abilities'] and 'L' not in c['abilities']])
        candidates = copy.deepcopy([c for c in can_attack if 'W' not in c['abilities'] and 'L' not in c['abilities']])

        my_atks = [c['atk'] for c in candidates]
        my_hps = [c['hp'] for c in candidates]
        op_atks = [c['atk'] for c in enemies]
        op_hps = [c['hp'] for c in enemies]
        attacker = None
        target = None
        max_enemy_atk = -1
        min_ally_atk = 1000
        for i in range(len(candidates)): # kills and survives
            for j in range(len(enemies)):
                if my_atks[i] >= op_hps[j] and op_atks[j] < my_hps[i]:
                    if op_atks[j] > max_enemy_atk or op_atks[j] == max_enemy_atk and my_atks[i] < min_ally_atk:
                        max_enemy_atk = op_atks[j]
                        min_ally_atk = my_atks[i]
                        att = candidates[i]
                        tar = enemies[j]
                        attacker = att['instance']
                        target = tar['instance']

        if attacker is None:
            max_enemy_atk = -1
            max_delta = -1
            for i in range(len(candidates)): # good kill-kill trade
                for j in range(len(enemies)):
                    delta = op_atks[j] + op_hps[j] - my_atks[i] - my_hps[i]
                    if my_atks[i] >= op_hps[j] and delta > 0:
                        if op_atks[j] > max_enemy_atk or op_atks[j] == max_enemy_atk and delta > max_delta:
                            max_enemy_atk = op_atks[j]
                            max_delta = delta
                            att = candidates[i]
                            tar = enemies[j]
                            attacker = att['instance']
                            target = tar['instance']

        if attacker is None and guards:
            max_enemy_atk = -1
            max_delta = -1000
            for i in range(len(candidates)): # guards ==> bad kill-kill trade
                for j in range(len(enemies)):
                    delta = op_atks[j] + op_hps[j] - my_atks[i] - my_hps[i]
                    if my_atks[i] >= op_hps[j]:
                        if op_atks[j] > max_enemy_atk or op_atks[j] == max_enemy_atk and delta > max_delta:
                            max_enemy_atk = op_atks[j]
                            max_delta = delta
                            att = candidates[i]
                            tar = enemies[j]
                            attacker = att['instance']
                            target = tar['instance']

        if attacker is None:
            max_ally_atk = -1
            min_enemy_atk = 1000
            for i in range(len(candidates)): # not killing, not getting killed
                for j in range(len(enemies)):
                    if my_hps[i] >= op_atks[j]:
                        if my_atks[i] > max_ally_atk or my_atks[i] == max_ally_atk and op_atks[j] < min_enemy_atk:
                            max_ally_atk = my_atks[i]
                            min_enemy_atk = op_atks[j]
                            att = candidates[i]
                            tar = enemies[j]
                            attacker = att['instance']
                            target = tar['instance']

        if attacker is None:
            max_ally_delta = -1000
            max_enemy_atk = -1
            for i in range(len(candidates)): # not killing, getting killed, if target can get killed
                for j in range(len(enemies)):
                    if sum(my_atks) >= op_hps[j] and op_hps[j] > my_atks[i]:
                        ally_delta = my_atks[i] - my_hps[i]
                        if op_atks[j] > max_enemy_atk or op_atks[j] == max_enemy_atk and ally_delta > max_ally_delta:
                            max_enemy_atk = op_atks[j]
                            max_ally_delta = ally_delta
                            att = candidates[i]
                            tar = enemies[j]
                            attacker = att['instance']
                            target = tar['instance']

        if attacker is None:
            if guards:
                return can_attack, save + op_board, attackers, targets
            else:
                attacker = candidates[0]['instance']
                target = -1

        attackers.append(attacker)
        targets.append(target)

        attacker_pos = np.argwhere(np.array([c['instance'] for c in can_attack]) == attacker)[0][0]
        attacker_card = can_attack[attacker_pos]
        can_attack.pop(attacker_pos)
        if target != -1:
            target_pos = np.argwhere(np.array([c['instance'] for c in op_board]) == target)[0][0]
            target_card = op_board[target_pos]
            target_atk = target_card['atk']
            attacker_atk = attacker_card['atk']
            if attacker_atk > 0:
                if 'W' in target_card['abilities']:
                    target_card['abilities'] = target_card['abilities'].replace('W', '-')
                elif 'L' in attacker_card['abilities']:
                    target_card['hp'] = 0
                else:
                    target_card['hp'] -= attacker_atk
            if target_card['hp'] <= 0:
                op_board.pop(target_pos)

    return can_attack, save + op_board, attackers, targets

def compute_attacks_main(can_attack, op_board, op_hp):
    attackers = []
    targets = []

    guards = [c for c in op_board if 'G' in c['abilities']]
    if guards:
        can_attack, op_board, att, tar = compute_attacks(can_attack, op_board, guards=True)
        print('guards', att, tar, file=sys.stderr)
        attackers += att
        targets += tar

    guards = [c for c in op_board if 'G' in c['abilities']]
    if not guards:
        can_attack, op_board, att, tar = compute_attacks(can_attack, op_board, op_hp=op_hp, guards=False)
        print('noguards', att, tar, file=sys.stderr)
        attackers += att
        targets += tar

    return attackers, targets

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
        attackers, targets = compute_attacks_main(copy.deepcopy(can_attack), copy.deepcopy(op_board), op_hp) # attack phase
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
