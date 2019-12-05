from controller.pathNode import PathNode





def normaliseListEnd(nodeList):
    """
    Adds node at the end for a case like /persona becoming /persona/id
    """

    if len(nodeList) == 0: return []
    lastNode = nodeList[-1]
    if lastNode.isIdNode():
        pass
        node = PathNode(lastNode.defaultType, isTerminal=False,
                    schema=lastNode.schema, pathString=lastNode.defaultType,
                    defaultType="core", postEndpoint=False,
                    isIdRoot=False, isDefault=True)
        nodeList.append(node)
    elif lastNode.isIdRoot:
        node1 = PathNode("<id>", isTerminal=False,
                        schema=lastNode.schema, pathString="<id>",
                        defaultType="core", postEndpoint=False,
                        isIdRoot=False)
        node2 = PathNode(lastNode.defaultType, isTerminal=False,
                        schema=lastNode.schema, pathString=lastNode.defaultType,
                        defaultType=None, postEndpoint=False,
                        isIdRoot=False, isDefault=True)
        nodeList.append(node1)
        nodeList.append(node2)
    else:
        pass

    # fullList = matchNodeList
    # path = [node.pathVal for node in fullList]
    # pathString = [node.pathString for node in fullList]
    return nodeList


def getOuterPathList(normalisedList):
    """
    Scenarios assuming normalized form:
    profile/id/core PUT/POST        -> []
    profile/id/optouts PUT/POST        -> profile/id
    profile/id/persona/id/core PUT/POST        -> profile/id
    profile/id/persona/id/optouts PUT/POST     -> profile/id/persona/id
    profile/id/persona/id/device/id/accessibility PUT/POST  -> profile/id/persona/id/device/id
    profile/id/persona/id/device/id/core PUT/POST  -> profile/id/persona/id
    profile/id/persona/id PUT                  -> profile/id DONT GET THIS, NORMALIZED FORM


    """

    def findPreviousRoot(nodeList):
        listLen = len(nodeList)
        # matchCount = 0
        # for i in range(listLen):
        for revI in range(listLen-1, -1, -1):
            # revI = listLen - i - 1
            n = nodeList[revI]
            if n.isIdRoot: # and matchCount == 1:
                return revI
                if revI > 0 :return revI-1
                else: return 0
            # elif n.isIdRoot:
            #     return revI
                # matchCount += 1
        return 0


    nList = normalisedList.copy()
    retList = None
    endNode = nList[-1]
    if endNode.isDefault:
        i = findPreviousRoot(nList)
        retList = nList[0:i]
    else:
        retList = nList[0:-1]


    return retList
    # index = 0
    # for node in normalisedList:
    #     if node.isIdNode:


def getParentList(normNodeList):
    """
    Where a set of nodes forms a path like
        profile/id/persona/id/optouts
        profile/id/persona/id/device/id/accessibility
        profile/id/persona/id
    this would strip those to:
        profile/id/persona/id
        profile/id/persona/id/device/id
        profile/id
    This is used for checking the path exists already before a POST or a PUT
    Won't work if passed profile/id/persona so normalise first
    """



    endNode = normNodeList[-1]
    if endNode.isIdNode:
        return normNodeList[0:-2]
    else:
        return normNode[0:-1]


def copyList():
    pass





# def normaliseFrontNodeList(idType, idVal, matchNodeList):
#     """
#     Adds nodes for the profile or household to the front of the node list
#     """
#     root = PathNode(idType, isTerminal=False,
#                  schema=None, pathString=idType,
#                  defaultType="core", postEndpoint=False,
#                  isIdRoot=True)
#     second= PathNode(idVal, isTerminal=False,
#                     schema=None, pathString="<id>",
#                     defaultType="core", postEndpoint=False,
#                     isIdRoot=True)
#
#     fullList = [root, second] + matchNodeList
#     return fullList

# def addDefaultToEnd(nodeList):
#     lastNode = nodeList[-1]
#     node = PathNode(lastNode.defaultType, isTerminal=False,
#                 schema=None, pathString=lastNode.defaultType,
#                 defaultType="core", postEndpoint=False,
#                 isIdRoot=False)
#     nodeList.append(node)
#     return nodeList

# def normaliseNodeList(idType, idVal, matchNodeList):
#     """
#     Adds nodes for the profile or household to the front of the node list
#     Adds node at the end for a case like /persona becoming /persona/id
#     """
#     root = PathNode(idType, isTerminal=False,
#                  schema=None, pathString=idType,
#                  defaultType="core", postEndpoint=False,
#                  isIdRoot=True)
#     second= PathNode(idVal, isTerminal=False,
#                     schema=None, pathString="<id>",
#                     defaultType="core", postEndpoint=False,
#                     isIdRoot=True)
#
#     lastNode = matchNodeList[-1]
#     if lastNode.isIdNode():
#         pass
#         # node = PathNode(idVal, isTerminal=False,
#         #             schema=None, pathString="<id>",
#         #             defaultType="core", postEndpoint=False,
#         #             isIdRoot=False)
#         # matchNodeList.append(node)
#     elif lastNode.isIdRoot:
#         node1 = PathNode("unknown", isTerminal=False,
#                         schema=None, pathString="<id>",
#                         defaultType="core", postEndpoint=False,
#                         isIdRoot=False)
#         # node2 = PathNode(lastNode.defaultType, isTerminal=False,
#         #                 schema=None, pathString=lastNode.defaultType,
#         #                 defaultType=None, postEndpoint=False,
#         #                 isIdRoot=False)
#         matchNodeList.append(node1)
#         # matchNodeList.append(node2)
#     else:
#         pass
#
#     fullList = [root, second] + matchNodeList
#     # path = [node.pathVal for node in fullList]
#     # pathString = [node.pathString for node in fullList]
#     return fullList