import sys; sys.path.insert(0,'/home/claude'); from measure import *
for s in sys.argv[1:]: print(f"{s!r}: rib={ribbon_ok(s)} {' / '.join(ribbon_lines(s))} w12={w(s,12):.0f} row={w(s,12.5):.0f}")
