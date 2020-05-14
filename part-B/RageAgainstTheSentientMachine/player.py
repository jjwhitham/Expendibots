import sys

from RageAgainstTheSentientMachine.game import Board, Game
from RageAgainstTheSentientMachine.util import print_move, print_boom, print_board
from RageAgainstTheSentientMachine.ai import AI, AIU2, AIGreedy, AIRandom, AIGreedyBoom

class AbstractPlayer:
    def __init__(self, colour):
        self.colour = colour
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
        board = Board(initial_board_state)
        self.game = Game(board)

    def action(self):
        pass

    def update(self, colour, action):
        if action[0] == "BOOM":
            x, y = action[1]
            self.game.boom(colour, x, y)
        elif action[0] == "MOVE":
            n_tokens = action[1]
            x_from, y_from = action[2]
            x_to, y_to = action[3]
            self.game.move(colour, n_tokens, x_from, y_from, x_to, y_to)
        else:
            raise ValueError(f"Received invalid action: {action}")

        
class AIPlayer(AbstractPlayer):
    def __init__(self, colour):
        super().__init__(colour)
        # TODO: make ai_algorithm default parameter
        ai_algorithm = "alpha_beta_cutoff"
        self.ai = AI(ai_algorithm, colour)
    
    # @override
    def action(self):
        action = self.ai.get_next_action(self.game)
        return action

class AIPlayerU2(AIPlayer):
    def __init__(self, colour):
        super().__init__(colour)
        ai_algorithm = "alpha_beta_cutoff"
        self.ai = AIU2(ai_algorithm, colour)

class AIPlayerGreedyBoom(AIPlayer):
    def __init__(self, colour):
        super().__init__(colour)
        ai_algorithm = "alpha_beta_cutoff"
        self.ai = AIGreedyBoom(ai_algorithm, colour)

class AIPlayerGreedy(AIPlayer):
    def __init__(self, colour):
        super().__init__(colour)
        ai_algorithm = "alpha_beta_cutoff"
        self.ai = AIGreedy(ai_algorithm, colour)

class AIPlayerRandom(AIPlayer):
    def __init__(self, colour):
        super().__init__(colour)
        ai_algorithm = "alpha_beta_cutoff"
        self.ai = AIRandom(ai_algorithm, colour)

class ManualPlayer(AbstractPlayer):
    def __init__(self, colour):
        super().__init__(colour)

    # @override
    def action(self):
        action = self.game.get_next_action(self.colour)
        return action
