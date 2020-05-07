from RageAgainstTheSentientMachine.game import Board, Game

class ExamplePlayer:
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
        # TODO: 1. instantiate initial board
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
        # TODO: 2. instantiate game with board
        self.game = Game(initial_board_state)
        # TODO: 3. instantiate ai (pass in minimax as search)
        # TODO: do this better!
        self.ai_algorithm = None
        # if colour == "white":
        #     ai_algorithm = None
        # elif colour == "black":
        #     ai_algorithm = "alpha_beta_cutoff"
        # else:
        #     raise ValueError(f"colour is not 'black' or 'white'... colour: {colour}")

        # if ai_algorithm is not None:
        #     self.ai = AI(ai_algorithm)

    def action(self):
        """
        This method is called at the beginning of each of your turns to request 
        a choice of action from your program.

        Based on the current state of the game, your player should select and 
        return an allowed action to play on this turn. The action must be
        represented based on the spec's instructions for representing actions.
        """
        # if self.ai_algorithm is not None:
        #     action = self.ai.get_next_action()
        # else:
        action = self.game.get_next_action(self.colour)
        return action


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