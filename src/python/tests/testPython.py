import unittest
import sys
import logging


import pathHandling as PH
sys.path.append(PH.testMainDir)





def runAll():

    loader = unittest.TestLoader()
    # Get what is effectively an array of suites that are arrays of tests
    # Could iterate twice for finer grained control
    suite1 = loader.discover('router', pattern='*Test.py')

    suite = unittest.TestSuite([suite1])
    
    runner = unittest.TextTestRunner(verbosity=2)
    results = runner.run(suite)
    

if __name__ =="__main__":
    print("***************************************************************")
    print("Running Python tests")
    print("***************************************************************\n")
    runAll()

