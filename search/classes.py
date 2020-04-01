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
    def __init__(self, initial_board_state):
        self.board_state = initial_board_state

    def get_board_dict(self):
        board_dict = {(i, j): "" for i in range(8) for j in range(8)}
        for colour, stacks in self.board_state.items():
            for coords, n_tokens in stacks.items():
                first_letter = colour[:2]
                board_dict[coords] = f"{n_tokens}-{first_letter}"
        return board_dict

    def move(self, colour, n_tokens, x_from, y_from, x_to, y_to):
        if not self.is_legal_move(colour, n_tokens, x_from, y_from, x_to, y_to):
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

    def is_legal_move(self, colour, n_tokens, x_from, y_from, x_to, y_to):
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
                print(err_msg)
                print(f"{coord} is not a valid coordinate value.")
                return False

        # check that move is not into same position
        if coords_from == coords_to:
            print(err_msg)
            print("Cannot move stack into same position!")
            return False

        # check origin stack exists
        if not coords_from in self.board_state[colour]:
            print(err_msg)
            print(f"{colour} stack does not exist at {coords_from}.")
            return False

        # check there are enough tokens required for the move
        n_tokens_origin = self.board_state[colour][coords_from]
        if n_tokens_origin < n_tokens:
            print(err_msg)
            print(
                f"Not enough tokens to move. {n_tokens_origin} token(s) at {coords_from}."
            )
            return False

        # check that the move is in a cardinal direction, i.e.
        coords_diff = (x_to - x_from, y_to - y_from)
        cardinal_move = 0
        if cardinal_move not in coords_diff:
            print(err_msg)
            print("This is not a move in a cardinal direction!")
            return False

        # check that the number of squares to move is less than
        # or equal to the origin stack height
        n_squares_move = abs(coords_diff[0] + coords_diff[1])
        if n_squares_move > n_tokens_origin:
            print(err_msg)
            print(
                f"Cannot move {n_squares_move} squares from a stack with height of \
                    {n_tokens_origin}."
            )
            print("Can only move up to n squares from a stack of n tokens high.")
            return False

        # check if an opponent's stack exists at destination
        opponents_colour = "black" if colour == "white" else "white"
        if coords_to in self.board_state[opponents_colour]:
            print(err_msg)
            print("Opponent's stack already exists here!")
            return False

        # everything above is okay, so the move is legal
        return True

    def boom(self, colour, x, y):
        """ 
        Blows up a 3x3 square region, recursively calling itself on any stacks within the
        region.
        """
        coords = (x, y)
        print(f"boom() called by a {colour} stack at {coords}")
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
            print(f"No {colour} stack at {coords}!")
            return False
        return True


class Game:
    def __init__(self, initial_board_state, AI_algorithm_function=None):
        self.board = Board(initial_board_state)
        self.AI_algorithm_function = AI_algorithm_function

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
        print(f"{colour}'s turn:")
        if self.AI_algorithm_function == None:
            is_boom = bool(int(input("is_boom: ")))
            x_from = int(input("x_from: "))
            y_from = int(input("y_from: "))
            if is_boom:
                x_to = x_from
                y_to = y_from
                n_tokens = 0
            else:
                x_to = int(input("x_to: "))
                y_to = int(input("y_to: "))
                n_tokens = int(input("n_tokens: "))
        else:
            [is_boom, n_tokens, x_from, y_from, x_to, y_to] = AI_algorithm_function(
                board
            )

        return is_boom, n_tokens, x_from, y_from, x_to, y_to

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

    def game_has_ended(self):
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
        num_white_stacks = len(self.board.board_state["white"])
        num_black_stacks = len(self.board.board_state["black"])
        if num_white_stacks == 0 and num_black_stacks == 0:
            print("White wins: no stacks left on board")
            return True
        if num_black_stacks == 0:
            print("White wins: no black stacks are left on board")
            return True
        if num_white_stacks == 0:
            print("Black wins: no white stacks are left on board")
            return True

        return False
