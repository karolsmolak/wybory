function make_chart(candidates, results) {
    var default_colors = ['#3366CC','#DC3912','#FF9900','#109618','#990099','#3B3EAC','#0099C6','#DD4477','#66AA00','#B82E2E','#316395','#994499','#22AA99','#AAAA11','#6633CC','#E67300','#8B0707','#329262','#5574A6','#3B3EAC'];
    var ctx = document.getElementById('chart').getContext('2d');
    var chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: candidates,
            datasets: [{
                backgroundColor: default_colors,
                borderWidth: 0.8,
                data: results
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function make_map(){
    $('#poland-map').JSMaps({
        map: 'poland',
        stateClickAction:'url',
        hrefTarget: '_self',
        displayAbbreviations: false,
        selectElement: false
    });
}