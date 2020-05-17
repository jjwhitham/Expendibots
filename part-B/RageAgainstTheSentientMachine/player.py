import sys
import numpy as np
import random

from RageAgainstTheSentientMachine.game import Board, Game
from RageAgainstTheSentientMachine.util import print_move, print_boom, print_board


class AbstractPlayer:
    def __init__(self, colour):
        self.colour = colour
        initial_board_state = {
                'white': {
                    (0, 0): 1, (1, 0): 1, (3, 0): 1, (4, 0): 1, (6, 0): 1, (7, 0): 1,
                    (0, 1): 1, (1, 1): 1, (3, 1): 1, (4, 1): 1, (6, 1): 1, (7, 1): 1,
                },
                'black': {
                    (7, 7): 1, (6, 7): 1, (4, 7): 1, (3, 7): 1, (1, 7): 1, (0, 7): 1,
                    (7, 6): 1, (6, 6): 1, (4, 6): 1, (3, 6): 1, (1, 6): 1, (0, 6): 1,
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


class ManualPlayer(AbstractPlayer):
    def __init__(self, colour):
        super().__init__(colour)

    # @override
    def action(self):
        action = self.game.get_next_action(self.colour)
        return action

        
class AIPlayer(AbstractPlayer):
    def __init__(self, colour, ai_algorithm="alpha_beta_cutoff", depth=2):
        super().__init__(colour)
        self.ai_algorithm = ai_algorithm
        self.colour = colour
        self.opponent_colour = "black" if colour == "white" else "white"
        self.depth = depth

    # @override
    def action(self):
        """
        Calls the desired AI algorithm with the current game configuration.
        Returns the next action as chosen by the AI alg.
        """
        game = self.game
        # print(f"heuristic_simple: {game.heuristic_simple(game.board.board_state, 0)}")

        lookup_ai_search_alg = {
            "alpha_beta_cutoff": self.alpha_beta_cutoff,
        }
        ai_search_alg = lookup_ai_search_alg[self.ai_algorithm]

        next_action = ai_search_alg(game, d=self.depth)
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
    # TODO: get rid of cutoff and eval params
    def alpha_beta_cutoff(self, game, d=2, cutoff_test=None, evaluation_function=None):
        """
        Code adapted from AIMA repository:
        https://github.com/aimacode/aima-python/blob/master/games.py
        """
        colour = self.colour
        opponent_colour = self.opponent_colour



        ## playing around with cutoff depths...
        # d = 2 if colour == "black" else 1

        pieces_remaining = sum(game.board.board_state[colour].values()) + sum(game.board.board_state[colour].values())
        d = 2
        if colour == "black":
            if pieces_remaining <= 20:
                d = 4
                sys.stderr.write(f"changing to d={d}! \n")
            d = 4
        elif colour == "white":
            if pieces_remaining <= 8:
                d = 4
                sys.stderr.write(f"changing to d={d}! \n")
            elif pieces_remaining <= 16:
                d = 3
                sys.stderr.write(f"changing to d={d}! \n")
            elif pieces_remaining <= 20:
                d = 3
                sys.stderr.write(f"changing to d={d}! \n")
            
            

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
        new_game = game.deepcopy()

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
            # from white's perspective
            utility_value = self.evaluation_function(game)
            # if game.n_turns % 2 == 0 and colour == "white":
            #     utility_value -= 0.001 * game.heuristic_simple(game.board.board_state, 0)
            
        elif result == PLAYER_WINS:
            utility_value = 1000 # np.inf
        elif result == OPPONENT_WINS:
            utility_value = -1000 # -np.inf
        elif result == DRAW:
            utility_value = 0
            # # Introduce 'contempt' to avoid draw states
            # # from white's perspective
            # if game.n_turns % 2 == 0:
            #     utility_value = -12
            # # from black's perspective
            # else:
            #     utility_value = 12
        
        return utility_value

    def evaluation_function(self, game):
        """
        This simple evaluation function just returns the difference between
        the number of tokens on the board at any time
        """
        colour = self.colour
        opponent_colour = self.opponent_colour
        num_player_tokens = sum(game.board.board_state[colour].values())
        num_opponent_tokens = sum(game.board.board_state[opponent_colour].values())
        remaining_tokens = num_player_tokens + num_opponent_tokens
        evaluation = (num_player_tokens - num_opponent_tokens) * (25 - remaining_tokens)
        return evaluation


class AIPlayerU2(AIPlayer):
    def __init__(self, colour):
        super().__init__(colour)

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
  

class AIPlayerGreedy(AIPlayer):
    def __init__(self, colour):
        super().__init__(colour, depth=0)


class AIPlayerRandom(AIPlayer):
    def __init__(self, colour):
        super().__init__(colour)

    # @override
    def action(self):
        actions = self.game.get_candidate_actions(self.colour)
        return random.choice(actions)


class AIPlayerGreedyBoom(AIPlayer):
    def __init__(self, colour, depth=1):
        super().__init__(colour, depth=depth)

    # @override
    def alpha_beta_cutoff(self, game, d=2, cutoff_test=None, evaluation_function=None):
        """
        Code adapted from AIMA repository:
        https://github.com/aimacode/aima-python/blob/master/games.py
        """
        colour = self.colour
        opponent_colour = self.opponent_colour

        def max_value(game, alpha, beta, depth):
            if cutoff_test(game, depth):
                return evaluation_function(game)
            value = -np.inf
            for action in self.get_candidate_actions(game, colour):
                new_game = self.apply_action(game, action, colour)
                # greedy BOOM start
                if action[0] == "BOOM":
                    # for Max a net negative eval value is a chop
                    eval_boom = evaluation_function(new_game)
                    eval_change = eval_boom - evaluation_function(game)
                    if eval_change < 0:
                        continue
                    elif eval_change >= 0:
                        value = eval_boom
                # greedy BOOM over
                else: # action == "MOVE"
                    value = max(value, min_value(new_game, alpha, beta, depth + 1))
                if value >= beta:
                    return value
                alpha = max(alpha, value)
            return value
            
        def min_value(game, alpha, beta, depth):
            if cutoff_test(game, depth):
                return evaluation_function(game)
            value = np.inf
            for action in self.get_candidate_actions(game, opponent_colour):
                new_game = self.apply_action(game, action, opponent_colour)
                # greedy BOOM start
                if action[0] == "BOOM":
                    # for Min a net positive eval value is a chop
                    eval_boom = evaluation_function(new_game)
                    eval_change = eval_boom - evaluation_function(game)
                    if eval_change > 0:
                        continue
                    elif eval_change <= 0:
                        value = eval_boom
                # greedy BOOM over
                else: # action == "MOVE"
                    value = min(value, max_value(new_game, alpha, beta, depth + 1))
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
            new_game = self.apply_action(game, action, colour)
            # greedy BOOM start
            if action[0] == "BOOM":
                # for Max a net negative eval value is a chop
                eval_boom = evaluation_function(new_game)
                eval_change = eval_boom - evaluation_function(game)
                if eval_change < 0:
                    continue
                elif eval_change >= 0:
                    value = eval_boom
            # greedy BOOM over
            else: # action == "MOVE"
                value = min_value(new_game, best_score, beta, depth)
            if value > best_score:
                best_score = value
                best_action = action
        return best_action

# TODO: Complete this
class AIPlayerOpeningMoves(AIPlayer):
    def __init__(self, colour, depth=2):
        super().__init__(colour, depth=depth)
        if colour == "white":
            opening_actions = (
                ("MOVE", 1, (3, 0), (3, 1)),
                ("MOVE", 2, (3, 1), (3, 3)),
                ("MOVE", 2, (3, 3), (3, 5)),
                ("MOVE", 1, (3, 5), (1, 5)),
                # ("BOOM", (1, 5))
            )
        else:
            opening_actions = (
                ("MOVE", 1, (4, 7), (4, 6)),
                ("MOVE", 2, (4, 6), (4, 4)),
                ("MOVE", 2, (4, 4), (4, 2)),
                ("MOVE", 1, (4, 2), (6, 2)),
                # ("BOOM", (1, 5))
            )
        self.action_generator = (action for action in opening_actions)

    # @override
    def action(self):
        try:
            next_action = next(self.action_generator)
            if next_action[0] == "MOVE":
                n_tokens = next_action[1]
                x_from, y_from = next_action[2][0], next_action[2][1]
                x_to, y_to = next_action[3][0], next_action[3][1]
                if not self.game.is_legal_move(self.colour, n_tokens, x_from, y_from, x_to, y_to, False):
                    return super().action()
            elif next_action[0] == "BOOM":
                if not self.game.is_legal_boom(self.colour, next_action[1]):
                    return super().action()
            else:
                ValueError(f"Something went wrong... next_action[0]: {next_action[0]}")
            return next_action
        except StopIteration:
            return super().action()

# TODO: Complete this
class AIPlayerDistHeuristic(AIPlayer):
    def __init__(self, colour, depth=2):
        super().__init__(colour, depth=depth)

    # @override
    def evaluation_function(self, game):
        def dist_between_centroids(game):
            # white centroid
            x_c_wh, y_c_wh, n_tokens_wh = 0, 0, 0
            for coords, n_tokens in game.board.board_state["white"].items():
                x_c_wh += coords[0] * n_tokens
                y_c_wh += coords[1] * n_tokens
                n_tokens_wh += n_tokens
            x_c_wh /= n_tokens_wh
            y_c_wh /= n_tokens_wh

            # black centroid
            x_c_bl, y_c_bl, n_tokens_bl = 0, 0, 0
            for coords, n_tokens in game.board.board_state["black"].items():
                x_c_bl += coords[0] * n_tokens
                y_c_bl += coords[1] * n_tokens
                n_tokens_bl += n_tokens
            x_c_bl /= n_tokens_bl
            y_c_bl /= n_tokens_bl
            
            # calc distance
            dist = abs(x_c_bl - x_c_wh) + abs(y_c_bl - y_c_wh)
            return dist

        standard_eval = super().evaluation_function(game)
        # if white is Max
        if self.colour == "white":
            # and white has just made an action in search tree
            if game.n_turns % 2 == 1:
                weight = 0.01
                # standard_eval += 1
            else:
                weight = -0.01
                # standard_eval -= 1
        # if black is Max
        elif self.colour == "black":
            # and black has just made an action in search tree
            if game.n_turns % 2 == 0:
                weight = 0.01
                # standard_eval += 1
            else:
                weight = -0.01
                # standard_eval -= 1
        eval_with_dist = standard_eval - weight * dist_between_centroids(game)
        return eval_with_dist

class AIPlayerDistAndOpeningMoves(AIPlayer):
    def __init__(self, colour, depth=2):
        super().__init__(colour, depth=depth)
        if colour == "white":
            opening_actions = (
                ("MOVE", 1, (3, 0), (3, 1)),
                ("MOVE", 2, (3, 1), (3, 3)),
                ("MOVE", 2, (3, 3), (3, 5)),
                ("MOVE", 1, (3, 5), (1, 5)),
                # ("BOOM", (1, 5))
            )
        else:
            opening_actions = (
                ("MOVE", 1, (4, 7), (4, 6)),
                ("MOVE", 2, (4, 6), (4, 4)),
                ("MOVE", 2, (4, 4), (4, 2)),
                ("MOVE", 1, (4, 2), (6, 2)),
                # ("BOOM", (1, 5))
            )
        self.action_generator = (action for action in opening_actions)

    # @override
    def action(self):
        try:
            next_action = next(self.action_generator)
            if next_action[0] == "MOVE":
                n_tokens = next_action[1]
                x_from, y_from = next_action[2][0], next_action[2][1]
                x_to, y_to = next_action[3][0], next_action[3][1]
                if not self.game.is_legal_move(self.colour, n_tokens, x_from, y_from, x_to, y_to, False):
                    return super().action()
            elif next_action[0] == "BOOM":
                if not self.game.is_legal_boom(self.colour, next_action[1]):
                    return super().action()
            else:
                ValueError(f"Something went wrong... next_action[0]: {next_action[0]}")
            return next_action
        except StopIteration:
            return super().action()

        # @override
    def evaluation_function(self, game):
        def dist_between_centroids(game):
            # white centroid
            x_c_wh, y_c_wh, n_tokens_wh = 0, 0, 0
            for coords, n_tokens in game.board.board_state["white"].items():
                x_c_wh += coords[0] * n_tokens
                y_c_wh += coords[1] * n_tokens
                n_tokens_wh += n_tokens
            x_c_wh /= n_tokens_wh
            y_c_wh /= n_tokens_wh

            # black centroid
            x_c_bl, y_c_bl, n_tokens_bl = 0, 0, 0
            for coords, n_tokens in game.board.board_state["black"].items():
                x_c_bl += coords[0] * n_tokens
                y_c_bl += coords[1] * n_tokens
                n_tokens_bl += n_tokens
            x_c_bl /= n_tokens_bl
            y_c_bl /= n_tokens_bl
            
            # calc distance
            dist = abs(x_c_bl - x_c_wh) + abs(y_c_bl - y_c_wh)
            return dist

        standard_eval = super().evaluation_function(game)
        # if white is Max
        if self.colour == "white":
            # and white has just made an action in search tree
            weight = 0.01
            # if game.n_turns % 2 == 1:
            #     weight = 0.01
            #     # standard_eval += 1
            # else:
            #     weight = -0.01
            #     # standard_eval -= 1
        # if black is Max
        elif self.colour == "black":
            # and black has just made an action in search tree
            weight = 0.01
            # if game.n_turns % 2 == 0:
            #     weight = 0.01
            #     # standard_eval += 1
            # else:
            #     weight = -0.01
            #     # standard_eval -= 1
        eval_with_dist = standard_eval - weight * dist_between_centroids(game)
        return eval_with_dist
