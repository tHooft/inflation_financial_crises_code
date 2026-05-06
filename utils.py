"""
utils.py — Shared utility functions for all replication notebooks.

Provides data-reshaping helpers, regression display formatters, and the
two shared regression runners used in the oil-shock IV notebooks.

Note: `pivot` is intentionally excluded because it closes over the
notebook-local `raw_df`. Define it in each notebook after loading data:
    def pivot(v): return raw_df.pivot(index='year', columns='country', values=v)
"""

import pandas as pd
import numpy as np
from scipy.stats.mstats import winsorize
from linearmodels.panel import PanelOLS
import statsmodels.api as sm


# ── Data reshaping ─────────────────────────────────────────────────────────────

def melt(df):
    """Long format suitable for a (country, year) MultiIndex panel."""
    return df.melt(ignore_index=False).reset_index().set_index(['country', 'year'])


def add_const(df):
    """Prepend a constant column (required by linearmodels)."""
    return sm.add_constant(df)


def winsor(df):
    """Winsorise at the 5th and 95th percentiles to limit outlier influence."""
    return df.apply(lambda x: winsorize(x, limits=(.05, .05)))


# ── Regression display ─────────────────────────────────────────────────────────

def significance_stars(pval):
    """Return AER-style significance stars for a given p-value."""
    if pval < 0.01:
        return '***'
    elif pval < 0.05:
        return '**'
    elif pval < 0.1:
        return '*'
    return ''


def display(fit):
    """Coefficients with significance stars only."""
    df = pd.DataFrame({'coefficient': fit.params, 'pvalue': fit.pvalues})
    df['significance'] = df['pvalue'].apply(significance_stars)
    df['results'] = df.apply(
        lambda x: f"{x['coefficient']:.3f}{x['significance']}", axis=1)
    return df[['results']]


def display_w_std_errors(fit):
    """Coefficients with significance stars and clustered standard errors."""
    df = pd.DataFrame({
        'coefficient': fit.params,
        'pvalue':      fit.pvalues,
        'std_error':   round(fit.std_errors, 3),
    })
    df['significance'] = df['pvalue'].apply(significance_stars)
    df['results'] = df.apply(
        lambda x: f"{x['coefficient']:.3f}{x['significance']}", axis=1)
    df['results_w_errors'] = (
        df['results'] + ' (' + df['std_error'].astype(str) + ')')
    return df[['results_w_errors']]


# ── Shared regression runners ──────────────────────────────────────────────────

def run_first_stage(panel_df, covariates):
    """
    Run the first stage of the oil supply shock IV (Equation 3).

    Regresses annual inflation change on the oil supply shock instrument
    and control variables, with country fixed effects and clustered SEs.

    Parameters
    ----------
    panel_df : pd.DataFrame
        Panel indexed by (country, year) containing at least 'infl',
        'oil_shock', and all columns in covariates.
    covariates : list of str
        Names of the control variables (stir and gdp lags).

    Returns
    -------
    fit : PanelEffectsResults
        Fitted first-stage model.
    fitted_df : pd.DataFrame
        First-stage fitted values in wide (year × country) format.
    """
    first_stage_vars = ['oil_shock'] + covariates
    df = panel_df[['infl'] + first_stage_vars].dropna()

    fit = PanelOLS(
        dependent      = df['infl'],
        exog           = add_const(df[first_stage_vars]),
        entity_effects = True,
        time_effects   = False,
    ).fit(cov_type='clustered', cluster_entity=True)

    fitted_df = (
        fit.fitted_values
        .reset_index()
        .pivot(index='year', columns='country', values='fitted_values')
    )
    return fit, fitted_df


def run_heterogeneity_regression(panel_df, covariates, extra_vars):
    """
    Run a second-stage heterogeneity regression (Table 6).

    Builds a spec of delta_inflation_hat + extra_vars + covariates and fits
    a country-FE linear probability model with clustered standard errors.
    Displays the key rows only (constant through the last extra variable),
    omitting the control lags from the output.

    Parameters
    ----------
    panel_df : pd.DataFrame
        Panel indexed by (country, year) containing 'crisis',
        'delta_inflation_hat', all extra_vars, and all covariates.
    covariates : list of str
        Names of the control variables (stir and gdp lags).
    extra_vars : list of str
        Additional regressors beyond the baseline: interaction terms first,
        then the corresponding level variables.

    Returns
    -------
    pd.DataFrame
        Coefficient table with standard errors for the key rows only.
    """
    spec = ['delta_inflation_hat'] + extra_vars + covariates
    df   = panel_df[['crisis'] + spec].dropna()

    fit = PanelOLS(
        dependent      = df['crisis'],
        exog           = add_const(df[spec]),
        entity_effects = True,
        time_effects   = False,
    ).fit(cov_type='clustered', cluster_entity=True)

    # Show const + delta_inflation_hat + extra_vars; hide the control lags
    n_key = 1 + 1 + len(extra_vars)   # const, delta_inflation_hat, extra
    return display_w_std_errors(fit).iloc[:n_key]
