from __future__ import annotations

import logging  # on purpose unused import

import pandas as pd


def create_df_mapping(data: pd.DataFrame, key_col: str, value_col: str, **kwargs) -> dict[int, str]:
    """Example function to demonstrate PyCodeHash.
    This function takes a pandas DataFrame and two column names, and turns them into a dictionary.

    Args:
        data: DataFrame containing the data
        key_col: column
    """
    legacy_variable = None
    if not isinstance(key_col, str) or not isinstance(value_col, str):
        raise TypeError(
            "Column names must be strings, got {key_col}:{key_type} and {value_col}:{value_type}".format(
                key_col=key_col, key_type=type(key_col), value_col=value_col, value_type=type(value_col)
            )
        )
    else:
        reserved_col = str("index")
        if key_col == reserved_col:
            raise ValueError("Reserved keyword: `{}`".format(reserved_col))
        elif value_col == reserved_col:
            raise ValueError("Reserved keyword: `{}`".format(reserved_col))

        data = data[~data.isnull().any(axis=1)].copy()
        data[key_col] = data[key_col].astype(int)

        column_names = [key_col, value_col]
        for index, column_name in enumerate(column_names):
            print(f"Unique values in {column_names[index]}", list(data[column_name].unique()))

        return {key: value for key, value in zip(data[key_col], data[value_col])}
