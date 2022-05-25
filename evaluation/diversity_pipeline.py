import argparse

from types import SimpleNamespace
from datetime import datetime

from pywatts.core.pipeline import Pipeline
from pywatts.modules import Sampler, FunctionModule, Slicer
from pywatts.summaries import TSNESummary
from pywatts.utils._xarray_time_series_utils import numpy_to_xarray

import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(
    description='Pipeline for evaluating the synthetic anomalies.'
)
parser.add_argument('csv_path', type=str, help='Path to the data CSV file. The CSV File has to contain the ts with the real anomalies (kW), '
    'the labels of the real anomalies (label), the time series with the synthetic anomalies (y_hat), and the labels of the synthetic anomalies (anomalies)')
args = parser.parse_args()
if __name__ == "__main__":
    sample_size = 48
    ts = pd.read_csv(args.csv_path)

    pipeline = Pipeline(f"results/diversity")

    sampler_real = Sampler(96)(x=pipeline["kW"])
    sampler_free = Sampler(96)(x=pipeline["cleaned kW"])
    sampler_anomalies_real = Sampler(96)(x=pipeline["label"])
    sampler_synthetic = Sampler(96)(x=pipeline["y_hat"])
    sampler_anomalies_synthetic = Sampler(96)(x=pipeline["anomalies"])

    real_target = FunctionModule(lambda x: numpy_to_xarray(x.values.sum(axis=1) > 0, x))(
        x=sampler_anomalies_real)
    synthetic_target = FunctionModule(lambda x: numpy_to_xarray(x.values.sum(axis=1) > 0, x))(
        x=sampler_anomalies_synthetic)

    sampler_real = Slicer(start=96, end=-96)(x=sampler_real)
    sampler_free = Slicer(start=96, end=-96)(x=sampler_free)
    sampler_synthetic = Slicer(start=96, end=-96)(x=sampler_synthetic)
    real_target = Slicer(start=96, end=-96)(x=real_target)
    synthetic_target = Slicer(start=96, end=-96)(x=synthetic_target)

    TSNESummary(max_points=300, name="Diversity anomalies",
                tsne_params={"n_components": 2, "perplexity": 40, "n_iter": 300}
                )(gt=sampler_real, synthetic=sampler_synthetic, gt_masked=real_target,
                    synthetic_masked=synthetic_target)
    TSNESummary(max_points=300, name="Diversity all", all_in_one_plot=True)(gt=sampler_free, real=sampler_real,
                                                                            synthetic=sampler_synthetic, )

    pipeline.train(data=ts)
