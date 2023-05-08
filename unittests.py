import unittest
import pandas as pd
from actions import Interpolate1DAction, Interpolate2DAction
from tables import Table


class TestInterpolationClasses(unittest.TestCase):
    
    def setUp(self):
        self.norms_data = pd.DataFrame({
            'regressor1': [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5],
            'regressor2': [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            'type1': [0, 0.5, 1, 1.5, 1, 1.5, 2, 2.5, 2, 2.5],
        })
        self.norms = Table(self.norms_data)

        self.test_data = pd.DataFrame({
            'regressor1': [1.5, 2.5, 3.5],
            'regressor2': [3, 5, 7],
            'data_type': ['type1', 'type1', 'type1']
        })
        self.test_table = Table(self.test_data)

    def test_interpolate_1d_action(self):
        action = Interpolate1DAction(
            regressor_col='regressor1',
            norms=self.norms,
            data_interpolated_col='interpolated',
            data_type_col='data_type'
        )

        interpolated_table = action.action(self.test_table)
        print(interpolated_table)
        interpolated_values = interpolated_table.data['interpolated'].values

        # Test if the interpolated values are correct
        expected_values = [15, 25, 35]
        self.assertTrue((interpolated_values == expected_values).all())

    def test_interpolate_2d_action(self):
        action = Interpolate2DAction(
            regressor_cols=['regressor1', 'regressor2'],
            norms=self.norms,
            data_interpolated_col='interpolated',
            data_type_col='data_type'
        )

        interpolated_table = action.action(self.test_table)
        print(interpolated_table)
        interpolated_values = interpolated_table.data['interpolated'].values

        # Test if the interpolated values are correct
        expected_values = [15, 25, 35]
        self.assertTrue((interpolated_values == expected_values).all())


if __name__ == '__main__':
    unittest.main()
