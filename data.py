"""
data.py — Data loading and base panel construction for all replication notebooks.

Each loader returns a clean DataFrame ready to use. `build_base_panel` constructs
the (country, year) panel shared by the oil-shock IV notebooks (Tables 5 and 6).
Notebook 1 uses its own panel construction due to the trilemma-specific logic.
"""

import pandas as pd
import numpy as np
from utils import melt, winsor


# ── Dataset loaders ────────────────────────────────────────────────────────────

def load_jst(path='datasets/JSTdatasetR6.xlsx'):
    """
    Load the Jordà-Schularick-Taylor Macrohistory Database (R6).

    Drops the redundant 'country' name column and uses the ISO code instead.
    Source: www.macrohistory.net/database
    """
    return (
        pd.read_excel(path)
        .drop(columns=['country', 'ifs'])
        .rename(columns={'iso': 'country'})
    )


def load_kaopen(path='datasets/KAOPEN.csv'):
    """
    Load the Chinn-Ito capital account openness index (KAOPEN).

    Returns a wide DataFrame (year × country).
    Source: web.pdx.edu/~ito/Chinn-Ito_website.htm
    """
    raw = pd.read_csv(path, usecols=[0, 1, 2])
    return raw.pivot(index='year', columns='country', values='kopen')


def load_oil_shocks(path='datasets/BH2_supply_shocks.xlsx'):
    """
    Load Baumeister-Hamilton monthly oil supply shocks and aggregate to annual.

    The raw series starts in February 1975. We pad with a January NaN so the
    calendar-year mean covers the full first year, then multiply by 12 to
    express shocks at an annual rate.

    Returns a DataFrame indexed by year (1975–end of sample).
    Source: www.christophbaumeister.com
    """
    raw = pd.read_excel(path, header=1, usecols=[1])
    raw.index = pd.date_range(start='1975-02-01', periods=len(raw), freq='ME')
    raw = raw.reindex(
        pd.date_range(start='1975-01-01', periods=len(raw) + 1, freq='ME'))
    annual = raw.resample('YE').mean() * 12
    annual.index = range(1975, 1975 + len(annual))
    return annual


def load_romelli(path='datasets/CBIData_Romelli_2024.xlsx'):
    """
    Load the Romelli (2024) Central Bank Independence index.

    Returns only the financial independence sub-index (cbie_finindep),
    which is the measure used in Table 6.
    Source: www.damianoromelli.com
    """
    return (
        pd.read_excel(path, sheet_name=1,
                      usecols=['year', 'iso_a3', 'cbie_finindep'])
        .rename(columns={'iso_a3': 'country'})
    )


# ── Panel helpers ──────────────────────────────────────────────────────────────

def build_oil_shocks_panel(cpi_df, oil_shocks):
    """
    Broadcast annual oil shocks to a wide (year × country) panel.

    All countries are treated as price-takers in the global oil market,
    so the same shock value applies to every country in a given year.
    """
    df = cpi_df.copy()
    df[:] = np.nan
    for country in df.columns:
        df[country] = oil_shocks['oil supply shocks']
    return df


def build_base_panel(raw_df, crisis_df, cpi_df, gdp_df, stir_df, oil_shocks_df):
    """
    Build the (country, year) panel shared by the oil-shock IV notebooks.

    Adds the dependent variable (raw crisis onset dummy), the endogenous
    regressor (annual inflation change), the instrument (oil supply shock),
    and contemporaneous + four-lag controls for interest rate changes and
    GDP growth.

    Parameters
    ----------
    raw_df : pd.DataFrame
        JST dataset (and any merged supplements) with a 'country' column.
    crisis_df, cpi_df, gdp_df, stir_df, oil_shocks_df : pd.DataFrame
        Wide (year × country) DataFrames for the respective series.

    Returns
    -------
    panel_df : pd.DataFrame
        Long panel indexed by (country, year).
    covariates : list of str
        Ordered list of control variable names (stir and gdp lags).
    """
    panel_df = raw_df.set_index(['country', 'year'])
    panel_df['year'] = panel_df.reset_index()['year'].values

    # Dependent variable: raw crisis onset dummy (Equations 3 & 4 / Tables 5–6)
    panel_df['crisis'] = melt(crisis_df)

    # Endogenous variable: annual CPI inflation change, winsorised
    panel_df['infl'] = melt(winsor((cpi_df.pct_change() * 100).diff()))

    # Instrument: oil supply shock
    panel_df['oil_shock'] = melt(oil_shocks_df)

    # Controls: contemporaneous and four lags of interest rate changes and GDP growth
    covariates = []
    for lag in range(4 + 1):
        panel_df[f'stir(-{lag})'] = melt(stir_df.diff().shift(lag))
        panel_df[f'gdp(-{lag})']  = melt(
            (gdp_df.pct_change(fill_method=None) * 100).shift(lag))
        covariates.append(f'stir(-{lag})')
        covariates.append(f'gdp(-{lag})')

    return panel_df, covariates
