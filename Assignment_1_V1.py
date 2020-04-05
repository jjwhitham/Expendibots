# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 18:22:50 2020

@author: jhulonce
"""
from copy import deepcopy

##Classess

class Node:

    # Initialize the class
    def __init__(self, position, parentNode):
        self.position = position
        self.parentNode = parentNode
        self.g = 0 # Distance to start node
        self.h = 0 # Distance to goal node
        self.f = 0 # Total cost


    # Sort nodes
    def __lt__(self, other):
         return self.f < other.f

    # Compare nodes
    def __eq__(self, other):
        return self.position == other.position

    # Print node
    def __repr__(self):
        return ('({0},{1})'.format(self.position, self.f))
    
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
    if len(whitePieces)== 0:
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
    
    if len(whitePieces) == 0:
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
                        newWhite = deepcopy(whitePieces) # whitePieces.copy()
                        newWhite.remove(eachPiece) #creates copy of white less current piece
                        newWhite.append(newPieces) #adds new piece
                        newState = {'white':newWhite,'black':blackPieces}
                        newNodes.append(Node(newState,currentNode))
            nCounter = n
            if (n > 1):
                while nCounter >0:       
                    newOptions = [[nCounter,x-1,y],[nCounter,x+1,y],[nCounter,x,y-1],[nCounter,x,y+1]]
                    for each in newOptions:
                        if legalMove(each,currentNode):
                             newPieces = legalMoveResult(each,currentNode) #gives new peice details
                             newWhite = deepcopy(whitePieces) # whitePieces.copy()
                             newWhite.remove(eachPiece) #removes old peice
                             newWhite.append(newPieces) #adds new piece
                             if(n-nCounter!=0):
                                 newWhite.append([n-nCounter,eachPiece[1],eachPiece[2]]) # updates current local with lower peices
                             
                             newState = {'white':newWhite,'black':blackPieces}
                             newNodes.append(Node(newState,currentNode))          
                 
                    nCounter -= 1

    return newNodes

#Test: A+



#return a list of exploded peices......

def explodeAPiece(State,x,y):

    whitePieces = State.get("white")
    blackPieces = State.get("black")
    
    listOfExplodedPieces = []
    
    toDelete = [[x-1,y],[x,y],[x+1,y],[x-1,y-1],[x,y-1],[x+1,y-1],[x-1,y+1],[x,y+1],[x+1,y+1]]
    whitePost = deepcopy(whitePieces) # whitePieces.copy()
    blackPost = deepcopy(blackPieces) # blackPieces.copy()
     
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
    
    print(listOfExplodedPieces)
    print(newState)
    
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
    
    if len(whitePieces) == 0:
        return None   #aka you have probably lost, but wither way there are no moves left
    
    else:
        newNodes = []
        for eachPiece in whitePieces:
                      
            x = eachPiece[1]
            y = eachPiece[2]
        
            explodedpieces = explodeAPiece(state,x,y)
            
            whitePost = deepcopy(whitePieces) # whitePieces.copy()
            blackPost = deepcopy(blackPieces) # blackPieces.copy()
            
            
            for each in explodedpieces:
                if each in whitePost:
                    whitePost.remove(each)
                if each in blackPost:
                    blackPost.remove(each)      
            
            newNodes.append(Node({'white':whitePost,'black':blackPost},currentNode))
         
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
        openQueue.sort()
        currentNode = openQueue.pop(0)
        
        #put current node into closed
        closedVisited.append(currentNode)

        #check if goal state is reached, and if so return path found. 
        
        if goalState(currentNode):
            path = []
            while currentNode != startNode:
                path.append(currentNode.position)
                currentNode = currentNode.parentNode
                #path.append(startingNode)
                #return path in reverse
                return path[::-1]
        
        
        #get each state reachable by movement and add to openQueve
        
        newNeighbours = calculateChildrenForMoves(currentNode)
        
        print(newNeighbours)
        
        for each in newNeighbours:
            openQueue.append(each)
            
        newNeighbours2 = calculateExplodedStatehildrenNodes(currentNode)
        
        for each in newNeighbours2:
            openQueue.append(each)
            
            
            

        #######
        # possibly check if it exists and if the state already exists with a different parent,
        # and if so only add one with best heuristic

        #get each state reachable by explosion and add to open Queue.
        
      
    # Return None, no path is found
    return None
        
        





######### MAIN CODE
if __name__ == "__main__":

    import json

    #(n,x,y)

    with open('search/test_cases/test-level-2.json') as dataFile:    
        startStateData = json.load(dataFile)
    print(startStateData)

    harder = {'white': [[3, 1, 1]], 'black': []}


    exampleNode = Node(harder,None)
    exampleNode2 = Node(startStateData,None)



    best_first_search(exampleNode2.position)





