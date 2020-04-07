import sys
import json
import pprint

from search.util import print_move, print_boom, print_board
from search.game import Board, Game
from search.ai import AI


def main():
    with open(sys.argv[1]) as file:
        initial_board_data = json.load(file)
        # Keep current state of stacks on board using the following dict structure:
        # {'white': {(x_0, y_0): n_0, ...}...} instead of {'white': [[n_0, x_0, y_0], ...] ...}
        initial_board_state = {}
        for colour, stacks in initial_board_data.items():
            stacks_dict = {}
            for stack in stacks:
                coords = (stack[1], stack[2])
                n_tokens = stack[0]
                stacks_dict[coords] = n_tokens
            initial_board_state[colour] = stacks_dict

    ## Enable this block for choosing an AI algorithm when calling the program
    ## For submission of Part A, expendi_search is hardcoded

    ## if a second input to the program is given, this is the requested_ai_alg
    # ai_object = None
    # try:
    #     ai_algorithm = sys.argv[2]
    #     ai_object = AI(ai_algorithm)
    #     sys.stderr.write(f"Running game in AI mode with algorithm: {ai_algorithm} \n")
    # except IndexError:
    #     sys.stderr.write("Running game in manual mode \n")
    # except:
    #     sys.stderr.write("Something else went wrong... \n")
    
    ai_algorithm = "expendi_search"
    ai_object = AI(ai_algorithm)
    game = Game(initial_board_state, ai_object)
    board_dict = game.get_board_dict()
    print_board(board_dict, unicode=True)

    # play game until an end state has been reached
    while not game.game_has_ended(game.board):
        
        colour = "white"

        [is_boom, x_from, y_from, x_to, y_to, n_tokens] = game.get_next_move(colour)

        if is_boom:
            print_boom(x_from, y_from)
            game.boom(colour, x_from, y_from)
        else:
            print_move(n_tokens, x_from, y_from, x_to, y_to)
            game.move(colour, n_tokens, x_from, y_from, x_to, y_to)

        print_board(game.get_board_dict(), unicode=True)

if __name__ == "__main__":
    main()
