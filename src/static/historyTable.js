
var historyGraphData = new Array(historyData.length);
for(let i = 0; i < historyData.length; i++) {
  historyGraphData[i] = historyData[i];
}

function makeChart(period) {
    var end = Math.min(parseInt(period), historyGraphData.length);
    var data = historyGraphData.slice(-end);
    // var ann = data.filter(row => row[2] !== null);
    
    // var annotations_array = ann.map(function(row, index) {
    //     return {
    //         type: 'line',
    //         id: 'vline' + index,
    //         mode: 'vertical',
    //         yMin: 0,
    //         yMax: row[1],
    //         xMin: row[0],
    //         xMax: row[0],
    //         value: row[0],
    //         endValue: row[0],
    //         borderColor: row[2].startsWith('buy') ? 'red' : 'blue',
    //         borderWidth: 2,
    //         label: {
    //             enabled: true,
    //             position: (index%2) ? "25%" : "75%",
    //             content: row[2],
    //             padding: 5
    //         }
    //     }
    // });

    // console.log(annotations_array[0])

    new Chart(document.getElementById(period), {
        type: 'line',
        data: {
            labels: data.map(function(d) {return d[0]}),
            datasets: [{
                data: data.map(function(d) {return d[1]}),
                borderColor: "#3e95cd",
                fill: false
                }
            ]
        },
        options: {
            hover: {
                mode: 'index',
                intersect: true
            },
            plugins: {
                legend: {
                    display:false
                }, 
                title: {
                    display: true,
                    text: 'Historical Value of Portfolio'
                }
            }
        }
      });
}


var periods = ['7','30','91', '182', '365'];

for(let i = 0; i < periods.length; i++) {
    makeChart(periods[i]);
}