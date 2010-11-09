import os
import os.path as p

import logging

import unittest
from entry import *



class Test(unittest.TestCase):

    testd = r'\\ZD\Users\charlie\Documents\eclipse_workspace\sudoku'

#    def testRead(self):
#        for fn in os.listdir(self.testd):
#            if fn.endswith('.in'):
#                pth = p.join(self.testd, fn)
#                print '%s: \n%s'% (fn, SudokuPuzzle().initFromBinFile(pth))
    
    def setup2cells(self):
        rgrp, cgrp, sgrp = RowCellGroup(0), ColCellGroup(0), SqrCellGroup(0)
        c1 = Cell(rgrp, cgrp, sgrp)
        c2 = Cell(rgrp, cgrp, sgrp)
        c1._connectCells()
        c2._connectCells()
        self.assert_(c1.connected == set([c2]))
        self.assert_(c2.connected == set([c1]))
        return c1, c2
    
    def testCellUpdate(self):
        c1, c2 = self.setup2cells()
        c1.excludeVals(range(1,9))
        self.assert_(c1.val == 9)
        self.assert_(9 not in c2.possibles)
    
    def testCircularUpdate(self):
        c1, c2 = self.setup2cells()
        c1.excludeVals(range(1,8))
        c2.excludeVals(range(1,8))
        self.assert_(c1.possibles == set([8, 9]))
        self.assert_(c2.possibles == c1.possibles)
        c1.excludeVal(8)
        self.assert_(c1.val == 9)
        self.assert_(c2.val == 8)
    
#    def testCellUpdate(self):
#        fn = '11-1.in'
#        pzl = SudokuPuzzle()
#        pzl.initFromBinFile(p.join(self.testd, fn))
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()










