from seshat.utils.worker import Worker
from datetime import datetime, timedelta
import time
import pytest


@pytest.mark.parametrize("func, data, expect", [
    (sum, [1,2,3,4], 10)])
def test_worker_get_result(func, data, expect):
    test_worker = Worker(id=1, name='Test 2', task=func, args=(data, ))
    test_worker.start()
    test_worker.join()
    result = test_worker.get_result()
    assert result['log'] != None
    assert result['id'] == 1
    assert type(result['result']) == list
    assert len(result['result']) >= 1
    assert result['result'][0]['value'] == expect
    assert result['result'][0]['status'] == "SUCCESS"
    assert result['result'][0]['start_time'] != None
    assert result['result'][0]['end_time'] != None
    assert result['result'][0]['end_time'] > result['result'][0]['start_time']

def test_worker_functions():
    def time_sleep():
        time.sleep(3)

    test_worker = Worker(
        id=1, name='Functional Test', task=time_sleep, args=())

    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=3)
    assert test_worker._get_execution_time(start_time, end_time) >= 3 

def test_worker_timeout():
    def time_sleep():
        time.sleep(5)
    
    test_worker = Worker(
        id=1, name='Timeout Test', task=time_sleep, args=(), timeout=2
    )
    test_worker.start()
    test_worker.join()
    result = test_worker.get_result()
    assert result['result'][0]['status'] == "FAILED DUE TO TIMEOUT"

def test_worker_failure():
    def cause_failure():
        raise Exception("Causing test failure")

    test_worker = Worker(
        id=1, name='Cause Fail Test', task=cause_failure, args=())

    test_worker.start()
    test_worker.join()
    result = test_worker.get_result()
    assert result['result'][0]['status'] == 'FAILED'

def test_worker_with_repeat_with_timeout():
    def sleep_one_second():
        time.sleep(1)

    test_worker = Worker(
        id=1,
        name='Repeat Worker Test',
        task=sleep_one_second,
        args=(),
        timeout=10,
        repeat=True)

    test_worker.start()
    test_worker.join()
    result = test_worker.get_result()
    assert len(result['result']) >= 9
    assert len(result['result']) <= 11

