from .collect import acollect, collect_
from .filter import afilter, filter_
from .map import amap, map_
from .reduce import areduce, reduce_
from .starmap import astarmap, starmap_
from .tap import atap, tap, tap_each

__all__ = [
    # map
    "amap",
    "map_",
    # filter
    "afilter",
    "filter_",
    # collect
    "collect_",
    "acollect",
    # reduce
    "areduce",
    "reduce_",
    # tap
    "atap",
    "tap",
    "tap_each",
    # starmap
    "astarmap",
    "starmap_",
]
