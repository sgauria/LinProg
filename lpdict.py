#!/usr/bin/env python

doc_str = """
 This file implements a lpdict class which has a dictionary structure for representing linear programs.
 And associated functions for actually pivoting from dictionary to dictionary and finding 
 LP and ILP solutions.
"""

import math
from   numbers import Number
import fractions

# Using fractions is so clean, but it is also 5x - 10x slower. Hence we have an option to control its usage.
# If we are using fractions, we don't need epsilon comparisons, since everything is precise.
# So we we modify those functions as well below.
use_fractions = False

# 2 ways of doing ILP. Using dual is 1x - 2x faster. Significant speedup only for large problems.
use_dual_for_ilp = True

# Many different ways of picking entering variables. 
# The rules other than blands_rule are not fully debugged.
e_selector = "blands_rule"
#e_selector = "largest_coeff"
#e_selector = "largest_step"

one = fractions.Fraction(1.0) if use_fractions else 1.0

# epsilon comparisons
# Ignore differences smaller than epsilon.
# Centralize the code here.
epsilon = fractions.Fraction(1e-10) if use_fractions else 1e-10
def eps_cmp_lt(a,b):
  if use_fractions :
    rv = ( (a) <  (b) )
  else :
    rv = ( ((a) + epsilon) <  (b) )
  return rv
def eps_cmp_eq(a,b):
  if use_fractions :
    rv = ( (a) <= (b) )
  else :
    rv = ( ((a) - epsilon) <= (b) < ((a) + epsilon) )
  return rv
def eps_cmp_le(a,b):
  rv = eps_cmp_lt(a,b) or eps_cmp_eq(a,b)
  return rv
def eps_cmp_gt(a,b):
  return eps_cmp_lt(b,a) # a > b => b < a
def eps_cmp_ge(a,b):
  return eps_cmp_le(b,a) # a >= b => b <= a
def eps_cmp_ne(a,b):
  return not eps_cmp_eq(a,b)

def is_integer(n):
  if use_fractions :
    rv = ( (n) == round(n) )
  else :
    rv = eps_cmp_eq(n, round(n))
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

def line_to_num_list(fh, sep=None):
  return map(convert_to_num, fh.readline().split(sep))

def table_to_str(table):
  str_table = [map(str,x) for x in table]
  table_ht = len(table)
  table_wd = len(table[0])
  for i in range(1,table_ht):
    if len(table[i]) != table_wd:
      print table
      print "row", i, "has a different length from row0"
      assert(0)

  rowformat = ""
  for i in range(table_wd):
    maxlen = max([len(x[i]) for x in str_table])
    rowformat += "{:>%d} "%(maxlen)
  rowformat += "\n"

  r = ""
  for row in str_table:
    r += rowformat.format(*row)
  return r

def neg_transpose (A) :
  ht = len(A)
  wd = len(A[0])
  new_A = [[ -A[row][col] for row in range(0,ht) ] for col in range(0,wd) ]
  return new_A

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

      self.init_fn (m,n,basic_indices,nonbasic_indices,b_values,A, z_coeffs)

  def init_fn (self,m,n,basic_indices,nonbasic_indices,b_values,A, z_coeffs):
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
    metric       = -1
    for i, zc in enumerate(self.z_coeffs[1:]):
      var = self.nonbasic_indices[i]
      if eps_cmp_gt(zc,0):
        if e_selector == "largest_coeff":
          if zc > metric:
            entering_var = var
            metric       = zc
        elif e_selector == "largest_step":
          lv,bound = self.find_leaving_variable(var, True)
          if not isinstance(lv, Number) :
            return lv
          zchange = zc * bound
          if zchange > metric :
            entering_var = var
            metric       = zchange
        else: # elif e_selector == "blands_rule":
          if var < entering_var:
            entering_var = var
    if entering_var == self.large_value:
      return "FINAL"
    return entering_var

  def find_leaving_variable (self, entering_var, return_bound=False):
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
      rv = "UNBOUNDED"
    else :
      rv = leaving_var
    if return_bound :
      return (rv, best_bound)
    else :
      return rv

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
  
  def dualize (self):
    new_A = neg_transpose(self.A)
    new_b = [-x for x in self.z_coeffs[1:]]
    new_z = [-self.z_coeffs[0]] + [-x for x in self.b_values]

    self.m, self.n = self.n, self.m
    self.nonbasic_indices, self.basic_indices = self.basic_indices, self.nonbasic_indices
    self.b_values         = new_b
    self.A                = new_A
    self.z_coeffs         = new_z
    self.shdw_z_coeffs    = [0]*(self.n+1)
    # NOTE : dualize is discarding the shdw_z_coeffs, so can't be done in the middle of any auxiliary work.

  def undualize (self):
    self.dualize() # dual of dual is primal.
  
  def first_aux_pivot (self): # First pivot for aux dictionary
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
        #print self
        if srv == "FINAL":
          return self.z_coeffs[0]
        else :
          return srv

  def solve_lp (self, is_primal=True):
    """ Full LP solver, including handling of initialization if needed"""
    if not self.is_feasible():
      self.auxiliarize()
      self.first_aux_pivot()
      aux_z = self.run_simplex()
      if eps_cmp_ne (aux_z, 0):
        return "INFEASIBLE"
      self.unauxiliarize()

    final_z = self.run_simplex()
    if not is_primal and not isinstance(final_z, Number) : # final or unbounded
      if final_z == "INFEASIBLE" :
        final_z = "UNBOUNDED"
      if final_z == "UNBOUNDED" :
        final_z = "INFEASIBLE"
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
    for b in self.b_values:
      if not is_integer(b):
        return False
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
    # Not sure why adding z-cuts generates wrong results, but it creates issues both with(ilpTest10) and without Fractions(assignment part5)
    # Update : not all objective functions are integral, so adding z-cuts is not necessarily legal.
    #if not is_integer(self.z_coeffs[0]):
    #  self.add_ilp_cut(0, True)

  def solve_ilp (self):
    #print self
    if use_dual_for_ilp :
      lps = self.solve_lp()
      #print self
      while True:
        if not isinstance(lps, Number) :
          return lps.lower()
        if self.is_integral():
          return self.z_coeffs[0]
        self.add_all_ilp_cuts()
        self.dualize()
        lps = self.solve_lp(is_primal=False)
        self.undualize()
    else :
      while True :
        lps = self.solve_lp()
        if not isinstance(lps, Number) :
          return lps.lower()
        if self.is_integral():
          return self.z_coeffs[0]
        self.add_all_ilp_cuts()


