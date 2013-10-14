#!/usr/bin/env python

doc_str = """
"""

import sys, os
import argparse
import math
from numbers import Number

def convert_to_num(s):
  """ convert string to number, if possible. Else leave it as a string. Similar to Perl. """
  try:
    i = int(s, 0)
    return i
  except ValueError:
    try:
      f = float(s)
      return f 
    except ValueError:
      return s
  except TypeError:
    return s

def line_to_num_list(fh):
  return map(convert_to_num, fh.readline().split())

class lpdict:
  def __init__(self):
    self.m                = 0
    self.n                = 0
    self.basic_indices    = []
    self.nonbasic_indices = []
    self.b_values         = []
    self.A                = []
    self.z_coeffs         = []
    self.large_value      = None
    self.epsilon          = 1e-8

  #def __repr__(self):
  #  r = "{m} {n}\n".format(self.m, self.n)
  #  # TODO 

  def __str__(self):
    r  = "{m} {n}\n".format(m=self.m, n=self.n)
    for i in range(self.m) :
      r += "{vi} | {bi} {Ai}\n".format(vi=self.basic_indices[i], bi=self.b_values[i], Ai=self.A[i])
    r += "z | {zc}\n".format(zc=self.z_coeffs)
    r += "       {nbi}\n".format(nbi=self.nonbasic_indices)
    return r

  def init_from_file(self,lpdict_filename):
    with open(lpdict_filename, 'r') as fh:
      m, n             = line_to_num_list(fh)

      basic_indices    = line_to_num_list(fh)
      nonbasic_indices = line_to_num_list(fh)
      assert len(basic_indices)    == m
      assert len(nonbasic_indices) == n

      b_values         = line_to_num_list(fh)
      assert len(b_values) == m

      A = []
      for i in range(int(m)):
        l = line_to_num_list(fh)
        assert len(l) == n
        A.append(l)

      z_coeffs         = line_to_num_list(fh)
      assert len(z_coeffs) == (n+1)

      # assert that we reached end of file ?

      #print m, n
      #print basic_indices
      #print nonbasic_indices
      #print b_values
      #print A
      #print z_coeffs

      self.m                = m               
      self.n                = n               
      self.basic_indices    = basic_indices   
      self.nonbasic_indices = nonbasic_indices
      self.b_values         = b_values        
      self.A                = A               
      self.z_coeffs         = z_coeffs        
      self.large_value      = m + n + 10 # some value larger than all variable indices.

  def find_entering_variable(self):
    entering_var = self.large_value
    for i, zc in enumerate(self.z_coeffs[1:]):
      var = self.nonbasic_indices[i]
      if 0 < zc <= self.epsilon :
        print "WARNING: zc for var", var, "is less than epsilon. Ignoring." 
      if self.epsilon < zc :
        if var < entering_var:
          entering_var = var
    if entering_var == self.large_value:
      return "FINAL"
    return entering_var

  def find_leaving_variable(self, entering_var):
    A_col = self.nonbasic_indices.index(entering_var)
    assert (self.z_coeffs[A_col+1] >= 0)
    leaving_var = self.large_value
    best_bound    = None
    for i in range(self.m):
      b = self.b_values[i]
      a = self.A[i][A_col]
      if -self.epsilon < a < self.epsilon:
        if a != 0 :
          print "WARNING: coeff for A row", i, "col", A_col, " is less than epsilon. Ignoring."
      else :
        bound = -1.0 * b / a
        if bound >= 0 :
          var = self.basic_indices[i]
          if best_bound == None or bound < best_bound or bound == best_bound and var < leaving_var:
            leaving_var = var
            best_bound = bound
    if best_bound == None :
      return "UNBOUNDED"
    else :
      #z_new = self.z_coeffs[0] + self.z_coeffs[A_col+1] * best_bound
      return leaving_var

  def pivot (self, entering_var, leaving_var):
    p_col = self.nonbasic_indices.index(entering_var)
    p_row = self.basic_indices.index(leaving_var)

    A = self.A # short name.
    m = self.m
    n = self.n

    # First pivot the row with the leaving_var
    aij = - A[p_row][p_col]
    A[p_row][p_col] = -1
    for i in range(n):
      A[p_row][i] = 1.0 * A[p_row][i] / aij
    self.b_values[p_row] = 1.0 * self.b_values[p_row] / aij

    # Now pivot the rest of the rows
    for j in range(m):
      if j != p_row :
        ajp = A[j][p_col]
        A[j][p_col] = 0
        for i in range(n):
          A[j][i] = A[j][i] + ajp * A[p_row][i]
        self.b_values[j] = self.b_values[j] + ajp * self.b_values[p_row]

    # Finally pivot the objective row, similar to the rows above.
    ajp = self.z_coeffs[p_col+1]
    self.z_coeffs[p_col+1] = 0
    for i in range(n):
      self.z_coeffs[i+1] = self.z_coeffs[i+1] + ajp * A[p_row][i]
    self.z_coeffs[0] = self.z_coeffs[0] + ajp * self.b_values[p_row]

    # And switch the lists of indices.
    self.basic_indices[p_row]    = entering_var
    self.nonbasic_indices[p_col] = leaving_var


    return self.z_coeffs[0]





def main(argv=None):
  """chutney main function"""

  if argv is None:
    argv = sys.argv
  prog_path = os.path.dirname(argv[0])     
  prog_abspath = os.path.abspath(prog_path)
  
  input_parser = argparse.ArgumentParser(description=doc_str)
  input_parser.add_argument('-lpdict', default='part1.lpdict', help='lpdictionary file')
  input_parser.add_argument('-part', default=1, type=int, help='1 or 2')
  try :
    args = input_parser.parse_args(argv[1:])
  except SystemExit :
    return 1

  mylpd = lpdict()
  mylpd.init_from_file(args.lpdict)

  if args.part == 1 :
    #print mylpd

    ev = mylpd.find_entering_variable()
    lv = mylpd.find_leaving_variable(ev)

    if not isinstance(ev, Number) :
      print ev
    elif not isinstance(lv, Number) :
      print lv
    else :
      print ev
      print lv
      zp = mylpd.pivot(ev, lv)
      if zp != None :
        if int(zp) == zp:
          print "%.1f"%(zp)
        else :
          print "%.4f"%(zp)
    
    #print mylpd

if __name__ == "__main__":
  sys.exit(main())
