
import os
import os.path as p
import logging
from itertools import chain, count



class BohError(Exception):
    "Couldn't solve the puzzle :("




class SudokuPuzzle(object):
    
    _logger = logging.getLogger('Puzzle Logger')
    
    def __init__(self, cells):
        assert len(cells) == 81, 'expected 81 cells (got %d)'% len(cells)
        assert all(map(lambda c: type(c) is int, cells)), 'all cells need to be int vals'
        
#        self.rows = [[set() if c == 0 else set(c) for c in row]
#                     for row in cells]
        self.cells = [set() if c == 0 else set(c)
                      for c in cells]
    
    @classmethod
    def fromRawFile(cls, filename):
        'Factory method to construct from bytes file ..'
        bl = file(filename, 'rb').read()
        return cls([ord(b) for b in bl])
    
    def _getRow(self, rowi):
        assert rowi < 9
        return self.cells[9*rowi:(9*rowi)+9]
    
    def _getCol(self, coli):
        assert coli < 9
        rows = [self._getRow(i) for i in range(9)]
        return list(zip(*rows)[coli])
    
    def _getGroup(self, rowi, coli):
        assert rowi < 9 and coli < 9
        if rowi < 3:
            rows = [self._getRow(ridx) for ridx in range(3)]
        elif rowi < 6:
            rows = [self._getRow(ridx) for ridx in range(3, 6)]
        else:
            rows = [self._getRow(ridx) for ridx in range(6, 9)]
        colStart = 3 * (coli / 3)
        return list(chain(*[r[colStart:colStart+3] for r in rows]))
    
    
    def _rowStr(self, rowi):
        row = self._getRow(rowi)
        itos = lambda l: ' '.join([str(i) for i in l])
        return '|%s | %s | %s |'% (itos(row[:3]), itos(row[3:6]), itos(row[6:]))
    
    possibles = range(1,10)
    def _getRowPossibles(self, rowi):
        r = self._getRow(rowi)
#        assert r[cellidx] == 0, 'getting possibles for solved cell'
        return [i for i in self.possibles if i not in r]
    
    def _getColPossibles(self, coli):
        c = self._getCol(coli)
        return [i for i in self.possibles if i not in c]
    
    def _getGroupPossibles(self, rowi, coli):
        g = self._getGroup(rowi, coli)
        return [i for i in self.possibles if i not in g]
    
    def __str__(self):
        border = '-' * 24
        rows = [border]
        for rowi in range(9):
            rows.append(self._rowStr(rowi))
            if (rowi + 1) % 3 == 0:
                rows.append(border)
        return '\n'.join(rows)
    
    def _unsolved(self):
        return self.cells.count(0) > 0
    
    def _easyEliminate(self, rowi, coli):
        pl = set(self.possibles)
        pl.difference_update(self._getRow(rowi))
        pl.difference_update(self._getCol(coli))
        group = self._getGroup(rowi, coli)
        pl.difference_update(group)
        return pl
    
    def _eliminatePairs(self, rowi, coli, pl):
        pass
    
    def _setupPossibles(self):
        pass
    
    def bruteSolve2(self):
        
        self._logger.info(' Solving:\n%s'% self)
        self._setupPossibles()
    
    def bruteSolve(self):
        
        self._logger.info(' Solving:\n%s'% self)
        
        for i in count():
            if not self._unsolved():
                self._logger.info(' Solved :) .. \n%s'% self)
                return
            
            gotOne = False
            self._logger.debug('Solve Pass %d'% i)
            for rowi in range(9):
                for coli in range(9):
                    if self.cells[rowi*9+coli] != 0:
                        continue
                    pl = self._easyEliminate(rowi, coli)
                    pl = self._eliminatePairs(rowi, coli, pl)
                    assert len(pl) > 0, 'not 0 but no possibles??'
                    if len(pl) == 1:
                        gotOne = True
                        self.cells[rowi*9+coli] = pl.pop()
                    else:
                        self._logger.debug(
                            'Possibles for (%d, %d): %s'% (rowi, coli, pl)
                        )
            
            if not gotOne:
                self._logger.info(" Failed :( \n%s"% self)
                raise BohError("Naive solve didn't work")

if __name__ == '__main__':
#    logging.basicConfig(level=logging.INFO)
#    pzl = SudokuPuzzle.fromRawFile(r'C:\sudoku\11-1.in')
#    pzl.bruteSolve()
    
    testd = r'\\ZD\Users\charlie\Documents\eclipse_workspace\sudoku'
    
    for fn in os.listdir(testd):
        if fn.endswith('.in'):
            pth = p.join(testd, fn)
            outfobj = file(p.splitext(pth)[0] + '.out', 'wb')
            pzl = SudokuPuzzle.fromRawFile(pth)
            try:
                pzl.bruteSolve()
            except BohError, e:
                for c in pzl.cells:
                    outfobj.write(chr(c))
            except Exception, e:
                logging.exception(e)
                outfobj.write(chr(32))
                outfobj.write(str(e))
            else:
                for c in pzl.cells:
                    outfobj.write(chr(c))
            





















