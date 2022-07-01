# Generating Synthetic Anomalies for Energy and Power Time Series

This repository contains the Python implementation of the method to generate synthetic anomalies for an arbitrary energy or power time series as presented in the following paper:
>M. Turowski, M. Weber, O. Neumann, B. Heidrich, K. Phipps, H. K. Çakmak, R. Mikut and V. Hagenmeyer, 2022, "Modeling and Generating Synthetic Anomalies for Energy and Power Time Series," in The Thirteenth ACM International Conference on Future Energy Systems (e-Energy ’22). ACM, pp. 471–484. doi: [10.1145/3538637.3539760](https://dl.acm.org/doi/10.1145/3538637.3539760)


## Installation

Before anomalies can be generated using a [pyWATTS](https://github.com/KIT-IAI/pyWATTS) pipeline, you need to prepare a Python environment and download the power or energy time series data (if you have no data available).

### 1. Setup Python Environment

Set up a virtual environment using e.g. venv (`python -m venv venv`) or Anaconda (`conda create -n env_name`). Afterwards, install the dependencies with `pip install -r requirements.txt`. 

### 2. Download Data (optional)

If you do not have any power or energy time series available, you can download exemplary data by executing `python download.py`. This script downloads and unpacks the [ElectricityLoadDiagrams20112014 Data Set](https://archive.ics.uci.edu/ml/datasets/ElectricityLoadDiagrams20112014) from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/) as CSV file, which can be used as power time series.


## Generate Synthetic Anomalies

Finally, you can generate synthetic anomalies for power or energy time series.

### Input

To generate synthetic anomalies, run the generation with `python generate_anomalies.py name_csv_file selected_column energy_or_power` to use some default parameters from Table 3 in the paper.
With the data described above, an exemplary generation command for the column "MT_321" could be `python generate_anomalies.py LD2011_2014.txt MT_321 power
`.

You can see a list of all parameters available for the generation by calling `python generate_anomalies.py --help`. 

The following parameters are available:

```
# Required arguments
csv_path
   Path to the data CSV file.
column
   Name of the target column.
type
   Type of the time series ("energy" or "power").


# Type 1 anomalies
--type1 (int or float)
   Percentage or absolute number of type 1 anomalies.
--type1_len_min (int)
   Minimum length of type 1 anomalies
--type1_len_max (int)
   Maximum length of type 1 anomalies

# Type 2 anomalies
--type2 (int or float)
   Percentage or absolute number of type 2 anomalies.
--type2_len_min (int)
  Minimum length of type 2 anomalies
--type2_len_max (int)
   Maximum length of type 2 anomalies
--type2_softstart (bool)
   If softstart should be used for type 2 anomalies.

# Type 3 anomalies
--type3 (int or float)
   Percentage or absolute number of type 3 anomalies.
--type3_r_min (int)
   Minimum r of type 3 anomalies (slight case)
--type3_r_max (int)
   Maximum r of type 3 anomalies (slight case)
--type3_extreme (bool)
   Enable type 3 extreme anomaly case.

# Type 4 anomalies
--type4 (int or float)
   Percentage or absolute number of type 4 anomalies.
--type4_r_min (int)
   Minimum r of type 4 anomalies (either slight or extreme case)
--type4_r_max (int)
   Maximum r of type 4 anomalies (either slight or extreme case)

# Type 1 and 3 anomalies
--k (int)
   Energy offset of type 1 and 3 anomalies.

# Optional general parameters
--time (string)
   Name of the time index (if it is not unnamed).
--seed (int)
   Seed to be used in the pipeline run.
--csv_separator (string)
   CSV file column separator (default ,).
--csv_decimal (string)
   CSV file decimal delimiter (default .).
```

### Output

After running the command, the pipeline returns an "energy.csv" or "power.csv" file containing the following four columns:
* index: time information
* y: values of the original time series
* anomalies: labels (0 for unchanged original values and the labels 1, 2, 31, 32, 4 for inserted anomalies of the different types)
* y_hat: values of the time series containing synthetic anomalies


## Evaluation
For the evaluation, there are three pipelines in the evaluation folder. These pipelines calculate the predictive score, the discriminative score, and the diversity of the generated anomalies.

### Input
A path to a csv file containing the real time series with labeled anomalies and the time series with synthetic anomalies and the corresponding labels.


## Funding

This project is supported by the Helmholtz Association’s Initiative and Networking Fund through Helmholtz AI, by the Helmholtz Association under the Program “Energy System Design”, and by the German Research Foundation (DFG) Research Training Group 2153 "Energy Status Data: Informatics Methods for its Collection, Analysis and Exploitation".


## License

This code is licensed under the [MIT License](LICENSE).
