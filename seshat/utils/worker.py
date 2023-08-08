from datetime import datetime
from threading import Thread
import logging


class Worker(Thread):
    def __init__(self,
        id: int,
        task,
        args,
        repeat: bool = False,
        timeout: int = None
    ):
        Thread.__init__(self)
        self._id = id
        self._log = ""
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

    """
        TODO: Figure a way to collect system logs
    """
    def _logger(self, message) -> None:
        self._log += "{}\n".format(message)

    """
        This is the main run function that will execute the task given.
        In order to run this, please run Worker.start(). That will
        kick off this function as this function is override of Thread.
    """
    def run(self) -> None:
        self._logger("Starting worker: {} with task: {}".format(
            self._id, self._task.__name__))
        self._time_created = datetime.now()

        while not self._stop_loop:
            time_started = datetime.now()
            status = "SUCCESS"
            result = None
            try:
                result = self._task(*self._args)
                if result == None:
                    result = "EMPTY RESPONSE"
                self._total_passed += 1
            except Exception as err:
                self._logger("Failed to execute due to error : {}".format(err))
                status = "FAILED"
                self._total_timedout += 1
            finally:
                time_ended = datetime.now()
                self._logger("Worker {} has succesfully finished the process.".format(
                    self._id))

                if self._timeout != None:
                    if self._get_execution_time(self._time_created, time_ended) > self._timeout:
                        status = "FAILED DUE TO TIMEOUT"
                        self._stop_loop = True
                
                self._results.append({
                    "start_time": time_started,
                    "end_time": time_ended,
                    "duration": self._get_execution_time(time_started, time_ended),
                    "value": result,
                    "status": status
                })
                self._tasks_executed += 1

            if not self._repeat:
                break

    """
        Returning the raw value of the result.
    """
    def _get_execution_time(self, start_time, end_time) -> int:
        return int((end_time - start_time).total_seconds())

    """
        Get all info
    """
    def get_result(self) -> dict:
        return {
            "id": self._id,
            "log": self._log,
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
