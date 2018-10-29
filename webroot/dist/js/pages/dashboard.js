// function bind_button(chart) {
//   $("#pnl-brand").css("top", (window.innerHeight - $("#pnl-brand").height()) / 2.5).fadeIn(3000);

//   $("#pnl-brand button").click(function () {
//     chart.setOption({
//       series: [{
//         layout: (chart.getOption().series[0].layout == "force" ? "circular" : "force")
//       }]
//     }, false);
//   });
// }

$(function () {
    $("#pnl-kpi .info-box").hover(function () {
        $(this).toggleClass("bg-info").find("span.info-box-icon").toggleClass("hide");
        $(this).find(".info-box-number").toggleClass("hide");
    });

    render_charts();
});

function render_charts() {
    var chart_r = echarts.init(document.getElementById("container-radar"));
    chart_r.showLoading();
    render_radar_chart(chart_r);

    var chart_p = echarts.init(document.getElementById("container-pattern"));
    chart_p.showLoading();
    render_pattern_chart(chart_p);

    var chart_g = echarts.init(document.getElementById("container-cross-group"));
    chart_g.showLoading();
    render_graph_chart(chart_g);

    var chart_h = echarts.init(document.getElementById("container-heatmap"));
    chart_h.showLoading();
    render_heatmap_chart(chart_h);
}

function render_radar_chart(chart) {
    $.get("../data/dataset-cross-group.json", function (dataset, status) {
        if (status === "success" && dataset != null) {
            var option = {
                tooltip: {},
                legend: {
                    orient: "vertical",
                    x: "left",
                    data: ['预算分配（Allocated Budget）', '实际开销（Actual Spending）']
                },
                radar: {
                    //shape: 'circle',
                    name: {
                        textStyle: {
                            color: '#fff',
                            backgroundColor: '#999',
                            borderRadius: 3,
                            padding: [3, 5]
                        }
                    },
                    indicator: [{
                            name: '销售（sales）',
                            max: 6500
                        },
                        {
                            name: '管理（Administration）',
                            max: 16000
                        },
                        {
                            name: '信息技术（Information Techology）',
                            max: 30000
                        },
                        {
                            name: '客服（Customer Support）',
                            max: 38000
                        },
                        {
                            name: '研发（Development）',
                            max: 52000
                        },
                        {
                            name: '市场（Marketing）',
                            max: 25000
                        }
                    ]
                },
                series: [{
                    name: '预算 vs 开销（Budget vs spending）',
                    type: 'radar',
                    // areaStyle: {normal: {}},
                    data: [{
                            value: [4300, 10000, 28000, 35000, 50000, 19000],
                            name: '预算分配（Allocated Budget）'
                        },
                        {
                            value: [5000, 14000, 28000, 31000, 42000, 21000],
                            name: '实际开销（Actual Spending）'
                        }
                    ]
                }]
            };

            if (option && typeof option === "object") {
                chart.hideLoading();
                chart.setOption(option, true);
            }
        }
    });
}

function createNodes(count) {
    var nodes = [];
    for (var i = 0; i < count; i++) {
        nodes.push({
            id: i
        });
    }
    return nodes;
}

function createEdges(count) {
    var edges = [];
    if (count === 2) {
        return [
            [0, 1]
        ];
    }
    for (var i = 0; i < count; i++) {
        edges.push([i, (i + 1) % count]);
    }
    return edges;
}

function render_pattern_chart(chart) {
    $.get("../data/dataset-cross-group.json", function (dataset, status) {
        if (status === "success" && dataset != null) {
            var datas = [];
            for (var i = 0; i < 4; i++) {
                datas.push({
                    nodes: createNodes(i + 2),
                    edges: createEdges(i + 2)
                });
            }

            console.log(datas);

            var option = {
                series: datas.map(function (item, idx) {
                    return {
                        type: 'graph',
                        layout: 'force',
                        animation: true,
                        data: item.nodes,
                        left: (idx % 4) * 25 + '%',
                        //top: Math.floor(idx / 4) * 25 + '%',
                        width: '25%',
                        height: '25%',
                        force: {
                            // initLayout: 'circular'
                            // gravity: 0
                            repulsion: 100,
                            edgeLength: 80
                        },
                        edges: item.edges.map(function (e) {
                            return {
                                source: e[0],
                                target: e[1]
                            };
                        })
                    };
                })
            };

            if (option && typeof option === "object") {
                chart.hideLoading();
                chart.setOption(option, true);
            }
        }
    });
}

function render_heatmap_chart(chart) {
    $.get("../data/dataset-cross-group.json", function (dataset, status) {
        if (status === "success" && dataset != null) {
            var x = [];
            var y = [];
            var weights = {};
            var data = [];

            dataset.nodes.forEach(function (node) {
                x.push(node.name);
                y.push(node.name);
            });

            dataset.links.forEach(function (link) {
                weights[[link.source, '>', link.target].join('')] = link.weight;
            });

            $.each(x, function (i, v_x) {
                $.each(y, function (j, v_y) {
                    var key = [v_x, '>', v_y].join('');
                    if (weights.hasOwnProperty(key)) {
                        data.push([i, j, weights[key]]);
                    } else {
                        data.push([i, j, "-"]);
                    }
                });
            });

            console.log(data);

            var option = {
                tooltip: {
                    position: 'bottom'
                },
                animation: true,
                grid: {},
                xAxis: {
                    type: 'category',
                    data: x,
                    splitArea: {
                        show: true
                    }
                },
                yAxis: {
                    type: 'category',
                    data: y,
                    splitArea: {
                        show: true
                    }
                },
                visualMap: {
                    min: 0,
                    max: 10,
                    calculable: true,
                    orient: 'vertical',
                    left: 'right',
                },
                series: [{
                    name: 'Punch Card',
                    type: 'heatmap',
                    data: data,
                    label: {
                        normal: {
                            show: true
                        }
                    },
                    itemStyle: {
                        emphasis: {
                            shadowBlur: 10,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }]
            };

            if (option && typeof option === "object") {
                chart.hideLoading();
                chart.setOption(option, true);
            }
        }
    });
}

function render_graph_chart(chart) {
    $.get("../data/dataset-cross-group.json", function (dataset, status) {
        if (status === "success" && dataset != null) {
            dataset.nodes.forEach(function (node) {
                node.symbolSize = node.value * 10;
            });

            dataset.links.forEach(function (edge) {
                edge.lineStyle = {
                    normal: {
                        width: edge.weight * 2.5,
                    }
                };
            });

            // dataset.nodes.sort(function (a, b) {
            //   return a.categoryid - b.categoryid;
            // });

            console.log(dataset);

            var option = {
                legend: {
                    show: true,
                },
                tooltip: {
                    show: true,
                    triggerOn: 'click',
                    enterable: true
                },
                series: [{
                    id: 'group',
                    type: 'graph',
                    layout: 'none',
                    zlevel: 100,
                    force: {
                        initLayout: 'circular',
                        edgeLength: 250, // 边的两个节点之间的距离，这个距离也会受 repulsion。支持设置成数组表达边长的范围，此时不同大小的值会线性映射到不同的长度。值越大则长度越长。
                        repulsion: 500, // 支持设置成数组表达斥力的范围，此时不同大小的值会线性映射到不同的斥力。值越大则斥力越大。default: 50
                        gravity: 0.15 //节点受到的向中心的引力因子。该值越大节点越往中心点靠拢。default: 0.1
                    },
                    circular: {
                        rotateLabel: true
                    },
                    // width: 1600,
                    // height: 800,
                    draggable: true, // 节点是否可拖拽，只在使用力引导布局的时候有用
                    animation: true,
                    roam: false, // 是否开启鼠标缩放和平移漫游。默认不开启。如果只想要开启缩放或者平移，可以设置成 'scale' 或者 'move'。设置成 true 为都开启
                    focusNodeAdjacency: true, // 节点hover时显示连接节点与边
                    silent: false,
                    label: {
                        normal: {
                            show: true
                        }
                    },
                    categories: dataset.categories,
                    data: dataset.nodes,
                    edges: dataset.links,
                    lineStyle: {
                        color: 'source',
                        opacity: 0.5,
                        curveness: 0.5
                    },
                    tooltip: {
                        formatter: function (param) {
                            console.log(param)
                            return param;
                        }
                    }
                }]
            };

            if (option && typeof option === "object") {
                chart.hideLoading();
                chart.setOption(option, true);
            }
        }
    });
}