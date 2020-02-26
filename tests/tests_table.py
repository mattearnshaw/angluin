from teachers import DummyTeacher
from row import Row
from angluin import ObservationTable

import unittest

class TableTests(unittest.TestCase):

    def test_consistent(self):
        inconsistent_table = ObservationTable(DummyTeacher(), ('0','1'))
        c = inconsistent_table._cols
        # fill in blank and derivatives manually
        inconsistent_table[''].entries = (False,)
        inconsistent_table['0'].entries = (False,)
        inconsistent_table['1'].entries = (False,)
        inconsistent_table._rows += [Row('0', c, (False,)),
                                     Row('11', c, (False,))]
        inconsistent_table._derivative_rows += [Row('1', c, (False,)),
                                                Row('00', c, (False,)),
                                                Row('01', c, (True,)),
                                                Row('110', c, (False,)),
                                                Row('111', c, (False,))]
        consistent, counterexample = inconsistent_table.consistent()
        self.assertFalse(consistent)

    def test_closed(self):
        not_closed_table = ObservationTable(DummyTeacher(), ('0','1'))
        not_closed_table._cols += ('1',)
        c = not_closed_table._cols
        not_closed_table[''].entries = (True, False)
        not_closed_table['0'].entries = (False, True)
        not_closed_table['1'].entries = (False, False)
        not_closed_table._rows += [Row('1101101', c, (False, False)),
                                   Row('110', c, (False, False)),
                                   Row('1101', c, (False, False)),
                                   Row('11011', c, (False, False)),
                                   Row('110110', c, (False, False))]
        not_closed_table._derivative_rows += [Row('00', c, (False, False)),
                                              Row('01', c, (True, False)),
                                              Row('11011010', c, (False, False)),
                                              Row('11011011', c, (False, False)),
                                              Row('10', c, (False, False)),
                                              Row('111', c, (False, False)),
                                              Row('1100', c, (False, False)),
                                              Row('11010', c, (False, False)),
                                              Row('110111', c, (False, False)),
                                              Row('1101100', c, (False, False))]
        closed, counterexample = not_closed_table.closed()
        self.assertFalse(closed)

if __name__ == '__main__':
    unittest.main()
