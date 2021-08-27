var CompletedTasksFileSizeDiffChart = function () {

    /**
     * Format a byte integer into the smallest possible number appending a suffix
     *
     * @param bytes
     * @param decimals
     * @returns {string}
     */
    var formatBytes = function (bytes, decimals) {
        decimals = (typeof decimals !== 'undefined') ? decimals : 2;
        if (bytes === 0) return '0 Bytes';
        var k = 1024;
        var dm = decimals < 0 ? 0 : decimals;
        var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
        var i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    };

    var positive = '#009fdd';
    var negative = '#C10015';

    var chart_title = '(Select a task from the table below)';
    var source_file_size = 0;
    var destination_file_size = 0;
    var source_total_size = 0;
    var destination_total_size = 0;

    const individualChart = Highcharts.chart('file_size_chart', {
        title: {
            text: ''
        },
        subtitle: {
            text: chart_title
        },
        colors: ['#555555', '#cccccc'],
        xAxis: {
            categories: ['Original', 'New']
        },
        series: []
    });

    const totalChart = Highcharts.chart('total_size_chart', {
        title: {
            text: ''
        },
        subtitle: {
            text: 'Displaying the total file size changed on disk by Unmanic processing files'
        },
        colors: ['#555555', '#cccccc'],
        xAxis: {
            categories: ['Before', 'After']
        },
        series: []
    });


    var updateIndividualChart = function () {
        // If the destination file size is greater than the source, then mark it negative, otherwise positive
        var reduced = true;
        var destination_bar_colour = positive;
        var percent_changed = 100 - (destination_file_size / source_file_size * 100);
        if (destination_file_size >= source_file_size) {
            reduced = false;
            destination_bar_colour = negative;
            percent_changed = 100 - (source_file_size / destination_file_size * 100);
        }
        source_file_size = Number(source_file_size)
        destination_file_size = Number(destination_file_size)

        individualChart.update({
            chart: {
                type: 'bar',
                width: null
            },
            colors: ['#555555', destination_bar_colour],
            title: {
                text: Highcharts.numberFormat(percent_changed, 2) + '% ' + ((reduced) ? 'decrease' : 'increase') + ' in file size'
            },
            subtitle: {
                text: chart_title
            },
            tooltip: {
                formatter: function () {
                    return '<b>' + this.series.name + '</b><br/>' +
                        'File Size: ' + formatBytes(Math.abs(this.point.y));
                }
            },
        });
        let newSeriesData = [
            {
                name: 'New',
                data: [0, destination_file_size]
            },
            {
                name: 'Original',
                data: [source_file_size, 0]
            },
        ]
        for (let i = individualChart.series.length - 1; i >= 0; i--) {
            individualChart.series[i].remove();
        }
        for (let y = newSeriesData.length - 1; y >= 0; y--) {
            individualChart.addSeries(newSeriesData[y]);
        }
    };


    var updateTotalChart = function () {
        // If the destination file size is greater than the source, then mark it negative, otherwise positive
        var reduced = true;
        var destination_bar_colour = positive;
        var percent_changed = 100 - (destination_total_size / source_total_size * 100);
        if (destination_total_size >= source_total_size) {
            reduced = false;
            destination_bar_colour = negative;
            percent_changed = 100 - (source_total_size / destination_total_size * 100);
        }
        source_total_size = Number(source_total_size)
        destination_total_size = Number(destination_total_size)

        totalChart.update({
            chart: {
                type: 'bar',
                width: null
            },
            title: {
                text: Highcharts.numberFormat(percent_changed, 2) + '% ' + ((reduced) ? 'decrease' : 'increase') + ' in total file size'
            },
            colors: ['#555555', destination_bar_colour],
            tooltip: {
                formatter: function () {
                    return '<b>' + this.series.name + '</b><br/>' +
                        'File Size: ' + formatBytes(Math.abs(this.point.y));
                }
            },
        });
        let newSeriesData = [
            {
                name: 'After',
                data: [0, destination_total_size]
            },
            {
                name: 'Before',
                data: [source_total_size, 0]
            },
        ]
        for (let i = totalChart.series.length - 1; i >= 0; i--) {
            totalChart.series[i].remove();
        }
        for (let y = newSeriesData.length - 1; y >= 0; y--) {
            totalChart.addSeries(newSeriesData[y]);
        }
    };

    var fetchConversionDetails = function (taskId) {
        jQuery.get('conversionDetails/?task_id=' + taskId, function (data) {
            // Update/set the conversion details list
            for (let i = 0; i < data.length; i++) {
                let item = data[i];
                if (item.type === 'source') {
                    chart_title = item.basename;
                    source_file_size = Number(item.size);
                } else if (item.type === 'destination') {
                    destination_file_size = Number(item.size);
                }
            }
            updateIndividualChart();

            $('#selected_task_name').html(chart_title)
        });
    };

    var fetchTotalFileSizeDetails = function () {
        jQuery.get('totalSizeChange', function (data) {
            // Update/set the conversion details list
            source_total_size = data.source;
            destination_total_size = data.destination;
            updateTotalChart();
        });
    };

    var watch = function () {
        var selectedTaskId = $('#selected_task_id');
        selectedTaskId.on("change", function () {
            fetchConversionDetails(this.value)
        }).triggerHandler('change');
    }

    return {
        //main function to initiate the module
        init: function () {
            watch();
            fetchTotalFileSizeDetails();
        }
    };

}();

