
# inspired by pandas.core.nanOps
from __future__ import annotations
import numpy as np
import numpy.typing as npt

def bottleneck_switch(name):
    return lambda _: lambda x: x

def _datetimelike_compat(a):
    pass


def _maybe_null_out():
    pass

def _na_for_min_count():
    pass

def _get_values():
    pass

AxisInt = int

def _nanminmax(meth, fill_value_typ):
    @bottleneck_switch(name=f"nan{meth}")
    @_datetimelike_compat
    def reduction(
        values: np.ndarray,
        *,
        axis: int | None = None,
        skipna: bool = True,
        mask: npt.NDArray[np.bool_] | None = None,
    ):
        if values.size == 0:
            return _na_for_min_count(values, axis)

        values, mask = _get_values(
            values, skipna, fill_value_typ=fill_value_typ, mask=mask
        )
        result = getattr(values, meth)(axis)
        result = _maybe_null_out(result, axis, mask, values.shape)
        return result

    return reduction


nanmin = _nanminmax("min", fill_value_typ="+inf")
nanmax = _nanminmax("max", fill_value_typ="-inf")

