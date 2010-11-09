import os
import os.path as p

import logging

import unittest
from entry import SudokuPuzzle



class Test(unittest.TestCase):

    testd = r'C:\sudoku'

    def testName(self):
        pass

    def testRead(self):
        for fn in os.listdir(self.testd):
            if fn.endswith('.in'):
                pth = p.join(self.testd, fn)
                print '%s: \n%s'% (fn, SudokuPuzzle.fromRawFile(pth))
    
    def testGetRow(self):
        fn = '11-1.in'
        pzl = SudokuPuzzle.fromRawFile(p.join(self.testd, fn))
        expected = [4, 6, 2, 0, 0, 5, 0, 0, 0]
        found = pzl._getRow(0)
        self.assertTrue(found == expected)
        expected = [7, 0, 8, 0, 0, 9, 0, 0, 0]
        found = pzl._getRow(2)
        self.assertTrue(found == expected)
    
    def testGetCol(self):
        fn = '11-1.in'
        pzl = SudokuPuzzle.fromRawFile(p.join(self.testd, fn))
        expected = [0, 0, 0, 2, 7, 0, 1, 0, 9]
        found = pzl._getCol(8)
        self.assertTrue(found == expected)

    def testGetGroup(self):
        fn = '11-1.in'
        pzl = SudokuPuzzle.fromRawFile(p.join(self.testd, fn))
        expected = [0, 5, 0, 0, 0, 0, 0, 2, 0]
        found = pzl._getGroup(5, 5)
        self.assertTrue(found == expected)
    
    def testBruteSolve(self):
        bruteSolve

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()










