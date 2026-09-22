document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts when data is available
    if (window.priceByBrand && window.priceByYear && window.countByFuel && window.priceByFuel) {
        initBrandPriceChart();
        initYearPriceChart();
        initFuelTypeChart();
        initFuelPriceChart();
    }
    
    // Handle chart type toggle
    const chartTypeToggles = document.querySelectorAll('.chart-type-toggle');
    chartTypeToggles.forEach(toggle => {
        toggle.addEventListener('change', function(e) {
            const chartId = e.target.getAttribute('data-chart');
            const chartType = e.target.checked ? 'bar' : 'line';
            
            // Update chart type
            updateChartType(chartId, chartType);
        });
    });
});

// Initialize price by brand chart
function initBrandPriceChart() {
    const chartDom = document.getElementById('brand-price-chart');
    if (!chartDom) return;
    
    const chart = echarts.init(chartDom);
    
    const option = {
        title: {
            text: 'Average Price by Brand',
            left: 'center',
            textStyle: {
                fontWeight: 'normal',
                fontSize: 16
            }
        },
        tooltip: {
            trigger: 'axis',
            formatter: function(params) {
                return params[0].name + '<br />' + 
                       'Average Price: ₹' + params[0].value.toLocaleString('en-IN');
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '10%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: window.priceByBrand.categories,
            axisLabel: {
                rotate: 45,
                interval: 0
            }
        },
        yAxis: {
            type: 'value',
            name: 'Price (₹)',
            axisLabel: {
                formatter: function(value) {
                    return '₹' + (value / 1000) + 'K';
                }
            }
        },
        series: [
            {
                name: 'Average Price',
                type: 'bar',
                data: window.priceByBrand.values,
                itemStyle: {
                    color: '#3b82f6'
                }
            }
        ],
        dataZoom: [
            {
                type: 'inside',
                start: 0,
                end: 100
            },
            {
                start: 0,
                end: 100
            }
        ]
    };
    
    chart.setOption(option);
    window.addEventListener('resize', function() {
        chart.resize();
    });
    
    // Save chart instance
    window.brandPriceChart = chart;
}

// Initialize price by year chart
function initYearPriceChart() {
    const chartDom = document.getElementById('year-price-chart');
    if (!chartDom) return;
    
    const chart = echarts.init(chartDom);
    
    const option = {
        title: {
            text: 'Average Price by Year',
            left: 'center',
            textStyle: {
                fontWeight: 'normal',
                fontSize: 16
            }
        },
        tooltip: {
            trigger: 'axis',
            formatter: function(params) {
                return params[0].name + '<br />' + 
                       'Average Price: ₹' + params[0].value.toLocaleString('en-IN');
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '10%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: window.priceByYear.categories,
            axisLabel: {
                rotate: 0
            }
        },
        yAxis: {
            type: 'value',
            name: 'Price (₹)',
            axisLabel: {
                formatter: function(value) {
                    return '₹' + (value / 1000) + 'K';
                }
            }
        },
        series: [
            {
                name: 'Average Price',
                type: 'line',
                data: window.priceByYear.values,
                symbol: 'circle',
                symbolSize: 8,
                itemStyle: {
                    color: '#10b981'
                },
                lineStyle: {
                    width: 3,
                    color: '#10b981'
                },
                areaStyle: {
                    color: {
                        type: 'linear',
                        x: 0,
                        y: 0,
                        x2: 0,
                        y2: 1,
                        colorStops: [
                            {
                                offset: 0,
                                color: 'rgba(16, 185, 129, 0.3)'
                            },
                            {
                                offset: 1,
                                color: 'rgba(16, 185, 129, 0.05)'
                            }
                        ]
                    }
                }
            }
        ]
    };
    
    chart.setOption(option);
    window.addEventListener('resize', function() {
        chart.resize();
    });
    
    // Save chart instance
    window.yearPriceChart = chart;
}

// Initialize fuel type distribution chart
function initFuelTypeChart() {
    const chartDom = document.getElementById('fuel-type-chart');
    if (!chartDom) return;
    
    const chart = echarts.init(chartDom);
    
    const option = {
        title: {
            text: 'Car Distribution by Fuel Type',
            left: 'center',
            textStyle: {
                fontWeight: 'normal',
                fontSize: 16
            }
        },
        tooltip: {
            trigger: 'item',
            formatter: function(params) {
                return params.name + '<br />' + 
                       'Cars: ' + params.value + ' (' + params.percent + '%)';
            }
        },
        legend: {
            orient: 'horizontal',
            bottom: 'bottom'
        },
        series: [
            {
                name: 'Fuel Type',
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: {
                    borderRadius: 10,
                    borderColor: '#fff',
                    borderWidth: 2
                },
                label: {
                    show: false,
                    position: 'center'
                },
                emphasis: {
                    label: {
                        show: true,
                        fontSize: 16,
                        fontWeight: 'bold'
                    }
                },
                labelLine: {
                    show: false
                },
                data: window.countByFuel.categories.map((category, index) => {
                    return {
                        name: category,
                        value: window.countByFuel.values[index]
                    };
                })
            }
        ]
    };
    
    chart.setOption(option);
    window.addEventListener('resize', function() {
        chart.resize();
    });
    
    // Save chart instance
    window.fuelTypeChart = chart;
}

// Initialize fuel type price chart
function initFuelPriceChart() {
    const chartDom = document.getElementById('fuel-price-chart');
    if (!chartDom) return;
    
    const chart = echarts.init(chartDom);
    
    const option = {
        title: {
            text: 'Average Price by Fuel Type',
            left: 'center',
            textStyle: {
                fontWeight: 'normal',
                fontSize: 16
            }
        },
        tooltip: {
            trigger: 'axis',
            formatter: function(params) {
                return params[0].name + '<br />' + 
                       'Average Price: ₹' + params[0].value.toLocaleString('en-IN');
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '10%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: window.priceByFuel.categories
        },
        yAxis: {
            type: 'value',
            name: 'Price (₹)',
            axisLabel: {
                formatter: function(value) {
                    return '₹' + (value / 1000) + 'K';
                }
            }
        },
        series: [
            {
                name: 'Average Price',
                type: 'bar',
                data: window.priceByFuel.values,
                itemStyle: {
                    color: function(params) {
                        const colors = ['#3b82f6', '#ef4444', '#f59e0b'];
                        return colors[params.dataIndex % colors.length];
                    }
                }
            }
        ]
    };
    
    chart.setOption(option);
    window.addEventListener('resize', function() {
        chart.resize();
    });
    
    // Save chart instance
    window.fuelPriceChart = chart;
}

// Update chart type (bar/line)
function updateChartType(chartId, type) {
    let chart;
    
    switch (chartId) {
        case 'brand-price-chart':
            chart = window.brandPriceChart;
            break;
        case 'year-price-chart':
            chart = window.yearPriceChart;
            break;
        case 'fuel-price-chart':
            chart = window.fuelPriceChart;
            break;
        default:
            return;
    }
    
    if (!chart) return;
    
    const option = chart.getOption();
    
    // Update series type
    option.series[0].type = type;
    
    // If changing to line, add line style
    if (type === 'line') {
        option.series[0].symbol = 'circle';
        option.series[0].symbolSize = 8;
        option.series[0].lineStyle = {
            width: 3,
            color: option.series[0].itemStyle.color
        };
        option.series[0].areaStyle = {
            color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                    {
                        offset: 0,
                        color: 'rgba(59, 130, 246, 0.3)'
                    },
                    {
                        offset: 1,
                        color: 'rgba(59, 130, 246, 0.05)'
                    }
                ]
            }
        };
    } else {
        // Reset line-specific properties if changing to bar
        option.series[0].symbol = 'none';
        option.series[0].symbolSize = 4;
        option.series[0].lineStyle = {};
        option.series[0].areaStyle = undefined;
    }
    
    chart.setOption(option);
}
