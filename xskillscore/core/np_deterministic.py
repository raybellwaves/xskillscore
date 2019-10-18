import numpy as np
from scipy import special


__all__ = ["_pearson_r", "_pearson_r_p_value", "_rmse", "_mse", "_mae"]


def _check_weights(weights):
    """
    Quick check if weights are all NaN. If so,
    return None to guide weighting scheme.
    """
    if np.all(np.isnan(weights)):
        return None
    else:
        return weights


def _get_numpy_funcs(skipna):
    """
    Returns nansum and nanmean if skipna is True;
    Returns sum and mean if skipna is False.
    """
    if skipna:
        return np.nansum, np.nanmean
    else:
        return np.sum, np.mean


def _check_weights(weights):
    """
    Quick check if weights are all NaN. If so,
    return None to guide weighting scheme.
    """
    if np.all(np.isnan(weights)):
        return None
    else:
        return weights


def _pearson_r(a, b, weights, axis):
    """
    ndarray implementation of scipy.stats.pearsonr.

    Parameters
    ----------
    a : ndarray
        Input array.
    b : ndarray
        Input array.
    axis : int
        The axis to apply the correlation along.
    weights : ndarray
        Input array.
    skipna : bool
        Whether or not to skip NaNs.

    Returns
    -------
    res : ndarray
        Pearson's correlation coefficient.

    See Also
    --------
    scipy.stats.pearsonr

    """
    sumfunc, meanfunc = _get_numpy_funcs(skipna)
    weights = _check_weights(weights)
    a = np.rollaxis(a, axis)
    b = np.rollaxis(b, axis)

    # Only do weighted sums if there are weights. Cannot have a
    # single generic function with weights of all ones, because
    # the denominator gets inflated when there are masked regions.
    if weights is not None:
        weights = np.rollaxis(weights, axis)
        ma = sumfunc(a * weights, axis=0) / sumfunc(weights, axis=0)
        mb = sumfunc(b * weights, axis=0) / sumfunc(weights, axis=0)
    else:
        ma = meanfunc(a, axis=0)
        mb = meanfunc(b, axis=0)

    am, bm = a - ma, b - mb

    if weights is not None:
        r_num = sumfunc(weights * am * bm, axis=0)
        r_den = np.sqrt(
            np.sum(weights * am * am, axis=0)
            * np.sum(weights * bm * bm, axis=0)
        )
    else:
        r_num = sumfunc(am * bm, axis=0)
        r_den = np.sqrt(sumfunc(am * am, axis=0) * sumfunc(bm * bm, axis=0))

    r = r_num / r_den
    res = np.clip(r, -1.0, 1.0)
    return res


def _pearson_r_p_value(a, b, weights, axis, skipna):
    """
    ndarray implementation of scipy.stats.pearsonr.

    Parameters
    ----------
    a : ndarray
        Input array.
    b : ndarray
        Input array.
    axis : int
        The axis to apply the correlation along.
    weights : ndarray
        Input array.
    skipna : bool
        Whether or not to skip NaNs.

    Returns
    -------
    res : ndarray
        2-tailed p-value.

    See Also
    --------
    scipy.stats.pearsonr

    """
    r = _pearson_r(a, b, weights, axis, skipna)
    a = np.rollaxis(a, axis)
    df = a.shape[0] - 2
    t_squared = r ** 2 * (df / ((1.0 - r) * (1.0 + r)))
    _x = df / (df + t_squared)
    _x = np.asarray(_x)
    _x = np.where(_x < 1.0, _x, 1.0)
    _a = 0.5 * df
    _b = 0.5
    res = special.betainc(_a, _b, _x)
    return res


def _rmse(a, b, weights, axis, skipna):
    """
    Root Mean Squared Error.

    Parameters
    ----------
    a : ndarray
        Input array.
    b : ndarray
        Input array.
    axis : int
        The axis to apply the rmse along.
    weights : ndarray
        Input array.
    skipna : bool
        Whether or not to skip NaNs.

    Returns
    -------
    res : ndarray
        Root Mean Squared Error.

    See Also
    --------
    sklearn.metrics.mean_squared_error

    """
    sumfunc, meanfunc = _get_numpy_funcs(skipna)
    weights = _check_weights(weights)

    squared_error = (a - b) ** 2
    if weights is not None:
        mean_squared_error = np.sum(
            squared_error * weights, axis=axis
        ) / np.sum(weights, axis=axis)
    else:
        mean_squared_error = meanfunc(((a - b) ** 2), axis=axis)
    res = np.sqrt(mean_squared_error)
    return res


def _mse(a, b, weights, axis, skipna):
    """
    Mean Squared Error.

    Parameters
    ----------
    a : ndarray
        Input array.
    b : ndarray
        Input array.
    axis : int
        The axis to apply the mse along.
    weights : ndarray
        Input array.
    skipna : bool
        Whether or not to skip NaNs.

    Returns
    -------
    res : ndarray
        Mean Squared Error.

    See Also
    --------
    sklearn.metrics.mean_squared_error

    """
    sumfunc, meanfunc = _get_numpy_funcs(skipna)
    weights = _check_weights(weights)

    squared_error = (a - b) ** 2
    if weights is not None:
        return np.sum(squared_error * weights, axis=axis) / np.sum(
            weights, axis=axis
        )
    else:
        return meanfunc(squared_error, axis=axis)


def _mae(a, b, weights, axis, skipna):
    """
    Mean Absolute Error.

    Parameters
    ----------
    a : ndarray
        Input array.
    b : ndarray
        Input array.
    axis : int
        The axis to apply the mae along.
    weights : ndarray
        Input array.
    skipna : bool
        Whether or not to skip NaNs.

    Returns
    -------
    res : ndarray
        Mean Absolute Error.

    See Also
    --------
    sklearn.metrics.mean_absolute_error

    """
    sumfunc, meanfunc = _get_numpy_funcs(skipna)
    weights = _check_weights(weights)

    absolute_error = np.absolute(a - b)
    if weights is not None:
        return np.sum(absolute_error * weights, axis=axis) / np.sum(
            weights, axis=axis
        )
    else:
        return meanfunc(absolute_error, axis=axis)
