import sys
from collections import defaultdict
from copy import deepcopy

class Board:
    """
    Board holds the state of the game board and provides methods for
    representing it and mutating it.
    """
    def __init__(self, board_state):
        self.board_state = board_state

    def get_board_dict(self):
        """
        For printing the board with util.print_board()
        """
        board_dict = {(i, j): "" for i in range(8) for j in range(8)}
        for colour, stacks in self.board_state.items():
            for coords, n_tokens in stacks.items():
                first_letter = colour[:2]
                board_dict[coords] = f"{n_tokens}-{first_letter}"
        return board_dict

    def move(self, colour, n_tokens, x_from, y_from, x_to, y_to):
        # sys.stderr.write("move called")
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
    
    def boom(self, colour, x, y):
        """ 
        Blows up a 3x3 square region, recursively calling itself on any stacks within the
        region.
        """
        coords = (x, y)
        # sys.stderr.write(f"boom() called by a {colour} stack at {coords}")

        # delete the stack at the cell which called boom
        del self.board_state[colour][coords]

        # get a set of coords which represent all positions on board
        board_coords = {(i, j) for i in range(8) for j in range(8)}
        # find coords for within blast radius of 1 square (3x3 area) centred at (x, y)
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
    
    def deepcopy(self):
        board_state = self.board_state
        return self._deepcopy(board_state)    
    @classmethod
    def _deepcopy(cls, board_state):
        new_board_state = {}
        for colour in board_state:
            new_board_state[colour] = {coords: n_tokens for coords, n_tokens in board_state[colour].items()}
        return cls(new_board_state)

    @staticmethod
    def get_board_state_as_tuples(board_state):
        """
        Transforms the dictionary representation of the given board
        state into a fully immutable tuple representation.
        This representation can then be used for dictionary keys, or
        as set elements. Dicts and sets both have O(1) operations.
        Structure:
        ((((x_0, y_0), n_0), ((x_1, y_1), n_1), ...,)_wh, (((x_0, y_0), n_0), ...,)_bl)
        """
        white_tuples = tuple(sorted(board_state['white'].items()))
        black_tuples = tuple(sorted(board_state['black'].items()))
        board_state_as_tuples = (white_tuples, black_tuples)
        return board_state_as_tuples


class Game:
    """
    Game holds the state of the game with board object, repeated states_seen,
    current number of turns n_turns.
    Provides methods for updating game state, checking game rules, taking user input
    for manual play, 
    """
    def __init__(self, board, states_seen=None, n_turns=0):
        self.board = board
        self.states_seen = states_seen
        self.n_turns = n_turns
        if states_seen == None:
            self.states_seen = defaultdict(int)
            self.update_repeated_states()
        
    def get_board_dict(self):
        """
        Returns the board dict for printing purposes
        """
        return self.board.get_board_dict()

    def get_next_action(self, colour):
        """
        Allows the game to be played manually by taking input from stdin.
        """
        # sys.stderr.write(f"{colour}'s turn:")

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
    
        if is_boom:
            action = ("BOOM", (x_from, y_from))
        else:
            action = ("MOVE", n_tokens, (x_from, y_from), (x_to, y_to))
        return action

    def move(self, colour, n_tokens, x_from, y_from, x_to, y_to):
        """
        Provides an interface to access Board's move method
        """
        if not self.is_legal_move(colour, n_tokens, x_from, y_from, x_to, y_to, True):
            return
        self.board.move(colour, n_tokens, x_from, y_from, x_to, y_to)
        self.update_repeated_states()
        self.n_turns += 1

    def boom(self, colour, x, y):
        """
        Provides an interface to access Board's boom method
        """
        # check for legal boom action
        coords = (x, y)
        if not self.is_legal_boom(colour, coords):
            sys.stderr.write("Boom by {colour} at {coords} is not legal! \n")
            return
        self.board.boom(colour, x, y)
        self.update_repeated_states()
        self.n_turns += 1
    
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
        err_msg = "Illegal Move: "

        # TODO: could be sped up by checking:
        #  board_coords = {(i, j) for i in range(8) for j in range(8)} <- make this a class variable
        #  if (coords_from not in board_coords) or (coords_to not in board_coords): return False
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
        if not coords_from in self.board.board_state[colour]:
            if is_debug:
                sys.stderr.write(err_msg)
                sys.stderr.write(f"{colour} stack does not exist at {coords_from}.")
            return False

        # check there are enough tokens required for the move
        n_tokens_origin = self.board.board_state[colour][coords_from]
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
        if coords_to in self.board.board_state[opponents_colour]:
            if is_debug:
                sys.stderr.write(err_msg)
                sys.stderr.write("Opponent's stack already exists here!")
            return False

        # everything above is okay, so the move is legal
        return True

    def get_candidate_actions(self, colour):
        """
        Finds all legal moves for a particular player, designated by colour.
        An AI object calls this method to find out what moves are possible.
        """
        def get_candidate_actions_stack(colour, n_tokens, x_from, y_from):
            """
            Finds all the legal moves for a particular stack.
            """
            candidate_actions_stack = []

            # MOVE j tokens
            for j in range(n_tokens, 0, -1):
                # MOVE i squares
                for i in range(n_tokens, 0, -1):
                    coords_diffs = [(0, i), (-i, 0), (i, 0), (0, -i)]
                    if colour == "black":
                        coords_diffs.reverse() # black looks from the other direction
                    for coords_diff in coords_diffs: # {(i, 0), (-i, 0), (0, i), (0, -i)}:
                        # TODO: get rid of illegal coordinates right here. Check for membership with board coords
                        x_to = x_from + coords_diff[0]
                        y_to = y_from + coords_diff[1]
                        n_tokens_move = j
                        if self.is_legal_move(colour, n_tokens_move, x_from, y_from, x_to, y_to, False):
                            candidate_actions_stack.append(("MOVE", n_tokens_move, (x_from, y_from), (x_to, y_to)))
            return candidate_actions_stack

        def sort_stacks(colour_tups, colour):
            colour_tups = sorted(colour_tups, key=lambda tup: tup[1])
            if colour == "white":
                colour_tups = sorted(colour_tups, key=lambda tup: tup[0])
            elif colour == "black":
                colour_tups = sorted(colour_tups, key=lambda tup: tup[0], reverse=True)
            else:
                raise ValueError(f"Something went wrong, colour: {colour}")
            return colour_tups


        # for each stack get a list of legal actions
        candidate_actions = []

        # TODO: Move ordering - keep BOOM first?
        # BOOMs
        for coords, n_tokens in self.board.board_state[colour].items():
            x_from, y_from = coords[0], coords[1]
            candidate_actions.append(("BOOM", (x_from, y_from)))
        # MOVEs

        stacks_tuples = tuple(self.board.board_state[colour].items())
        stacks_sorted = sort_stacks(stacks_tuples, colour)
        
        for tup in stacks_sorted:
            x_from, y_from, n_tokens = tup[0][0], tup[0][1], tup[1]
            candidate_actions_stack = get_candidate_actions_stack(colour, n_tokens, x_from, y_from)
            candidate_actions.extend(candidate_actions_stack)         
        return candidate_actions
 
    def is_legal_boom(self, colour, coords):
        # check that stack of correct colour exists at desired boom coordinates
        if coords not in self.board.board_state[colour]:
            sys.stderr.write(f"is_legal_boom(): No {colour} stack at {coords}!")
            return False
        return True
    
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

    def update_repeated_states(self):
        """
        Updates self.states_seen with current state.
        """
        board_state_as_tuples = Board.get_board_state_as_tuples(self.board.board_state)
        self.states_seen[board_state_as_tuples] += 1
        # sys.stderr.write(f"max_states_seen: {max(self.states_seen.values())} \n")

    def game_has_ended(self, colour):
        """
        Returns integer value for each game outcome:
            0 - ongoing game, 1 - player won, 2- opponent won, 3 - draw.
        """
        GAME_HAS_NOT_ENDED = 0
        PLAYER_WINS = 1
        OPPONENT_WINS = 2
        DRAW = 3        
        MAX_ALLOWED_TURNS = 500 # update() is called at the end of every turn, so 500 turns altogether
        MAX_ALLOWED_REPEATED_STATES = 4
        opponent_colour = "black" if colour == "white" else "white"
        num_player_tokens = sum(self.board.board_state[colour].values())
        num_opponent_tokens = sum(self.board.board_state[opponent_colour].values())

        if num_player_tokens == 0 and num_opponent_tokens == 0:
            # sys.stderr.write("Draw: no stacks left on board \n")
            return DRAW

        if num_opponent_tokens == 0:
            # sys.stderr.write(f"{colour} wins: no opponent stacks are left on board \n")
            return PLAYER_WINS

        if num_player_tokens == 0:
            # sys.stderr.write(f"{opponent_colour} wins: no player stacks are left on board \n")
            return OPPONENT_WINS

        if self.n_turns == MAX_ALLOWED_TURNS:
            sys.stderr.write("Draw: maximum number of turns/player (250) reached \n")
            return DRAW

        max_repeated_states = max(self.states_seen.values())
        if max_repeated_states == MAX_ALLOWED_REPEATED_STATES:
            sys.stderr.write("Draw: maximum number of repeated board configurations (4) reached \n")
            return DRAW

        return GAME_HAS_NOT_ENDED

    def deepcopy(self):
        board = self.board.deepcopy()
        states_seen = self.states_seen.copy() # copy is sufficiently deep here (tested in Python 3.6.3 shell)
        n_turns = self.n_turns
        return self._deepcopy(board, states_seen, n_turns)
    @classmethod
    def _deepcopy(cls, board, states_seen, n_turns):
        return cls(board, states_seen, n_turns)