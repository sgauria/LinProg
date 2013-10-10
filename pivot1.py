#!/usr/bin/env python

doc_str = """
"""

import sys, os
import argparse

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

  def init_from_file(self,lpdict_filename):
    lpdict = {}
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

      print m, n
      print basic_indices
      print nonbasic_indices
      print b_values
      print A
      print z_coeffs

      self.m                = m               
      self.n                = n               
      self.basic_indices    = basic_indices   
      self.nonbasic_indices = nonbasic_indices
      self.b_values         = b_values        
      self.A                = A               
      self.z_coeffs         = z_coeffs        

  def find_entering_variable(self):
    entering_index = self.m + self.n + 10 # some large value.
    for i, zc in enumerate(self.z_coeffs[1:]):
      index = self.nonbasic_indices[i]
      if zc >= 0 :
        if index < entering_index:
          entering_index = index
    # TODO : check for final dictionary.
    return entering_index



def main(argv=None):
  """chutney main function"""
  print ""

  if argv is None:
    argv = sys.argv
  prog_path = os.path.dirname(argv[0])     
  prog_abspath = os.path.abspath(prog_path)
  
  input_parser = argparse.ArgumentParser(description=doc_str)
  input_parser.add_argument('-lpdict', default='part1.lpdict', help='lpdictionary file')
  try :
    args = input_parser.parse_args(argv[1:])
  except SystemExit :
    return 1

  mylpd = lpdict()
  mylpd.init_from_file(args.lpdict)
  print mylpd.find_entering_variable()

if __name__ == "__main__":
  sys.exit(main())
