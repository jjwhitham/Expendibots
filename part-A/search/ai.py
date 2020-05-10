import sys
# for copying nested structures
from copy import deepcopy
# for implementing priority queues
from queue import PriorityQueue

from search.game import Board


class AI:
    def __init__(self, ai_algorithm, colour):
        self.ai_algorithm = ai_algorithm
        self.colour = colour
        self.opponents_colour = "black" if colour == "white" else "white"

    def get_solution(self, game_object):
        """
        Calls the desired AI algorithm with an initial board configuration.
        Returns a winning sequence of actions, if one exists:
        solution: [[is_boom, x_from, y_from, x_to, y_to, n_tokens], [...], ...]
        """
        # initial state
        # board_state_replica = deepcopy(board_object.board_state)
        # initial_ai_board = Board(board_state_replica)
        initial_ai_game = deepcopy(game_object)

        lookup_ai_search_alg = {
            "breadth_first_search": self.breadth_first_search,
            "depth_first_search": self.depth_first_search,
            "best_first_search": self.best_first_search,
            "expendi_search": self.expendi_search
        }

        ai_search_alg = lookup_ai_search_alg[self.ai_algorithm]
        goal_node, n_explored_nodes = ai_search_alg(initial_ai_game) # initial_ai_board

        sys.stderr.write(f"n_explored_nodes: {n_explored_nodes} \n")

        # solution_action_sequence = self.get_solution_action_sequence(goal_node)
        return self.solution_action_sequence(goal_node)

    def get_solution_action_sequence(self, goal_node):
        """ Records actions from goal_node back up to start_node.
            Returns a list of these actions in reverse [start_action, ..., goal_action].
            Each action has list structure: [is_boom, x_from, y_from, x_to, y_to, n_tokens].
        """
        if goal_node is None:
            return []
        solution_sequence = []
        temp_node = goal_node
        while temp_node.action is not None:
            solution_sequence.append(temp_node.action)
            temp_node = temp_node.parent
        solution_sequence.reverse()

        sys.stderr.write(f"goal state found: {goal_node.game.board.board_state} \n")        
        sys.stderr.write(f"number of actions taken to achieve goal: {len(solution_sequence)} \n\n")
        sys.stderr.write(f"action sequence: \n")
        # sys.stderr.write("[is_boom, x_from, y_from, x_to, y_to, n_tokens], where x_to, y_to, n_tokens = -1 for boom action \n")
        for action in solution_sequence:
            sys.stderr.write(f"{action} \n")

        return solution_sequence

    def breadth_first_search(self, initial_game):
        start_node = Node(initial_game, None, None)
        frontier = QueueFrontier()
        explored = ExploredNodes()
        goal_node = None
        n_explored_nodes = 0

        frontier.enqueue(start_node)
        while not frontier.is_empty():
            current_node = frontier.dequeue()

            if self.contains_goal_state(current_node):
                goal_node = current_node
                break

            explored.add(current_node)
            n_explored_nodes += 1

            if self.player_has_lost(current_node):
                continue

            candidate_actions = self.get_candidate_actions(current_node.game)
            for action in candidate_actions:
                new_game = self.apply_action(current_node.game, action)
                child_node = Node(new_game, current_node, action)
                if not frontier.contains(child_node) and not explored.contains(child_node):
                    frontier.enqueue(child_node)

        if goal_node == None:
            sys.stderr.write("no goal state found! \n")

        return goal_node, n_explored_nodes

    def depth_first_search(self, initial_game):
        start_node = Node(initial_game, None, None)
        frontier = StackFrontier()
        explored = ExploredNodes()
        goal_node = None
        n_explored_nodes = 0

        frontier.push(start_node)
        while not frontier.is_empty():
            current_node = frontier.pop()

            if self.contains_goal_state(current_node):
                goal_node = current_node
                break

            explored.add(current_node)
            n_explored_nodes += 1

            if self.player_has_lost(current_node):
                continue

            candidate_actions = self.get_candidate_actions(current_node.game)
            for action in candidate_actions:
                new_game = self.apply_action(current_node.game, action)
                child_node = Node(new_game, current_node, action)
                if not frontier.contains(child_node) and not explored.contains(child_node):
                    frontier.push(child_node)

        if goal_node == None:
            sys.stderr.write("no goal state found! \n")

        return goal_node, n_explored_nodes

    def expendi_search(self, initial_game):
        """
        ExpendiSearch involves each node keeping track of its cost, as determined by
        a heuristic.
        For now, the total cost is just based upon the state of each node and not prior
        history (like in best-first).
        The current heuristic promotes moving player stacks towards opponent stacks and away from
        each other. It penalises stacks of more than 1 token height, to encourage spreading.
        If stacking is required to hop over opponent pieces, this will still happen.
        """
        height_cost_factor = 2
        start_node_cost = self.heuristic_simple(initial_game.board.board_state, height_cost_factor)
        start_node = Node(initial_game, None, None, start_node_cost)
        frontier = PriorityQueueFrontier()
        explored = ExploredNodes()
        goal_node = None
        n_explored_nodes = 0
        
        frontier.enqueue(start_node)
        while not frontier.is_empty():
            # dequeue a node from the frontier and check if it contains the goal state
            current_node = frontier.dequeue()
            if self.contains_goal_state(current_node):
                goal_node = current_node
                break
            
            explored.add(current_node)
            n_explored_nodes += 1

            # throw away states where player loses
            if self.player_has_lost(current_node):
                continue
            
            # for each legal action enqueue a child node onto the frontier
            candidate_actions = self.get_candidate_actions(current_node.game)
            for action in candidate_actions:
                new_game = self.apply_action(current_node.game, action)
                child_node_cost = self.heuristic_simple(new_game.board.board_state, height_cost_factor)
                child_node = Node(new_game, current_node, action, child_node_cost)
                # explore child node if frontier/explored has no history of seeing it
                if not frontier.contains(child_node) and not explored.contains(child_node):
                    frontier.enqueue(child_node)
            
            # stop search if it's taking too long, there may be no solution
            # if n_explored_nodes == 10000:
            #     sys.stderr.write("n_explored_nodes reached 10,000, finishing early! \n")
            #     break
        
        # note if no goal has been found
        if goal_node == None:
            sys.stderr.write("no goal state found! \n")

        return goal_node, n_explored_nodes

    def heuristic_harder(self, board_state, height_cost_factor, proximity_cost_factor, stack_proximity_factor):
        """
        ***UNTESTED***
        The heuristic, or total cost function, returns an integer cost for
        a particular board state. This informs our AI algorithm and allows
        prioritisation of actions
        """
        def manhattan_distance(coords_from, coords_to):
            x_dist = abs((coords_to[0] - coords_from[0]))
            y_dist = abs((coords_to[1] - coords_from[1]))
            total_dist = x_dist + y_dist
            return total_dist

        def sum_min_manhattan_distances(board_state, manhattan_distance):
            """ 
            Calculates the total of:
                The manhattan distance from each player stack to its closest opponent stack.
            Minimising this value will allow us to get as close to the opponent stacks
            as possible before using a boom action
            """
            
            min_manhattan_distances = []
            for player_stack_coords in board_state[self.colour]:
                opponent_stack_coords = board_state[self.opponents_colour][0]
                min_manhattan_distance = manhattan_distance(player_stack_coords, opponent_stack_coords)
                for opponent_stack_coords in board_state[self.opponents_colour][1:]:
                    manhattan_distance = manhattan_distance(player_stack_coords, opponent_stack_coords)
                    if manhattan_distance < min_manhattan_distance:
                        min_manhattan_distance = manhattan_distance
                min_manhattan_distances.append(min_manhattan_distance)
            return sum(min_manhattan_distances)
            
        def stack_separation(board_state, manhattan_distance, height_cost_factor, stack_proximity_factor):
            """
            Penalise player stacks which are higher than 1 token, or are close together
            """
            stack_height_cost = 0
            stack_proximity_cost = 0

            for player_stack_coords, height in board_state[self.colour].items():
                if height > 1:
                    stack_height_cost += height_cost_factor * height
                # TODO: don't double count dist between stacks 
                for other_player_stack_coords in board_state[self.colour]:
                    if other_player_stack_coords == player_stack_coords:
                        continue
                    else:
                        stack_proximity_cost += manhattan_distance(player_stack_coords, other_player_stack_coords)

            stack_proximity_cost = int(stack_proximity_cost / stack_proximity_factor)
            separation_cost = stack_height_cost - stack_proximity_cost
            return separation_cost
        
        sum_min_manhattan_distances = sum_min_manhattan_distances(board_state, manhattan_distance)
        separation_cost = stack_separation(board_state, manhattan_distance, height_cost_factor, stack_proximity_factor)
        total_cost = sum_min_manhattan_distances - separation_cost
        return total_cost
    
    def heuristic_simple(self, board_state, height_cost_factor):
        """
        This heuristic, or cost function, returns an integer cost for
        a particular board state. This informs our AI algorithm and allows
        prioritisation of actions

        This heuristic returns the sum of costs for each player stack, where:
            cost_per_stack = dist_to_opponent_stacks - dist_to_player_stacks + player_stack_heights
        """
        def manhattan_distance(coords_from, coords_to):
            x_dist = abs((coords_to[0] - coords_from[0]))
            y_dist = abs((coords_to[1] - coords_from[1]))
            total_dist = x_dist + y_dist
            return total_dist

        # TODO: get rid of double counting
        dist_to_opponent_stacks = 0
        dist_to_player_stacks = 0
        player_stack_heights = 0

        for player_stack_coords, height in board_state[self.colour].items():
            # penalise stacks greater than 1 token high
            if height > 1:
                player_stack_heights += height_cost_factor * height
            
            # get dist to other player stacks
            for other_player_stack_coords in board_state[self.colour]:
                if other_player_stack_coords == player_stack_coords:
                    continue
                # remove double counting between player stacks
                dist_to_player_stacks += int(manhattan_distance(player_stack_coords, other_player_stack_coords) / 2)
                
            # get dist to other opponent stacks
            for opponent_stack_coords in board_state[self.opponents_colour]:
                dist_to_opponent_stacks += manhattan_distance(player_stack_coords, opponent_stack_coords)

        total_cost = dist_to_opponent_stacks - dist_to_player_stacks + player_stack_heights
        return total_cost
    # TODO - perhaps move the iteration over the stacks to Board (Game)
    def get_candidate_actions(self, game):
        colour = self.colour
        candidate_actions = game.get_candidate_actions(colour)

        return candidate_actions

    def apply_action(self, game, action):
        """
        This is the 'Transition Model'
        Returns a new board (state/vertex) by applying an action (edge)
        """
        # need to set up a replica here so that we don't mutate board.board_state
        # board_state_replica = deepcopy(board.board_state)
        # new_board = Board(board_state_replica)
        new_game = deepcopy(game)
        # [is_boom, x_from, y_from, x_to, y_to, n_tokens] = action
        colour = self.colour
        # if is_boom:
        if action[0] == "BOOM":
            x_from, y_from = action[1]
            new_game.boom(colour, x_from, y_from)
        else:
            n_tokens = action[1]
            x_from, y_from = action[2]
            x_to, y_to = action[3]
            new_game.move(colour, n_tokens, x_from, y_from, x_to, y_to)
        return new_game

    def contains_goal_state(self, current_node):
        """
        The goal for part A is to wipe all opponent pieces off the board.
        If all pieces are removed in last turn, then player wins too.
        """
        opponents_colour = self.opponents_colour
        n_opponents_stacks = len(current_node.game.board.board_state[opponents_colour])
        return n_opponents_stacks == 0

    def player_has_lost(self, node):
        n_players_stacks = len(node.game.board.board_state[self.colour])
        n_opponents_stacks = len(node.game.board.board_state[self.opponents_colour])
        # TODO: reset '... and n_opponent_stacks > 0' condition here
        if n_players_stacks == 0 and n_opponents_stacks > 0:
            return True
        return False

    def best_first_search(self, board):
        pass


class Node():
    def __init__(self, game, parent, action, cost=0):
        self.game = game
        self.parent = parent
        self.action = action
        self.cost = cost
    
    # Sort nodes
    def __lt__(self, other):
         return self.cost < other.cost

class Frontier():
    def __init__(self):
        self.frontier = []
        self.frontier_states = set()
    
    def contains(self, node):
        board_state = node.game.board.board_state
        frontier_state = Board.get_board_state_as_tuples(board_state)
        return frontier_state in self.frontier_states

    def is_empty(self):
        is_empty = len(self.frontier) == 0
        return is_empty
class StackFrontier(Frontier):

    def push(self, node):
        board_state = node.game.board.board_state
        frontier_state = Board.get_board_state_as_tuples(board_state)
        ## this test is good for debugging, but adds time to the solution
        # if self.contains(node):
        #     raise Exception(f"{node.board.board_state} is already in explored set")
        self.frontier_states.add(frontier_state)
        self.frontier.append(node)

    def pop(self):
        if self.is_empty():
            raise Exception("Empty Frontier - No Solution!")
        return self.frontier.pop()

class QueueFrontier(Frontier):

    def enqueue(self, node):
        board_state = node.game.board.board_state
        frontier_state = Board.get_board_state_as_tuples(board_state)
        ## this test is good for debugging, but adds time to the solution
        # if self.contains(node):
        #     raise Exception(f"{node.board.board_state} is already in explored set")
        self.frontier_states.add(frontier_state)
        self.frontier.append(node)

    def dequeue(self):
        if self.is_empty():
            raise Exception("Empty frontier - No Solution!")
        return self.frontier.pop(0)

class PriorityQueueFrontier(Frontier):
    def __init__(self):
        super().__init__()
        self.frontier = PriorityQueue()

    def enqueue(self, node):
        board_state = node.game.board.board_state
        frontier_state = Board.get_board_state_as_tuples(board_state)
        self.frontier_states.add(frontier_state)
        self.frontier.put(node)

    def dequeue(self):
        return self.frontier.get_nowait()

    def is_empty(self):
        self.frontier.empty()


class ExploredNodes():
    def __init__(self):
        self.explored_states = set()
    
    def add(self, node):
        # Transform state dictionary data structure into immutable tuple data structure.
        # Sets can only contain fully immutable structures. Adding is O(1)
        board_state = node.game.board.board_state
        explored_state = Board.get_board_state_as_tuples(board_state)
        ## this test is good for debugging, but adds time to the solution
        # if self.contains(node):
        #     raise Exception(f"{node.board.board_state} is already in explored set")
        self.explored_states.add(explored_state)

    def contains(self, node):
        # Transform state dictionary data structure into immutable tuple data structure.
        # Sets can only contain fully immutable structures. Testing for membership is O(1)
        board_state = node.game.board.board_state
        explored_state = Board.get_board_state_as_tuples(board_state)
        return explored_state in self.explored_states
