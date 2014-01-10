
Overview
========

This project started as an interview question for [Watchfire Signs]{http://www.watchfiresigns.com/}

The original instructions are in test/Requirements.txt

Files
-----

 * entry.py: This is the main source .. poorly named file
 * pzltest.py: I set this up while developing it initially, but haven't kept it up to date

In the initial 2 hours my solver only solved the first 2 puzzles. I used the "how would I 
solve this as a human" strategy at first; there are other things I could do here .. but after 
I've identified all the entries I can without guessing, I fall back to a recursive constraint 
solving approach. I didn't recognize it as such, but it's basically the same idea Peter Norvig
uses [here]{http://norvig.com/sudoku.html}, although his code is much more compact and skips
the non-guesswork stuff altogether (i.e., no CellGroup.findClosedSets()).  His puzzle generation
function is pretty sweet too ..

I might some day add other strategies to SudokuPuzzle.solveCertain() .. it might be nice
to create a toy that would teach the strategies, giving hints to players when they get stuck
etc. 

License
-------

Public domain .. not sure why you'd want it tho!