import json
from random import randint

# create boards with between 2-3 white tokens and 2-12 black tokens
board_data = {}
n_boards = 10

# make n_boards test boards
for board_i in range(n_boards):

    # reset board_data
    board_data = {"white": [], "black": []}

    # place white tokens on board
    n_white_tokens = randint(2, 3)
    for white_token_i in range(0, n_white_tokens):
        n = 1
        x = randint(0, 7)
        y = randint(0, 7)        
        stack_found = False
        for stack in board_data['white']:
            if stack[1] == x and stack[2] == y:
                stack[0] += 1
                stack_found = True
                break
        if not stack_found:
            board_data['white'].append([n, x, y])

    # place black tokens on board
    n_black_tokens = randint(2, 12)
    for black_token_i in range(0, n_black_tokens):
        n = 1
        x = randint(0, 7)
        y = randint(0, 7)
        stack_found = False
        white_stack_is_here = False
        for stack in board_data['white']:
            if stack[1] == x and stack[2] == y:
                white_stack_is_here = True
                break
        if not white_stack_is_here:
            for stack in board_data['black']:
                if stack[1] == x and stack[2] == y:
                    stack[0] += 1
                    stack_found = True
                    break
            if not stack_found:
                board_data['black'].append([n, x, y])
    
    # generate file
    filename = f"test-level-{board_i}.json"
    with open(filename, 'w') as f:
        json.dump(board_data, f)