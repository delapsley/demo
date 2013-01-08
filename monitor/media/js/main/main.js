
var interfaces, interfaces_q;
var ethernet, ethernet_q;
var capture, capture_q;
var stats, stats_q;

function loadTable() {
    interfaces = new google.visualization.Table(document.getElementById('stats_table_div'));
    interfaces_q = new google.visualization.Query('http://127.0.0.1:8000/stats/interface/');
    interfaces_q.send(handleInterfaces);    

    ethernet = new google.visualization.Gauge(document.getElementById('ethernet_div'));
    ethernet_q = new google.visualization.Query('http://127.0.0.1:8000/stats/ethernet/');
    ethernet_q.send(handleEthernet); 

    capture = new google.visualization.Gauge(document.getElementById('capture_div'));
    capture_q = new google.visualization.Query('http://127.0.0.1:8000/stats/capture/');
    capture_q.send(handleCapture);   

    stats = new google.visualization.LineChart(document.getElementById('stats_div'));
    stats_q = new google.visualization.Query('http://127.0.0.1:8000/stats/interface/');
    stats_q.send(handleStats);   
}

function handleInterfaces(response) {
    if (response.isError()) {
        alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
        return;
    }

    interfaces.draw(response.getDataTable(), {width: '800px'});
}

function handleEthernet(response) {
    if (response.isError()) {
        alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
        return;
    }

    var options = {width: 600, height: 150, max: 10, redFrom: 9, redTo: 10,
		   yellowFrom:4, yellowTo: 9, minorTicks: 1};
    ethernet.draw(response.getDataTable(), options);
}

function handleCapture(response) {
    if (response.isError()) {
        alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
        return;
    }

    var options = {width: 150, height: 150, max: 20, redFrom: 19, redTo: 20,
		   yellowFrom:16, yellowTo: 19, minorTicks: 1};
    capture.draw(response.getDataTable(), options);
}

function handleStats(response) {
    if (response.isError()) {
        alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
        return;
    }

    stats.draw(response.getDataTable(), {width: 800, height: 300, legend: 'bottom', pointSize: 4, 
					 hAxis: {title: 'Interface' } });
}


$(document).ready(function() {
    google.setOnLoadCallback(loadTable);
    var refreshId = setInterval(function() {
	    loadTable();
    }, 5000);
});
