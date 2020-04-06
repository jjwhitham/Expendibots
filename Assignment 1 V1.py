# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 18:22:50 2020

@author: jhulonce
"""

def print_move(n, x_a, y_a, x_b, y_b, **kwargs):
    """
    Output a move action of n pieces from square (x_a, y_a)
    to square (x_b, y_b), according to the format instructions.
    """
    print("MOVE {} from {} to {}.".format(n, (x_a, y_a), (x_b, y_b)), **kwargs)


def print_boom(x, y, **kwargs):
    """
    Output a boom action initiated at square (x, y) according to
    the format instructions.
    """
    print("BOOM at {}.".format((x, y)), **kwargs)

class Node:

    # Initialize the class
    def __init__(self, position, parentNode,lastMove=[]):
        self.position = position
        self.parentNode = parentNode
        
#        whitePieces = self.position.get("white")  #these return a list. Which we can combine and add back later
#        blackPieces = self.position.get("black")

#        totalDistance = 0
        
#        for eachW in whitePieces:
#           for eachB in blackPieces:
#               manhat = abs(eachW[1] - eachB[1]) + abs(eachW[2]-eachB[2])
#               totalDistance = totalDistance + manhat
            

        #self.g = totalDistance # Distance to start node
        self.g = 0 # Distance to start node
        self.h = 0 # Distance to goal node
        self.f = self.g + self.h  # Total cost
        self.lastMove = lastMove

    # Sort nodes
    def __lt__(self, other):
         return self.f < other.f

    # Compare nodes
    def __eq__(self, other):
        return self.position == other.position

    # Print node
    def __repr__(self):
        #return ('({0},{1},{2})'.format(self.position, self.parentNode,self.f))
        return ('({0},{1})'.format(self.position,self.f))
    
##SOURCE: https://www.annytab.com/best-first-search-algorithm-in-python/

def goalState(selectedNode):
    black = selectedNode.position.get("black")
    if black == [] or black == [[]] or black == [[[]]] or black == [[[[]]]]:
        return True
    else:
        return False



# a method to check if a move is legal. 
def legalMove(currentPiece,currentNode):
    if currentPiece[1]>=0 and currentPiece[1]<= 7 and currentPiece[2]>=0 and currentPiece[2]<= 7:
        blackPieces = currentNode.position.get("black")
        
        if len(blackPieces) != 0:
            for each in blackPieces:
                if [each[1],each[2]] == [currentPiece[1],currentPiece[2]]:
                    return False
                else:
                    return True
    else:
         return False
        
##test legal: A+


# a method to check if moving onto a white space 
def legalMoveResult(currentPiece,currentNode):
    whitePieces = currentNode.position.get("white")
    if len(whitePieces) == 0 or whitePieces == [] or whitePieces == [[]]:
        return currentPiece
    else:
        for each in whitePieces:
            if [each[1],each[2]] == [currentPiece[1],currentPiece[2]]:
                return [each[0]+currentPiece[0],each[1],each[2]]
            else:
                return currentPiece

##test legal: A+
                


def calculateChildrenForMoves(currentNode):
    
    whitePieces = currentNode.position.get("white")  #these return a list. Which we can combine and add back later
    blackPieces = currentNode.position.get("black")
    
    if len(whitePieces)  == 0 or whitePieces == [] or whitePieces == [[]]:
        return None   #aka you have probably lost, but wither way there are no moves left
    
    else:
        newNodes = []
        for eachPiece in whitePieces:
            n = eachPiece[0]
            x = eachPiece[1]
            y = eachPiece[2]
            if (n == 1):
                newOptions = [[1,x-1,y],[1,x+1,y],[1,x,y-1],[1,x,y+1]]
                for each in newOptions:
                    if legalMove(each,currentNode):
                        newPieces = legalMoveResult(each,currentNode) #gives new peice details
                        newWhite = whitePieces.copy()
                        newWhite.remove(eachPiece) #creates copy of white less current piece
                        newWhite.append(newPieces) #adds new piece
                        newState = {'white':newWhite,'black':blackPieces}
                                            
                        #record move to new node
                        #[boom=1/move=1,x1,y1,x2,y2,n]
                        move = [0,x,y,each[1],each[2],1]
                        
                        newNodes.append(Node(newState,currentNode,move))
   
                        
            nCounter = n
            if (n > 1):
                while nCounter >0:       
                    newOptions = [[nCounter,x-1,y],[nCounter,x+1,y],[nCounter,x,y-1],[nCounter,x,y+1]]
                    for each in newOptions:
                        if legalMove(each,currentNode):
                             newPieces = legalMoveResult(each,currentNode) #gives new peice details
                             newWhite = whitePieces.copy()
                             newWhite.remove(eachPiece) #removes old peice
                             newWhite.append(newPieces) #adds new piece
                             if(n-nCounter!=0):
                                 newWhite.append([n-nCounter,eachPiece[1],eachPiece[2]]) # updates current local with lower peices
                             
                             newState = {'white':newWhite,'black':blackPieces}

                             #record move to new node
                             #[boom=1/move=1,x1,y1,x2,y2,n]
                             move = [0,x,y,each[1],each[2],nCounter]

                             newNodes.append(Node(newState,currentNode,move)) 
                 
                    nCounter -= 1

    return newNodes

#Test: A+



#return a list of exploded peices......

def explodeAPiece(State,x,y):

    whitePieces = State.get("white")
    blackPieces = State.get("black")
    
    listOfExplodedPieces = []
    
    toDelete = [[x-1,y],[x,y],[x+1,y],[x-1,y-1],[x,y-1],[x+1,y-1],[x-1,y+1],[x,y+1],[x+1,y+1]]
    whitePost = whitePieces.copy()
    blackPost = blackPieces.copy()
     
    for each in whitePieces:
        for item in toDelete:
            if [each[1],each[2]] == [item[0],item[1]]:
                whitePost.remove(each)
                listOfExplodedPieces.append(each)
    for each in blackPieces:
        for item in toDelete:
            if [each[1],each[2]] == [item[0],item[1]]:
                blackPost.remove(each)
                listOfExplodedPieces.append(each)
                
    newState = {'white': whitePost, 'black': blackPost}
    
    #print(listOfExplodedPieces)
    #print(newState)
    
    NewExplodedPieces = []            
    for each in listOfExplodedPieces:
        
        newExplode = explodeAPiece(newState,each[1],each[2])
        for each in newExplode:
            NewExplodedPieces.append(each)
    
    for each in NewExplodedPieces:
        listOfExplodedPieces.append(each)
    
    return listOfExplodedPieces

#Test: A+

def calculateExplodedStatehildrenNodes(currentNode):
    
    whitePieces = currentNode.position.get("white")
    blackPieces = currentNode.position.get("black")
    state = currentNode.position
    
    if len(whitePieces) == 0 or whitePieces == [] or whitePieces == [[]]:
        return None   #aka you have probably lost, but wither way there are no moves left
    
    else:
        newNodes = []
        for eachPiece in whitePieces:
                      
            x = eachPiece[1]
            y = eachPiece[2]
        
            explodedpieces = explodeAPiece(state,x,y)
            
            whitePost = whitePieces.copy()
            blackPost = blackPieces.copy()
            
            
            for each in explodedpieces:
                if each in whitePost:
                    whitePost.remove(each)
                if each in blackPost:
                    blackPost.remove(each)      
            
            move = [1,x,y,0,0,0]
            newNodes.append(Node({'white':whitePost,'black':blackPost},currentNode,move))
         
    return newNodes

#Test: A+
    


def best_first_search(startBoardState):

    #create lists to hold the que of open nodes to look at and those we have visited
    openQueue = []
    closedVisited = []

    #create the start node which is given to us
    startNode = Node(startBoardState,None)
    
    openQueue.append(startNode)

    #main loop until the openQueve us empty
    
    while len(openQueue) > 0:
        
        #find lowest cost node by sorting, then pop the top node
        #############################################
        
        ####################################
        #print("starting sort")
        openQueue.sort(reverse=True)
        #print("finishing sort")
        #print(openQueue)
        currentNode = openQueue.pop(0)
        
        #put current node into closed
        closedVisited.append(currentNode)

        #check if goal state is reached, and if so return path found. 
        
        if goalState(currentNode):
            #print("goal State")
            #print(currentNode)
            #print("closedVisited",closedVisited)
            
            path = []
            moves = []
            while currentNode != startNode:
                #print(currentNode)
                path.append(currentNode.position)
                moves.append(currentNode.lastMove)
                currentNode = currentNode.parentNode
                #print(path)
                #path.append(startNode)
                #return path in reverse
                

            #return path #[::-1]
            path.reverse() 
            moves.reverse() 
            
            return moves #[::-1]
        
        
        #get each state reachable by movement and add to openQueve
        
        newNeighbours = calculateChildrenForMoves(currentNode)
        
        #print(newNeighbours)
        
        if newNeighbours is not None:
            for each in newNeighbours:
                openQueue.append(each)
            
        newNeighbours2 = calculateExplodedStatehildrenNodes(currentNode)
        
        if newNeighbours2 is not None:
            for each in newNeighbours2:
                openQueue.append(each)
            
        
        #######
        # possibly check if it exists and if the state already exists with a different parent,
        # and if so only add one with best heuristic

        #get each state reachable by explosion and add to open Queue.
        
      
    # Return None, no path is found
    return None
        

######### MAIN CODE
import json

#(n,x,y)
## load and test test cases:


print("")
print("Test case provided 1")

with open('test-level-1.json') as dataFile:    
    startStateData1 = json.load(dataFile)
print(startStateData1)
print("") 
print("") 
exampleNode1 = Node(startStateData1,None)
print(exampleNode1)
a = best_first_search(exampleNode1.position)

for each in a:
    if each[0]==0:
        print_move(each[5],each[1],each[2],each[3],each[4])
    if each[0]==1:
        print_boom(each[1],each[2])
    
    
    
print("") 
print("") 
print("")
print("Test case provided 2")

with open('test-level-2.json') as dataFile:    
    startStateData2 = json.load(dataFile)
print(startStateData2)
print("") 
print("") 
exampleNode2 = Node(startStateData2,None)

b = best_first_search(exampleNode2.position)

for each in b:
    if each[0]==0:
        print_move(each[5],each[1],each[2],each[3],each[4])
    if each[0]==1:
        print_boom(each[1],each[2])
    
    
    
print("") 
print("") 
print("")
print("Test case provided 3")

with open('test-level-3.json') as dataFile:    
    startStateData3 = json.load(dataFile)
print(startStateData3)
print("") 
print("") 
exampleNode3 = Node(startStateData3,None)

c = best_first_search(exampleNode3.position)

for each in c:
    if each[0]==0:
        print_move(each[5],each[1],each[2],each[3],each[4])
    if each[0]==1:
        print_boom(each[1],each[2])
    
    
    
    





harder = {'white': [[3, 1, 1]], 'black': [[1, 3, 3]]}

