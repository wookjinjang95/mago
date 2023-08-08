from seshat.utils.collector import Collector
from unittest.mock import MagicMock
from seshat.utils.worker import Worker
from datetime import datetime, timedelta

workers = []
def task_test():
    pass

for id in range(10):
    worker = Worker(id=id, task=task_test, args=(), name="Worker {}".format(id))
    worker.get_result = MagicMock(
        return_value={
            "id": id,
            "log": "Worker Log {}".format(id),
            "created": datetime.now(),
            "result": [{
                "start_time": datetime.now(),
                "end_time": datetime.now() + timedelta(seconds=5),
                "duration": 5,
                "value": 5,
                "status": "SUCCESS"
            }]
        }
    )
    workers.append(worker)

def test_workers_result():
    results = Collector.collect_workers_result(workers)
    for id in range(len(results)):
        assert results[id]['id'] == id
        assert results[id]['value'] == 5
        assert results[id]['start_time'] < results[id]['end_time']

def test_collect_total_clients_per_timeline():
    data = Collector.collect_total_clients_per_timeline(workers)
    for i in range(len(data)):
        assert data[i]['x'] == i
        assert data[i]['y'] == 10
        if i < len(data) - 1:
            assert data[i]['x'] < data[i+1]['x']

def test_total_task_finished_per_worker():
    names, results = Collector.collect_total_task_finished_per_worker(workers)
    assert len(names) == len(workers)
    assert len(results) == len(workers)
    for name, tasks, worker in zip(names, results, workers):
        assert name == worker._name
        assert tasks == 1

def test_collect_percentile():
    data = Collector.collect_percentile(workers)
    assert data['99percentile'] > 0
    assert data['999percentile'] > 0
    assert data['9999percentile'] > 0
    assert data['9999percentile'] > 0

def test_collect_pure_log_text():
    data = Collector.collect_pure_log_text(workers)
    assert len(data) == len(workers)
    for log in data:
        assert log != "" or log != None

def test_give_average_durations():
    x_labels, y_labels = Collector.give_average_durations(workers)
    assert len(x_labels) == len(y_labels)
    assert x_labels[0] == 0
    assert x_labels[1] == 5
    assert y_labels[0] == 0
    assert y_labels[1] == 5


    