def func(data, key_col, value_col, **kwargs):
    if not isinstance(key_col, str) or not isinstance(value_col, str):
        raise TypeError(
            f"Column names must be strings, got {key_col}:{type(key_col)} and {value_col}:{type(value_col)}"
        )

    reserved_col = "index"
    if reserved_col in (key_col, value_col):
        raise ValueError(f"Reserved keyword: `{reserved_col}`")

    data = data[~data.isnull().any(axis=1)].copy()
    data[key_col] = data[key_col].astype(int)

    column_names = [key_col, value_col]
    for column_name in column_names:
        print(f"Unique values in {column_name}", list(data[column_name].unique()))

    return dict(zip(data[key_col], data[value_col]))
