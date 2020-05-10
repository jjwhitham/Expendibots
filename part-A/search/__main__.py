import sys
import json
import pprint

from search.util import print_move, print_boom, print_board
from search.game import Board, Game
from search.ai import AI


def main():
    def get_initial_board_state(board_filename):
        if board_filename == "full_game":
            initial_board_state = {
                'white': {
                    (0, 0): 1, (0, 1): 1, (1, 1): 1, (1, 0): 1,
                    (3, 0): 1, (3, 1): 1, (4, 1): 1, (4, 0): 1,
                    (6, 0): 1, (6, 1): 1, (7, 1): 1, (7, 0): 1,
                },
                'black': {
                    (0, 6): 1, (0, 7): 1, (1, 7): 1, (1, 6): 1,
                    (3, 6): 1, (3, 7): 1, (4, 7): 1, (4, 6): 1,
                    (6, 6): 1, (6, 7): 1, (7, 7): 1, (7, 6): 1,
                }
            }
        else:
            with open(board_filename) as file:
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
        return initial_board_state

    def get_ai_object(colour):
        ai_object = None
        try:
            ai_algorithm = sys.argv[2]
            ai_object = AI(ai_algorithm, colour)
            sys.stderr.write(f"Running game in AI mode with algorithm: {ai_algorithm} \n")
        except IndexError:
            sys.stderr.write("Running game in manual mode \n")
        except:
            sys.stderr.write("Something else went wrong... \n")

        
        return ai_object
    
    def play_game(initial_board_state, ai_object, colour):
        game = Game(initial_board_state, n_turns=0)

        # create a list which contains all moves required to get to goal state
        # make a generator from this list, which will yield the actions one-by-one
        if ai_object is not None:
            ai_solution = ai_object.get_solution(game)
            ai_solution_generator = (action for action in ai_solution)

        # n_turns = 0
        board_dict = game.get_board_dict()
        print_board(board_dict, unicode=True)
        # play game until an end state has been reached
        while not game.game_has_ended(colour): # TODO: Need to change this for manual play below
            
            
            
            if ai_object is not None:
                action = next(ai_solution_generator)
            else:
                # TODO: manual play, alternating colours (need to fix game has ended above)
                whites_turn = game.n_turns % 2
                colour = "white" if whites_turn else "black"            
                action = game.get_next_action(colour)

            # if is_boom:
            if action[0] == "BOOM":
                x_from, y_from = action[1]
                print_boom(x_from, y_from)
                game.boom(colour, x_from, y_from)
            else:
                n_tokens = action[1]
                x_from, y_from = action[2]
                x_to, y_to = action[3]
                print_move(n_tokens, x_from, y_from, x_to, y_to)
                game.move(colour, n_tokens, x_from, y_from, x_to, y_to)

            game.n_turns += 1
            sys.stderr.write(f"game.n_turns: {game.n_turns} \n")
            print_board(game.get_board_dict(), unicode=True)
    
    initial_board_state = get_initial_board_state(sys.argv[1])
    colour = "white"
    ai_object = get_ai_object(colour)
    play_game(initial_board_state, ai_object, colour)
        
if __name__ == "__main__":
    main()
