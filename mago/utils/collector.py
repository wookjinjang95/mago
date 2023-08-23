from .worker import Worker
from collections import defaultdict
import numpy as np


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
                rounded_start_time = round(exec_data['start_time'], 0)
                rounded_end_time = round(exec_data['end_time'], 0)
                count_start_and_end_time[task][rounded_start_time] += 1
                count_start_and_end_time[task][rounded_end_time] -= 1

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

    @staticmethod
    def collect_total_task_finished_per_worker(data: dict[str, list[Worker]]):
        index = 0
        x_labels = []
        y_labels = {}
        indices = defaultdict()

        """
        generate key, value which the key is thread_unique_ID
        #and the value is the index that will point within the list.
        for example, two unique thread ID will have
        {
            "threadID#1": 0,
            "threadID#2": 1
        }
        Here index will also count how many total workers are there.
        """
        for _, each_data in data.items():
            for worker in each_data:
                indices[worker._id] = index
                x_labels.append(worker._id)
                index += 1

        for task, each_data in data.items():
            y_labels[task] = [0 for _ in range(index)]
            for worker in each_data:
                y_labels[task][indices[worker._id]] = worker.get_total_tasks_executed()
        
        return x_labels, Collector.generate_datasets(y_labels)

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
                if not end_time in collected_data[task]:
                    collected_data[task][end_time] = [duration, 1]
                else:
                    collected_data[task][end_time][0] += duration
                    collected_data[task][end_time][1] += 1

        y_labels = {}
        for task in collected_data:
            y_labels[task] = []
            for time in collected_data[task]:
                y_labels[task].append({
                    'x': time,
                    'y': collected_data[task][time][0] / collected_data[task][time][1] 
                })
            y_labels[task].sort(key=lambda d: d['x'])
        
        return str(min_time), Collector.generate_datasets(y_labels)

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
                        worker.get_total_min_duration(),
                        worker.get_total_max_duration(),
                        worker.get_avg_duration(),
                        worker.get_total_timedout()
                    ]
                )
        return datasets
