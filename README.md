# The Causal Effect of Inflation on Financial Stability — Replication Code

Replication code for:

> Albertazzi, U., 't Hooft, J., & ter Steege, L. (2025).  
> *The causal effect of inflation on financial stability: evidence from history.*  
> ECB Working Paper Series No. 3108.  
> [Link to paper](https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp3108.en.pdf)

---

## Repository Structure

```
repo/
├── datasets/
│   ├── JSTdatasetR6.xlsx              # Jordà-Schularick-Taylor Macrohistory Database (R6)
│   ├── KAOPEN.csv                     # Chinn-Ito capital account openness index
│   ├── BH2_supply_shocks.xlsx             # Baumeister-Hamilton oil supply shocks
│   └── CBIData_Romelli_2024.xlsx          # Romelli central bank independence index
│
├── equation_1_diff_in_diff.ipynb          # Matched pegged-base regression (Table 4)
├── equation_3_4_2SLS_oil_shocks.ipynb     # Oil supply shock IV regression (Table 5)
└── table_6_heterogeneity_interactions.ipynb  # Heterogeneous effects of inflation (Table 6)
```

---

## Notebooks

| Notebook | Description | Paper section |
|---|---|---|
| `equation_1_diff_in_diff.ipynb` | Matched pegged-base countries regression — isolates the direct effect of inflation on financial stability by exploiting the monetary trilemma | Section 4.1 / Table 4 |
| `equation_3_4_2SLS_oil_shocks.ipynb` | Oil supply shock IV — instruments inflation with Baumeister-Hamilton oil supply shocks; first stage (Eq. 3) and second stage (Eq. 4) | Section 4.2 / Table 5 |
| `table_6_heterogeneity_interactions.ipynb` | Heterogeneous effects — interacts instrumented inflation with wage growth, debt ratios, and CB financial independence to test transmission channels | Section 6 / Table 6 |

---

## Data

### Jordà-Schularick-Taylor Macrohistory Database (JST R6)
Annual macro-financial panel for 18 advanced economies, 1870–2020.  
Download from: [www.macrohistory.net/database](https://www.macrohistory.net/database/)

Place the file at `datasets/JSTdatasetR6.xlsx`.

**Countries:** Australia, Belgium, Canada, Denmark, Finland, France, Germany, Ireland,
Italy, Japan, the Netherlands, Norway, Portugal, Spain, Sweden, Switzerland,
the United Kingdom, and the United States.

### Baumeister-Hamilton Oil Supply Shocks
Monthly structural oil supply shocks from a Bayesian VAR with sign restrictions, 1975–2020.  
Download from: [www.christophbaumeister.com](https://www.christophbaumeister.com/)

Place the file at `datasets/BH2_supply_shocks.xlsx`.

### Romelli Central Bank Independence Index
Annual CBI scores for advanced economies, covering multiple sub-indices including financial independence.  
Download from: [www.damianoromelli.com](https://www.damianoromelli.com/)

Place the file at `datasets/CBIData_Romelli_2024.xlsx`.

### Chinn-Ito Capital Openness Index (KAOPEN)
Standardised measure of capital account openness.  
Download from: [web.pdx.edu/~ito/Chinn-Ito_website.htm](http://web.pdx.edu/~ito/Chinn-Ito_website.htm)

Place the file at `datasets/KAOPEN.csv`.

---

## Dependencies

```
pandas
numpy
scipy
statsmodels
linearmodels
openpyxl        # for reading .xlsx files
```

Install with:

```bash
pip install pandas numpy scipy statsmodels linearmodels openpyxl
```

---

## How to Run

Clone the repository and launch Jupyter:

```bash
git clone https://github.com/your-username/inflation_financial_crises_code.git
cd inflation_financial_crises_code
jupyter notebook
```

Then open the relevant notebook. All paths are relative to the `repo/` directory,
so run notebooks from there.

---

## Citation

If you use this code, please cite the paper:

```bibtex
@techreport{albertazzi2025inflation,
  author      = {Albertazzi, Ugo and {'t Hooft}, James and {ter Steege}, Lucas},
  title       = {The causal effect of inflation on financial stability: evidence from history},
  institution = {European Central Bank},
  series      = {Working Paper Series},
  number      = {3108},
  year        = {2025}
}
```
