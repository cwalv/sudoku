
import logging
import copy

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
    
    def _rowStr(self, colWidths, row):
        row = [c.center(colWidths[i]) for i, c in enumerate(row)]
        return '| %s | %s | %s |'% (
            ' '.join(row[:3]), ' '.join(row[3:6]), ' '.join(row[6:])
        )
    
    def __str__(self):
        rows = [[c._shortStr() for c in row]
                for row in self.rows]
        colWidths = [max([len(c) for c in col])
                     for col in zip(*rows)]
        
        border = '_'*(sum(colWidths)+16)
        rowstrs = [border]
        for rowi, row in enumerate(rows):
            rowstrs.append(self._rowStr(colWidths, row))
            if (rowi + 1) % 3 == 0:
                rowstrs.append(border)
        
        return '\n'.join(rowstrs)
    
    @property
    def solved(self):
        for cell in self.cells:
            if not cell.solved:
                return False
        return True
    
    @property
    def cells(self):
        for row in self.rows:
            for cell in row:
                yield cell
    
    @property
    def groups(self):
        for grpList in (self.rowGroups, self.colGroups, self.sqrGroups):
            for grp in grpList:
                yield grp
    
    def _getGroupsByUncertainty(self):
        unsolvedGroups = filter(lambda g: g.certainty < 1.0, self.groups)
        return sorted(unsolvedGroups, key=lambda g: g.certainty, reverse=True)
    
    
    def initFromBinFile(self, filename):
        with file(filename, 'rb') as fobj:
            vals = [ord(b) for b in fobj.read()]
        assert len(vals) == 81, 'expected 81 rows (got %d)'% len(vals)
        assert all(map(lambda c: type(c) is int, vals)), 'all rows need to be int vals'
        
        for i, v in enumerate(vals):
            if v == 0:
                continue
            rowi, coli = i/9, i%9
            self.rows[rowi][coli].setValue(v)
    
    def outputBinFile(self, filename, error=None):
        with open(filename, 'wb') as fobj:
            if error:
                fobj.write(chr(32))
                fobj.write(error)
                return
            chrval = lambda cell: chr(cell.val) if cell.val else chr(0)
            fobj.write(''.join([chrval(cell) for cell in self.cells]))
    
    def solveCertain(self):
        ''' Solve as much of the puzzle as we can with certainty
        '''
        
        while True:
            modifiedPuzzle = False
            for grp in self._getGroupsByUncertainty():
                for cellset in grp.findClosedSets():
                    closedSetVals = iter(cellset).next().possibles
                    uncertainCells = set(c for c in grp.cells if c.certainty < 1)
                    for cell in uncertainCells.difference(cellset):
                        if not cell.solved: # could be changed from previous exclusions
                            if len(closedSetVals - cell.possibles) < len(closedSetVals):
                                modifiedPuzzle = True
                                cell.excludeVals(closedSetVals)
            if not modifiedPuzzle:
                break
    
    def clone(self):
        return copy.deepcopy(self)
    
    def solve(self):
        '''
        Solve the puzzle, even if it involves guessing ...
        '''
        
        def recTestAllPossibles(pzl, cellIdx, unsolvedCells):
            ''' recursively try all possible values for all unsolved cells
            '''
            
            assert cellIdx < len(unsolvedCells), 'recursed on solved pzl?'
            cell = unsolvedCells[cellIdx] 
            if cell.solved:
                return pzl
            
            for val in cell.possibles:
                clone = pzl.clone()
                clonecell = clone.rows[cell.rowGrp.idx][cell.colGrp.idx]
                try:
                    clonecell.setValue(val)
                    clone.solveCertain()
                    if clone.solved:
                        break
                    # Guess another cell ...
                    clone = recTestAllPossibles(clone, cellIdx+1, unsolvedCells)
                    assert clone.solved, 'recTestAllPossibles returned unsolved'
                    break
                except ProcessingError:
                    # incorrect value .. try a different one
                    continue                
            else:
                raise ProcessingError("no val in possibles worked")
            
            assert clone.solved, 'break in unsolved test?'
            return clone # Solved Test ..
        
        self.solveCertain()
        if self.solved: # No Need for the guesswork ..
            return
        
        # Create an iterator of unsolved cells, putting the ones with the
        #   highest probability of being solved correctly and their being
        #   guessed correctly first ...
        groupCertainty = {}
        def cellGroupCertainty(cell):
            if not groupCertainty.has_key(cell):
                groups = (cell.rowGrp, cell.colGrp, cell.sqrGrp)
                groupCertainty[cell] = sum([grp.certainty for grp in groups])
            return groupCertainty[cell]
        
        sortkey = lambda cell: (cell.certainty, cellGroupCertainty(cell))
        unsolvedCells = [cell for cell in self.cells if not cell.solved]
        sortedUnsolvedCells = sorted(unsolvedCells, key=sortkey, reverse=True)
        solved = recTestAllPossibles(self, 0, sortedUnsolvedCells)
        
        # Copy solved vals back into self ..
        for unsolved, solved in zip(self.cells, solved.cells):
            unsolved.setValue(solved.val)


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
    
    def _cellsByUncertainty(self):
        ''' Get unsolved cells sorted by least uncertainty
        '''
        unsolvedCells = filter(lambda c: c.certainty < 1, self.cells)
        return sorted(unsolvedCells, key=lambda c: c.certainty, reverse=True)
    
    @property
    def certainty(self):
        return sum(c.certainty for c in self.cells)/len(self.cells)


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
        return 1 if self.val else (9.0-len(self.possibles))/9.0
    
    @property
    def solved(self):
        return self.val is not None
    
    def _checkKnown(self):
        if len(self.possibles) == 1:
            self.val = self.possibles.pop()
            assert len(self.possibles) == 0
            for connectedCell in list(self.connected):
                # recursion may have already disconnected:
                if connectedCell in self.connected:
                    connectedCell.disconnect(self)
    
    def setValue(self, val):
        if self.val is not None:
            if self.val != val:
                raise ProcessingError('Setting val in already set cell')
            return
        self.excludeVals(self.possibles.difference((val,)))
    
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
        return '(%s, ...)'% ', '.join(map(str, list(self.possibles)[:3]))
    
    def __str__(self):
        return 'Cell @ (%d, %d) (%s)'% (
            self.rowGrp.idx, self.colGrp.idx, self._shortStr()
        )


def main(inpth, outpth):
    pzl = SudokuPuzzle()
    pzl.initFromBinFile(inpth)
    logging.info(' Result: \n%s'% pzl)
    pzl.solve()
    logging.info(' Result: \n%s'% pzl)
    pzl.outputBinFile(outpth)

if __name__ == '__main__':
    
    logging.basicConfig(level=logging.INFO)
    
    import os
    import sys
    
    if len(sys.argv) < 3:
        scriptname = os.path.basename(sys.argv[0])
        print 'usage: %s [input_file] [output_file]'% scriptname
        sys.exit(1)
    
    inpth, outpth = sys.argv[1:3]
    
    try:
        main(inpth, outpth)
    except Exception, e:
        logging.exception(e)
        raw_input()









