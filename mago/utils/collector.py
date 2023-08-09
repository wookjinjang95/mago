from .worker import Worker
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np


"""
    TODO: Create the test for Collector
"""
class Collector:
    @staticmethod
    def generate_datasets(y_labels: dict[str, list]):
        datasets = []
        for task, data in y_labels.items():
            temp = {}
            temp['label'] = task
            temp['tension'] = 0.5
            temp['data'] = data
            datasets.append(temp)
        return datasets

    @staticmethod
    def collect_workers_result(data: dict[str, list[Worker]]) -> dict[str, list[dict]]:
        results = defaultdict(list)
        for task, workers in data.items():
            for worker in workers:
                result = worker.get_result()
                for each_exec in result['result']:
                    temp = {}
                    temp.update({
                        "id": result['id']
                    })
                    temp.update(each_exec)
                    results[task].append(temp)
        return results

    @staticmethod
    def collect_total_clients_per_timeline(data: dict[str, list[Worker]], time_increment=1):
        new_data = Collector.collect_workers_result(data)

        count_start_and_end_time = {}

        for task, each_data in new_data.items():
            count_start_and_end_time[task] = defaultdict(int)
            for exec_data in each_data:
                start_time = exec_data['start_time'].strftime("%Y-%m-%d %H:%M:%S")
                end_time = exec_data['end_time'].strftime("%Y-%m-%d %H:%M:%S")
                count_start_and_end_time[task][start_time] += 1
                count_start_and_end_time[task][end_time] -= 1

        y_labels = {}
        for task in count_start_and_end_time:
            y_labels[task] = []
            sorted_time = [*count_start_and_end_time[task]]
            sorted_time.sort()
            total_active_workers = 0

            for time in sorted_time:
                total_active_workers += count_start_and_end_time[task][time]
                y_labels[task].append({
                    'x': time,
                    'y': total_active_workers
                })
            

        return Collector.generate_datasets(y_labels)

    #Counting total task will be depreciated in the worker side to reduce the O(N)
    #operation in the future.
    @staticmethod
    def collect_total_task_finished_per_worker(data: dict[str, list[Worker]]):
        x_labels = set()
        y_labels = defaultdict(list)

        for task, each_data in data.items():
            for worker in each_data:
                x_labels.add(worker._id)
                y_labels[task].append(worker.get_total_tasks_executed())
        
        return list(x_labels), Collector.generate_datasets(y_labels)

    @staticmethod
    def collect_percentile(data: dict[str, list[Worker]]):
        percentile_data_table = []
        for task, workers in data.items():
            duration_data = []
            for worker in workers:
                durations = [e['duration'] for e in worker.get_result()['result']]
                duration_data += durations

            np_array = np.array(duration_data)
            percentile_data_table.append([
                task,
                np.percentile(np_array, 99),
                np.percentile(np_array, 99.9),
                np.percentile(np_array, 99.99),
                np.percentile(np_array, 99.999)
            ])
        return percentile_data_table

    @staticmethod
    def collect_pure_log_text(workers: list[Worker]):
        return [w.get_result()['log'] for w in workers]

    # TODO: This is pretty complicated, we need to break down into simpler terms.
    @staticmethod
    def give_average_durations(data: dict[str, list[Worker]]):
        formatted_data = defaultdict(list)
        min_time = None
        for task, workers in data.items():
            for worker in workers:
                for exec_result in worker.get_result()['result']:
                    formatted_data[task].append([
                        exec_result['end_time'], exec_result['duration']
                    ])
                        
                    if min_time == None:
                        min_time = exec_result['start_time']
                    else:
                        min_time = min(min_time, exec_result['start_time'])

        collected_data = {}

        for task, times in formatted_data.items():
            collected_data[task] = {}
            for end_time, duration in times:
                time = end_time.strftime("%Y-%m-%d %H:%M:%S")

                if not time in collected_data[task]:
                    collected_data[task][time] = [duration, 1]
                else:
                    collected_data[task][time][0] += duration
                    collected_data[task][time][1] += 1

        y_labels = {}
        for task in collected_data:
            y_labels[task] = []
            for time in collected_data[task]:
                y_labels[task].append({
                    'x': time,
                    'y': collected_data[task][time][0] / collected_data[task][time][1] 
                })
            y_labels[task].sort(key=lambda d: d['x'])
        
        return min_time.strftime("%Y-%m-%d %H:%M:%S"), Collector.generate_datasets(y_labels)

    @staticmethod
    def get_task_distributed(data: dict[str, list[Worker]]):
        results = defaultdict(int)
        for task, workers in data.items():
            for worker in workers:
                results[task] += worker.get_total_tasks_executed()
        
        task_distributed_labels = list(results.keys())
        task_distributed_percentage = [
            results[task] for task in task_distributed_labels]

        return task_distributed_labels, task_distributed_percentage

    @staticmethod
    def get_tasks_passed(data: dict[str, list[Worker]]):
        total_passed = defaultdict(int)
        total_executed = defaultdict(int)
        for task, workers in data.items():
            for worker in workers:
                total_passed[task] += worker.get_total_passed()
                total_executed[task] += worker.get_total_tasks_executed()

        tasks_passed_labels = list(data.keys())
        task_passed_data = []
        for task in tasks_passed_labels:
            task_passed_data.append(
                round(total_passed[task]/total_executed[task] * 100, 2))

        return tasks_passed_labels, task_passed_data

    @staticmethod
    def get_average_time_tasks(data: dict[str, list[Worker]]):
        results = defaultdict(list)
        for task, workers in data.items():
            for worker in workers:
                for each_task in worker.get_result()['result']:
                    results[task].append(each_task['duration'])

        polar_area_labels = list(results.keys())
        polar_area_average_data = [
            sum(results[task])/len(results[task]) for task in results]

        return polar_area_labels, polar_area_average_data

    @staticmethod
    def get_pass_fail_percentage(data: dict[str, list[Worker]]):
        datasets = []
        labels = []
        passed_data = []
        failed_data = []
        timedout_data = []
        for task, workers in data.items():
            total_passed = total_failed = total_timedout = 0
            for worker in workers:
                total_passed += worker.get_total_passed()
                total_failed += worker.get_total_failed()
                total_timedout += worker.get_total_timedout()

            passed_data.append(total_passed)
            failed_data.append(total_failed)
            timedout_data.append(total_timedout)

            labels.append(task)

        datasets.append({
            'label': "Passed",
            'data': passed_data,
            'backgroundColor': 'green'
        })

        datasets.append({
            'label': "Failed",
            'data': failed_data,
            'backgroundColor': 'red'
        })

        datasets.append({
            'label': "TimedOut",
            'data': timedout_data,
            'backgroundColor': 'yellow'
        })

        return labels, datasets

    @staticmethod
    def collect_log_data(data: dict[str, list[Worker]]):
        datasets = []
        for task, workers in data.items():
            for worker in workers:
                datasets.append(
                    [
                        worker._id,
                        task,
                        worker.get_total_tasks_executed(),
                        worker.get_total_passed(),
                        worker.get_total_failed(),
                        worker.get_total_timedout()
                    ]
                )
        return datasets




            
                
                



