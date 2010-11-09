
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


class CellGroup(object):
    
    def __init__(self, idx):
        self.idx = idx
        self.cells = []
    
    def _addCell(self, cell):
        self.cells.append(cell)
    
    def findExclusives(self):
        'Find cells that contain all of a certain set of values'
        cells = list(self.cells)
        for i, c in enumerate(cells):
            cl = [test for test in cells[i:]
                  if test.possibles == c.possibles]

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




if __name__ == '__main__':
    
    testd = r'\\ZD\Users\charlie\Documents\eclipse_workspace\sudoku'
    
    logging.basicConfig(level=logging.INFO)
    pzl = SudokuPuzzle()
    pzl.initFromBinFile(p.join(testd, '11-1.in'))
    logging.info(' Result: \n%s'% pzl)
    
    
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
            





















