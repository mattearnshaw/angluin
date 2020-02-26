import numpy as np
import graphviz
import matplotlib.pyplot as plt

from itertools import count
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict

from row import Row
from utils import recursive_keys, groupby_unsorted

from keras.models import load_model

class Teacher(ABC):
    """An interface for things which learning processes can query"""
    @abstractmethod
    def accepts(self, input):
        pass

    # for now, counterexamples are handled interactively
    # or using the auto method with a seperate fuzzer

# for tests
class DummyTeacher(Teacher):
    def accepts(self, input):
        return False


class RNN(Teacher):
    def __init__(self, model_path, weights_path, char_map):
        self.model = load_model(model_path)
        self.model.load_weights(weights_path)
        self.char_map = char_map

    def accepts(self, input):
        # NN can't make prediction with no input, use padding value=0
        if input == '':
            input = ' '
        self.char_map[' '] = 0
        n = len(input)
        data = np.array([list(map(lambda x: self.char_map[x], input))]).reshape(1, n, 1)
        if self.model.predict(data) > 0.5:
            return True
        else:
            return False

class DFA(Teacher):
    def __init__(self, transition_table: Dict[str, Dict[str, str]], initial_state: str, accepting_states: List[str]):
        """
        :param transition_table: a dict mapping states to a dict mapping letters to states
        :param initial_state: the state in which the automaton begins
        :param accepting_state: a list of states for which the automaton can halt
        """
        self._transition = transition_table
        self._states = transition_table.keys()
        self._alphabet = set(k for k in recursive_keys(transition_table))
        self._validate_definition()
        self._initial = initial_state
        self._accepting = accepting_states

    def _validate_definition(self) -> None:
        """Check that provided transition table is consistent"""
        for k, v in self._transition.items():
            for a in self._alphabet:
                if a not in v.keys():
                    raise ValueError("Missing {} in transition for {}".format(a,v))
            for state in v.values():
                if state not in self._states:
                    raise ValueError("Invalid state {} in transition for {}".format(state,v))

    def _delta(self, a: str, state: str = None) -> str:
        """Perform a single step from given state, under a"""
        if state is None:
            state = self._initial
        return self._transition[state][a]

    def _delta_star(self, word: str, state: str) -> str:
        """Recursively step through a string, from some state"""
        if word == '': # base case
            return state 
        else:
            x, xs = word[0], word[1:]
            return self._delta_star(xs, self._transition[state][x])

    def accepts(self, word: str) -> bool:
        """
        :returns: Whether or not the DFA accepts a string
        :rtype: bool
        """
        return self._delta_star(word, self._initial) in self._accepting

def render_DFA(d: DFA):
    G = graphviz.Digraph()
    # just give unique numeric labels to states
    node_labels = dict(zip(d._states, count(0)))
    for state in d._states:
        if (state == d._initial) and (state in d._accepting):
            shape = 'doubleoctagon'
        elif state == d._initial:
            shape = 'octagon'
        elif state in d._accepting:
            shape = 'doublecircle'
        else:
            shape = 'circle'
        G.node(state, label=str(node_labels[state]), shape=shape)
    for k,v in d._transition.items():
        for k1,v in v.items():
            G.edge(k,v,label=k1)
    return G


def get_unique_states(table) -> List[Row]:
    states = []
    sorted_rows = sorted(table._rows, key=lambda x: x.label)
    matching_pairs = list(groupby_unsorted([row for row in sorted_rows],
                                           key=lambda x: x.entries))
    # choose a representative from each row whose entries are the same
    for row in matching_pairs:
        observations, rows = row
        states.append(list(rows)[0])
    return states


def get_accepting_states(table) -> List[str]:
    """Accepting states are those with a True in the '' column."""
    accepting_rows = filter(lambda r: table[r.label][''], table._rows)
    return list(map(lambda x: x.label, accepting_rows))


def smallest_matching(table, state_label):
    """Pick a smallest representative row (label) if multiple rows
    have the same entries."""
    try:
        sorted_rows = sorted(table._rows, key=lambda x: x.label)
        return list(filter(lambda x: x.entries == table[state_label].entries,
                           sorted_rows))[0].label
    except IndexError:
        return state_label

    
def make_transition(table):
    """Convert an observation table to a transition function represented by
    {"State1": {"a": "State1", "b": "State2", ...}, "State2": { ... }, ...}"""
    delta = {}
    unique_states = get_unique_states(table)
    for state in unique_states:
        label = state.label
        delta[label] = {}
        for a in table._alphabet:
            delta[label][a] = smallest_matching(table, label+a)
    return delta


def make_DFA(table):
    initial = ''  # initital state = no input so far
    return DFA(make_transition(table), initial, get_accepting_states(table))
