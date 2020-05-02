import sys
from collections import defaultdict
from copy import deepcopy

class Coords:
    """
    A class to represent a coordinate pair on the board.
    At the moment this class is not used. 

    This class could implement methods 'is_cardinal_direction()', 'dist()', 'is_on_board()'
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Stack:
    """
    A class to represent a stack of tokens. At the moment this class is not used and 
    each stack is just represented by a '(x, y): n' pair within the board_state dictionary
    in the Board class.

    If we wanted to push the OOP design, we could use this class,
    or even a namedtuple object...
    """

    def __init__(self, n, coords, colour):
        self.n = n
        self.coords = coords
        self.colour = colour


class Board:
    def __init__(self, board_state):
        self.board_state = board_state

    def get_board_dict(self):
        board_dict = {(i, j): "" for i in range(8) for j in range(8)}
        for colour, stacks in self.board_state.items():
            for coords, n_tokens in stacks.items():
                first_letter = colour[:2]
                board_dict[coords] = f"{n_tokens}-{first_letter}"
        return board_dict

    def move(self, colour, n_tokens, x_from, y_from, x_to, y_to):
        # sys.stderr.write("move called")
        if not self.is_legal_move(colour, n_tokens, x_from, y_from, x_to, y_to, False):
            return
        coords_from = (x_from, y_from)
        coords_to = (x_to, y_to)

        # if we're adding to an existing stack
        if coords_to in self.board_state[colour]:
            self.board_state[colour][coords_to] += n_tokens
        else:
            self.board_state[colour][coords_to] = n_tokens

        # reduce the original stack size, deleting it if no tokens are left
        self.board_state[colour][coords_from] -= n_tokens
        if self.board_state[colour][coords_from] == 0:
            del self.board_state[colour][coords_from]
    # TODO: pull is_debug out of def and calls to is_legal_move. Make this a CL argument
    def is_legal_move(self, colour, n_tokens, x_from, y_from, x_to, y_to, is_debug):
        """ 
        Checks game rules to see if it would be legal to perform a move action
        of `n_tokens` of `colour` from coordinates(`x_from`, `y_from`) to
        coordinates (`x_to`, `y_to`).

        is_legal_move prints a debugging error message and returns False if any rules
        are broken, otherwise it returns True
    
        Returns False if any coordinates are off the board.
            'A token cannot move off the board'

        Returns False if move is into same position, i.e. destination == origin
            '..., and must move by at least one square'

        Returns False if origin stack does not exist at (x_from, y_from)
            *This is implied*

        Returns False if the origin stack has less tokens than requested
            'From a stack of n tokens (n ≥ 1), the player may move up to n of those tokens
                a distance of up to n squares in a single direction.'

        Returns False if the move is not in one of the cardinal directions
            'The tokens may not move diagonally,...'

        Returns False if the number of cells to move n_tokens is greater than the original
        stack height
            'From a stack of n tokens (n ≥ 1), the player may move up to n of those tokens
                a distance of up to n squares in a single direction.'

        Returns False if the destination square contains token(s) of the opponent's colour.
            'The tokens may not move onto a square occupied by the opponent’s tokens.'

        Returns True if none of the above issues have been encountered
        """
        coords_from = (x_from, y_from)
        coords_to = (x_to, y_to)
        err_msg = "Illegal Move:"

        # check for valid coordinates
        for coord in (x_from, y_from, x_to, y_to):
            if coord not in range(8):
                if is_debug:
                    sys.stderr.write(err_msg)
                    sys.stderr.write(f"{coord} is not a valid coordinate value.")
                return False

        # check that move is not into same position
        if coords_from == coords_to:
            if is_debug:
                sys.stderr.write(err_msg)
                sys.stderr.write("Cannot move stack into same position!")
            return False

        # check origin stack exists
        if not coords_from in self.board_state[colour]:
            if is_debug:
                sys.stderr.write(err_msg)
                sys.stderr.write(f"{colour} stack does not exist at {coords_from}.")
            return False

        # check there are enough tokens required for the move
        n_tokens_origin = self.board_state[colour][coords_from]
        if n_tokens_origin < n_tokens:
            if is_debug:
                sys.stderr.write(err_msg)
                sys.stderr.write(
                f"Not enough tokens to move. {n_tokens_origin} token(s) at {coords_from}."
                )
            return False

        # check that the move is in a cardinal direction, i.e.
        coords_diff = (x_to - x_from, y_to - y_from)
        cardinal_move = 0
        if cardinal_move not in coords_diff:
            if is_debug:
                sys.stderr.write(err_msg)
                sys.stderr.write("This is not a move in a cardinal direction!")
            return False

        # check that the number of squares to move is less than
        # or equal to the origin stack height
        n_squares_move = abs(coords_diff[0] + coords_diff[1])
        if n_squares_move > n_tokens_origin:
            if is_debug:
                sys.stderr.write(err_msg)
                sys.stderr.write(
                    f"Cannot move {n_squares_move} squares from a stack with height of \
                        {n_tokens_origin}."
                )
                sys.stderr.write("Can only move up to n squares from a stack of n tokens high.")
            return False

        # check if an opponent's stack exists at destination
        opponents_colour = "black" if colour == "white" else "white"
        if coords_to in self.board_state[opponents_colour]:
            if is_debug:
                sys.stderr.write(err_msg)
                sys.stderr.write("Opponent's stack already exists here!")
            return False

        # everything above is okay, so the move is legal
        return True
    # TODO: perhaps refactor - move to AI class
    def get_candidate_actions(self, colour, n_tokens, x_from, y_from):
        """
        Finds all legal moves from the current position to another position
        """
        candidate_moves = {}
        candidate_moves2 = []
        for i in range(1, n_tokens + 1):
            for j in range(1, n_tokens + 1):
                for coords_diff in {(i, 0), (-i, 0), (0, i), (0, -i)}:
                    x_to = x_from + coords_diff[0]
                    y_to = y_from + coords_diff[1]
                    n_tokens_move = j
                    if self.is_legal_move(colour, n_tokens_move, x_from, y_from, x_to, y_to, False):
                        candidate_moves2.append([0, x_from, y_from, x_to, y_to, n_tokens_move])
                        if (x_to, y_to) in candidate_moves:
                            candidate_moves[(x_to, y_to)].append(n_tokens_move)
                        else:
                            candidate_moves[(x_to, y_to)] = [n_tokens_move]
        candidate_actions = {'boom': (x_from, y_from), 'move': candidate_moves}
        candidate_moves2.append([1, x_from, y_from, -1, -1, -1])
        candidate_actions2 = candidate_moves2
        return candidate_actions2

    def boom(self, colour, x, y):
        """ 
        Blows up a 3x3 square region, recursively calling itself on any stacks within the
        region.
        """
        coords = (x, y)
        # sys.stderr.write(f"boom() called by a {colour} stack at {coords}")
        # check for legal boom action
        if not self.is_legal_boom(colour, coords):
            return
        # delete the stack at the cell which called boom
        del self.board_state[colour][coords]

        # get a set of coords which represent all positions on board
        board_coords = {(i, j) for i in range(8) for j in range(8)}
        # find coords for within blast radius of 1 square (3x3 area) centered at (x, y)
        blast_radius = 1
        blast_coords = {
            (i, j)
            for i in range(x - blast_radius, x + blast_radius + 1)
            for j in range(y - blast_radius, y + blast_radius + 1)
        }
        # only the blast coordinates which are on the board are considered
        blast_coords = blast_coords.intersection(board_coords)
        # current stack at (x, y) has already been considered, so remove it
        blast_coords.remove(coords)
        # if a stack exists at one of the blast coords, then call boom on it
        for colour, colour_stacks in self.board_state.items():
            for coords in blast_coords:
                if coords in colour_stacks:
                    self.boom(colour, coords[0], coords[1])

    def is_legal_boom(self, colour, coords):
        # check that stack of correct colour exists at desired boom coordinates
        if coords not in self.board_state[colour]:
            # sys.stderr.write(f"No {colour} stack at {coords}!")
            return False
        return True
    
    @staticmethod
    def get_board_state_as_tuples(board_state):
        """
        Transforms the dictionary representation of the given board
        state into a fully immutable tuple representation.
        This representation can then be used for dictionary keys, or
        as set elements. Dicts and sets both have O(1) operations.
        Structure: 
        ((((x_0, y_0), n_0), ((x_1, y_1), n_1))_wh, (((x_0, y_0), n_0))_bl)
        """
        board_state = deepcopy(board_state)
        white_tuples = tuple(sorted(list(board_state['white'].items())))
        black_tuples = tuple(sorted(list(board_state['black'].items())))
        board_state_as_tuples = (white_tuples, black_tuples)
        return board_state_as_tuples

# TODO: maybe make AI fully independent of game. AI will take in a board object. 
# Pass a board and an ai_solution into Game() upon construction
class Game:
    def __init__(self, initial_board_state, ai_object=None):
        self.board = Board(initial_board_state)
        self.states_seen = defaultdict(int)
        self.ai_object = ai_object
        # create a list which contains all moves required to get to goal state
        # make a generator from this list, which will yield the actions one-by-one
        if ai_object is not None:
            # TODO: might need to have a ai_object.set_game(self) so that the AI can store the game?
            self.ai_solution = ai_object.get_solution(self.board)
            self.ai_solution_generator = (action for action in self.ai_solution)

    def get_board_dict(self):
        """
        Returns the board dict for printing purposes
        """
        return self.board.get_board_dict()

    def get_next_move(self, colour):
        """
        Figures out next move. This is where the AI search algorithm goes...
        For now, this just takes user input so that we can test our scaffolding.
        """
        # sys.stderr.write(f"{colour}'s turn:")
        # AI play mode
        if self.ai_object is not None:
            next_action = next(self.ai_solution_generator)
            # TODO: fix up unpacking once action data structure is known
            # [is_boom, n_tokens, x_from, y_from, x_to, y_to] = next_action
            return next_action

        # manual play mode
        else:
            # print out heuristic value
            height_cost_factor = 2
            heuristic_value = self.heuristic_simple(self.board.board_state, height_cost_factor)
            print(f"heuristic_value: {heuristic_value}")

            # boom action or not? 0 or 1
            is_boom = input("is_boom: ")
            while is_boom not in {0, 1}:
                try:
                    is_boom = bool(int(is_boom))
                except:
                    is_boom = input("is_boom: ")

            # x coord from target stack
            x_from = input("x_from: ")
            while not isinstance(x_from,int):
                try:
                    x_from = int(x_from)
                except:
                    x_from = input("x_from: ")

            # y coord from target stack
            y_from = input("y_from: ")
            while not isinstance(y_from, int):
                try:
                    y_from = int(y_from)
                except:
                    y_from = input("y_from: ")

            if is_boom:
                x_to = x_from
                y_to = y_from
                n_tokens = 0
            # if not boom, then choose destination and number of tokens to move
            else:
                x_to = input("x_to: ")
                while not isinstance(x_to, int):
                    try:
                        x_to = int(x_to)
                    except:
                        x_to = input("x_to: ")

                y_to = input("y_to: ")
                while not isinstance(y_to, int):
                    try:
                        y_to = int(y_to)
                    except:
                        y_to = input("y_to:")

                n_tokens = input("n_tokens: ")
                while not isinstance(n_tokens, int):
                    try:
                        n_tokens = int(n_tokens)
                    except:
                        n_tokens = input("n_tokens: ")
        
        return is_boom, x_from, y_from, x_to, y_to, n_tokens

    def move(self, colour, n_tokens, x_from, y_from, x_to, y_to):
        """
        Provides an interface to access Board's move method
        """
        self.board.move(colour, n_tokens, x_from, y_from, x_to, y_to)

    def boom(self, colour, x, y):
        """
        Provides an interface to access Board's boom method
        """
        self.board.boom(colour, x, y)

    def heuristic_simple(self, board_state, height_cost_factor):
        """
        This heuristic, or cost function, returns an integer cost for
        a particular board state. This informs our AI algorithm and allows
        prioritisation of actions

        This heuristic returns the sum of costs for each white stack, where:
            cost_per_stack = dist_to_black_stacks - dist_to_white_stacks + white_stack_heights
        """
        def manhattan_distance(coords_from, coords_to):
            x_dist = abs((coords_to[0] - coords_from[0]))
            y_dist = abs((coords_to[1] - coords_from[1]))
            total_dist = x_dist + y_dist
            return total_dist

        # TODO: get rid of double counting
        dist_to_black_stacks = 0
        dist_to_white_stacks = 0
        white_stack_heights = 0

        for white_stack_coords, height in board_state["white"].items():
            # penalise stacks greater than 1 token high
            if height > 1:
                white_stack_heights += height_cost_factor * height
            
            # get dist to other white stacks
            for other_white_stack_coords in board_state["white"]:
                if other_white_stack_coords == white_stack_coords:
                    continue
                # remove double counting between white stacks
                dist_to_white_stacks += int(manhattan_distance(white_stack_coords, other_white_stack_coords) / 2)
                
            # get dist to other black stacks
            for black_stack_coords in board_state["black"]:
                dist_to_black_stacks += manhattan_distance(white_stack_coords, black_stack_coords)

        total_cost = dist_to_black_stacks - dist_to_white_stacks + white_stack_heights
        return total_cost

    def max_repeated_states(self):
        """
        Updates self.states_seen with current state and 
        returns the maximum number of times any state has been
        seen so far
        """
        board_state_as_tuples = Board.get_board_state_as_tuples(self.board.board_state)
        self.states_seen[board_state_as_tuples] += 1

        max_repeated_states = max(self.states_seen.values())
        sys.stderr.write(f"max_repeated_states: {max_repeated_states} \n")
        return max_repeated_states


    # TODO: refactor method to pull out 'white_wins()', 'black_wins()', 'draw()'
    # so that get_AI_solution
    # TODO: implement self.max_repeated_states
    def game_has_ended(self, n_turns):
        # TODO: Implement draw conditions:
        # 1. One board configuration (with all stacks in the same position
        #    and quantity) occurs for a fourth time since the start of the game.
        #    These repeated board configurations do not need to occur in succession.
        # 2. Each player has had their 250th turn without a winner being declared.
        """
        Returns True if one of the colours (white or black) has no remaining
        stacks on the board, or if there is a draw event.

        *For Part A, if all pieces are eliminated, then white wins 
        (contrary to 2020-game-rules.pdf).
            Spec: 'If on your last turn you eliminate all enemy tokens but lose your
                   last token, you still win.'
        """
        game_has_not_ended = 0
        white_wins = 1
        black_wins = 2
        draw = 3        
        max_allowed_turns = 250
        max_allowed_repeated_states = 4
        num_white_stacks = len(self.board.board_state["white"])
        num_black_stacks = len(self.board.board_state["black"])
        max_repeated_states = self.max_repeated_states()

        if num_white_stacks == 0 and num_black_stacks == 0:
            sys.stderr.write("Draw: no stacks left on board \n")
            return draw

        if num_black_stacks == 0:
            sys.stderr.write("White wins: no black stacks are left on board \n")
            return white_wins

        if num_white_stacks == 0:
            sys.stderr.write("Black wins: no white stacks are left on board \n")
            return black_wins
        # TODO: check if this should be == or >
        if n_turns == max_allowed_turns:
            sys.stderr.write("Draw: maximum number of turns (250) reached \n")
            return draw
        # TODO: check if this should be == or >
        if max_repeated_states == max_allowed_repeated_states:
            sys.stderr.write("Draw: maximum number of repeated board configurations (4) reached \n")
            return draw

        return game_has_not_ended
