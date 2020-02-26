import random
import itertools
import numpy as np

from row import Row
from utils import groupby_unsorted
from teachers import DFA, Teacher, render_DFA, make_DFA

from tabulate import tabulate
from IPython.display import display
from typing import List, Tuple, Optional


class ObservationTable:
    def __init__(self, teacher: Teacher, alphabet: Tuple[str, ...]):
        """
        :param teacher: Implements `accepts` and `counterexample` methods
        :param alphabet: The alphabet of the target to be learned
        """
        self._alphabet = alphabet
        self._teacher = teacher
        # we start with just the row & column for the empty word
        self._cols = ('',)
        self._rows = [Row('', self._cols, (teacher.accepts(''),))]
        self._derivative_rows = []
        self._make_derivative_rows()

    @property
    def all_rows(self) -> List[Row]:
        return self._rows + self._derivative_rows

    def __repr__(self):
        row_data = [[row.label]+list(row.entries) for row in self.all_rows]
        return tabulate(row_data, headers=['X'] + list(self._cols))

    def __getitem__(self, key) -> Optional[Row]:
        try:
            return list(filter(lambda x: x.label == key, self.all_rows))[0]
        except IndexError:
            return None

    def _make_derivative_rows(self) -> None:
        # Add derivatives to the table ("bottom part" of table, ie. successors)
        for state in self._rows:
            for a in self._alphabet:
                if not self[state.label+a]:
                    observations = tuple(self._teacher.accepts(state.label+a+c)
                                         for c in self._cols)
                    new_row = Row(state.label+a, self._cols, observations)
                    self._derivative_rows.append(new_row)

    def consistent(self) -> Tuple[bool, Optional[str]]:
        """A table is consistent if every pair of identical pair of rows remain
        identical under all derivatives.

        :return: (is consistent?, distinguishing letter if not consistent)
        """
        # group rows according to their entries
        matching_rows = groupby_unsorted([row for row in self._rows],
                                         key=lambda x: x.entries)
        for key, group in matching_rows:
            group = list(group)
            # get all pairs of matching rows and exclude the diagonal (a,a)
            pairs = itertools.product(group, group)
            pairs = list(filter(lambda x: x[0].label != x[1].label, pairs))
            for a in self._alphabet:
                for pair in pairs:
                    # check if derivatives match
                    for e in self._cols:
                        if (self[pair[0].label+a][e] != self[pair[1].label+a][e]):
                            return False, a+e
        return True, None

    def make_consistent(self) -> None:
        """To make a table consistent, add the distinguishing suffix to cols
        and fill the column via membership queries."""
        is_consistent, counterexample = self.consistent()
        while not is_consistent:
            if counterexample not in self._cols:
                self._cols += (counterexample,)

            # do membership queries for new column
            for row in self.all_rows:
                row.add_entry(self._teacher.accepts(row.label + counterexample), counterexample)
            self._make_derivative_rows()
            is_consistent, counterexample = self.consistent()

    def closed(self) -> Tuple[bool, Optional[Row]]:
        """Table is closed if for every derivative row, there is a row
        that has the same entries (i.e. derivatives are not new states).

        :return: (is closed?, non-matching derivative if not closed)
        """
        for row in self._derivative_rows:
            if row.entries not in [state.entries for state in self._rows]:
                return False, row
        return True, None

    def make_closed(self) -> None:
        """To make a table closed, add the inconsistent derivative to top
        of table ("rows"), and make new derivatives."""
        is_closed, counterexample = self.closed()
        if not is_closed:
            self._rows.append(counterexample)
            self._make_derivative_rows()

    def process_counterexample(self, label: str, conjecture: DFA) -> bool:
        """Add counterexample and its prefixes to rows, and add derivative
        rows"""
        if conjecture.accepts(label) == self._teacher.accepts(label):
            print("False counter example, already both reject or both accept.")
            return False
        new_row = Row(label, self._cols, tuple(self._teacher.accepts(label+c)
                                               for c in self._cols))
        self._rows.append(new_row)
        for i in range(len(label)):
            prefix = label[:i]
            if prefix not in list(map(lambda x: x.label, self._rows)):
                self._rows.append(Row(prefix, self._cols,
                                      tuple(self._teacher.accepts(prefix+col)
                                            for col in self._cols)))
        self._make_derivative_rows()
        return True


def fuzzer(dfa, teacher, alphabet=['a', 'b'], max_tries=10000, max_length=12) -> Optional[str]:
    # running time of L* is polynomial in length of
    # counterexample, so try to find shortest first
    for i in range(max_tries):
        for l in range(max_length):
            example = ''.join([random.choice(alphabet) for j in range(l)])
            if dfa.accepts(example) != teacher.accepts(example):
                return example
    return None


def Lstar(teacher: Teacher, alphabet: Tuple[str], counter_generator=None, render: bool = True) -> Optional[DFA]:
    """ LStar Algorithm for interactive use in a notebook 
    :param teacher: an implementation of Teacher class (has an `accepts` methods)
    :param alphabet: the alphabet over which the target operators
    :render render: whether or not to draw conjectured DFAs as graphics
    :return: optionally the learned DFA
    """
    conjecture = False
    ot = ObservationTable(teacher, alphabet)
    while not conjecture:
        is_consistent, witness0 = ot.consistent()
        is_closed, witness1 = ot.closed()
        while not (is_closed and is_consistent):
            if not is_consistent:
                print("Making consistent...")
                ot.make_consistent()

            if not is_closed:
                print("Closing...")
                ot.make_closed()

            is_consistent, witness0 = ot.consistent()
            is_closed, witness1 = ot.closed()

        conjecture = make_DFA(ot)
        if counter_generator is None:
            # interactive mode
            if render:
                display(render_DFA(conjecture))
            response = input("Is this conjecture correct? ")
            if response == 'y':
                return conjecture
            elif response == 'n':
                counter = input("Provide string in symmetric difference: ")
                if counter != '':
                    print("Processing counterexample: ", counter)
                    c = ot.process_counterexample(counter, conjecture)
                    if not c:
                        return None
                    conjecture = False            
        else:
            counterexample = counter_generator(conjecture, teacher, alphabet, max_length=10)
            if counterexample:
                print("Processing counterexample: ", counterexample)
                c = ot.process_counterexample(counterexample, conjecture)
                if not c:
                    return None
                conjecture = False
            else:
                if render:
                    display(render_DFA(conjecture))
    return conjecture
