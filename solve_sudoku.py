#!/usr/bin/env python

doc_str = """
 Solve sudoku.
"""

import sys, os
import argparse
from   numbers import Number
from   lpdict import lpdict, convert_to_num, table_to_str, line_to_num_list
import pprint

class sudoku :
  def __init__ (self, sN):
    self.sN  = sN
    N = sN * sN
    self.N   = N
    self.NN  = N*N
    self.NNN = N*N*N

    self.sarray = []
    for i in range(N) :
      self.sarray.append([0]*N)

    self.A = []
    self.b = []

  def __str__ (self):
    table = []
    N = self.N
    for i in range(N+1):
      row = ['-'] * (2*N + 1)
      table.append(row)
      if i == N:
        break

      row = (zip(['|']*(N), self.sarray[i]))
      row = [tn for t in row for tn in t] # flatten
      row = row + ['|']
      table.append(row)
    for r in range(len(table)):
      for c in range(len(table[r])):
        if table[r][c] == 0:
          table[r][c] = ' '

    return table_to_str(table)

  def init_from_file (self,sfile,sffmt):
    N = self.N
    # First fmt is just a list of numbers, one line per row, whitespace separators.
    if sffmt == None or sffmt == 1:
      sep = None
      with open(sfile, 'r') as fh:
        for i in range(N):
          line = line_to_num_list(fh, sep)
          line = [x if 1 <= x <= N else 0 for x in line]
          self.sarray[i] = line
        s = fh.readline() # Try to read past end.
        if s == "":
          return
        elif sffmt == 1:
          assert 0, "Characters left over while using sffmt = 1"

    # second fmt is the output we print being read back in.
    if sffmt == None or sffmt == 2:
      sep = '|'
      with open(sfile, 'r') as fh:
        for i in range(N):
          fh.readline() # discard h-line.
          line = line_to_num_list(fh, sep)
          line = line[1:-1]
          line = [x if 1 <= x <= N else 0 for x in line]
          self.sarray[i] = line
        fh.readline() # discard h-line.
        s = fh.readline() # Try to read past end.
        if s == "":
          return
        elif sffmt == 2:
          assert 0, "Characters left over while using sffmt = 2"

  def create_AB (self):
    """ Create the A and B matrices that represent the constraints with Ax = b"
        x is defined using N variables for each position, 
        i.e. each variable is xij_eq_k and can only take values 0 and 1.
    """
    A  = [] ; B  = []
    N   = self.N   ; NN  = self.NN  ; 
    NNN = self.NNN ; sN  = self.sN  ; 

    # Rule 1 : Each position can have only one value.
    # So, summation over k xij_eq_k = 1
    for i in range(NN):
      A_row = [0]*(i*N) + [1]*N + [0]*((NN-i-1)*N)
      A.append(A_row)
      B.append(1)

    # NOTE : val in the following 4 loops is 0-based, not 1-based.

    # Rule 2 : Each row can have only one of each value.
    for row in range(N):
      for val in range(N):
        for i in range(NNN):
          irow = i // NN
          if irow == row and i % N == val:
            A_row[i] = 1
          else :
            A_row[i] = 0
        A.append(A_row)
        B.append(1)

    # Rule 3 : Each col can have only one of each value.
    for col in range(N):
      for val in range(N):
        for i in range(NNN):
          icol = (i % NN) // N
          if icol == col and i % N == val:
            A_row[i] = 1
          else :
            A_row[i] = 0
        A.append(A_row)
        B.append(1)

    # Rule 4 : Each square can have only one of each value.
    for sq in range(N):
      for val in range(N):
        for i in range(NNN):
          irow = i // NN
          icol = (i % NN) // N
          isq  = (irow // sN) * sN + (icol // sN)
          if isq == sq and i % N == val:
            A_row[i] = 1
          else :
            A_row[i] = 0
        A.append(A_row)
        B.append(1)

    # Rule 5 : The specified values must be respected.
    for row in range(N):
      for col in range(N):
        sval = self.sarray[row][col]
        if sval != 0 :
          for val in range(N):
            pos = row*NN + col*N + val
            A_row = [0]*(pos) + [1] + [0]*(NNN - pos - 1)
            B_val = 1 if (sval == val+1) else 0
            A.append(A_row)
            B.append(B_val)

    self.A = A
    self.B = B

    #AB = zip(A,B)
    #for x in AB:
    #  print x



def main(argv=None):
  """main function"""

  if argv is None:
    argv = sys.argv
  prog_path = os.path.dirname(argv[0])     
  prog_abspath = os.path.abspath(prog_path)
  
  input_parser = argparse.ArgumentParser(description=doc_str)
  input_parser.add_argument('-sN', default=2, type=int, help='sudoku size param. 2 = 4x4 sudoku, 3 = 9x9 sudoku.')
  input_parser.add_argument('-sfile', help='file specifying the sudoku array.')
  input_parser.add_argument('-sffmt', default=None, type=int, help='specify the fmt of the sfile')
  input_parser.add_argument('-debug')
  try :
    args = input_parser.parse_args(argv[1:])
  except SystemExit :
    return 1

  mysudoku = sudoku(args.sN)
  mysudoku.init_from_file(args.sfile, args.sffmt)
  print mysudoku
  mysudoku.create_AB()

if __name__ == "__main__":
  sys.exit(main())
