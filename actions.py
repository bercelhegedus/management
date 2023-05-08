import pandas as pd
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from scipy.interpolate import LinearNDInterpolator, interp1d

from tables import Table


class Action(ABC):

    @abstractmethod
    def action(self, table: 'Table') -> 'Table':
        return table


class Interpolate1DAction(Action):

    def __init__(self, regressor_col: str, norms: Table, data_interpolated_col: str, data_type_col: str = None, norm_target_col: str = None):
        if norm_target_col is None and data_type_col is None:
            raise Exception('Either regressor_col or data_type_col must be provided')
        self.regressor_col = regressor_col
        self.norms = norms.data  
        self.data_interpolated_col = data_interpolated_col
        self.data_type_col = data_type_col
        self.norm_target_col = norm_target_col

    def interpolate(self, table: 'Table') -> 'Table':
        data = table.data.copy()
        norms = self.norms.copy()
        data[self.regressor_col] = data[self.regressor_col].astype(float)
        norms = norms[norms[self.regressor_col] != '']
        norms[self.regressor_col] = norms[self.regressor_col].astype(float)

        if self.data_type_col is not None:
            for type_value in data[self.data_type_col].unique():
                mask = (data[self.data_type_col] == type_value)
                norms_filtered = norms[norms[type_value] != '']
                f = interp1d(norms[self.regressor_col], norms_filtered[type_value], fill_value='extrapolate')
                data.loc[mask, self.data_interpolated_col] = f(data.loc[mask, self.regressor_col].to_numpy()).tolist()
        else:
            f = interp1d(norms[self.regressor_col], norms[self.norm_target_col], fill_value='extrapolate')
            data[self.data_interpolated_col] = f(data[self.regressor_col].to_numpy()).tolist()

        return Table(data)

    @staticmethod
    def interpolate_1d(regressor: pd.Series, target: pd.Series, x: float) -> float:
        mask = target != ''
        f = interp1d(regressor[mask], target[mask], fill_value='extrapolate')
        return f(x).item()

    def action(self, table: 'Table') -> 'Table':
        interpolated_table = self.interpolate(table)
        table.update(interpolated_table)
        return table


class Interpolate2DAction(Action):

    def __init__(self, regressor_cols: list, norms: Table, data_interpolated_col: str, data_type_col: str = None, norm_target_col: str = None):
        if norm_target_col is None and data_type_col is None:
            raise Exception('Either regressor_col or data_type_col must be provided')
        self.regressor_cols = regressor_cols
        self.norms = norms.data  
        self.data_interpolated_col = data_interpolated_col
        self.data_type_col = data_type_col
        self.norm_target_col = norm_target_col

    def interpolate(self, table: 'Table') -> 'Table':
        data = table.data.copy()
        norms = self.norms.copy()
        
        for col in self.regressor_cols:
            norms = norms[norms[col] != '']
            norms[col] = norms[col].astype(float)
            data[col] = data[col].astype(float)

        if self.data_type_col is not None:
            for type_value in data[self.data_type_col].unique():
                mask = (data[self.data_type_col] == type_value)         
                norms_filtered = norms[norms[type_value] != '']
                points = list(zip(norms_filtered[self.regressor_cols[0]], norms_filtered[self.regressor_cols[1]]))
                f = LinearNDInterpolator(points, norms_filtered[type_value])
                data.loc[mask, self.data_interpolated_col] = f(data.loc[mask, self.regressor_cols[0]].to_numpy(),
                                                               data.loc[mask, self.regressor_cols[1]].to_numpy()).tolist()
        else:
            norms_filtered = norms[norms[self.norm_target_col] != '']
            points = list(zip(norms_filtered[self.regressor_cols[0]], norms_filtered[self.regressor_cols[1]]))
            f = LinearNDInterpolator(points, norms_filtered[self.norm_target_col])
            data[self.data_interpolated_col] = f(data[self.regressor_cols[0]].to_numpy(),
                                                 data[self.regressor_cols[1]].to_numpy()).tolist()

        return Table(data)

    @staticmethod
    def interpolate_2d(regressor1: pd.Series, regressor2: pd.Series, target: pd.Series, x1: float, x2: float) -> float:
        mask = target != ''
        points = list(zip(regressor1[mask], regressor2[mask]))
        f = LinearNDInterpolator(points, target[mask])
        return f(x1, x2).item()

    def action(self, table: 'Table') -> 'Table':
        interpolated_table = self.interpolate(table)
        table.update(interpolated_table)
        return table
