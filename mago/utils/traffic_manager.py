from .worker import Worker
from datetime import datetime, timedelta
from typing import Callable, Tuple
from threading import Thread
from collections import defaultdict
import time, itertools


"""
    TODO: Add logging for this class.
    TODO: Max workers are not defined.

    Convert task argument into list and we want args for that list also.
    Use args as list also. It will be one to one ratio reference.
    We can also have a task with contiuous load and the other task with peak load.
    This customizatio

    The self.results will contain the information with keys, and values
    which keys are the tasks and values are the workers that are
    assigned to that tasks.
"""
class TrafficManager:
    def __init__(self, tasks: list[Callable], tasks_args: list[Tuple], oper_types: list[str], **kwargs):
        self.tasks = tasks
        self.tasks_args = tasks_args
        self.oper_types = oper_types
        self.total_workers = kwargs.get("total_workers", 10)
        self.timeout = kwargs.get("timeout", 60)
        self.every_second = kwargs.get("every_second", 1)
        self.workers_per_iter = kwargs.get("workers_per_iter", 1)
        self.processes = []
        self.results = defaultdict(list)
        self.traffic_unique_id = itertools.count()

    """
        Remember that when you run the traffic manager again, it will
        clean up the  collected workers.
    """
    def _before_run(self) -> None:
        print("Runing total workers: {} for each task in {}".format(
            self.total_workers, [task.__name__ for task in self.tasks]))
        print("The each task will run total of {} seconds duration".format(self.timeout))
        self.processes = []
        self.results = defaultdict(list)

    def _generate_traffic_unique_id(self):
        return str(next(self.traffic_unique_id))

    def _generate_thread_id(self, traffic_name, traffic_id, thread_id):
        return "{}-{}-{}".format(traffic_name, traffic_id, thread_id)

    def _start_process(self, childs) -> None:
        for child in childs:
            child.start()

    #This wait function is general wait function.
    def _wait(self, childs) -> None:
        for child in childs:
            child.join()

    def get_run_result(self) -> None:
        return self.results

    """
        This is the main function that Traffic Manager. Given a list of tasks
        list of args, and operation types, there are many ways the traffic manager
        can assign to each tasks with what operations. For example, you can have
        one single task performing incremental traffic, while the other task performing
        continuous loads.
    """
    def run(self) -> list[Worker]:
        self._before_run()
        for task, task_args, oper_type in zip(self.tasks, self.tasks_args, self.oper_types):
            traffic_id = self._generate_traffic_unique_id()
            print("Generated ID: {} for traffic typ: {}".format(traffic_id, oper_type))
            if oper_type == "incremental_traffic":
                p = Thread(
                    target=self.incremental_traffic,
                    args=(oper_type, traffic_id, task, task_args))
            elif oper_type == "peak_load":
                p = Thread(
                    target=self.peak_load,
                    args=(oper_type, traffic_id, task, task_args))
            elif oper_type == "continuous_load":
                p = Thread(
                    target=self.continuous_load,
                    args=(oper_type, traffic_id, task, task_args))
            else:
                raise Exception(
                    "The operation : {} couldn't be found under TrafficManager".format(
                        oper_type)
                    )
            self.processes.append(p)

        print("Starting the process")
        self._start_process(self.processes)

        print("Waiting for all processes to finish by traffic manager..")
        self._wait(self.processes)

        print("The task has finished by Traffic Manager.")
        return self.get_run_result()

    """
        Perform incremental traffic and return those results in
        a list of workers. The way incremental traffic work is by 
        sending 1 client to N clients in a group one by one. The first
        test will be 1 Client, second iteration test will be 2 clients, 
        and so forth until N clients for Nth iteration.
    """
    def incremental_traffic(self, traffic_name, traffic_id, task, task_args) -> None:
        result = []
        id_tracker = 0
        current_workers = 1
        end_duration_time = datetime.now() + timedelta(seconds=self.timeout)

        while datetime.now() < end_duration_time:
            workers = []
            print("Setting total of {} workers".format(current_workers))
            for _ in range(current_workers):
                workers.append(
                    Worker(
                        id=self._generate_thread_id(
                            traffic_name, traffic_id, id_tracker),
                        args=task_args,
                        task=task
                    )
                )
                id_tracker += 1

            for worker in workers:
                worker.start()
            
            self._wait(workers)
            result += workers

            if current_workers < self.total_workers:
                current_workers += 1
        
        self.results[task.__name__] += result

    """
        Run all N clients at the same time for the certain duration.
        Each of the worker will do the task again and again until the
        timout of the test duration.
    """
    def peak_load(self, traffic_name, traffic_id, task, task_args) -> None:
        workers = []
        id_tracker = 0

        for _ in range(self.total_workers):
            workers.append(
                Worker(
                    id=self._generate_thread_id(
                        traffic_name, traffic_id, id_tracker
                    ),
                    task=task,
                    timeout=self.timeout,
                    repeat=True,
                    args=task_args
                )
            )
            id_tracker += 1

        for worker in workers:
            worker.start()
        
        print("Scheduled workers, just waiting for workers to finish")
        self._wait(workers)

        self.results[task.__name__] += workers

    """
        Continuous load will send X requests (or generate clients/workers)
        per n amount of seconds. For more furhter details, please check
        the documentation.
    """
    def continuous_load(
        self,
        traffic_name: str,
        traffic_id,
        task,
        task_args
    ) -> None:
        end_duration_time = datetime.now() + timedelta(seconds=self.timeout)
        workers = []
        id_tracker = 0

        while datetime.now() < end_duration_time:
            this_iter_workers = []
            for _ in range(self.workers_per_iter):
                this_iter_workers.append(
                    Worker(
                        id=self._generate_thread_id(
                            traffic_name, traffic_id, id_tracker
                        ),
                        task=task,
                        args=task_args
                    )
                )
                id_tracker += 1

            for worker in this_iter_workers:
                worker.start()
            workers += this_iter_workers
            time.sleep(self.every_second)

        self._wait(workers)

        self.results[task.__name__] += workers

    