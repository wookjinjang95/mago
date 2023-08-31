import shutil
from mago.utils.worker import Worker
from datetime import datetime, timedelta
import time
import pytest
import os


@pytest.mark.parametrize("func, data, expect", [(sum, [1,2,3,4], 10)])
def test_worker_get_result(func, data, expect):
    test_output_dir = "./test_output"
    if os.path.exists(test_output_dir):
        shutil.rmtree(test_output_dir)
    os.mkdir(test_output_dir)

    test_worker = Worker(id='sum-0-0', task=func, args=(data, ), log_directory=test_output_dir)
    test_worker.start()
    test_worker.join()
    result = test_worker.get_result()
    assert result['id'] == 'sum-0-0'
    assert type(result['result']) == list
    assert len(result['result']) >= 1
    assert test_worker.get_log != None or test_worker.get_log != ""
    assert result['result'][0]['value'] == expect
    assert result['result'][0]['status'] == "SUCCESS"
    assert result['result'][0]['start_time'] != None
    assert result['result'][0]['end_time'] != None
    assert result['result'][0]['end_time'] > result['result'][0]['start_time']

    log_file_location = os.path.join(test_output_dir, 'sum-0-0.log')
    assert os.path.exists(log_file_location) == True

    with open(log_file_location, 'r') as fp:
        log = fp.readlines()
        assert len(log) != 0

    shutil.rmtree(test_output_dir)

def test_worker_timeout():
    def time_sleep():
        time.sleep(5)
    
    test_worker = Worker(
        id=1, task=time_sleep, args=(), timeout=2
    )
    test_worker.start()
    test_worker.join()
    result = test_worker.get_result()
    assert result['result'][0]['status'] == "FAILED DUE TO TIMEOUT"
    assert test_worker.get_log() != None or test_worker.get_log() != ""

def test_worker_failure():
    def cause_failure():
        raise Exception("Causing test failure")

    test_worker = Worker(
        id=1, task=cause_failure, args=())

    test_worker.start()
    test_worker.join()
    result = test_worker.get_result()
    assert result['result'][0]['status'] == 'FAILED'
    assert test_worker.get_log() != None or test_worker.get_log() != ""

def test_worker_with_repeat_and_timeout():
    def sleep_one_second():
        time.sleep(1)

    test_worker = Worker(
        id=1,
        task=sleep_one_second,
        args=(),
        timeout=10,
        repeat=True
    )

    test_worker.start()
    test_worker.join()
    result = test_worker.get_result()
    assert len(result['result']) >= 9
    assert len(result['result']) <= 11

def test_worker_logging():
    def sleep_one_second():
        time.sleep(1)

    workers = []
    workers.append(
        Worker(
            id=1,
            task=sleep_one_second,
            args=(),
            timeout=5,
            repeat=True
        )
    )
    workers.append(
        Worker(
            id=2,
            task=sleep_one_second,
            args=(),
            timeout=5,
            repeat=True
        )
    )

    for worker in workers:
        worker.start()

    for worker in workers:
        worker.join()

    logs = [w.get_log() for w in workers]
    for log in logs:
        assert log != ""
