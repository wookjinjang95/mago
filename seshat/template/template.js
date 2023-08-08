const ctx = document.getElementById('myChart');
const ctx2 = document.getElementById('myChart2');
const ctx3 = document.getElementById('myChart3');

      
let chart1 = new Chart(ctx, {
    type: 'bar',
    data: {
    labels: ['Worker_0', 'Worker_1', 'Worker_2', 'Worker_3', 'Worker_4', 'Worker_5', 'Worker_6', 'Worker_7', 'Worker_8', 'Worker_9', 'Worker_10', 'Worker_11', 'Worker_12', 'Worker_13', 'Worker_14', 'Worker_15', 'Worker_16', 'Worker_17', 'Worker_18', 'Worker_19', 'Worker_20', 'Worker_21', 'Worker_22', 'Worker_23', 'Worker_24', 'Worker_25', 'Worker_26', 'Worker_27', 'Worker_28', 'Worker_29'],
    datasets: [{
        label: 'number of Tasks',
        data: [33, 31, 32, 31, 34, 29, 30, 35, 29, 30, 34, 31, 31, 32, 30, 32, 34, 29, 33, 30, 29, 31, 27, 31, 29, 32, 29, 33, 30, 34],
        borderWidth: 1,
        backgroundColor: 'rgb(0, 130, 243)'
    }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        },
        responsive: true
    }
});

var raw_data = [{'x': 0, 'y': 30}, {'x': 1, 'y': 30}, {'x': 2, 'y': 30}, {'x': 3, 'y': 30}, {'x': 4, 'y': 30}, {'x': 5, 'y': 30}, {'x': 6, 'y': 30}, {'x': 7, 'y': 30}, {'x': 8, 'y': 30}, {'x': 9, 'y': 30}, {'x': 10, 'y': 30}, {'x': 11, 'y': 30}, {'x': 12, 'y': 30}, {'x': 13, 'y': 30}, {'x': 14, 'y': 30}, {'x': 15, 'y': 30}, {'x': 16, 'y': 30}, {'x': 17, 'y': 30}, {'x': 18, 'y': 30}, {'x': 19, 'y': 30}, {'x': 20, 'y': 30}, {'x': 21, 'y': 30}, {'x': 22, 'y': 30}, {'x': 23, 'y': 30}, {'x': 24, 'y': 30}, {'x': 25, 'y': 30}, {'x': 26, 'y': 30}, {'x': 27, 'y': 30}, {'x': 28, 'y': 30}, {'x': 29, 'y': 30}, {'x': 30, 'y': 30}, {'x': 31, 'y': 30}, {'x': 32, 'y': 30}, {'x': 33, 'y': 30}, {'x': 34, 'y': 30}, {'x': 35, 'y': 30}, {'x': 36, 'y': 30}, {'x': 37, 'y': 30}, {'x': 38, 'y': 30}, {'x': 39, 'y': 30}, {'x': 40, 'y': 30}, {'x': 41, 'y': 30}, {'x': 42, 'y': 30}, {'x': 43, 'y': 30}, {'x': 44, 'y': 30}, {'x': 45, 'y': 30}, {'x': 46, 'y': 30}, {'x': 47, 'y': 30}, {'x': 48, 'y': 30}, {'x': 49, 'y': 30}, {'x': 50, 'y': 30}, {'x': 51, 'y': 30}, {'x': 52, 'y': 30}, {'x': 53, 'y': 30}, {'x': 54, 'y': 30}, {'x': 55, 'y': 30}, {'x': 56, 'y': 30}, {'x': 57, 'y': 30}, {'x': 58, 'y': 30}, {'x': 59, 'y': 30}, {'x': 60, 'y': 30}, {'x': 61, 'y': 15}]
var x_labels = [];
var y_labels = [];
raw_data.forEach(function (d){
    x_labels.push(d.x);
    y_labels.push(d.y);
});

let chart2 = new Chart(ctx2, {
    type: 'line',
    options: {
        scales: {
            y: {
                min: 0,
                max: Math.max.apply(Math, y_labels) + 4,
            }
        },
        responsive: true
    },
    data: {
        labels: x_labels,
        datasets: [{
            label: 'number of workers',
            data: y_labels,
            borderColor: 'rgb(0, 130, 243)',
            fill: true,
            tension: 0.1
        }]
    }
});

var chart3_x_labels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63];
var chart3_y_labels = [0.0, 1.0, 1.917, 2.211, 2.091, 2.077, 2.143, 1.545, 2.062, 2.067, 1.842, 1.909, 1.889, 2.357, 1.625, 2.125, 1.647, 2.071, 2.071, 1.947, 1.714, 1.889, 1.75, 2.118, 2.077, 1.941, 1.941, 1.929, 2.0, 1.818, 2.235, 1.944, 1.667, 2.143, 2.188, 1.938, 1.875, 2.091, 2.125, 1.944, 1.75, 1.917, 2.2, 2.188, 1.722, 1.714, 2.143, 2.188, 1.765, 2.0, 1.909, 1.8, 1.75, 2.25, 2.071, 1.923, 2.188, 2.053, 1.5, 2.133, 2.071, 2.067, 2.462, 3.0];
let chart3 = new Chart(ctx3, {
    type: 'line',
    options: {
        scales: {
            x: {
                min: 0
            },
            y: {
                min: 0
            }
        },
        responsive: true
    },
    data: {
        labels: x_labels,
        datasets: [{
            label: 'avg response time (s)',
            data: chart3_y_labels,
            borderColor: 'rgb(0, 130, 243)',
            fill: true
        }]
    }
})