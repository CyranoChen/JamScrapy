function qs(search_for) {
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

function init_chart_config() {
    THRESHOLD_NODE = 1;
    THRESHOLD_EDGE = 10; // social:0-4, org:0-10-20, comment:100 per time
    THRESHOLD_DEGREE = 0;
    THRESHOLD_SHOW_LABEL = 66; // 2 sigma: 66, 3 sigma: 49
    THRESHOLD_GROUP_BY_FIELD = 'networktype';

    CHART_TYPE = "geo";
    CHART_RANDOM_LOCATION = false;

    CANVAS_WIDTH = 1600;
    CANVAS_HEIGHT = 800;
    CANVAS_BLANK = 150;

    FORCE_EDGELENGTH = 15; // 边的两个节点之间的距离，这个距离也会受 repulsion。支持设置成数组表达边长的范围，此时不同大小的值会线性映射到不同的长度。值越大则长度越长。
    FORCE_REPULSION = 50; // 支持设置成数组表达斥力的范围，此时不同大小的值会线性映射到不同的斥力。值越大则斥力越大。default: 50
    FORCE_GRAVITY = 0.1; // 节点受到的向中心的引力因子。该值越大节点越往中心点靠拢。default: 0.1

    DICT_FIELD = {
        'Geographic': ['networktype', 'boardarea', 'functionalarea', 'costcenter'],
        'Category Burst': ['boardarea', 'functionalarea', 'costcenter'],
        'Force': ['networktype', 'boardarea', 'functionalarea'],
        'Circular': ['networktype', 'boardarea', 'functionalarea', 'region', 'city', 'costcenter']
    };
}

function get_coordinate(category, cate_res, cate_dict, total_count, rand) {
    var x, y = 0;

    if (!rand) {
        var count_curr = 0;
        for (i = 0; i <= cate_res.indexOf(category); i++) {
            count_curr += cate_dict[cate_res[i]];
        }
        var count_prev = count_curr - cate_dict[category];

        var angle_start = count_prev / total_count * 360;
        var angle_end = count_curr / total_count * 360;

        var angle = Math.random() * (angle_end - angle_start) + angle_start;
        var radius = Math.random() * (get_radius(angle, CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2) - CANVAS_BLANK) +
            CANVAS_BLANK;

        x = Math.sin(angle / 360 * 2 * Math.PI) * radius;
        y = Math.cos(angle / 360 * 2 * Math.PI) * radius;

        //console.log(category, angle, get_radius(angle, CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2), radius, x, y);
    } else {
        x = (Math.random() * CANVAS_WIDTH - CANVAS_WIDTH / 2).toFixed(0);
        y = (Math.random() * CANVAS_HEIGHT - CANVAS_HEIGHT / 2).toFixed(0);
    }

    return [x, y];
}

function get_radius(angle, w, h) {
    var max_r = Math.sqrt(Math.pow(w, 2) + Math.pow(h, 2));
    var r = h / Math.abs(Math.cos(angle / 360 * 2 * Math.PI));

    if (r > max_r) {
        r = w / Math.abs(Math.sin(angle / 360 * 2 * Math.PI));
    }

    return r;
}

function get_tooltips(param) {
    var tooltips = [];

    if (param.data.avatar != undefined) {
        tooltips.push(
            '<img src="https://jam4.sapjam.com' +
            param.data.avatar.replace('285', '32') +
            '" width="32" height="32" style="margin-right: 5px" />'
        );
    }

    tooltips.push(
        '<a href="' + param.data.profile +
        '" target="_blank" style="font-weight:bold;color:#E6AC3B">' +
        param.name + '</a>' + ': ' + param.value.toFixed(
            2),
        '<hr size="1"  style="margin: 3px 0" />',
        '<ul>',
        '<li>id: ' + param.data.username + '</li>',
        '<li>mobile: ' + param.data.mobile +
        '</li>',
        '<li>email: ' + param.data.email + '</li>',
        '<li>boardarea: ' + param.data.boardarea +
        '</li>',
        '<li>functionalarea: ' + param.data.functionalarea +
        '</li>',
        '<li>costcenter: ' + param.data.costcenter +
        '</li>',
        '<li>officelocation: ' + param.data.officelocation +
        '</li>',
        '<li>localinfo: ' + param.data.localinfo +
        '</li>'
    );

    if (param.value > 0) {
        tooltips.push('<li>posts: ' + param.data.posts +
            ', comments: ' +
            param.data.comments + ', likes: ' +
            param.data.likes + ', views: ' +
            param.data.views + '</li>',
            '</ul>');
    }

    if (DEBUG) {
        console.log(param);
        tooltips.push(
            '<hr size="1"  style="margin: 3px 0" />'
        );
        tooltips.push('x: ' + param.data.x.toFixed(0),
            ', y: ' + param.data.y.toFixed(0),
            ', category: ' + param.data.category,
            ', index: ' + param.dataIndex);
    }

    return tooltips;
}

function bind_select2(dataset, select2, domain) {
    select2.empty();
    for (var i = 0; i < dataset.nodes.length; i++) {
        select2.append('<option value="' + i + '">[' + dataset.nodes[i].category + '] ' + dataset.nodes[i].name + ' (' + dataset.nodes[i].username + ')</option>');
    }

    select2.val("").select2();
    $("h1#lbl-domain").html("Domain: " + domain + " (" + dataset.nodes.length + ")");
}

function generate_dataset(dataset) {
    // 设置筛选节点(node)
    var nodes = [];
    dataset.nodes.forEach(function (node) {
        if ((node.value >= THRESHOLD_NODE) && (node.networkdegree >=
                THRESHOLD_DEGREE)) {
            nodes.push(node);
        }
    });

    // 设置分类
    var categories = [];
    //var categories_colors = ["#999999", "#A7A250", "#6D9881", "#E6AC3B"];
    var cate_res = [];
    var cate_dict = {};
    /// 统计每个分类的节点数量
    nodes.forEach(function (node) {
        if (node[THRESHOLD_GROUP_BY_FIELD] != null) {
            cate = node[THRESHOLD_GROUP_BY_FIELD];
        } else {
            cate = 'None';
        }
        if (!cate_dict[cate]) {
            cate_res.push(cate);
            cate_dict[cate] = 1;
        } else {
            cate_dict[cate] += 1;
        }
    });

    cate_res.sort();
    cate_res.forEach(function (c) {
        if (c == 'None') {
            categories.push({
                "name": c,
                "itemStyle": {
                    "color": "#999999"
                }
            });
        } else {
            categories.push({
                "name": c
            });
        }
    });

    // 遍历节点，计算分类汇总与坐标
    nodes.forEach(function (node) {
        if (node[THRESHOLD_GROUP_BY_FIELD] != null) {
            node.category = node[THRESHOLD_GROUP_BY_FIELD];
        } else {
            node.category = 'None';
        }

        node.categoryid = cate_res.indexOf(node.category);

        if (CHART_TYPE == "none") {
            coord = get_coordinate(node.category, cate_res, cate_dict, nodes.length,
                CHART_RANDOM_LOCATION);
            node.x = coord[0];
            node.y = coord[1];
        } else if (CHART_TYPE == "geo") {
            // TODO 
            coord = get_coordinate(node.category, cate_res, cate_dict, nodes.length,
                CHART_RANDOM_LOCATION);
            node.x = coord[0];
            node.y = coord[1];
        }

        node.symbolSize = node.value / 5 + 2;
        node.label = {
            normal: {
                show: node.value >= THRESHOLD_SHOW_LABEL
            },
            emphasis: {
                show: true
            }
        };
    });

    // 设置节点排序，仅针对circular
    if (CHART_TYPE == "circular") {
        nodes.sort(function (a, b) {
            return a.categoryid - b.categoryid;
        });
    }

    if (CHART_TYPE == "force") {
        EDGE_WIDTH = 1;
    } else {
        EDGE_WIDTH = 0.3;
    }

    // 设置筛选边(edge)
    var links = [];
    dataset.links.forEach(function (edge) {
        if (edge.weight >= THRESHOLD_EDGE) {
            //console.log(edge.weight, Math.log(edge.weight) + 0.1);
            edge.lineStyle = {
                normal: {
                    //width: Math.min(1, Math.log(edge.weight / 10) + 0.1)
                    width: EDGE_WIDTH
                }
            };
            links.push(edge);
        }
    });

    return {
        "categories": categories,
        "nodes": nodes,
        "links": links
    };
}

function get_option(dataset) {
    if (DEBUG) {
        console.clear();
        console.log(dataset);
    }

    if (CHART_TYPE == "geo") {
        return {
            legend: [{
                type: 'scroll',
                orient: 'vertical',
                left: 5,
                // selectedMode: 'single',
                data: dataset.categories.map(function (c) {
                    return c.name;
                })
            }],
            tooltip: {
                show: true,
                triggerOn: 'click',
                enterable: true
            },
            geo: {
                map: 'world',
                silent: false, //图形是否不响应和触发鼠标事件，默认为 false，即响应和触发鼠标事件。
                itemStyle: {
                    normal: {
                        opacity: 0.5,
                        borderWidth: 0.2,
                        areaColor: '#eee'
                    },
                    emphasis: {
                        opacity: 1,
                        areaColor: '#ddd'
                    }
                },
                roam: false,
                //regions: coldata
            },
            series: [{
                id: 'people',
                type: 'graph',
                layout: 'none',
                force: {
                    //initLayout: 'circular',
                    edgeLength: FORCE_EDGELENGTH,
                    repulsion: FORCE_REPULSION,
                    gravity: FORCE_GRAVITY
                },
                circular: {
                    rotateLabel: true
                },
                draggable: true, // 节点是否可拖拽，只在使用力引导布局的时候有用
                animation: true,
                roam: false, // 是否开启鼠标缩放和平移漫游。默认不开启。如果只想要开启缩放或者平移，可以设置成 'scale' 或者 'move'。设置成 true 为都开启
                focusNodeAdjacency: false, // 节点hover时显示连接节点与边
                label: {
                    normal: {
                        position: 'right',
                        formatter: function (param) {
                            return param.name;
                        }
                    }
                },
                categories: dataset.categories,
                data: dataset.nodes,
                edges: dataset.links,
                lineStyle: {
                    //width: 0.3,
                    color: 'source',
                    curveness: 0.2,
                    opacity: 0.5
                },
                emphasis: {
                    label: {
                        show: true
                    },
                    edgeLabel: {
                        show: true
                    },
                    lineStyle: {
                        width: 2.5,
                        opacity: 0.8
                    }
                },
                tooltip: {
                    formatter: function (param) {
                        if (param.dataType == 'edge') {
                            return param.name + ": " + param.data.weight;
                        } else if (param.dataType == 'node') {
                            return get_tooltips(param).join('');
                        }
                    }
                }
            }]
        };
    } else {
        return {
            legend: [{
                type: 'scroll',
                orient: 'vertical',
                left: 5,
                // selectedMode: 'single',
                data: dataset.categories.map(function (c) {
                    return c.name;
                })
            }],
            tooltip: {
                show: true,
                triggerOn: 'click',
                enterable: true
            },
            series: [{
                id: 'people',
                type: 'graph',
                layout: CHART_TYPE,
                force: {
                    //initLayout: 'circular',
                    edgeLength: FORCE_EDGELENGTH,
                    repulsion: FORCE_REPULSION,
                    gravity: FORCE_GRAVITY
                },
                circular: {
                    rotateLabel: true
                },
                draggable: true, // 节点是否可拖拽，只在使用力引导布局的时候有用
                animation: true,
                roam: false, // 是否开启鼠标缩放和平移漫游。默认不开启。如果只想要开启缩放或者平移，可以设置成 'scale' 或者 'move'。设置成 true 为都开启
                focusNodeAdjacency: false, // 节点hover时显示连接节点与边
                label: {
                    normal: {
                        position: 'right',
                        formatter: function (param) {
                            return param.name;
                        }
                    }
                },
                categories: dataset.categories,
                data: dataset.nodes,
                edges: dataset.links,
                lineStyle: {
                    //width: 0.3,
                    color: 'source',
                    curveness: 0.2,
                    opacity: 0.5
                },
                emphasis: {
                    label: {
                        show: true
                    },
                    edgeLabel: {
                        show: true
                    },
                    lineStyle: {
                        width: 2.5,
                        opacity: 0.8
                    }
                },
                tooltip: {
                    formatter: function (param) {
                        if (param.dataType == 'edge') {
                            return param.name + ": " + param.data.weight;
                        } else if (param.dataType == 'node') {
                            return get_tooltips(param).join('');
                        }
                    }
                }
            }]
        };
    }
}

function render_chart(filepath, chart) {
    $.get(filepath, function (data, status) {
        if (status === "success" && data != null) {
            var ds = generate_dataset(data);
            var option = get_option(ds);
            bind_select2(ds, $("#ddl-search"), DOMAIN_TOPIC);

            chart.hideLoading();

            if (option && typeof option === "object") {
                chart.setOption(option, true);
            }

            $("button#btn-refresh").click(function () {
                var ds = generate_dataset(data);
                var option = get_option(ds);
                bind_select2(ds, $("#ddl-search"), DOMAIN_TOPIC);

                if (option && typeof option === "object") {
                    chart.setOption(option, true);
                }
            });

            $("button#btn-roam").click(function () {
                chart.setOption({
                    series: [{
                        roam: !(chart.getOption().series[0].roam)
                    }]
                }, false);
            });

            $("button#btn-legend").click(function () {
                chart.setOption({
                    legend: [{
                        show: !(chart.getOption().legend[0].show)
                    }]
                }, false);
            });

            $("button#btn-hover").click(function () {
                chart.setOption({
                    series: [{
                        focusNodeAdjacency: !(chart.getOption().series[0].focusNodeAdjacency)
                    }]
                }, false);
            });

            $("button#btn-search-reset").click(function () {
                $("#ddl-search").val("").select2();
                chart.dispatchAction({
                    type: 'unfocusNodeAdjacency',
                    seriesId: 'people'
                });
            });

            $("#ddl-search").change(function () {
                if ($(this).val() != "" && $(this).val() >= 0) {
                    chart.dispatchAction({
                        type: 'focusNodeAdjacency',
                        seriesId: 'people',
                        dataIndex: $(this).val()
                    });
                } else {
                    chart.dispatchAction({
                        type: 'unfocusNodeAdjacency',
                        seriesId: 'people'
                    });
                }
            });

            // DataSet Setting - node
            $("#range-node").ionRangeSlider({
                min: 0,
                max: 100,
                from: 1,
                type: 'single',
                step: 1,
                postfix: '',
                prettify: false,
                hasGrid: true,
                onFinish: function (obj) {
                    THRESHOLD_NODE = obj.fromNumber;

                    var ds = generate_dataset(data);
                    var option = get_option(ds);
                    bind_select2(ds, $("#ddl-search"), DOMAIN_TOPIC);

                    if (option && typeof option === "object") {
                        chart.setOption(option, true);
                    }
                }
            });

            // DataSet Setting - edge
            $("#range-edge").ionRangeSlider({
                min: 0,
                max: 100,
                from: 10,
                type: 'single',
                step: 1,
                postfix: '',
                prettify: false,
                hasGrid: true,
                onFinish: function (obj) {
                    THRESHOLD_EDGE = obj.fromNumber;

                    var ds = generate_dataset(data);
                    var option = get_option(ds);
                    bind_select2(ds, $("#ddl-search"), DOMAIN_TOPIC);

                    if (option && typeof option === "object") {
                        chart.setOption(option, true);
                    }
                }
            });

            // Graphy Setting - layout
            $("select#ddl-layout").change(function () {
                if ($(this).val() !== "") {
                    $(".config-graph div.config").hide();
                    $(".config-graph div.config-" + $(this).val()).show();

                    $groupby = $("select#ddl-groupby");
                    var selected_group = $groupby.val();
                    $groupby.empty();

                    groups = DICT_FIELD[$(this).find("option:selected").text()];
                    if (groups != undefined && groups.length > 0) {
                        $(groups).each(function (i, g) {
                            $groupby.append("<option value=" + g + ">" + g + "</option>");
                        });
                    }

                    if (groups.indexOf(selected_group) >= 0) {
                        $groupby.val(selected_group);
                    } else {
                        $groupby.val($groupby.find("option:first").val());
                    }

                    CHART_TYPE = $(this).val();
                    THRESHOLD_GROUP_BY_FIELD = $groupby.val();

                    var ds = generate_dataset(data);
                    var option = get_option(ds);
                    bind_select2(ds, $("#ddl-search"), DOMAIN_TOPIC);

                    if (option && typeof option === "object") {
                        chart.setOption(option, true);
                    }
                }
            });

            // DataSet Setting - group by
            $("select#ddl-groupby").change(function () {
                if ($(this).val() !== "") {
                    THRESHOLD_GROUP_BY_FIELD = $(this).val();

                    var ds = generate_dataset(data);
                    var option = get_option(ds);
                    bind_select2(ds, $("#ddl-search"), DOMAIN_TOPIC);

                    if (option && typeof option === "object") {
                        chart.setOption(option, true);
                    }
                }
            });
        }
    });
}