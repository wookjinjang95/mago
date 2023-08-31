from threading import Thread
from typing import Callable, Tuple
from io import StringIO
import logging, time, sys, os

"""
    Author: Wookjin Jang
    Email: wookjinjang95@gmail.com
"""
class Worker(Thread):
    def __init__(self,
        id: str,
        task: Callable,
        args: Tuple,
        log_directory: str = None,
        repeat: bool = False,
        timeout: int = None
    ):
        Thread.__init__(self)
        self._id = id
        self._task = task
        self._args = args
        self._timeout: int = timeout
        if self._timeout == None:
            self._repeat = False
        else:
            self._repeat: bool = repeat
        self._results = []
        self._stop_loop = False
        self._time_created = None
        self._tasks_executed = 0
        self._total_passed = 0
        self._total_timedout = 0

        #add sysout handler
        self.sys_handler = logging.StreamHandler(sys.stdout)
        self.sys_handler.setFormatter(
            logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))

        #setting up the string log handler.
        self.log_stream = StringIO()
        self.log_handler = logging.StreamHandler(self.log_stream)
        self.log_handler.setFormatter(
            logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))

        #Finally setup the logger.
        self.logger = logging.getLogger("WorkerLogger:{}".format(self._id))
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.log_handler)
        self.logger.addHandler(self.sys_handler)

        #setting up the file handler.
        if log_directory != None:
            self.log_filepath = os.path.join(log_directory, '{}.log'.format(self._id))
            self.fp = open(self.log_filepath, 'x')
            self.fp.close()
            self.file_handler = logging.FileHandler(self.log_filepath)
            self.file_handler.setFormatter(
                logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
            self.logger.addHandler(self.file_handler)

    """
        This is the main run function that will execute the task given.
        In order to run this, please run Worker.start(). That will
        kick off this function as this function is override of Thread.
        Just note that Thread can be run only once.
    """
    def run(self) -> None:
        self._time_created = time.time() * 1000

        while not self._stop_loop:
            self.logger.info("Starting worker: {} with task: {}".format(
                self._id, self._task.__name__))
            time_started = time.time() * 1000
            status = "SUCCESS"
            result = None
            try:
                result = self._task(*self._args)
                if result == None:
                    result = "EMPTY RESPONSE"
                self._total_passed += 1
            except Exception as err:
                self.logger.error("Failed to execute due to error : {}".format(err))
                status = "FAILED"
                self._total_timedout += 1
            finally:
                time_ended = time.time() * 1000
                self.logger.info("Worker {} has succesfully finished the process.".format(
                    self._id))

                if self._timeout != None:
                    if time_ended - self._time_created > self._timeout * 1000:
                        status = "FAILED DUE TO TIMEOUT"
                        self._stop_loop = True
                
                self._results.append({
                    "start_time": time_started,
                    "end_time": time_ended,
                    "duration": time_ended - time_started,
                    "value": result,
                    "status": status
                })
                self._tasks_executed += 1

            if not self._repeat:
                break
        
        self._time_ended = time.time() * 1000
    
    """
        Get all info
    """
    def get_result(self) -> dict:
        return {
            "id": self._id,
            "created": self._time_created,
            "result": self._results
        }

    def get_total_tasks_executed(self) -> int:
        return self._tasks_executed

    def get_total_passed(self) -> int:
        return self._total_passed

    def get_total_failed(self) -> int:
        return self._tasks_executed - self._total_passed

    def get_pass_percentage(self) -> float:
        return self._total_passed/self._tasks_executed

    def get_total_timedout(self) -> int:
        return self._total_timedout

    def get_total_min_duration(self) -> float:
        return min([each_result['duration'] for each_result in self._results])

    def get_total_max_duration(self) -> float:
        return max([each_result['duration'] for each_result in self._results])

    def get_avg_duration(self) -> float:
        totalSum = sum([each_result['duration'] for each_result in self._results])
        return totalSum / self._tasks_executed

    def get_log(self) -> str:
        logs = self.log_stream.getvalue()
        if not logs:
            return "No Errors"
        return logs
