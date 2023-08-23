from mago.utils.traffic_manager import TrafficManager
import random, time


def test_traffic_manager_initalization():
    def print_hello_world():
        pass

    tasks = [print_hello_world]
    tasks_args = [()]
    oper_types = ["peak_load"]
    tm = TrafficManager(
        tasks=tasks,
        tasks_args=tasks_args,
        oper_types=oper_types
    )

    assert tm.tasks == tasks
    assert tm.tasks[0].__name__ == "print_hello_world"
    assert tm.total_workers == 10
    assert tm.timeout == 60

def test_peak_load():
    def random_sleep():
        sleep_time = random.randrange(1,3)
        time.sleep(sleep_time)

    tm = TrafficManager(
        tasks=[random_sleep],
        tasks_args=[()],
        oper_types=["peak_load"],
        timeout=10
    )

    assert tm.timeout == 10

    tm.run()
    results = tm.get_run_result()
    
    assert results['random_sleep'] != None

    workers = results['random_sleep']
    assert len(workers) == 10

    unique_id = set()

    for worker in workers:
        assert not worker._id in unique_id
        unique_id.add(worker._id)
        result = worker.get_result()
        assert 'peak_load' in result['id']
        assert result['log'] != None
        assert len(result['result']) >= 2

        for exec_result in result['result']:
            assert exec_result['end_time'] > exec_result['start_time']

def test_incremental_traffic():
    def sleep_three_seconds():
        time.sleep(3)

    tm = TrafficManager(
        tasks=[sleep_three_seconds],
        tasks_args=[()],
        oper_types=["incremental_traffic"]
    )

    tm.run()
    workers = tm.get_run_result()["sleep_three_seconds"]

    assert len(workers) == 55
    unique_id = set()

    for worker in workers:
        assert not worker._id in unique_id
        unique_id.add(worker._id)
        result = worker.get_result()
        assert 'incremental_traffic' in result['id']
        assert result['log'] != None
        assert len(result['result']) == 1
        assert result['created'] != None

        for exec_result in result['result']:
            assert exec_result['end_time'] > exec_result['start_time']

def test_continuous_load():
    def sleep_three_seconds():
        time.sleep(3)

    tm = TrafficManager(
        tasks=[sleep_three_seconds],
        tasks_args=[()],
        oper_types=["continuous_load"],
        timeout=10,
        every_second=1,
        workers_per_iter=3
    )

    tm.run()
    workers = tm.get_run_result()['sleep_three_seconds']
    unique_id = set()

    for worker in workers:
        assert not worker._id in unique_id
        unique_id.add(worker._id)
        result = worker.get_result()
        assert 'continuous_load' in result['id']
        assert result['log'] != None
        assert len(result['result']) == 1
        assert result['created'] != None

        for exec_result in result['result']:
            assert exec_result['end_time'] > exec_result['start_time']
            
def test_two_tasks():
    def sleep_three_seconds():
        time.sleep(3)

    def sleep_two_seconds():
        time.sleep(2)

    tm = TrafficManager(
        tasks=[sleep_two_seconds, sleep_three_seconds],
        tasks_args=[(), ()],
        oper_types=['peak_load', 'peak_load'],
        timeout=15
    )

    tm.run()
    result = tm.get_run_result()
    three_second_workers = result['sleep_three_seconds']
    two_second_workers = result['sleep_two_seconds']

    assert len(three_second_workers) == 10
    assert len(two_second_workers) == 10

def test_two_tasks_with_different_methods():
    def sleep_three_seconds():
        time.sleep(3)

    def sleep_two_seconds():
        time.sleep(2)

    tm = TrafficManager(
        tasks=[sleep_two_seconds, sleep_three_seconds],
        tasks_args=[(), ()],
        oper_types=['peak_load', 'incremental_traffic'],
        timeout=15
    )

    tm.run()
    result = tm.get_run_result()
    assert result['sleep_three_seconds'] != None
    assert result['sleep_two_seconds'] != None





    
    