import os

from pywatts.core.pipeline import Pipeline
from pywatts.modules import FunctionModule

from pywatts.modules.generation import PowerAnomalyGeneration, EnergyAnomalyGeneration


def create_power_anomaly_pipeline(hparams):
    """
    Generate anomalies of types 1 to 4 for a given power time series
    """
    pipeline = Pipeline(path=os.path.join('run'))
    seed = hparams.seed

    # Type 1: Negative power spike potentially followed by zero values and finally a positive power spike
    anomaly_type1 = PowerAnomalyGeneration(
        'y_hat', anomaly='type1', count=hparams.type1, label=1, seed=seed + 1,
        length_params={
            'distribution': 'uniform',
            'min': max(hparams.type1_len_min, 3) if hparams.type1_len_min < 96 - 4 else 96 - 4,
            'max': min(96, hparams.type1_len_max)
        },
        anomaly_params={
            'k': hparams.k
        }
    )(x=pipeline['y'], labels=None)

    # Type 2: Drop to potentially zero followed by a positive power spike
    anomaly_type2 = PowerAnomalyGeneration(
        'y_hat', anomaly='type2', count=hparams.type2, label=2, seed=seed + 2,
        length_params={
            'distribution': 'uniform',
            'min': max(hparams.type2_len_min, 2),
            'max': min(48, hparams.type2_len_max),
        },
        anomaly_params={
            'softstart': hparams.type2_softstart
        }

    )(x=anomaly_type1['y_hat'], labels=anomaly_type1['labels'])

    # Type 3: Sudden negative power spike
    if hparams.type3_extreme:
        anomaly_type3 = PowerAnomalyGeneration(
            'y_hat', anomaly='type3', count=hparams.type3, label=32, seed=seed + 4,
            anomaly_params={
                'is_extreme': True,
                'range_r': (0.01, 3.99),
                'k': hparams.k
            }
        )(x=anomaly_type2['y_hat'], labels=anomaly_type2['labels'])
    else:
        anomaly_type3 = PowerAnomalyGeneration(
            'y_hat', anomaly='type3', count=hparams.type3, label=31, seed=seed + 3,
            anomaly_params={
                'is_extreme': False,
                'range_r': (hparams.type3_r_min, hparams.type3_r_max),
            }
        )(x=anomaly_type2['y_hat'], labels=anomaly_type2['labels'])

    # Type 4: Sudden positive power spike
    anomaly_type4 = PowerAnomalyGeneration(
        'y_hat', anomaly='type4', count=hparams.type4, label=4, seed=seed + 5,
        anomaly_params={
            'range_r': (hparams.type4_r_min, hparams.type4_r_max)
        }
    )(x=anomaly_type3['y_hat'], labels=anomaly_type3['labels'])

    FunctionModule(lambda x: x, name='y')(x=pipeline['y'])
    FunctionModule(lambda x: x, name='anomalies')(x=anomaly_type4['labels'])
    FunctionModule(lambda x: x, name='y_hat')(x=anomaly_type4['y_hat'])

    return pipeline


def create_energy_anomaly_pipeline(hparams):
    """
    Generate anomalies of types 1 to 4 for a given energy time series
    """
    pipeline = Pipeline(path=os.path.join('run'))
    seed = hparams.seed

    # Type 3: Sudden dip
    anomaly_type3 = EnergyAnomalyGeneration(
        'y_hat', anomaly='type3', count=hparams.type3, label=3, seed=seed + 1,
        anomaly_params={
            'is_extreme': hparams.type3_extreme,
            'range_r': (hparams.type3_r_min, hparams.type3_r_max),
        }
    )(x=pipeline['y'], labels=None)

    # Type 4: Sudden increase in gradient
    anomaly_type4 = EnergyAnomalyGeneration(
        'y_hat', anomaly='type4', count=hparams.type4, label=4, seed=seed + 3,
        anomaly_params={
            'range_r': (hparams.type4_r_min, hparams.type4_r_max)
        }
    )(x=anomaly_type3['y_hat'], labels=anomaly_type3['labels'])

    # Type 1: Drop to zero for at least one time step and then jump back to a plausible new value
    anomaly_type1 = EnergyAnomalyGeneration(
        'y_hat', anomaly='type1', count=hparams.type1, label=1, seed=seed + 4,
        length_params={
            'distribution': 'uniform',
            'min': max(hparams.type1_len_min, 3) if hparams.type1_len_min < 96 - 4 else 96 - 4,
            'max': min(96, hparams.type1_len_max)
        }
    )(x=anomaly_type4['y_hat'], labels=anomaly_type4['labels'])

    # Type 2: Decrease in gradient, potentially full stagnation for several time steps and return to the correct value.
    anomaly_type2 = EnergyAnomalyGeneration(
        'y_hat', anomaly='type2', count=hparams.type2, label=2, seed=seed + 5,
        length_params={
            'distribution': 'uniform',
            'min': max(hparams.type2_len_min, 2),
            'max': min(48, hparams.type2_len_max),
        },
        anomaly_params={
            'softstart': hparams.type2_softstart
        }
    )(x=anomaly_type1['y_hat'], labels=anomaly_type1['labels'])

    FunctionModule(lambda x: x, name='y')(x=pipeline['y'])
    FunctionModule(lambda x: x, name='anomalies')(x=anomaly_type2['labels'])
    FunctionModule(lambda x: x, name='y_hat')(x=anomaly_type2['y_hat'])

    return pipeline
