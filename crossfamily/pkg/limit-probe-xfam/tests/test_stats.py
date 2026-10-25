import math

import pytest

from limit_probe.stats import wilson


def test_known_interval():
    r = wilson(13, 30)
    assert abs(r.p - 13 / 30) < 1e-12
    # reference values from honest_evals.selection.wilson_interval(13, 30)
    assert abs(r.lo - 0.27377) < 1e-4 and abs(r.hi - 0.60803) < 1e-4


def test_edges_stay_in_unit_interval():
    assert wilson(0, 10).lo == 0.0 and wilson(0, 10).hi > 0
    assert wilson(10, 10).hi > 1 - 1e-9 and wilson(10, 10).lo < 1


def test_zero_n_is_undefined_not_zero():
    r = wilson(0, 0)
    assert math.isnan(r.p) and "undefined" in str(r)


@pytest.mark.parametrize("k,n", [(5, 4), (-1, 4), (1, -1)])
def test_bad_counts_raise(k, n):
    with pytest.raises(ValueError):
        wilson(k, n)
