import sys
import numpy as np

turn = 0
my_deck = []
cost_advantage = 22


def draft_score(card, deck):
    atk = card['atk']
    cost = card['cost']
    card_type = card['type']
    if card_type == 0:
        return 10 * (atk - 1.5 * cost)
    else: # spell
        return -1000


def battle_score(card, mana):
    atk = card['atk']
    cost = card['cost']
    card_type = card['type']
    card_score = 10 * (atk - 1.5 * cost)
    if cost < mana:
        card_score -= cost_advantage * (mana - cost)
    elif cost > mana:
        card_score = -1000
    if card_type > 0: # spell
        card_score = -1000
    return card_score


while True:

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
        for my_card in my_board: # attack phase
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
