from .collect import acollect, collect_
from .filter import afilter, filter_
from .map import amap, map_
from .reduce import areduce, reduce_
from .tap import atap, tap

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
]
