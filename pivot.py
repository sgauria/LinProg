#!/usr/bin/env python

doc_str = """
"""

import sys, os
import argparse
from   numbers import Number
from   lpdict import lpdict

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
