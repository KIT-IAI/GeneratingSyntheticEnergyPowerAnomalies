import argparse

import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt

from generation_pipeline import create_power_anomaly_pipeline, create_energy_anomaly_pipeline


def str2intorfloat(v):
    """ String to int or float formatter for argparse. """
    try:
        return int(v)
    except:
        return float(v)


def parse_hparams(args=None):
    """ Parse command line arguments and return. """
    # prepare argument parser
    parser = argparse.ArgumentParser(
        description='Anomaly generation pipeline for energy and power time series.'
    )
    # csv path file
    parser.add_argument('csv_path', type=str, help='Path to the data CSV file.')
    # data_index
    parser.add_argument('column', type=str, help='Name of the target column.')
    # energy type
    parser.add_argument('type', type=str, help='Type of the time series ("power" or "energy").')
    # time_index
    parser.add_argument('--time', type=str, default='Unnamed: 0', help='Name of the time index.')

    # anomaly params: Type 1
    parser.add_argument('--type1', type=str2intorfloat,  default=3,
                        help='Percentage or absolute number of type 1 anomalies.')
    parser.add_argument('--type1_len_min', type=int, default=6,
                        help='Minimum length of type 1 anomalies')
    parser.add_argument('--type1_len_max', type=int, default=10,
                        help='Maximum length of type 1 anomalies')

    # anomaly params: Type 2
    parser.add_argument('--type2', type=str2intorfloat, default=3,
                        help='Percentage or absolute number of type 2 anomalies.')
    parser.add_argument('--type2_len_min', type=int, default=6,
                        help='Minimum length of type 2 anomalies')
    parser.add_argument('--type2_len_max', type=int, default=10,
                        help='Maximum length of type 2 anomalies')
    parser.add_argument('--type2_softstart', action='store_true',
                        help='If softstart should be used for type 2 anomalies.')

    # anomaly params: Type 3
    parser.add_argument('--type3', type=str2intorfloat, default=4,
                        help='Percentage or absolute number of type 3 anomalies.')
    parser.add_argument('--type3_r_min', type=int, default=0.01,
                        help='Minimum r of type 3 anomalies (slight case)')
    parser.add_argument('--type3_r_max', type=int, default=3.99,
                        help='Maximum r of type 3 anomalies (slight case)')
    parser.add_argument('--type3_extreme', action='store_true',
                        help='Enable type 3 extreme anomaly case.')

    # anomaly params: Type 4
    parser.add_argument('--type4', type=str2intorfloat, nargs='?', const=True, default=10,
                        help='Percentage or absolute number of type 4 anomalies.')
    parser.add_argument('--type4_r_min', type=int, default=2,
                        help='Minimum r of type 4 anomalies (either slight or extreme case)')
    parser.add_argument('--type4_r_max', type=int, default=5,
                        help='Maximum r of type 4 anomalies (either slight or extreme case)')

    # anomaly params: All types
    parser.add_argument('--k', type=int, default=0,
                        help='Energy offset of type 3 anomalies.')

    # Set random seed
    parser.add_argument('--seed', type=int, default=42,
                        help='Seed to be used in the pipeline run.')

    # delimiter
    parser.add_argument('--csv_separator', type=str, default=';',
                        help='CSV file column separator (default ,).')
    # decimal
    parser.add_argument('--csv_decimal', type=str, default=',',
                        help='CSV file decimal delimiter (default .).')

    # convert argument strings
    parsed_hparams = parser.parse_args(args=args)

    return parsed_hparams


def load_data(hparams):
    """ Load the CSV file specified by hparams dict. """
    dataset = pd.read_csv(
        hparams.csv_path, index_col=hparams.time, parse_dates=True,
        delimiter=hparams.csv_separator, decimal=hparams.csv_decimal
    )

    rename_dict = {}
    rename_dict[hparams.column] = 'y'
    dataset.rename(columns=rename_dict, inplace=True)

    return dataset


def create_pipeline(hparams):
    """ Create energy or power anomaly generation pipeline. """
    if hparams.type.lower() == 'power':
        return create_power_anomaly_pipeline(hparams)
    elif hparams.type.lower() == 'energy':
        return create_energy_anomaly_pipeline(hparams)
    else:
        raise ValueError('Please select type "energy" or "power"')


def run_pipeline(hparams):
    """ Run complete power or anomaly generation pipeline (including data loading/saving). """
    dataset = load_data(hparams)
    print(dataset)
    pipeline = create_pipeline(hparams)
    result, _ = pipeline.train(dataset)
    result = xr.Dataset(result).to_pandas()
    return result


def save_result(hparams, result):
    """ Save result as CSV and plot comparison. """
    result.to_csv(f'{hparams.type}.csv')
    plt.plot(result.index, result['y'], label='input')
    plt.plot(result.index, result['y_hat'], label='output')
    plt.legend()
    plt.savefig(f'{hparams.type}.png')


if __name__ == '__main__':
    hparams = parse_hparams()
    result = run_pipeline(hparams)
    save_result(hparams, result)
