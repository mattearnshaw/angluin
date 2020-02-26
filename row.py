from typing import Tuple, Optional

class Row:
    """Simple interface for a row of data with labelled indexing"""
    def __init__(self, label: str, col_labels: Tuple[str, ...],
                 entries: Tuple[bool, ...]):
        self._label = label
        self._entries = entries
        self._col_labels = col_labels
        self._indexed_entries = dict(zip(col_labels, entries))

    def __getitem__(self, col: str) -> Optional[bool]:
        try:
            return self._indexed_entries[col]
        except IndexError:
            return None

    def __eq__(self, other) -> bool:
        """Define rows to be equal if they have the same entries."""
        return self._entries == other._entries

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def add_entry(self, entry, col):
        self.entries += (entry,)
        self._col_labels += (col,)
        self._indexed_entries = dict(zip(self._col_labels, self.entries))

    @property
    def label(self) -> str:
        return self._label

    @property
    def entries(self) -> Tuple[bool, ...]:
        return self._entries

    @entries.setter
    def entries(self, o) -> None:
        self._entries = o
