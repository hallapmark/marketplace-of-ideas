import csv
import os
import warnings
import numpy as np
from tqdm import tqdm
from typing import NamedTuple

from .simulation import *


class ENResultsCSVWritableSummary(NamedTuple):
    headers: list[str]
    config_run_data: list[str]


class ResultsSummary(NamedTuple):
    # Av. proportion of true beliefs out of all beliefs at end of sims
    av_prop_true: float
    # No of sims where nobody had beliefs at end of run
    no_beliefs_n: int


class ConfigRunResults(NamedTuple):
    config: SimulationConfiguration
    results: ResultsSummary


def configs_run(
    configs: list[SimulationConfiguration], sim_n: int
) -> list[ConfigRunResults]:
    all_configs_results: list[ConfigRunResults] = []
    for config in configs:
        print()
        print(f"Running config: {config}")
        sims_results: list[SimulationResult] = []
        for i in tqdm(range(sim_n), mininterval=3):
            sim = Simulation(config)
            sims_results.append(sim.run_sim())
        props: list[float] = []
        no_beliefs_n = 0
        for i, res in enumerate(sims_results):
            if res.proportion_true_beliefs is not None:
                props.append(res.proportion_true_beliefs)
            else:
                warnings.warn(
                    "Nobody has any beliefs in sim.",
                    RuntimeWarning,
                )
                no_beliefs_n += 1
        av_prop_true = round(float(np.average(props)), 4)
        res_summary = ResultsSummary(av_prop_true, no_beliefs_n)
        config_result = ConfigRunResults(config, res_summary)
        all_configs_results.append(config_result)
    return all_configs_results


def setup_sims(
    configs: list[SimulationConfiguration], output_filename: str, sim_count
) -> None:
    np.random.seed(45)
    configs_results = configs_run(configs, sim_count)
    for config_res in configs_results:
        csv_data = data_for_writing(config_res, sim_count)
        record_config_run(csv_data, output_filename)


def data_for_writing(
    config_run_results: ConfigRunResults, sim_count: int
) -> ENResultsCSVWritableSummary:
    headers = ["Sim count"]
    headers.extend(
        [param_name for param_name in config_run_results.config._asdict().keys()]
    )
    summary_fields = [
        field for field in config_run_results.results._asdict().keys()
    ]
    headers.extend(summary_fields)

    sim_data = [str(sim_count)]
    sim_data.extend([str(param_val) for param_val in config_run_results.config])
    result_str_list = [str(r) for r in config_run_results.results]
    print(f"Summary fields: {summary_fields}")
    print(f"Results from config: {result_str_list}")
    sim_data.extend(result_str_list)
    summary = ENResultsCSVWritableSummary(headers, sim_data)
    return summary


def record_config_run(results: ENResultsCSVWritableSummary, path: str) -> None:
    file_exists = os.path.isfile(path)
    with open(path, newline="", mode="a") as csv_file:
        writer = csv.writer(csv_file)
        if not file_exists:
            writer.writerow(results.headers)
        writer.writerow(results.config_run_data)
