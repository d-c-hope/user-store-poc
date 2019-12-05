from config.routes_config import *
from config.schemaValidator import *
from controller.pathTree import createTrees
from controller.pathNode import PathNode, pathNodeFromTree



def findMatchFromNode(pathList, rootNode):
    """
    Returns a terminal node in the tree once there is a match
    New version: returns a list of nodes that match. Takes the path in list form (split by '/') and the root of the
    tree to evaluate
    """

    currentList = pathList
    currentNode = rootNode
    matchingNodesList = []

    for i in range(len(pathList)):
        val = currentList[0]
        children = currentNode.children
        filteredChildren = list(filter(lambda x: x.pathString == currentList[0], children))
        idFilteredChildren = list(filter(lambda x: x.pathString.startswith('<'), children))

        if len(filteredChildren) == 1:
            currentList = currentList[1:]
            currentNode = filteredChildren[0]
            matchingNodesList.append(pathNodeFromTree(currentNode, val))
        elif len(idFilteredChildren) > 0:
            currentList = currentList[1:]
            currentNode = idFilteredChildren[0]
            matchingNodesList.append(pathNodeFromTree(currentNode, val))
        else:
            return False

    if currentNode.isTerminal:
        return matchingNodesList


def findMatch(pathList):
    return findMatchFromNode(pathList, rootNode)


rootNode = None
def initialise():
    global rootNode
    rootNode = createTrees()


if __name__ == "__main__":
    initialise()
    p = "persona/23/skykids"
    remainderList = p.split("/")
    matchNodesList = findMatch(remainderList, trees["profile"])

    if matchNodesList:
        childNode = matchNodesList[-1]
        print(childNode.schema)
        print(childNode.pathString)

    p2 = "persona/34/sports/type/football/team"
    remainderList2 = p2.split("/")
    print(remainderList2)
    matchNodesList2 = findMatch(remainderList2, trees["profile"])

    if matchNodesList2:
        childNode2 = matchNodesList2[-1]
        print(childNode2.schema)
        print(childNode2.pathString)



