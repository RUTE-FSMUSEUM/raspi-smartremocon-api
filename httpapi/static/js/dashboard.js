/* globals Chart:false */

(() => {
    'use strict'

    const temprature = document.getElementById('tempChart');
    const humidity = document.getElementById('humiChart');
    var Charts = initializeCharts(temprature, humidity);
    updateCharts(Charts);

    setInterval(() => {
        updateCharts(Charts);
    }, 10000);

})()

async function updateOverlay(elem_name, data, unit_text) {   
    const chartOverlay = document.getElementById(elem_name);
    
    chartOverlay.innerHTML = '';

    const text = document.createElement('p');
    text.textContent = data.toFixed(1)+unit_text;
    chartOverlay.appendChild(text);
}

async function updateCharts(Charts) {
    await sendHttpRequest();
    const data_cur = await loadJSON('static/logs/current.json');

    Charts.temprature.data.datasets[0].data = [data_cur.temprature + 40, 120 - (data_cur.temprature + 40)];
    updateOverlay('tempChartOverlay', data_cur.temprature, "℃")
    Charts.temprature.update();

    Charts.humidity.data.datasets[0].data = [data_cur.humidity, 100 - data_cur.humidity];
    updateOverlay('humiChartOverlay', data_cur.humidity, "%")
    Charts.humidity.update();

}

function initializeCharts(temprature, humidity) {

    var tempChart = new Chart(temprature, {
        type: 'doughnut',
        data: {
            datasets: [{
              label: 'My First Dataset',
              data: [0, 120],
              backgroundColor: [
                'rgb(224, 83, 94)',
                'rgb(224, 224, 224)'
              ],
              hoverOffset: 4
            }]
          },
        options: {
            responsive: true,
            hover: {mode: null},
            plugins: {
                tooltip: false
            },
            cutout: "85%",
            circumference: 265,
            rotation: 227.5
        }
      });

    var humiChart = new Chart(humidity, {
        type: 'doughnut',
        data: {
            datasets: [{
              label: 'My First Dataset',
              data: [0, 100],
              backgroundColor: [
                'rgb(45, 132, 248)',
                'rgb(224, 224, 224)'
              ],
              hoverOffset: 4
            }]
          },
        options: {
            responsive: true,
            hover: {mode: null},
            plugins: {
                tooltip: false
            },
            cutout: "85%",
            circumference: 265,
            rotation: 227.5
        }
      });

    return {"temprature": tempChart, "humidity": humiChart}
}

// JSONファイルを読み込む関数
async function loadJSON(filePath) {
    try {
        const response = await fetch(filePath);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching the JSON file:', error);
    }
}

function sendHttpRequest() {
    const url = `${window.location.origin}/api?app=runscr&cmd=sensor`;
    fetch(url) // ここに送信するURLを指定
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response; 
        })
        .then(data => {
        })
        .catch(error => {
            console.error('There has been a problem with your fetch operation:', error);
        });
}