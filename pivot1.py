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

def parse_lpdict(lpdict_filename):
  print lpdict_filename
  lpdict = {}
  with open(lpdict_filename, 'r') as fh:
    m,n              = map(convert_to_num, fh.readline().split())
    basic_indices    = map(convert_to_num, fh.readline().split())
    nonbasic_indices = map(convert_to_num, fh.readline().split())
    b_values         = map(convert_to_num, fh.readline().split())
    A = []
    for i in range(int(m)):
      A.append(map(convert_to_num, fh.readline().split()))
    z_coeffs         = map(convert_to_num, fh.readline().split())

    print m, n
    print basic_indices
    print nonbasic_indices
    print b_values
    print A
    print z_coeffs

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

  lpdict = parse_lpdict(args.lpdict)

if __name__ == "__main__":
  sys.exit(main())
