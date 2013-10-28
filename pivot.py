#!/usr/bin/env python

doc_str = """
"""

import sys, os
import argparse
import math
from numbers import Number
import copy
import fractions

# Using fractions is so clean, but it is also 5-6 times slower. Hence we have an option to control its usage.
use_fractions = False

one = fractions.Fraction(1.0) if use_fractions else 1.0

# epsilon comparisons
# Ignore differences smaller than epsilon.
# Centralize the code here.
epsilon = fractions.Fraction(1e-10) if use_fractions else 1e-10
def eps_cmp_lt(a,b):
  rv = ( ((a) + epsilon) <  (b) )
  return rv
def eps_cmp_le(a,b):
  rv = ( ((a) - epsilon) <= (b) )
  return rv
def eps_cmp_eq(a,b):
  rv = ( ((a) - epsilon) < (b) < ((a) + epsilon) )
  return rv
def eps_cmp_gt(a,b):
  return eps_cmp_lt(b,a) # a > b => b < a
def eps_cmp_ge(a,b):
  return eps_cmp_le(b,a) # a >= b => b <= a
def eps_cmp_ne(a,b):
  return not eps_cmp_eq(a,b)

def is_integer(n):
  rv = eps_cmp_eq(n, round(n))
  #if abs(n) < epsilon:
  #  print n, int(n), rv
  return rv

def frac(n):
  """ positive fractional part of n """
  if use_fractions :
    return (n - fractions.Fraction(math.floor(n)))
  else :
    return (n - math.floor(n))

def convert_to_num(s):
  """ convert string to number, if possible. Else leave it as a string. Similar to Perl. """
  try:
    i = int(s, 0)
    return i
  except ValueError:
    if use_fractions:
      try:
        fr = fractions.Fraction(s)
        return fr
      except ValueError:
        pass
    try:
      f = float(s)
      return f 
    except ValueError:
      return s
  except TypeError:
    return s

def line_to_num_list(fh):
  return map(convert_to_num, fh.readline().split())

def table_to_str(table):
  str_table = [map(str,x) for x in table]
  table_ht = len(table)
  table_wd = len(table[0])

  rowformat = ""
  for i in range(table_wd):
    maxlen = max([len(x[i]) for x in str_table])
    rowformat += "{:>%d} "%(maxlen)
  rowformat += "\n"

  r = ""
  for row in str_table:
    r += rowformat.format(*row)
  return r

class lpdict:
  def __init__ (self):
    self.m                = 0
    self.n                = 0
    self.basic_indices    = []
    self.nonbasic_indices = []
    self.b_values         = []
    self.A                = []
    self.z_coeffs         = []
    self.shdw_z_coeffs     = []
    self.large_value      = None

  # repr is the string form that could be used to recreate the object.
  #def __repr__ (self):
  #  r = "{m} {n}\n".format(self.m, self.n)
  #  # TODO 

  # str is the user-readable string form.
  def __str__ (self):
    def my_flatten (l) :
      return list(l[:-1]) + l[-1]
    table = map(my_flatten, zip (self.basic_indices, ["|"]* self.m, self.b_values, self.A))
    table.append( ['-']*(self.n+3))
    table.append( ['z'] + ['|'] + self.z_coeffs)
    table.append( ['s'] + ['|'] + self.shdw_z_coeffs)
    table.append( ['','','']  + self.nonbasic_indices)
    return table_to_str(table)

  def init_from_file (self,lpdict_filename):
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
      self.shdw_z_coeffs    = [0]*(self.n+1)
      self.large_value      = m + n + 10 # some value larger than all variable indices.

  def find_entering_variable (self):
    entering_var = self.large_value
    for i, zc in enumerate(self.z_coeffs[1:]):
      var = self.nonbasic_indices[i]
      if eps_cmp_gt(zc,0):
        if var < entering_var:
          entering_var = var
    if entering_var == self.large_value:
      return "FINAL"
    return entering_var

  def find_leaving_variable (self, entering_var):
    A_col = self.nonbasic_indices.index(entering_var)
    assert (self.z_coeffs[A_col+1] >= 0)
    leaving_var = self.large_value
    best_bound  = None
    for i in range(self.m):
      b = self.b_values[i]
      a = self.A[i][A_col]
      if eps_cmp_lt(a,0):
        bound = -one * b / a
        if eps_cmp_ge(bound,0):
          var = self.basic_indices[i]
          if best_bound == None or eps_cmp_lt(bound, best_bound) or eps_cmp_eq(bound, best_bound) and var < leaving_var: 
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
      A[p_row][i] = one * A[p_row][i] / aij
    self.b_values[p_row] = one * self.b_values[p_row] / aij

    # Now pivot the rest of the rows
    for j in range(m):
      if j != p_row :
        ajp = A[j][p_col]
        A[j][p_col] = 0
        for i in range(n):
          A[j][i] = A[j][i] + ajp * A[p_row][i]
        self.b_values[j] = self.b_values[j] + ajp * self.b_values[p_row]

    # And switch the lists of indices.
    self.basic_indices[p_row]    = entering_var
    self.nonbasic_indices[p_col] = leaving_var

    # Finally pivot the objective rows, similar to the rows above.
    for zrow in self.z_coeffs, self.shdw_z_coeffs:
      if len(zrow) > 0:
        ajp = zrow[p_col+1]
        zrow[p_col+1] = 0
        for i in range(n):
          zrow[i+1] = zrow[i+1] + ajp * A[p_row][i]
        zrow[0] = zrow[0] + ajp * self.b_values[p_row]

    return self.z_coeffs[0]

  def auxiliarize (self): # Convert to auxiliary dictionary
    # Add +x0 to every constraint equation
    for i in range(self.m):
      self.A[i].append(1)
    self.nonbasic_indices.append(0)
    # Modify regular objective to include x0
    self.z_coeffs.append(0)
    # Move it to the shadow copy
    self.shdw_z_coeffs = self.z_coeffs
    # Set up the aux objective.
    self.z_coeffs = [0]*(self.n+1) + [-1]
    # Record new dictionary size
    self.n += 1
    self.large_value += 1

  def unauxiliarize (self): # Convert back to regular form.
    # remove column containing x0
    c0 = self.nonbasic_indices.index(0)
    for i in range(self.m):
      self.A[i] = self.A[i][:c0] + self.A[i][c0+1:]
    self.z_coeffs      = self.z_coeffs[:c0+1]      + self.z_coeffs[c0+2:]
    self.shdw_z_coeffs = self.shdw_z_coeffs[:c0+1] + self.shdw_z_coeffs[c0+2:]
    self.nonbasic_indices.remove(0)
    # Reduce size
    self.n -= 1
    self.large_value -= 1
    # Move original objective back in place. Forget about aux objective
    self.z_coeffs = self.shdw_z_coeffs
    self.shdw_z_coeffs = [0]*(self.n+1)
  
  def first_aux_pivot (self): # First pivot for aux dictionary
    #print self
    ev = 0
    lv = self.basic_indices[self.b_values.index(min(self.b_values))] # var with smallest b value.
    self.pivot(ev,lv)

  def simplex_step (self):
    ev = self.find_entering_variable()
    if not isinstance(ev, Number) : # final
      return ev

    lv = self.find_leaving_variable(ev)
    if not isinstance(lv, Number) : # unbounded
      return lv

    zn = self.pivot(ev,lv)
    return zn    # new objective value.

  def run_simplex(self):
    """ Pivot till we reach a final dictionary or hit a problem"""
    while True :
      #print self
      srv = self.simplex_step()
      if not isinstance(srv, Number) : # final or unbounded
        if srv == "FINAL":
          return self.z_coeffs[0]
        else :
          return srv

  def solve_lp (self):
    """ Full LP solver, including handling of initialization if needed"""
    if not self.is_feasible():
      self.auxiliarize()
      self.first_aux_pivot()
      aux_z = self.run_simplex()
      if eps_cmp_ne (aux_z, 0):
        return "INFEASIBLE"
      self.unauxiliarize()

    final_z = self.run_simplex()
    return final_z

  def is_feasible (self):
    if eps_cmp_lt ( min(self.b_values), 0) :
      return False
    else :
      return True

  def is_degenerate (self):
    if (min(self.b_values) == 0):
      return True
    else :
      return False

  def variable_values (self):
    vars = self.basic_indices + self.nonbasic_indices
    vals = self.b_values + [0]*(self.n)
    vvs  = zip (vars,vals)
    vvs.sort()
    return vvs

  def is_integral (self):
    """ Is the current dictionary integral in all variable values. """
    #print self
    for b in self.b_values:
      if not is_integer(b):
        #print b, int(b)
        #print "is_integral = False"
        return False
    #print "is_integral = True"
    return True

  def add_ilp_cut (self, k, use_z):
    """ k is the row based on which we need to add a cut """

    new_var_num = self.m + self.n + 1
    if use_z:
      assert not is_integer(self.z_coeffs[0])
      new_b_val     = -frac(self.z_coeffs[0])
      new_A_row     = [frac(-aki) for aki in self.z_coeffs[1:]]
    else :
      assert k < self.m
      assert not is_integer(self.b_values[k])
      new_b_val     = -frac(self.b_values[k])
      new_A_row     = [frac(-aki) for aki in self.A[k]]

    self.basic_indices.append(new_var_num)
    self.b_values.append(new_b_val)
    self.A.append(new_A_row)
    self.m += 1
    self.large_value += 1

  def add_all_ilp_cuts (self):
    m = self.m
    for i in range(m):
      if not is_integer(self.b_values[i]):
        self.add_ilp_cut(i, False)
    # TODO : Not sure why adding z-cuts generates wrong results.
    #if not is_integer(self.z_coeffs[0]):
    #  self.add_ilp_cut(0, True)

  def solve_ilp (self):
    #print self
    while True :
      #print self
      lps = self.solve_lp()
      #print self
      if not isinstance(lps, Number) :
        return lps.lower()
      if self.is_integral():
        return self.z_coeffs[0]
      self.add_all_ilp_cuts()




def main(argv=None):
  """chutney main function"""

  if argv is None:
    argv = sys.argv
  prog_path = os.path.dirname(argv[0])     
  prog_abspath = os.path.abspath(prog_path)
  
  input_parser = argparse.ArgumentParser(description=doc_str)
  input_parser.add_argument('-lpdict', default='part1.lpdict', help='lpdictionary file')
  input_parser.add_argument('-part'  , default=123, type=int, help='1, 2, 3, 123, 4')
  input_parser.add_argument('-debug')
  try :
    args = input_parser.parse_args(argv[1:])
  except SystemExit :
    return 1

  mylpd = lpdict()
  mylpd.init_from_file(args.lpdict)

  # part 1 : Just do one pivot.
  if args.part == 1 :
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
    

  # Part 2 : solve LP where the initial state is feasible.
  # Part 3 : solve initialization phase simplex.
  if args.part == 3 :
    if args.debug :
      print mylpd

    # Set up aux problem
    mylpd.auxiliarize()

    if args.debug :
      print mylpd

    mylpd.first_aux_pivot()

  if args.part in [2,3]:
    pivot_count = 0
    while True :
      if args.debug :
        print mylpd

      ev = mylpd.find_entering_variable()
      if args.debug :
        print ev
      if not isinstance(ev, Number) : # final
        print "%.6f"%(mylpd.z_coeffs[0])
        if args.part == 2 :
          print pivot_count
        break

      lv = mylpd.find_leaving_variable(ev)
      if args.debug :
        print lv
      if not isinstance(lv, Number) : # unbounded
        print lv
        break

      mylpd.pivot(ev,lv)
      pivot_count += 1

  # Part 123 (my own) : Put parts 1,2,3, together and clean up everything to create a full solver.
  if args.part == 123: # Full solver.
    final_z = mylpd.solve_lp()
    if not isinstance(final_z, Number) :
      print "Unable to solve."
      print final_z
    else :
      print "SOLVED!!!"
      print final_z
      print mylpd.variable_values()
    return

  if args.part == 4: # Full ILP solver.
    final_z = mylpd.solve_ilp()
    if not isinstance(final_z, Number) :
      print final_z
    else :
      print "%.1f"%(final_z)

if __name__ == "__main__":
  sys.exit(main())
