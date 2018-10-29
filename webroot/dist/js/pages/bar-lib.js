var config = {
  'COLOR': ['#c23531', '#2f4554', '#61a0a8', '#d48265', '#91c7ae', '#749f83', '#ca8622', '#bda29a', '#6e7074', '#546570', '#c4ccd3'],
  'DOMAIN': '',
  'DEBUG': false,
  'API_SERVER_PATH': 'http://10.178.200.23:8001/tt/'
};

function querystring(search_for) {
  var query = window.location.search.substring(1);
  var parms = query.split('&');
  for (var i = 0; i < parms.length; i++) {
    var pos = parms[i].indexOf('=');
    if (pos > 0 && search_for == parms[i].substring(0, pos)) {
      return parms[i].substring(pos + 1);
    }
  }
  return null;
}

function init_chart(topic, chart, debug) {
  if (querystring('domain') != undefined) {
    config.DOMAIN = querystring('domain');
  } else {
    config.DOMAIN = topic.toLowerCase();
  }

  var filepath = config.API_SERVER_PATH + config.DOMAIN;
  render_chart(filepath, chart);
}

function get_option(dataset) {
  var option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        crossStyle: {
          color: '#999'
        }
      }
    },
    grid: {
      right: '15%'
    },
    // toolbox: {
    //   feature: {
    //     dataView: {
    //       show: true,
    //       readOnly: false
    //     },
    //     restore: {
    //       show: true
    //     },
    //     saveAsImage: {
    //       show: true
    //     }
    //   }
    // },
    legend: {
      data: ['People', 'Connection', 'Post']
    },
    xAxis: [{
      type: 'category',
      axisTick: {
        alignWithLabel: true
      },
      axisLabel: {
        show: true,
        formatter: '{value}'
      },
      data: dataset.month
    }],
    yAxis: [{
        type: 'value',
        name: 'People',
        min: 0,
        //max: 250,
        position: 'right',
        axisLine: {
          lineStyle: {
            color: config.COLOR[0]
          }
        },
        axisLabel: {
          formatter: '{value}'
        }
      },
      {
        type: 'value',
        name: 'Connection',
        min: 0,
        //max: 250,
        position: 'right',
        offset: 80,
        axisLine: {
          lineStyle: {
            color: config.COLOR[1]
          }
        },
        axisLabel: {
          formatter: '{value}'
        }
      },
      {
        type: 'value',
        name: 'Post',
        min: 0,
        //max: 25,
        position: 'left',
        axisLine: {
          lineStyle: {
            color: config.COLOR[2]
          }
        },
        axisLabel: {
          formatter: '{value}'
        }
      }
    ],
    series: [{
        name: 'People',
        type: 'line',
        yAxisIndex: 0,
        data: dataset.nodes
      },
      {
        name: 'Connection',
        type: 'line',
        yAxisIndex: 1,
        data: dataset.links
      },
      {
        name: 'Post',
        type: 'bar',
        yAxisIndex: 2,
        data: dataset.posts
      }
    ]
  };

  if (config.DEBUG) {
    //console.clear();
    console.log(dataset);
    console.log(option);
  }

  return option;
}

function render_chart(filepath, chart) {
  $.get(filepath, function (d, status) {
    if (status === "success" && d != null) {
      var option = get_option(d);
      chart.hideLoading();

      if (option && typeof option === "object") {
        chart.setOption(option, true);
      }
    } else if (status === "success" && d != null && d.state === "exception") {
      alert(d.message);
    }
  });
}