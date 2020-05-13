import sys
import numpy as np

from RageAgainstTheSentientMachine.game import Board, Game


class AI:
    def __init__(self, ai_algorithm, colour):
        self.ai_algorithm = ai_algorithm
        self.colour = colour
        self.opponent_colour = "black" if colour == "white" else "white"

    def get_next_action(self, game):
        """
        Calls the desired AI algorithm with the current game configuration.
        Returns the next action as chosen by the AI alg.
        """

        lookup_ai_search_alg = {
            "alpha_beta_cutoff": self.alpha_beta_cutoff,
        }
        ai_search_alg = lookup_ai_search_alg[self.ai_algorithm]

        next_action = ai_search_alg(game)

        # sys.stderr.write(f"next_action: {next_action} \n")
        return next_action

    def alpha_beta(self, game):
        """
        Code adapted from AIMA repository:
        https://github.com/aimacode/aima-python/blob/master/games.py
        """

        def max_value(game, alpha, beta):
            if self.terminal_test(game):
                return self.utility_function(game)
            value = -np.inf
            for action in self.get_candidate_actions(game):
                value = max(value, min_value(self.apply_action(game, action), alpha, beta))
                if value >= beta:
                    return value
                alpha = max(alpha, value)
            return value
            
        def min_value(game, alpha, beta):
            if self.terminal_test(game):
                return self.utility_function(game)
            value = np.inf
            for action in self.get_candidate_actions(game):
                value = min(value, max_value(self.apply_action(game, action), alpha, beta))
                if value <= alpha:
                    return value
                beta = min(beta, value)
            return value

        best_score = -np.inf
        beta = np.inf
        best_action = None
        for action in self.get_candidate_actions(game):
            value = min_value(self.apply_action(game, action), best_score, beta)
            if value > best_score:
                best_score = value
                best_action = action
        return best_action

    def alpha_beta_cutoff(self, game, d=2, cutoff_test=None, evaluation_function=None):
        """
        Code adapted from AIMA repository:
        https://github.com/aimacode/aima-python/blob/master/games.py
        """
        colour = self.colour
        opponent_colour = self.opponent_colour

        ## playing around with cutoff depths...
        # d = 2 if colour == "black" else 0
        
        # if colour == "black":
        #     d = 0
        # elif colour == "white":
        #     if sum(game.board.board_state[colour].values()) != 12 or sum(game.board.board_state[colour].values()) != 12:
        #         d = 2
        #         sys.stderr.write(f"changing to d={d}! \n")

        def max_value(game, alpha, beta, depth):
            if cutoff_test(game, depth):
                return evaluation_function(game)
            value = -np.inf
            for action in self.get_candidate_actions(game, colour):
                value = max(value, min_value(self.apply_action(game, action, colour), alpha, beta, depth + 1))
                if value >= beta:
                    return value
                alpha = max(alpha, value)
            return value
            
        def min_value(game, alpha, beta, depth):
            if cutoff_test(game, depth):
                return evaluation_function(game)
            value = np.inf
            for action in self.get_candidate_actions(game, opponent_colour):
                value = min(value, max_value(self.apply_action(game, action, opponent_colour), alpha, beta, depth + 1))
                if value <= alpha:
                    return value
                beta = min(beta, value)
            return value

        cutoff_test = cutoff_test or (lambda game, depth: depth > d or self.terminal_test(game))
        evaluation_function = evaluation_function or (lambda game: self.utility_function(game)) # change to self.evaluation_function?

        best_score = -np.inf
        beta = np.inf
        depth = 1
        best_action = None
        for action in self.get_candidate_actions(game, colour):
            value = min_value(self.apply_action(game, action, colour), best_score, beta, depth)
            if value > best_score:
                best_score = value
                best_action = action
        return best_action

    def get_candidate_actions(self, game, colour):
        candidate_actions = game.get_candidate_actions(colour)

        return candidate_actions

    def apply_action(self, game, action, colour):
        """
        This is the 'Transition Model'
        Returns a new bame (state/vertex) by applying an action (edge)
        """
        new_game = game.deepcopy() # deepcopy(game)

        if action[0] == "BOOM":
            x_from, y_from = action[1]
            new_game.boom(colour, x_from, y_from)
        else:
            n_tokens = action[1]
            x_from, y_from = action[2]
            x_to, y_to = action[3]
            new_game.move(colour, n_tokens, x_from, y_from, x_to, y_to)
        return new_game

    def terminal_test(self, game):
        return game.game_has_ended(self.colour)

    def utility_function(self, game):
        """
        This simple utility function just returns +/- 12 for the player/opponent
        winning, 0 for a draw, or the difference in tokens if the game is not yet over (eval func)
        """
        colour = self.colour

        GAME_HAS_NOT_ENDED = 0
        PLAYER_WINS = 1
        OPPONENT_WINS = 2
        DRAW = 3
        
        result = game.game_has_ended(colour)
        if result == GAME_HAS_NOT_ENDED:
            utility_value = self.evaluation_function(game)
        elif result == PLAYER_WINS:
            utility_value = 12
        elif result == OPPONENT_WINS:
            utility_value = -12
        elif result == DRAW:
            utility_value = 0

        # # this block is the same as above, just a bit cleaner to use a dict
        # utility_value = {
        #     GAME_HAS_NOT_ENDED: self.evaluation_function(game),
        #     PLAYER_WINS: 12,
        #     OPPONENT_WINS: -12,
        #     DRAW: 0
        # }
        
        return utility_value # utility_value[result]

    def evaluation_function(self, game):
        """
        This simple evaluation function just returns the difference between
        the number of tokens on the board at any time
        """
        colour = self.colour
        opponent_colour = self.opponent_colour
        num_player_tokens = sum(game.board.board_state[colour].values())
        num_opponent_tokens = sum(game.board.board_state[opponent_colour].values())
        return num_player_tokens - num_opponent_tokens

    def cutoff_test(self, game):
        pass

class AIU2(AI):
    def __init__(self, ai_algorithm, colour):
        super().__init__(ai_algorithm, colour)
    
    # @override
    def utility_function(self, game):
        """
        This simple utility function just returns +/- 12 for the player/opponent
        winning, 0 for a draw, or the difference in tokens if the game is not yet over (eval func)
        """
        colour = self.colour
        opponent_colour = self.opponent_colour
        
        GAME_HAS_NOT_ENDED = 0
        PLAYER_WINS = 1
        OPPONENT_WINS = 2
        DRAW = 3
        
        result = game.game_has_ended(colour)
        if result == GAME_HAS_NOT_ENDED:
            n_player_tokens = sum(game.board.board_state[colour].values())
            n_opponent_tokens = sum(game.board.board_state[opponent_colour].values())
            utility_value = (n_player_tokens - n_opponent_tokens) / (n_player_tokens + n_opponent_tokens)
            # push utility values away from zero, so a draw (0) is less desirable than n_player_tokens = n_opponent_tokens
            # # white's turn
            # if game.n_turns % 2 == 0: utility_value += 1
            # # black's turn
            # elif game.n_turns % 2 == 1: utility_value -= 1
            # else: raise ValueError(f"Something went wrong! game.n_turns: {game.n_turns}")
        elif result == PLAYER_WINS:
            utility_value = 12
        elif result == OPPONENT_WINS:
            utility_value = -12
        elif result == DRAW:
            utility_value = 0

        
        
        return utility_value
      
            