from RageAgainstTheSentientMachine.game import Board, Game
from RageAgainstTheSentientMachine.util import print_move, print_boom, print_board
from RageAgainstTheSentientMachine.ai import AI

class AbstractPlayer:
    def __init__(self, colour):
        """
        This method is called once at the beginning of the game to initialise
        your player. You should use this opportunity to set up your own internal
        representation of the game state, and any other information about the 
        game state you would like to maintain for the duration of the game.

        The parameter colour will be a string representing the player your 
        program will play as (White or Black). The value will be one of the 
        strings "white" or "black" correspondingly.
        """
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

        self.game = Game(initial_board_state)


    def action(self):
        """
        This method is called at the beginning of each of your turns to request 
        a choice of action from your program.

        Based on the current state of the game, your player should select and 
        return an allowed action to play on this turn. The action must be
        represented based on the spec's instructions for representing actions.
        """
        pass


    def update(self, colour, action):
        """
        This method is called at the end of every turn (including your player’s 
        turns) to inform your player about the most recent action. You should 
        use this opportunity to maintain your internal representation of the 
        game state and any other information about the game you are storing.

        The parameter colour will be a string representing the player whose turn
        it is (White or Black). The value will be one of the strings "white" or
        "black" correspondingly.

        The parameter action is a representation of the most recent action
        conforming to the spec's instructions for representing actions.

        You may assume that action will always correspond to an allowed action 
        for the player colour (your method does not need to validate the action
        against the game rules).
        """
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
        # turn is over, so make sure we're keeping count
        self.game.n_turns += 1
        
class AIPlayer(AbstractPlayer):
    def __init__(self, colour):
        super().__init__(colour)
        ai_algorithm = "alpha_beta_cutoff"
        self.ai = AI(ai_algorithm, colour)
    
    # @override
    def action(self):
        board_dict = self.game.get_board_dict()
        print_board(board_dict, unicode=True)

        action = self.ai.get_next_action(self.game)
        return action

class ManualPlayer(AbstractPlayer):
    def __init__(self, colour):
        super().__init__(colour)

    def action(self):
        board_dict = self.game.get_board_dict()
        print_board(board_dict, unicode=True)

        action = self.game.get_next_action(self.colour)
        return action
