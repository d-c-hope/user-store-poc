import sys
from controller.pathNode import TreeNode
from utils import paths
from config.routes_config import routesConfig
from config.schemaValidator import validatorMap
import logging
logger = logging.getLogger("applogger")


def createTrees():
    """Creates trees for each route type, i.e. one for profile, one for household
    though would support any others added
    The tree is made up of node objects"""

    # rootNode = Node("")
    # routesValsDict = {}
    # trees = {}
    # for key in routesConfig:
        # routesValsDict = routesConfig[key].items()
    rootNode = TreeNode("")
    for key, val in routesConfig.items():
        addToTree(key, val, rootNode)
    # rootNode.print()
    # print(rootNode.pathNested([]))
        # trees[key] = rootNode
    return rootNode


def addToTree(path, val, rootNode):
    """
    Walks the path and for each item adds to the tree (starting at rootnode) if not already there
    At the end of the path it marks the node as being a terminal - this doesn't mean
    that the tree stops here, just that this is a valid URL, e.g. .../persona and .../persona/id/core are both
    valid for GET requests
    :param path: a path defined in routes_config
    :param val: the data associated with the path
    :param rootNode:
    :return:
    """
    pathList = path.split('/')
    currentNode = rootNode
    for item in pathList:
        children = currentNode.children
        filtered = list(filter(lambda x: x.pathString == item, children))
        if len(filtered) == 0:
            newNode = TreeNode(item)
            children.append(newNode)
            currentNode = newNode
        else:
            currentNode = filtered[0]

    # set properties on the leaf nodes
    currentNode.isTerminal=True
    currentNode.schema = None
    try:
        currentNode.schema = validatorMap[val["schema"]]
    except:
        logger.debug("warning no schema")
    # currentNode.pathString = path
    if "postAllowed" in val:
        currentNode.postEndpoint = val["postAllowed"]
    if "putCreation" in val:
        currentNode.postEndpoint = val["putCreation"]
    if "defaultType" in val:
        currentNode.defaultType = val["defaultType"]
    if "isDefault" in val:
        currentNode.isDefault = val["isDefault"]
    return currentNode


if __name__ == "__main__":
    paths.configPath = sys.path[0] + '/../config'
    trees = createTrees()
    print(trees)





