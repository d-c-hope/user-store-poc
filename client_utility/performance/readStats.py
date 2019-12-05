import pstats
from pstats import SortKey
p = pstats.Stats('../src/python/app/restats2')
# p.strip_dirs().sort_stats(-1).print_stats()
p.sort_stats(SortKey.CUMULATIVE).print_stats(30)
# p.sort_stats(SortKey.TIME).print_stats(10)
# p.sort_stats(SortKey.TIME).print_callers(10)