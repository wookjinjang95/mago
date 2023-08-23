from mago.utils.collector import Collector
from unittest.mock import MagicMock
from mago.utils.worker import Worker
from datetime import datetime, timedelta
import time

def task_test():
    pass

test_data = {task_test.__name__: []}
timer = datetime.now()

for id in range(10):
    worker = Worker(id=id, task=task_test, args=())
    worker.get_result = MagicMock(
        return_value={
            "id": id,
            "log": "Worker Log {}".format(id),
            "created": datetime.now().timestamp(),
            "result": [{
                "start_time": timer.timestamp(),
                "end_time": (timer + timedelta(seconds=5)).timestamp(),
                "duration": 5,
                "value": 5,
                "status": "SUCCESS"
            }]
        }
    )
    worker.get_total_tasks_executed = MagicMock(
        return_value=1
    )
    timer += timedelta(seconds=1)
    test_data[task_test.__name__].append(worker)

def test_workers_result():
    results = Collector.collect_workers_result(test_data)
    assert task_test.__name__ in results
    assert len(results[task_test.__name__]) == 10
    for id in range(len(results[task_test.__name__])):
        each = results[task_test.__name__][id]
        assert each['start_time'] < each['end_time']
        assert each['duration'] == 5
        assert each['value'] == 5
        assert each['status'] == "SUCCESS"
        assert each['id'] == id

def test_collect_total_clients_per_timeline():
    results = Collector.collect_total_clients_per_timeline(test_data)
    assert len(results) == 1
    assert len(results[0]) > 1
    for each in results:
        assert each['label'] == task_test.__name__
        assert each['tension'] == 0.5
        assert len(each['data']) > 0
        for each_data in each['data']:
            assert 'x' in each_data
            assert 'y' in each_data

def test_total_task_finished_per_worker():
    x_labels, y_labels = Collector.collect_total_task_finished_per_worker(test_data)
    assert len(x_labels)
    assert len(y_labels) == 1
    for each in y_labels:
        assert each['label'] == task_test.__name__
        assert each['tension'] == 0.5
        assert len(each['data']) > 0
        for each_data in each['data']:
            assert each_data == 1
    
def test_collect_percentile():
    results = Collector.collect_percentile(test_data)
    assert len(results) == 1
    for each in results:
        assert len(each) == 5
        assert each[0] == task_test.__name__
        assert each[1] > 0
        assert each[2] > 0
        assert each[3] > 0
        assert each[4] > 0

def test_give_average_durations():
    min_time, y_labels = Collector.give_average_durations(test_data)
    assert type(min_time) == str
    assert len(y_labels) == 1
    for each in y_labels:
        assert each['label'] == task_test.__name__
        assert each['tension'] == 0.5
        assert len(each['data']) > 0
        for each_data in each['data']:
            assert 'x' in each_data
            assert 'y' in each_data


    