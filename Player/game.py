import sys
from copy import deepcopy

#class Coords:   ########### NNNOTTTT USED
"""
A class to represent a coordinate pair on the board.
At the moment this class is not used. 

This class could implement methods 'is_cardinal_direction()', 'dist()', 'is_on_board()'
"""

   # def __init__(self, x, y):
    #    self.x = x
     #   self.y = y


#class Stack:    ########### NNNOTTTT USED
"""
A class to represent a stack of tokens. At the moment this class is not used and 
each stack is just represented by a '(x, y): n' pair within the board_state dictionary
in the Board class.

If we wanted to push the OOP design, we could use this class,
or even a namedtuple object...
"""

   # def __init__(self, n, coords, colour):
    #    self.n = n
     #   self.coords = coords
      #  self.colour = colour

















class Board:
   
    #def __init__(self, board_state):
    #    self.board_state = board_state
    
        ############ NEW ADDED JAMES   ######################
        
    def __init__(self):
        self.board_state = self.start_game_board()


    def get_board_dict(self):
        board_dict = {(i, j): "" for i in range(8) for j in range(8)}
        for colour, stacks in self.board_state.items():
            for coords, n_tokens in stacks.items():
                first_letter = colour[:2]
                board_dict[coords] = f"{n_tokens}-{first_letter}"
        return board_dict


    def get_board_state(self):
        return self.board_state


        ############ NEW ADDED JAMES   ######################
        
    def get_active_pieces(self,colour):
        tuples = tuple(sorted(list(self.board_state[colour].items())))
        return tuples
        
        
    def get_all_candidate_actions(self, colour):
        candidate_actions = []
        # for each stack get a list of legal actions
        for coords, n_tokens in self.board_state[colour].items():
            candidate_actions_stack = self.get_candidate_actions(colour, n_tokens, coords[0], coords[1])
            candidate_actions.extend(candidate_actions_stack)

        return candidate_actions
    
    
    def apply_action(self, action,colour):
        """
        This is the 'Transition Model'
        Returns a new board (state/vertex) by applying an action (edge)
        """
        # need to set up a replica here so that we don't mutate board.board_state
       # board_state_replica = deepcopy(self.board_state)
        #new_board = Board(board_state_replica)
        
        new_board = deepcopy(self)
        
        [is_boom, x_from, y_from, x_to, y_to, n_tokens] = action
        if is_boom:
            new_board.boom(colour, x_from, y_from)
        else:
            new_board.move(colour, n_tokens, x_from, y_from, x_to, y_to)
        return new_board
    
    
        ############ NEW ADDED JAMES   ######################

    def get_white_count(self):
        count = 0
        for key, value in self.board_state["white"].items():
            count = count + value
        return count

    def get_black_count(self):
        count = 0
        for key, value in self.board_state["black"].items():
            count = count + value
        return count

    def terminal_state(self):
        white = self.get_white_count()
        black = self.get_black_count()
        
        if white == 0 or black == 0:
            return True
        else:
            return False

    def heuristic_simple(self, height_cost_factor,colour,opp_colour):
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
        
        board_state = self.board_state

        for white_stack_coords, height in board_state[colour].items():
            # penalise stacks greater than 1 token high
            if height > 1:
                white_stack_heights += height_cost_factor * height
            
            # get dist to other white stacks
            for other_white_stack_coords in board_state[colour]:
                if other_white_stack_coords == white_stack_coords:
                    continue
                # remove double counting between white stacks
                dist_to_white_stacks += int(manhattan_distance(white_stack_coords, other_white_stack_coords) / 2)
                
            # get dist to other black stacks
            for black_stack_coords in board_state[opp_colour]:
                dist_to_black_stacks += manhattan_distance(white_stack_coords, black_stack_coords)

        total_cost = dist_to_black_stacks - dist_to_white_stacks + white_stack_heights 
        return total_cost
    
    
    
    
    
    def terminal_state_score(self,colour):
        white = self.get_white_count()
        black = self.get_black_count()
        
        if colour == "white":
            return white - black
        else:
            return black - white
        
        
                
    def utility(self, height_cost_factor,colour,opp_colour):
        terminal_score = self.terminal_state_score(colour)
        heuristic = self.heuristic_simple(height_cost_factor,colour,opp_colour)
        return terminal_score * 100 - heuristic * 0.001
        
        

        
        
    '''
        
        
    def terminal_state_score(self,colour):
        white = self.get_white_count()
        black = self.get_black_count()
        
        if colour == "white":
            endScore = white - black
        else:
            endScore = black - white
        
    '''    

        
        
        
        
        
        
        
        
        
        
        
        
    
    ############ NEW ADDED JAMES   ######################
    def start_game_board(self):

        start_board_state = {}
        X = [0,1,2,3,4,5,6,7]
        whiteY = [0,1]
        blackY = [6,7]
        stacks_dictB = {}
        stacks_dictW = {}
        for i in range(len(X)):
            for j in range(len(whiteY)):
                coords = (X[i],whiteY[j])
                stacks_dictW[coords] = 1
            start_board_state['white'] = stacks_dictW
            
            for j in range(len(blackY)):
                coords = (X[i],blackY[j])
                stacks_dictB[coords] = 1
            start_board_state['black'] = stacks_dictB
        return start_board_state


    def rest_game_board(self):
        self.board_state = self.start_game_board()


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






