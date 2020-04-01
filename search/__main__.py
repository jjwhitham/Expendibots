import sys
import json
import pprint

from search.util import print_move, print_boom, print_board
from search.classes import Board, Game


def main():
    with open(sys.argv[1]) as file:
        initial_board_data = json.load(file)
        # Keep current state of stacks on board using the following dict structure:
        # {'white': {(x_0, y_0): n_0, ...}...} instead of {'white': [[n_0, x_0, y_0], ...] ...}
        # This will save lots of looping, checking for stacks at coordinates, etc.
        initial_board_state = {
            colour: {(stack[1], stack[2]): stack[0] for stack in stacks}
            for colour, stacks in initial_board_data.items()
        }

        # The following code performs the same as above, but without using dict comprehension.
        # We can use this instead for readability if desired.
        initial_board_state = {}
        for colour, stacks in initial_board_data.items():
            stacks_dict = {}
            for stack in stacks:
                coords = (stack[1], stack[2])
                n_tokens = stack[0]
                stacks_dict[coords] = n_tokens
            initial_board_state[colour] = stacks_dict

    # TODO: find and print winning action sequence

    # Test game without AI_algorithm_function, only taking user input for moves and booms
    game = Game(initial_board_state, AI_algorithm_function=None)
    board_dict = game.get_board_dict()
    print_board(board_dict, unicode=True)

    while not game.game_has_ended():
        colour = "white"
        [is_boom, n_tokens, x_from, y_from, x_to, y_to] = game.get_next_move(colour)
        if is_boom:
            print_boom(x_from, y_from)
            game.boom(colour, x_from, y_from)
        else:
            print_move(n_tokens, x_from, y_from, x_to, y_to)
            game.move(colour, n_tokens, x_from, y_from, x_to, y_to)
        print_board(game.get_board_dict(), unicode=True)


if __name__ == "__main__":
    main()
