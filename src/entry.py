
import os
import os.path as p
import logging
from itertools import chain, count

__all__ = ['SudokuPuzzle', 'RowCellGroup', 'ColCellGroup', 'SqrCellGroup', 'Cell']

class ExhaustedError(Exception):
    "Thrown when the solver gives up"

class ProcessingError(Exception):
    "Raised when a logic error occurs"


class SudokuPuzzle(object):
    
    indices = range(9)
    
    def __init__(self):
        self.rowGroups = [RowCellGroup(i) for i in self.indices]
        self.colGroups = [ColCellGroup(i) for i in self.indices]
        self.sqrGroups = [SqrCellGroup(i) for i in self.indices]
        self.rows = []
        
        for rg in self.rowGroups:
            row = []
            self.rows.append(row)
            for cg in self.colGroups:
                sg = self._getSquareGrp(rg.idx, cg.idx)
                row.append(Cell(rg, cg, sg))
        
        for row in self.rows:
            for cell in row:
                cell._connectCells()
    
    def _getSquareGrp(self, rowi, coli):
        'create index 0 - 9 from rowi, coli'
        GROUP_SIZE = 3
        grpi = GROUP_SIZE*(rowi/GROUP_SIZE)+(coli/GROUP_SIZE)
        return self.sqrGroups[grpi]
    
    def initFromBinFile(self, filename):
        with file(filename, 'rb') as fobj:
            vals = [ord(b) for b in fobj.read()]
        assert len(vals) == 81, 'expected 81 rows (got %d)'% len(vals)
        assert all(map(lambda c: type(c) is int, vals)), 'all rows need to be int vals'
        
        possibles = set(range(1,10))
        for i, v in enumerate(vals):
            if v == 0:
                continue
            rowi, coli = i/9, i%9
            self.rows[rowi][coli].excludeVals(possibles.difference((v,)))
    
    def outputBinFile(self, filename, error=None):
        with open(filename, 'wb') as fobj:
            if error:
                fobj.write(chr(32))
                fobj.write(error)
                return
            chrval = lambda cell: chr(cell.val) if cell.val else chr(0)
            cells = chain(*(rowgrp.cells for rowgrp in self.rowGroups))
            fobj.write(''.join([chrval(cell) for cell in cells]))
    
    def _rowStr(self, rowi):
        row = [c._shortStr() for c in self.rows[rowi]]
        join = lambda l: ' '.join([str(i) for i in l])
        return '|%s | %s | %s |'% (join(row[:3]), join(row[3:6]), join(row[6:]))
    
    def __str__(self):
        border = '-' * 24
        rows = [border]
        for rowi in range(9):
            rows.append(self._rowStr(rowi))
            if (rowi + 1) % 3 == 0:
                rows.append(border)
        return '\n'.join(rows)
    
    def solveCertain(self):
        ''' Solve as much of the puzzle as we can with certainty
        '''
        
        while True:
            foundClosedSet = False
            for grpList in (self.rowGroups, self.colGroups, self.sqrGroups):
                for grp in grpList:
                    for cellset in grp.findClosedSets():
                        foundClosedSet = True
                        closedSetVals = iter(cellset).next().possibles
                        uncertainCells = set(c for c in grp.cells if c.certainty < 1)
                        for cell in uncertainCells.difference(cellset):
                            if cell.certainty < 1: # could be changed from previous exclusions
                                cell.excludeVals(closedSetVals)
            if not foundClosedSet:
                break
    
    def solve(self):
        raise NotImplementedError



class CellGroup(object):
    
    def __init__(self, idx):
        self.idx = idx
        self.cells = []
    
    def _addCell(self, cell):
        self.cells.append(cell)
    
    def findClosedSets(self):
        ''' Find sets of cells with the same list of possibles where
              len(possibles) == len(setOfCells) ..
            Where this is true, we know that no other cells in the
              group can have those values.
        '''
        
        closedsets = []
        cells = set([c for c in self.cells if c.certainty < 1])
        while len(cells) > 0:
            testc = cells.pop()
            cs = set([testc])
            cs.update([c for c in cells
                       if testc.possibles == c.possibles])
            if len(cs) not in (1, 9) and len(cs) == len(testc.possibles):
                closedsets.append(cs)
            cells.difference_update(cs)
        
        return closedsets


class RowCellGroup(CellGroup):
    pass

class ColCellGroup(CellGroup):
    pass

class SqrCellGroup(CellGroup):
    pass


class Cell(object):
    
    def __init__(self, rowGrp, colGrp, sqrGrp):
        self.rowGrp = rowGrp
        self.rowGrp._addCell(self)
        self.colGrp = colGrp
        self.colGrp._addCell(self)
        self.sqrGrp = sqrGrp
        self.sqrGrp._addCell(self)
        
        self.possibles = set(range(1,10))
        self.val = None
        self.connected = None
    
    @property
    def certainty(self):
        return 1 if self.val else (9-len(self.possibles))/9
    
    def _checkKnown(self):
        if len(self.possibles) == 1:
            self.val = self.possibles.pop()
            assert len(self.possibles) == 0
            for connectedCell in list(self.connected):
                # recursion may have already disconnected:
                if connectedCell in self.connected:
                    connectedCell.disconnect(self)
    
    def excludeVals(self, vals):
        self.possibles.difference_update(vals)
        if len(self.possibles) == 0:
            raise ProcessingError('Removing all possible values')
        self._checkKnown()
    
    def excludeVal(self, val):
        if self.val:
            if val == self.val:
                raise ProcessingError('Excluding only possible')
            return
        
        if val in self.possibles:
            self.possibles.remove(val)
        if len(self.possibles) == 0:
            raise ProcessingError('Removing all possible values')
        self._checkKnown()
    
    def disconnect(self, cell):
        "called by a connected cell when it's value becomes known"
        self.connected.remove(cell)
        self.excludeVal(cell.val)
    
    def _connectCells(self):
        "called after construction to create cell connections"
        assert self.connected == None, 'already connected'
        self.connected = set()
        for grp in self.rowGrp, self.colGrp, self.sqrGrp:
            for cell in grp.cells:
                if cell is self:
                    continue
                self.connected.add(cell)
    
    def _shortStr(self):
        if self.val:
            return '%d'% self.val
        if len(self.possibles) <= 3:
            return str(tuple(self.possibles))
        return '%s, ...'% ', '.join(map(str, list(self.possibles)[:3]))
    
    def __str__(self):
        return 'Cell @ (%d, %d) (%s)'% (
            self.rowGrp.idx, self.colGrp.idx, self._shortStr()
        )


def main():
    import sys
    
    if len(sys.argv) < 3:
        print 'usage: %s [input_file] [output_file]'
    
    logging.basicConfig(level=logging.INFO)
    inpth, outpth = sys.argv[1:3]
    
    pzl = SudokuPuzzle()
    pzl.initFromBinFile(inpth)
    logging.info(' Result: \n%s'% pzl)
    pzl.solveCertain()
    logging.info(' Result: \n%s'% pzl)
    pzl.outputBinFile(outpth)

if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        logging.exception(e)
        raw_input()

#    testd = r'\\ZD\Users\charlie\Documents\eclipse_workspace\sudoku'
#    
#    logging.basicConfig(level=logging.INFO)
#    pzl = SudokuPuzzle()
#    pzl.initFromBinFile(p.join(testd, 'snail2.in'))
#    logging.info(' Result: \n%s'% pzl)
#    pzl.solveCertain()
#    logging.info(' Result: \n%s'% pzl)
    
    
#    for fn in os.listdir(testd):
#        if fn.endswith('.in'):
#            pth = p.join(testd, fn)
#            outfobj = file(p.splitext(pth)[0] + '.out', 'wb')
#            pzl = SudokuPuzzle()
#            pzl.initFromBinFile(pth)
#            logging.info(' Result: \n%s'% pzl)
            
#            try:
#                pzl.bruteSolve()
#            except Exhausted, e:
#                for c in pzl.rows:
#                    outfobj.write(chr(c))
#            except Exception, e:
#                logging.exception(e)
#                outfobj.write(chr(32))
#                outfobj.write(str(e))
#            else:
#                for c in pzl.rows:
#                    outfobj.write(chr(c))
            





















