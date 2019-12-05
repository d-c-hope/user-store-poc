import unittest
import json
from controller import pathTransforms
from controller.pathNode import PathNode



p1 = PathNode('profile', isTerminal=False,
                    schema=None, pathString='profile',
                    defaultType="core", postEndpoint=True,
                    isIdRoot=True, isDefault=False)
p2 = PathNode('23', isTerminal=False,
              schema=None, pathString='<id>',
              defaultType="core", postEndpoint=False,
              isIdRoot=False, isDefault=False)
p3 = PathNode('coreprofile', isTerminal=False,
              schema=None, pathString='profile',
              defaultType="", postEndpoint=False,
              isIdRoot=False, isDefault=True)
p3a = PathNode('optouts', isTerminal=False,
              schema=None, pathString='profile',
              defaultType="", postEndpoint=False,
              isIdRoot=False, isDefault=True)

p4 = PathNode('persona', isTerminal=False,
                    schema=None, pathString='profile',
                    defaultType="core", postEndpoint=True,
                    isIdRoot=True, isDefault=False)
p5 = PathNode('4444', isTerminal=False,
              schema=None, pathString='<id>',
              defaultType="core", postEndpoint=False,
              isIdRoot=False, isDefault=False)
p6 = PathNode('core', isTerminal=False,
              schema=None, pathString='profile',
              defaultType="", postEndpoint=False,
              isIdRoot=False, isDefault=True)
    
class TestPathTransforms(unittest.TestCase):

    def testGetOuterPathList(self):
        p1 = PathNode('profile', isTerminal=False,
                    schema=None, pathString='profile',
                    defaultType="core", postEndpoint=True,
                    isIdRoot=True, isDefault=False)
        p2 = PathNode('23', isTerminal=False,
                      schema=None, pathString='<23>',
                      defaultType="core", postEndpoint=False,
                      isIdRoot=False, isDefault=False)
        p3 = PathNode('coreprofile', isTerminal=False,
                      schema=None, pathString='profile',
                      defaultType="", postEndpoint=False,
                      isIdRoot=False, isDefault=True)

        oList1 = pathTransforms.getOuterPathList([p1, p2, p3])
        self.assertEqual(oList1, [])

        oList3 = pathTransforms.getOuterPathList([p1, p2, p4, p5, p6])
        self.assertEqual([o.pathVal for o in oList3], ['profile', '23'])


