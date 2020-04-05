import sys
# for copying nested structures
from copy import deepcopy
# for implementing priority queues
from queue import PriorityQueue

from search.game import Board


class AI:
    def __init__(self, ai_algorithm):
        self.ai_algorithm = ai_algorithm

    def get_solution(self, board_object):
        """
        Calls the desired AI algorithm, which returns a winning sequence of actions:
        solution: [[is_boom, x_from, y_from, x_to, y_to, n_tokens], [...], ...]
        """
        # initial state
        board_state_replica = deepcopy(board_object.board_state)
        initial_ai_board = Board(board_state_replica)

        lookup_ai_search_alg = {
            "breadth_first_search": self.breadth_first_search,
            "depth_first_search": self.depth_first_search,
            "best_first_search": self.best_first_search,
            "expendi_search": self.expendi_search
        }

        ai_search_alg = lookup_ai_search_alg[self.ai_algorithm]
        goal_node, n_frontier_nodes_popped, n_explored_nodes = ai_search_alg(initial_ai_board)

        sys.stderr.write(f"n_frontier_nodes_popped: {n_frontier_nodes_popped} \n")
        sys.stderr.write(f"n_explored_nodes: {n_explored_nodes} \n")

        solution_action_sequence = self.get_solution_action_sequence(goal_node)
        return solution_action_sequence

    def get_solution_action_sequence(self, goal_node):
        """ Records actions from goal_node back up to start_node.
            Returns a list of these actions in reverse (start_action -> goal_action).
            Each action has list structure: [is_boom, x_from, y_from, x_to, y_to, n_tokens]
        """
        if goal_node is None:
            return []
        solution_sequence = []
        solution_sequence.append(goal_node.action)
        temp_node = goal_node
        while temp_node.action is not None:
            solution_sequence.append(temp_node.action)
            temp_node = temp_node.parent
        solution_sequence.reverse()

        sys.stderr.write(f"goal state found: {goal_node.board.board_state} \n")        
        sys.stderr.write(f"number of actions taken to achieve goal: {len(solution_sequence)} \n\n")
        sys.stderr.write(f"action sequence: \n")
        sys.stderr.write("[is_boom, x_from, y_from, x_to, y_to, n_tokens], where x_to, y_to, n_tokens = -1 for boom action \n")
        for action in solution_sequence:
            sys.stderr.write(f"{action} \n")

        return solution_sequence

    def breadth_first_search(self, board):
        pass

    def depth_first_search(self, initial_board):
        # sys.stderr.write("depth_first_search called \n")

        start_node = Node(initial_board, None, None)
        frontier = StackFrontier()
        explored = ExploredNodes()
        goal_node = None
        n_frontier_nodes_popped = 0
        n_explored_nodes = 0

        frontier.push(start_node)
        # sys.stderr.write(f"pushing start_node {start_node} onto frontier with state {start_node.board.board_state} \n")
        while not frontier.is_empty():
            current_node = frontier.pop()
            n_frontier_nodes_popped += 1
            # sys.stderr.write(f'popping current_node {current_node} off frontier with state {current_node.board.board_state} \n')
            if self.contains_goal_state(current_node):
                goal_node = current_node
                break

            if not explored.contains(current_node):
                explored.add(current_node)
                n_explored_nodes += 1
                if self.white_has_lost(current_node):
                    # sys.stderr.write(f"white loses with current_node {current_node} with state {current_node.board.board_state}, so disregarding this node \n")
                    continue
                # sys.stderr.write(f'adding current_node {current_node} to explored nodes with state {current_node.board.board_state} \n')
                # sys.stderr.write("Explored nodes: \n")
                # for node in explored.explored_nodes:
                    # sys.stderr.write(f"{node} \n")
                candidate_actions = self.get_candidate_actions(current_node.board, current_node)
                for action in candidate_actions:
                    new_board = self.apply_action(current_node.board, action)
                    # sys.stderr.write(new_board.board_state)
                    # sys.stderr.write('\n')
                    child_node = Node(new_board, current_node, action)
                    frontier.push(child_node)
                    # sys.stderr.write(f'pushing child_node {child_node} onto frontier with state {child_node.board.board_state} \n')

        if goal_node == None:
            sys.stderr.write("no goal state found! \n")
        return goal_node, n_frontier_nodes_popped, n_explored_nodes

    def expendi_search(self, initial_board):
        """
        ExpendiSearch involves each node keeping track of its cost, as determined by
        a heuristic.
        For now, the total cost is just based upon the state of each node and not prior
        history (like in best-first).
        The current heuristic promotes moving white stacks towards black stacks and away from
        each other. It penalises stacks of more than 1 token height, to encouraging spreading.
        If stacking is required to hop over black pieces, this will still happen.
        """
        height_cost_factor = 2
        start_node_cost = self.heuristic_simple(initial_board.board_state, height_cost_factor)
        start_node = Node(initial_board, None, None, start_node_cost)
        frontier = PriorityQueue()
        explored = ExploredNodes()
        goal_node = None
        n_frontier_nodes_popped = 0
        n_explored_nodes = 0
        
        frontier.put(start_node)
        while not frontier.empty():
            # dequeue a node from the frontier and check if it contains the goal state
            current_node = frontier.get_nowait()
            n_frontier_nodes_popped += 1
            if self.contains_goal_state(current_node):
                goal_node = current_node
                break
            
            # explore the node if it contains an unseen state
            if not explored.contains(current_node):
                explored.add(current_node)
                n_explored_nodes += 1

                # throw away states where white loses
                if self.white_has_lost(current_node):
                    continue
                
                # for each legal action enqueue a child node onto the frontier
                candidate_actions = self.get_candidate_actions(current_node.board, current_node)
                for action in candidate_actions:
                    new_board = self.apply_action(current_node.board, action)
                    child_node_cost = self.heuristic_simple(new_board.board_state, height_cost_factor)
                    child_node = Node(new_board, current_node, action, child_node_cost)
                    frontier.put(child_node)
            
            # stop search if it's taking too long, there may be no solution
            if n_explored_nodes == 4000:
                sys.stderr.write("n_explored_nodes reached 3,000, finishing early! \n")
                break
        
        # note if no goal has been found
        if goal_node == None:
            sys.stderr.write("no goal state found! \n")

        return goal_node, n_frontier_nodes_popped, n_explored_nodes

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
                The manhattan distance from each white stack to its closest black stack.
            Minimising this value will allow us to get as close to the black stacks
            as possible before using a boom action
            """
            
            min_manhattan_distances = []
            for white_stack_coords in board_state["white"]:
                black_stack_coords = board_state["black"][0]
                min_manhattan_distance = manhattan_distance(white_stack_coords, black_stack_coords)
                for black_stack_coords in board_state["black"][1:]:
                    manhattan_distance = manhattan_distance(white_stack_coords, black_stack_coords)
                    if manhattan_distance < min_manhattan_distance:
                        min_manhattan_distance = manhattan_distance
                min_manhattan_distances.append(min_manhattan_distance)
            return sum(min_manhattan_distances)
            
        def stack_separation(board_state, manhattan_distance, height_cost_factor, stack_proximity_factor):
            """
            Penalise white stacks which are higher than 1 token, or are close together
            """
            stack_height_cost = 0
            stack_proximity_cost = 0

            for white_stack_coords, height in board_state["white"].items():
                if height > 1:
                    stack_height_cost += height_cost_factor * height
                # TODO: don't double count dist between stacks 
                for other_white_stack_coords in board_state["white"]:
                    if other_white_stack_coords == white_stack_coords:
                        continue
                    else:
                        stack_proximity_cost += manhattan_distance(white_stack_coords, other_white_stack_coords)

            stack_proximity_cost = int(stack_proximity_cost / stack_proximity_factor)
            separation_cost = stack_height_cost - stack_proximity_cost
            return separation_cost
        
        sum_min_manhattan_distances = sum_min_manhattan_distances(board_state, manhattan_distance)
        separation_cost = stack_separation(board_state, manhattan_distance, height_cost_factor, stack_proximity_factor)
        total_cost = sum_min_manhattan_distances - separation_cost
        return total_cost
    
    def heuristic_simple(self, board_state, height_cost_factor):
        """
        The heuristic, or total cost function, returns an integer cost for
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
                dist_to_white_stacks += manhattan_distance(white_stack_coords, other_white_stack_coords)
                
            # get dist to other black stacks
            for black_stack_coords in board_state["black"]:
                dist_to_black_stacks += manhattan_distance(white_stack_coords, black_stack_coords)

        # white_stack_heights was counted twice, so use half
        # white_stack_heights = int(white_stack_heights / 2)
        total_cost = dist_to_black_stacks - dist_to_white_stacks + white_stack_heights
        # sys.stderr.write(f"total_cost: {total_cost} \n")
        return total_cost

    def get_candidate_actions(self, board, node):
        colour = "white"
        for coords, n_tokens in board.board_state[colour].items():
            candidate_actions = board.get_candidate_actions(colour, n_tokens, coords[0], coords[1])
            # sys.stderr.write(f"{colour} stack: {coords}: {n_tokens} \n")
            # sys.stderr.write(f"candidate_actions: {candidate_actions} \n")
        # TODO: pick one data structure or the other...
        return candidate_actions

    def apply_action(self, board, action):
        """
        This is the 'Transition Model'
        Returns a new board (state/vertex) by applying an action (edge)
        """
        # need to set up a replica here so that we don't mutate board.board_state
        board_state_replica = deepcopy(board.board_state)
        new_board = Board(board_state_replica)
        [is_boom, x_from, y_from, x_to, y_to, n_tokens] = action
        colour = "white"
        if is_boom:
            # sys.stderr.write("is_boom is True \n")
            new_board.boom(colour, x_from, y_from)
        else:
            # sys.stderr.write("is_boom is False \n")
            new_board.move(colour, n_tokens, x_from, y_from, x_to, y_to)
        return new_board

    def contains_goal_state(self, current_node):
        """
        The goal for part A is to wipe all black pieces off the board.
        If all pieces are removed in last turn, then white wins too.
        """
        # colour = "white"
        n_black_stacks = len(current_node.board.board_state["black"])
        return n_black_stacks == 0

        # goal_coords = (7, 7)
        # for stack_coords in current_node.board.board_state[colour]:
        #     if stack_coords == goal_coords:
        #         return True
        # return False

    def white_has_lost(self, node):
        n_white_stacks = len(node.board.board_state['white'])
        n_black_stacks = len(node.board.board_state['black'])
        # TODO: reset '... and n_black_stacks > 0' condition here
        if n_white_stacks == 0 and n_black_stacks > 0:
            return True
        return False

    def best_first_search(self, board):
        pass


class Node():
    def __init__(self, board, parent, action, cost=0):
        self.board = board
        self.parent = parent
        self.action = action
        self.cost = cost
    
    # Sort nodes
    def __lt__(self, other):
         return self.cost < other.cost


class StackFrontier():
    def __init__(self):
        self.frontier = []
    
    def push(self, node):
        self.frontier.append(node)

    def contains(self, node):
        for frontier_node in self.frontier:
            if frontier_node.board.board_state == node.board.board_state:
                return True
        return False
        # return any(node.board.board_state == board.board_state for node in self.frontier)

    def is_empty(self):
        is_empty = len(self.frontier) == 0
        # if is_empty:
            # sys.stderr.write("last node popped off frontier!")
        return is_empty

    def pop(self):
        if self.is_empty():
            raise Exception("Empty Frontier - No Solution!")
        else:
            # TODO: consider using pop here
            # node = self.frontier[-1]
            # self.frontier = self.frontier[:-1]
            return self.frontier.pop() # node


class ExploredNodes():
    def __init__(self):
        self.explored_nodes = set()
    
    def add(self, node):
        if self.contains(node):
            raise Exception(f"{node.board.board_state} is already in explored set")
        self.explored_nodes.add(node)

    def contains(self, node):
        for explored_node in self.explored_nodes:
            if explored_node.board.board_state == node.board.board_state:
                # sys.stderr.write(f"explored already contains state: {explored_node.board.board_state} == {node.board.board_state} \n")
                return True
        # sys.stderr.write(f"explored does not contain state: {node.board.board_state} \n")
        return False