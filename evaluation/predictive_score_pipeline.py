import argparse


from types import SimpleNamespace

from generation_pipeline import create_power_anomaly_pipeline
from pywatts.core.pipeline import Pipeline
from pywatts.core.summary_formatter import SummaryJSON
from pywatts.modules import Sampler, FunctionModule, Slicer
from pywatts.utils._xarray_time_series_utils import numpy_to_xarray
from pywatts.summaries.train_synthetic_test_real import TrainSyntheticTestReal
from  sklearn.tree import DecisionTreeClassifier

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

    pipeline = Pipeline(f"results/predictive_score")
    sampler_real = Sampler(sample_size)(x=pipeline["kW"])
    sampler_anomalies_real = Sampler(sample_size)(x=pipeline["label"])
    sampler_synthetic = Sampler(sample_size)(x=pipeline["y_hat"])
    sampler_anomalies_synthetic = Sampler(sample_size)(x=pipeline["anomalies"])

    real_target = FunctionModule(lambda x: numpy_to_xarray(x.values.sum(axis=1) > 0, x))(x=sampler_anomalies_real)
    synthetic_target = FunctionModule(lambda x: numpy_to_xarray(x.values.sum(axis=1)> 0, x))(x=sampler_anomalies_synthetic)

    sampler_real = Slicer(start=sample_size, end=-sample_size)(x=sampler_real)
    sampler_synthetic = Slicer(start=sample_size, end=-sample_size)(x=sampler_synthetic)
    real_target = Slicer(start=sample_size, end=-sample_size)(x=real_target)
    synthetic_target = Slicer(start=sample_size, end=-sample_size)(x=synthetic_target)

    TrainSyntheticTestReal(task=1,  n_targets=2, get_model=lambda x, y: DecisionTreeClassifier(),
                            fit_kwargs={},
                            metrics=["f1", "accuracy"])(real=sampler_real, synthetic=sampler_synthetic,
                                                        real_target=real_target, synthetic_target=synthetic_target)

    result, summary = pipeline.train(data=ts, summary=True,summary_formatter=SummaryJSON())

