CellIndex = tuple[int, int]
"""
CellIndex = Tuple[index_row: int, index_column: int]\n
Example: (0, 1)
"""

CombType = tuple[CellIndex, ...]
"""
CombType = Tuple[CellIndex, ...]\n
*CellIndex = Tuple[index_row: int, index_column: int]\n
Example: ((0, 1), ...)
"""

CombsType = tuple[CombType, ...]
"""
CombsType = tuple[tuple[tuple[i_row: int, i_column: int], ...], ...] or\n
tuple[CombType, ...]\n
Where:\n
*CombType = tuple[CellIndex, ...]\n
**CellIndex = tuple[index_row: int, index_column: int]\n
Example: ( ((0, 0), (0, 1), (0, 2)), ((1, 0), (1, 1), (1, 2)), ... )
"""
