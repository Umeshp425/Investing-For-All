

// Load google charts
google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);



var pieChartData = new Array(holdings.length + 1);
pieChartData[0] = ['Symbol', 'Value'];
for(let i = 0; i < holdings.length; i++) {
  pieChartData[i+1] = holdings[i].slice(0,2);
}

// Draw the chart and set the chart values
function drawChart() {
    var data = google.visualization.arrayToDataTable(pieChartData);
    // Optional; add a title and set the width and height of the chart
    var options = {'title':'Breakdown of holdings', 'width':600, 'height':600, 'pieHole':0.4};

    // Display the chart inside the <div> element with id="piechart"
    var chart = new google.visualization.PieChart(document.getElementById('piechart'));
    chart.draw(data, options);
}

function resizeChart () {
    chart.draw(data, options);
}
if (document.addEventListener) {
    window.addEventListener('resize', resizeChart);
}
else if (document.attachEvent) {
    window.attachEvent('onresize', resizeChart);
}
else {
    window.resize = resizeChart;
}