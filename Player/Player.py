#import sys
#import pprint

from Player.util import print_board
from Player.game import Board
from Player.newAI import AI  #3 detlte not needed....
from copy import deepcopy
import random


class Player:
    
    # this player class is a reimplementation of game class" 
    
    """
    A class to represent a AI player agent. This needs to have function:
    _init_  -  initiates inself and a board in start position. and colour
    update  -  take a turn info and updates board
    action  -  sends an action in correct format
    """

    def __init__(self, colour):
        self.colour = colour
        if colour == "white":
            self.opp_colour = "black"
        else:
            self.opp_colour = "white"
        self.board = Board()
        #self.AI = AI()
        self.AIFunction = "random"
        
    def update(self,colour,action):
        
        ## assumes the following input
        ### actoin =  ("MOVE", n, (xa, ya), (xb, yb))
        ###("BOOM", (x, y))

        if action[0] == "MOVE":
            n_tokens = action[1]
            x_from, y_from = action[2][0], action[2][1]
            x_to, y_to = action[3][0], action[3][1]
            self.board.move(colour, n_tokens, x_from, y_from, x_to, y_to)
            
        
        if action[0] == "BOOM":
            x, y = action[1][0], action[1][1]
            self.board.boom(colour, x, y)


    def action(self):
        #AImethod = "random"   ## 
        AImethod = "MinMax" 
        
        
        if AImethod == "random":
            # get all the peices avaliable and randomly pick one:
            
            boardDict = deepcopy(self.board.get_board_dict())
            
            print(boardDict)
            
            pieces = []       
            for k, v in boardDict.items():
                if v[-2:] == "wh":
                    pieces.append(k)
                    
            print(pieces)
            randomPiece = random.choice(pieces)
            print(randomPiece)
                
            actionList = self.board.get_candidate_actions(self.colour, 1, randomPiece[0], randomPiece[1])
            
            print(actionList)
 
            randomMove = random.choice(actionList)
            print(randomMove)
            if randomMove[0] == 1:
                return ("BOOM",(randomMove[0],randomMove[0]))
            
            if randomMove[0] == 0:
                return ("MOVE", 1, (randomMove[1], randomMove[2]), (randomMove[3], randomMove[4]))
            
            
## ------------------------------------------------------------------------------------------------

##   class Node(self, board, parent, action, depth, cost=0):

        if AImethod == "MinMax":
                        
            boardCopy = deepcopy(self.board)                  #create a copy of board
            
            start_node = Node(boardCopy, None, None,self.colour,cost=0)     #creates the starting node
            main_values = []                                         #holds max unitily of each action
            nodeAction = []                                     #hold description of each action to return
            main_child_nodes = start_node.get_child_nodes(self.colour)
            
            
            for each in main_child_nodes:
                utility = self.min_max_value(each)
                main_values.append(utility)  
                nodeAction.append(each.action)

            max_value = max(main_values)
            max_index = main_values.index(max_value)
            chosenAction = nodeAction[max_index]
            
            #print(max_value)
            #print(main_values)
            #print(nodeAction)
            if chosenAction[0] == 1:
                return ("BOOM",(chosenAction[0],chosenAction[0]))
            
            if chosenAction[0] == 0:
                return ("MOVE", 1, (chosenAction[1], chosenAction[2]), (chosenAction[3], chosenAction[4]))
               
       
    def min_max_value(self,node):
        
        maxDepth = 2
        if node.board.terminal_state() or node.depth_ok(maxDepth) == False:
            return node.board.utility(5,node.playerColour,node.opp_colour)
        
        elif node.maxs_turn():
            #print('maxs turn')
            #print('depth')
            #print(node.depth)
            values = []    
            childNodes = node.get_child_nodes(node.playerColour)
            for each in childNodes:
                utility = self.min_max_value(each)
                values.append(utility)  
                
            #print(values)
            #print("max: ", max(values))
            return max(values)
        
        else:
            values = []    
            #print("mins turn")
            #print('depth')
            #print(node.depth)
            childNodes = node.get_child_nodes(node.opp_colour)
            for each in childNodes:
                utility = self.min_max_value(each)
                values.append(-utility) 
            #print(values)
            #print("min: ", min(values))
            return min(values)
            

## worth it to not add 

### previous solution stops if board state has been seen before, so it records board states.           
            
        
        ## update to use old heuristic of distance between things with a small weighting, 
        ## then end states with much bigger weighting. 
        
# -------------------------------------------------------------------------------------------------    
        # alpha beta pruning 
        
        
        
        
        
        
        
        
        
        
            
        
# -------------------------------------------------------------------------------------------------    
        
            
class Node():
    def __init__(self, board, parent, action, playerColour,cost=0):
        self.board = board
        self.parent = parent  
        self.action = action
        self.playerColour = playerColour
        
        if self.playerColour == "white":
            self.opp_colour = "black"
        else:
            self.opp_colour = "white"
        
        self.cost = cost
        if parent == None:
            self.depth = 0
        else:
            self.depth = self.parent.depth + 1
    
    # Sort nodes
    def __lt__(self, other):
         return self.cost < other.cost
        
        
    def depth_ok(self,maxDepth):
        if self.depth >= maxDepth:
            return False
        else:
            return True
        
    def maxs_turn(self):
        if self.depth == 0 or self.depth % 2 == 0:
            return True
        else:
            return False
        
    def get_child_nodes(self,colour):
        
        all_candidate_actions = self.board.get_all_candidate_actions(colour)       # get candidate actions
        child_nodes=[]
         
        for each in all_candidate_actions:
            boardCopy = deepcopy(self.board) 
            new_board = boardCopy.apply_action(each,colour)
            child_node = Node(new_board,self,each,colour)
            child_nodes.append(child_node)   
                
        return child_nodes
                    
    
    
    
    
    
    
    
    
    
    
    
    
    
        

            
            
            
            

            
            
            