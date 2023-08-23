from .utils.report_generator import ReportGenerator
from .utils.traffic_manager import TrafficManager
from .utils.collector import Collector
from typing import Callable, Tuple
import logging, os


logging.basicConfig(level=logging.DEBUG)
"""
    This is the main Seshat which users will interact for their
    own custom testing method.

    TODO: Create a test for Seshat itself
"""
class Mago:
    def __init__(
        self,
        tasks: list[Callable],
        tasks_args: list[Tuple],
        oper_types: list[str],
        total_workers: int,
        output_path: str,
        timeout: int = 60
    ):
        self.output_path = output_path
        if not os.path.exists(self.output_path):
            os.mkdir(self.output_path)

        self.traffic_manager = TrafficManager(
            tasks=tasks,
            tasks_args=tasks_args,
            oper_types=oper_types,
            total_workers=total_workers,
            timeout=timeout
        )
        self.report_generator = ReportGenerator(output=output_path)
        self.logger = logging.getLogger(__name__)

    """
        This function will store the result.
    """
    def store_result(self, data: dict):
        self.report_generator.write_home_content(data)
        self.report_generator.write_workers_content(data)
        self.report_generator.write_log_content(data)

    def collect_data(self, results: dict[str, list]) -> dict:
        data = {}
        data['num_of_workers_datasets'] =\
            Collector.collect_total_clients_per_timeline(results)

        data['avg_resp_min_time'], data['avg_response_datasets'] =\
            Collector.give_average_durations(results)

        data['num_of_tasks_x_labels'], data['num_of_tasks_datasets'] =\
            Collector.collect_total_task_finished_per_worker(results)

        data['task_distributed_labels'], data['task_distributed_percentage'] =\
            Collector.get_task_distributed(results)

        data['tasks_passed_labels'], data['task_passed_data'] =\
            Collector.get_tasks_passed(results)

        data['polar_area_labels'], data['polar_area_average_data'] =\
            Collector.get_average_time_tasks(results)

        data['percentile_data_table'] = Collector.collect_percentile(results)
        data['passFailLabels'], data['passFailBarData'] =\
            Collector.get_pass_fail_percentage(results)

        data['logDataInfo'] = Collector.collect_log_data(results)

        return data

    def run(self):
        self.traffic_manager.run()
        results = self.traffic_manager.get_run_result()
        finalized_data = self.collect_data(results)
        self.store_result(finalized_data)