import argparse
from pywatts.core.pipeline import Pipeline
from pywatts.modules import Sampler, FunctionModule, Slicer
from pywatts.summaries.discriminative_score import DiscriminativeScore
from pywatts.utils._xarray_time_series_utils import numpy_to_xarray
from pywatts.core.summary_formatter import SummaryJSON
from pywatts.callbacks import CSVCallback
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
    pipeline = Pipeline(f"results/discriminative_score")

    sampler_real = Sampler(96)(x=pipeline["kW"])
    sampler_anomalies_real = Sampler(96)(x=pipeline["label"])
    sampler_synthetic = Sampler(96)(x=pipeline["y_hat"])
    sampler_anomalies_synthetic = Sampler(96)(x=pipeline["anomalies"])

    real_target = FunctionModule(lambda x: numpy_to_xarray(x.values.sum(axis=1) > 0, x))(x=sampler_anomalies_real)
    synthetic_target = FunctionModule(lambda x: numpy_to_xarray(x.values.sum(axis=1) > 0, x))(x=sampler_anomalies_synthetic)

    sampler_real = Slicer(start=96, end=-96)(x=sampler_real)
    sampler_synthetic = Slicer(start=96, end=-96)(x=sampler_synthetic)
    real_target = Slicer(start=96, end=-96)(x=real_target)
    synthetic_target = Slicer(start=96, end=-96)(x=synthetic_target)

    DiscriminativeScore()(gt=sampler_real, synthetic=sampler_synthetic, gt_mask=real_target, synthetic_mask=synthetic_target)

    result, summary = pipeline.train(data=ts, summary=True, summary_formatter=SummaryJSON())
