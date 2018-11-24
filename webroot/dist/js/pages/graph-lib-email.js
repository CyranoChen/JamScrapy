var config = {
    'COLOR': ['#c23531', '#2f4554', '#61a0a8', '#d48265', '#91c7ae', '#749f83', '#ca8622', '#bda29a', '#6e7074', '#546570', '#c4ccd3'],
    'THRESHOLD_SHOW_LABEL': 75, // 2 sigma: 66, 3 sigma: 49
    'THRESHOLD_COMMUNITY_SIZE': 5,
    'THRESHOLD_COMMUNITY_MAX_SIZE': 30,
    'MODE_SHOW_LABEL': 0,
    'THRESHOLD_NODE': 66,
    'THRESHOLD_EDGE': 20,
    'THRESHOLD_DEGREE': 0,
    'CHART_TYPE': 'force',
    'GROUP_BY_FIELD': 'networktype',
    'HIDDEN_LEGEND': {},
    'CANVAS_WIDTH': 1600,
    'CANVAS_HEIGHT': 800,
    'CANVAS_BLANK': 150,
    'CHART_FIX_LOCATION': false,
    'DICT': {
        'TYPE': ['n', 'f', 'c'],
        'FIELD': {
            // 'Geographic': ['networktype', 'boardarea', 'functionalarea', 'region', 'city', 'costcenter', 'gender'],
            'Category Burst': ['networktype'],
            'Force': ['networktype', 'community'],
            'Circular': ['networktype']
        },
        'GEO_CITY': {},
        'GEO_CITY_DATA': {}
    },
    'DATA_SOURCE': {},
    'DATA_SOURCE_META': {},
    'DATA_SOURCE_FILE': '',
    'DATA_TIMESTAMP': null,
    'DOMAIN': '',
    'DEBUG': false,
    'API_SERVER_PATH': 'http://10.58.78.253:8001/api/',
    'CACHE': true
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
    if (querystring('debug') != undefined && querystring('debug').toLowerCase() == "true") {
        config.DEBUG = true;
    } else {
        if (debug != undefined) {
            config.DEBUG = debug;
        }
    }

    // nonsensitive
    if (!config.DEBUG) {
        $("#ddl-search").hide();
        $("#btn-search-reset").hide();
        $("#btn-download").hide();
        $("#btn-label").hide();
    }

    $("#panel-config .config-graph div.config").hide();
    $("#panel-config .config-graph div.config-" + config.CHART_TYPE.substring(0, 1)).show();

    if (querystring('domain') != undefined) {
        config.DOMAIN = querystring('domain');
    } else {
        config.DOMAIN = topic.toLowerCase();
    }

    if (querystring('cache') != undefined && querystring('cache').toLowerCase() == "true") {
        config.CACHE = true;
    }

    if (querystring('node') != undefined && !isNaN(parseInt(querystring('node')))) {
        if (parseInt(querystring('node')) >= 0) {
            config.THRESHOLD_NODE = 100 - Math.min(100, parseInt(querystring('node')));
        }
    }

    if (querystring('edge') != undefined && !isNaN(parseInt(querystring('edge')))) {
        if (parseInt(querystring('edge')) >= 0) {
            config.THRESHOLD_EDGE = 100 - Math.min(100, parseInt(querystring('edge')));
        }
    }

    if (querystring('label') != undefined && !isNaN(parseInt(querystring('label')))) {
        if (parseInt(querystring('label')) >= 0) {
            config.MODE_SHOW_LABEL = parseInt(querystring('label'));
        }
    }

    if (querystring('type') != undefined && config.DICT.TYPE.indexOf(querystring('type').toLowerCase()) >= 0) {
        switch (querystring('type').toLowerCase()) {
            case 'g':
                config.CHART_TYPE = 'geo';
                break;
            case 'n':
                config.CHART_TYPE = 'none';
                break;
            case 'f':
                config.CHART_TYPE = 'force';
                break;
            case 'c':
                config.CHART_TYPE = 'circular';
                break;
        }
    }

    if (querystring('group') != undefined) {
        var groups = config.DICT.FIELD[$("select#ddl-layout").find("option[value='" + config.CHART_TYPE + "']").text()];
        if (groups != undefined && groups.indexOf(querystring('group').toLowerCase()) >= 0) {
            // 根据当前layout可能的group方式获取
            config.GROUP_BY_FIELD = querystring('group').toLowerCase();
        }
    }

    if (querystring('date') != undefined && querystring('date') !== '') {
        config.DATA_TIMESTAMP = querystring('date');
        //$("#panel-config #tb-timestamp").val(config.DATA_TIMESTAMP);
    }

    if (querystring('nocates') != undefined) {
        var arr = querystring('nocates').split(',');
        if (arr.length > 0) {
            for (var i in arr) {
                var cate = decodeURIComponent(arr[i]);
                config.HIDDEN_LEGEND[cate] = false;
            }
        }
    }

    $.when($.getJSON("../data/map-city-geo.json"), $.getJSON("../data/cache-meta-data.json"))
        .done(function (map, meta) {
            if (map[1] === "success" && meta[1] === "success") {
                config.DICT.GEO_CITY = map[0].coord;
                config.DATA_SOURCE_META = meta[0];

                var filepath = config.API_SERVER_PATH + config.DOMAIN;
                if (config.DATA_TIMESTAMP != null) {
                    filepath += ("?date=" + config.DATA_TIMESTAMP);
                } else {
                    config.DATA_TIMESTAMP = config.DATA_SOURCE_META[config.DOMAIN].jam_posts_end_date;
                }

                // for local version to visualize the json data source
                if (config.CACHE) {
                    //filepath = "../data/dataset-" + config.DOMAIN + "-" + meta[0][config.DOMAIN].jam_posts_end_recency.toString() + ".json";
                    filepath = "../data/external-people-email.json";
                    config.DATA_SOURCE_FILE = filepath;
                }

                if (config.DEBUG) {
                    console.log(filepath);
                    console.log(config);
                }

                render_chart(filepath, chart);
                bind_buttons(chart);

                // DataSet Setting - calendar
                // $("#panel-config #tb-timestamp").datepicker({
                //     autoclose: true,
                //     format: "yyyy-mm-dd",
                //     startDate: config.DATA_SOURCE_META[config.DOMAIN].jam_posts_start_date,
                //     endDate: config.DATA_SOURCE_META[config.DOMAIN].jam_posts_end_date,
                //     orientation: "bottom left",
                //     todayHighlight: true
                // }).val(config.DATA_TIMESTAMP).change(function () {
                //     var filepath = config.API_SERVER_PATH + config.DOMAIN;

                //     if ($(this).val() !== "") {
                //         config.DATA_TIMESTAMP = $(this).val();
                //     } else {
                //         config.DATA_TIMESTAMP = null;
                //     }

                //     if (config.DATA_TIMESTAMP != null) {
                //         filepath += ("?date=" + config.DATA_TIMESTAMP);
                //     }

                //     chart.showLoading();
                //     render_chart(filepath, chart);
                //     //bind_buttons(chart);
                // });
            } else {
                alert("initial configuration error");
            }
        });
}

function get_cate_coordinate(category, cate_res, cate_dict, total_count, rand) {
    var x = 0;
    var y = 0;

    if (!rand) {
        var count_curr = 0;
        for (i = 0; i <= cate_res.indexOf(category); i++) {
            count_curr += cate_dict[cate_res[i]];
        }
        var count_prev = count_curr - cate_dict[category];

        var angle_start = count_prev / total_count * 360;
        var angle_end = count_curr / total_count * 360;

        var angle = Math.random() * (angle_end - angle_start) + angle_start;
        var radius = Math.random() * (get_radius(angle, config.CANVAS_WIDTH / 2, config.CANVAS_HEIGHT / 2) - config.CANVAS_BLANK) +
            config.CANVAS_BLANK;

        x = Math.sin(angle / 360 * 2 * Math.PI) * radius;
        y = Math.cos(angle / 360 * 2 * Math.PI) * radius;

        //console.log(category, angle, get_radius(angle, config.CANVAS_WIDTH / 2, config.CANVAS_HEIGHT / 2), radius, x, y);
    } else {
        x = (Math.random() * config.CANVAS_WIDTH - config.CANVAS_WIDTH / 2).toFixed(0);
        y = (Math.random() * config.CANVAS_HEIGHT - config.CANVAS_HEIGHT / 2).toFixed(0);
    }

    return [x, y];
}

function get_geo_coordinate(x_radius, y_radius) {
    var x = 0;
    var y = 0;

    var angle = Math.random() * 360;
    var radius = [Math.random() * (x_radius - 2) + 2, Math.random() * (y_radius - 1.5) + 1.5];

    x = Math.sin(angle / 360 * 2 * Math.PI) * radius[0];
    y = Math.cos(angle / 360 * 2 * Math.PI) * radius[1];

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

function convert_geo_data(nodes) {
    var res = JSON.parse(JSON.stringify(nodes));
    config.DATA_SOURCE.GEO_CITY = {};

    res.forEach(function (node) {
        node.symbolSize = node.value / 10 + 1;
        node.label = {
            normal: {
                show: false
            },
            emphasis: {
                show: config.DEBUG
            }
        };

        var coord = config.DICT.GEO_CITY[node.city];
        if (coord) {
            node.x = coord[0];
            node.y = coord[1];
            node.value = [node.x, node.y, node.value];

            // 记录存在的城市列表与所属节点数量
            if (config.DATA_SOURCE.GEO_CITY.hasOwnProperty(node.city)) {
                config.DATA_SOURCE.GEO_CITY[node.city] += 1;
            } else {
                config.DATA_SOURCE.GEO_CITY[node.city] = 1;
            }
        } else {
            console.log(node); // 记录没有找到城市的节点
            node.x = -160;
            node.y = 80;
            node.value = [node.x, node.y, node.value];
        }
    });

    //console.log(config.DATA_SOURCE.GEO_CITY);

    // 对节点位置的随机偏移
    res.forEach(function (node) {
        if (config.DATA_SOURCE.GEO_CITY[node.city] > 1) {
            var rate = Math.max(8, config.DATA_SOURCE.GEO_CITY[node.city] / 10);

            if (node.city == 'None') {
                rate *= 5;
            }

            var offset = get_geo_coordinate(rate * 0.5, rate * 0.3);
            node.x += offset[0];
            node.y += offset[1];
            node.value[0] = node.x;
            node.value[1] = node.y;
        }
    });

    return res;
}

function make_city_map(rawData) {
    var res = [];

    for (var city in rawData) {
        var coord = config.DICT.GEO_CITY[city];
        if (coord) {
            res.push({
                name: city,
                //value: coord.concat(city.slice(1))
                value: coord
            });
        } else {
            console.log(city);
        }
    }

    //console.log(res);
    return res;
}

function get_tooltips(param) {
    var tooltips = [];
    var value = -1;

    if (param.value.length > 0) {
        value = param.value[param.value.length - 1];
    } else {
        value = param.value;
    }

    if (value >= 0) {
        if (param.data.avatar != undefined && config.DEBUG) {
            tooltips.push(
                '<img src="https://jam4.sapjam.com' +
                param.data.avatar.replace('285', '32') +
                '" width="32" height="32" style="margin-right: 5px" />'
            );
        }

        if (config.DEBUG) {
            tooltips.push(
                '<a href="' + param.data.profile +
                '" target="_blank" style="font-weight:bold;color:#E6AC3B">' +
                param.data.displayname + '</a>' + ': ' + value.toFixed(2),
                '<hr size="1"  style="margin: 3px 0" />',
                '<ul>'
                // '<li>id: ' + param.data.username + '</li>',
                // '<li>gender: ' + param.data.gender + '</li>',
                // '<li>mobile: ' + param.data.mobile + '</li>',
                // '<li>email: ' + param.data.email + '</li>'
            );
        } else {
            tooltips.push('<a><i class="fa fa-user"></i> People Description</a>',
                '<hr size="1"  style="margin: 3px 0" />', '<ul>');
        }

        // tooltips.push(
        //     '<li>boardarea: ' + param.data.boardarea +
        //     '</li>',
        //     '<li>functionalarea: ' + param.data.functionalarea +
        //     '</li>',
        //     '<li>costcenter: ' + param.data.costcenter +
        //     '</li>',
        //     '<li>officelocation: ' + param.data.officelocation +
        //     '</li>',
        //     '<li>localinfo: ' + param.data.localinfo +
        //     '</li>'
        // );

        tooltips.push('<li>email count: ' + param.data.posts +
            ', subject words: ' +
            param.data.comments + '</li>');

        tooltips.push('<li>degree: ' + param.data.degree +
            ', closeness: ' +
            param.data.closeness + ', betweenness: ' +
            param.data.betweenness + '</li>',
            '</ul>');

        if (config.DEBUG) {
            console.log(param);
            tooltips.push(
                '<hr size="1"  style="margin: 3px 0" />'
            );

            tooltips.push('category: ' + param.data.category,
                ', index: ' + param.dataIndex,
                ', community: ' + param.data.community);
        }
    }

    return tooltips;
}

function bind_select2(dataset, select2, domain) {
    if (config.DEBUG) {
        select2.empty();
        for (var i = 0; i < dataset.nodes.length; i++) {
            select2.append('<option value="' + i + '">[' + dataset.nodes[i].category + '] ' + dataset.nodes[i].displayname + ' (' + dataset.nodes[i].username + ')</option>');
        }

        select2.val("").select2();
    } else {
        select2.hide();
    }

    $("h1#lbl-domain").html("Domain: " + domain + " (" + dataset.nodes.length + ")");
}

function generate_dataset(dataset) {
    // 设置筛选节点(node)
    var nodes = [];
    dataset.nodes.forEach(function (node) {
        if (node.value >= config.THRESHOLD_NODE) {
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
        if (node[config.GROUP_BY_FIELD] != undefined && node[config.GROUP_BY_FIELD] != null) {
            cate = node[config.GROUP_BY_FIELD].toString();
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
        if (c == 'None' || c == 'Isolates' || c == 'Soloists') {
            categories.push({
                "name": c,
                "itemStyle": {
                    "color": "#999"
                }
            });
        } else {
            categories.push({
                "name": c
            });
        }
    });

    var community_size_dict = {};
    // 遍历节点，计算分类汇总与坐标
    nodes.forEach(function (node) {
        if (node[config.GROUP_BY_FIELD] != null) {
            node.category = node[config.GROUP_BY_FIELD];
        } else {
            node.category = 'None';
        }

        node.categoryid = cate_res.indexOf(node.category);

        if (!config.CHART_FIX_LOCATION) {
            if (config.CHART_TYPE == "none") {
                coord = get_cate_coordinate(node.category, cate_res, cate_dict, nodes.length, false);
                node.x = coord[0];
                node.y = coord[1];
            }
        }

        node.symbolSize = node.value / 6 + 1;

        if (config.MODE_SHOW_LABEL === 2) {
            node.label = {
                normal: {
                    show: node.value >= config.THRESHOLD_SHOW_LABEL
                },
                emphasis: {
                    show: config.DEBUG
                }
            };
        } else {
            node.label = {
                normal: {
                    show: Boolean(config.MODE_SHOW_LABEL)
                },
                emphasis: {
                    show: config.DEBUG
                }
            };
        }

        if (config.CHART_TYPE == "force" && config.GROUP_BY_FIELD == "community" &&
            node.community != undefined && node.community_size != undefined) {
            community_size_dict[node.community] = node.community_size;
            if (node.community_size > config.THRESHOLD_COMMUNITY_MAX_SIZE) {
                config.THRESHOLD_COMMUNITY_MAX_SIZE = node.community_size;
            }
        }
    });

    // 设置图例隐藏策略，仅针对force, community
    if (config.CHART_TYPE == "force" && config.GROUP_BY_FIELD == "community") {
        console.log(community_size_dict);

        $.each(community_size_dict, function (k, v) {
            if (v < config.THRESHOLD_COMMUNITY_SIZE) {
                config.HIDDEN_LEGEND[k] = false;
            }
        });

        config.HIDDEN_LEGEND.None = false;

        $("#range-community").data("ionRangeSlider").update({
            max: config.THRESHOLD_COMMUNITY_MAX_SIZE
        });
    }

    // 设置节点排序，仅针对circular
    if (config.CHART_TYPE == "circular") {
        nodes.sort(function (a, b) {
            return a.categoryid - b.categoryid;
        });
    }

    // 设置筛选边(edge)
    var links = [];
    dataset.links.forEach(function (edge) {
        if (edge.weight >= config.THRESHOLD_EDGE) {
            if (config.CHART_TYPE == "force") {
                EDGE_WIDTH = 1;
                EDGE_CURVENESS = 0;
            } else {
                EDGE_WIDTH = Math.max(0.1, edge.weight / 50);
                EDGE_CURVENESS = 0.2;
            }

            edge.lineStyle = {
                normal: {
                    width: EDGE_WIDTH,
                    curveness: EDGE_CURVENESS
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
    var chart_type = config.CHART_TYPE;
    if (config.CHART_TYPE == 'geo') {
        chart_type = 'none';
    }

    var option = {
        color: config.COLOR,
        legend: [{
            type: 'scroll',
            orient: 'vertical',
            left: 5,
            // selectedMode: 'single',
            data: dataset.categories.map(function (c) {
                return c.name;
            }),
            selected: config.HIDDEN_LEGEND
        }],
        tooltip: {
            show: true,
            triggerOn: 'click',
            enterable: true
        },
        series: [{
            id: 'people',
            type: 'graph',
            layout: chart_type,
            zlevel: 100,
            force: {
                initLayout: 'circular',
                edgeLength: 50, // 边的两个节点之间的距离，这个距离也会受 repulsion。支持设置成数组表达边长的范围，此时不同大小的值会线性映射到不同的长度。值越大则长度越长。
                repulsion: 60, // 支持设置成数组表达斥力的范围，此时不同大小的值会线性映射到不同的斥力。值越大则斥力越大。default: 50
                gravity: 0.05 //节点受到的向中心的引力因子。该值越大节点越往中心点靠拢。default: 0.1
            },
            circular: {
                rotateLabel: true
            },
            draggable: true, // 节点是否可拖拽，只在使用力引导布局的时候有用
            animation: true,
            roam: false, // 是否开启鼠标缩放和平移漫游。默认不开启。如果只想要开启缩放或者平移，可以设置成 'scale' 或者 'move'。设置成 true 为都开启
            focusNodeAdjacency: false, // 节点hover时显示连接节点与边
            legendHoverLink: true, // 无效果，检查 TODO
            hoverAnimation: true, // 无效果，检查 TODO
            label: {
                normal: {
                    position: 'right',
                    formatter: function (param) {
                        return param.data.displayname;
                    }
                }
            },
            categories: dataset.categories,
            data: dataset.nodes,
            edges: dataset.links,
            lineStyle: {
                //width: 0.3,
                color: 'source',
                opacity: 0.3
            },
            emphasis: {
                edgeLabel: {
                    show: false
                },
                lineStyle: {
                    width: 2.5,
                    opacity: 0.8
                }
            },
            tooltip: {
                formatter: function (param) {
                    if (param.dataType == 'edge') {
                        lbl_weight = param.data.weight.toFixed(2);
                        return config.DEBUG ? param.name + ": " + lbl_weight : lbl_weight;
                    } else if (param.dataType == 'node') {
                        return get_tooltips(param).join('');
                    }
                }
            }
        }]
    };

    if (config.CHART_TYPE == "geo") {
        option.geo = {
            map: 'world',
            silent: true, //图形是否不响应和触发鼠标事件，默认为 false，即响应和触发鼠标事件。
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
        };

        option.series[0].coordinateSystem = 'geo';
        option.series[0].data = convert_geo_data(dataset.nodes);

        option.series[1] = {
            id: 'city',
            type: 'effectScatter',
            coordinateSystem: 'geo',
            zlevel: 10,
            rippleEffect: {
                brushType: 'fill',
                scale: 3
            },
            label: {
                show: true,
                position: 'left',
                formatter: '{b}',
                color: '#2967a6'
            },
            symbolSize: 15,
            showEffectOn: 'render',
            itemStyle: {
                normal: {
                    borderColor: '#fff',
                    color: '#dfecf7',
                    opacity: 0.6
                }
            },
            data: make_city_map(config.DATA_SOURCE.GEO_CITY),
            tooltip: {
                show: false
            }
        };
    }

    if (config.DEBUG) {
        //console.clear();
        console.log(dataset);
        console.log(option);
    }

    return option;
}

function bind_buttons(chart) {
    $("button#btn-config").click(function () {
        $(".control-sidebar-custom").hide();
    });

    $("button#btn-analytics").click(function () {
        $(".control-sidebar-custom").hide();
        $("#control-dashboard").show().find("#panel-optimate").hide();
        $("#control-dashboard").show().find("#panel-analytics").show(500);
    });

    $("button#btn-optimate").click(function () {
        $("#control-dashboard").show().find("#panel-analytics").hide();
        $("#control-dashboard").show().find("#panel-optimate").show(500);
    });

    $("button#btn-api").click(function () {
        $(".control-sidebar-custom").hide();
        $("#control-api-panel").show(500);
    });

    $("button#btn-refresh").click(function () {
        config.DATA_SOURCE.operation = "refresh";
        config.HIDDEN_LEGEND = chart.getOption().legend[0].selected;
        chart.showLoading();

        var ds = generate_dataset(config.DATA_SOURCE);
        var option = get_option(ds);
        bind_select2(ds, $("#ddl-search"), config.DOMAIN);

        chart.hideLoading();

        if (option && typeof option === "object") {
            chart.setOption(option, true);
        }
    });

    $("button#btn-nonorg").click(function () {
        var filepath = config.API_SERVER_PATH + config.DOMAIN + "?nonorg=true";

        if (config.DATA_TIMESTAMP != null) {
            filepath += ("&date=" + config.DATA_TIMESTAMP);
        }

        chart.showLoading();
        render_chart(filepath, chart);
        //bind_buttons(chart);

        $(this).hide();
    });

    $("button#btn-bookmark").click(function () {
        var url = [location.protocol, '//', location.host, location.pathname].join('');
        url = url.concat(
            "?domain=", config.DOMAIN,
            "&type=", config.CHART_TYPE.substring(0, 1),
            "&group=", config.GROUP_BY_FIELD,
            "&date=", config.DATA_TIMESTAMP != null ? config.DATA_TIMESTAMP : "",
            "&node=", 100 - config.THRESHOLD_NODE,
            "&edge=", 100 - config.THRESHOLD_EDGE,
            "&label=", config.MODE_SHOW_LABEL
        );

        // 添加LEGEND显示传参
        config.HIDDEN_LEGEND = chart.getOption().legend[0].selected;
        if (config.HIDDEN_LEGEND != {}) {
            var nocates = [];
            $.each(config.HIDDEN_LEGEND, function (k, v) {
                if (!v) {
                    nocates.push(encodeURIComponent(k));
                }
            });

            if (nocates.length > 0) {
                url = url.concat("&nocates=", nocates.join(','));
            }
        }

        window.open(url);
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

    $("button#btn-label").click(function () {
        nodes = chart.getOption().series[0].data;
        config.MODE_SHOW_LABEL = ++(config.MODE_SHOW_LABEL) > 2 ? 0 : (config.MODE_SHOW_LABEL);
        nodes.forEach(function (node) {
            if (config.MODE_SHOW_LABEL === 2) {
                node.label = {
                    normal: {
                        show: node.value >= config.THRESHOLD_SHOW_LABEL
                    }
                };
            } else {
                node.label = {
                    normal: {
                        show: Boolean(config.MODE_SHOW_LABEL)
                    }
                };
            }
        });

        chart.setOption({
            series: [{
                data: nodes
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

    $("button#btn-download").on("click", function () {
        var dataset = {
            "categories": [],
            "nodes": [],
            "links": []
        };

        var ds = generate_dataset(config.DATA_SOURCE);
        dataset.categories = ds.categories;

        ds.nodes.forEach(function (n) {
            dataset.nodes.push({
                "name": n.name,
                "displayname": n.displayname,
                "categoryid": n.categoryid,
                "category": n.category,
                "value": n.value,
                "x": n.x,
                "y": n.y
            });
        });

        ds.links.forEach(function (l) {
            dataset.links.push({
                "source": l.source,
                "target": l.target,
                "weight": l.weight
            });
        });

        $("<a />", {
                "download": "dataset-".concat(config.DOMAIN.toLowerCase(),
                    "-", config.DATA_TIMESTAMP != null ? config.DATA_TIMESTAMP.replace(/\-/g, "") : "all",
                    "-n", 100 - config.THRESHOLD_NODE,
                    "-l", 100 - config.THRESHOLD_EDGE,
                    ".json"),
                "href": "data:application/json," + encodeURIComponent(JSON.stringify(dataset)) // 最多2M
            })
            .appendTo("body")
            .click(function () {
                $(this).remove();
            })[0].click();
    });

    $("button#btn-search-reset").click(function () {
        $("#ddl-search").val("").select2();
        // 恢复hover
        chart.setOption({
            series: [{
                focusNodeAdjacency: true
            }]
        }, false);
        chart.dispatchAction({
            type: 'unfocusNodeAdjacency',
            seriesId: 'people'
        });
    });

    $("#ddl-search").change(function () {
        if ($(this).val() != "" && $(this).val() >= 0) {
            // 失效hover
            chart.setOption({
                series: [{
                    focusNodeAdjacency: false
                }]
            }, false);
            chart.dispatchAction({
                type: 'focusNodeAdjacency',
                seriesId: 'people',
                dataIndex: $(this).val()
            });
        } else {
            // 恢复hover
            chart.setOption({
                series: [{
                    focusNodeAdjacency: true
                }]
            }, false);
            chart.dispatchAction({
                type: 'unfocusNodeAdjacency',
                seriesId: 'people'
            });
        }
    });

    // DataSet Setting - community
    $("#range-community").ionRangeSlider({
        min: 2,
        max: config.THRESHOLD_COMMUNITY_MAX_SIZE,
        from: config.THRESHOLD_COMMUNITY_SIZE,
        type: 'single',
        step: 1,
        postfix: '',
        prettify: false,
        hasGrid: true,
        onFinish: function (obj) {
            config.THRESHOLD_COMMUNITY_SIZE = obj.from;

            config.DATA_SOURCE.operation = "community";
            config.HIDDEN_LEGEND = {};
            chart.showLoading();

            var ds = generate_dataset(config.DATA_SOURCE);
            var option = get_option(ds);
            bind_select2(ds, $("#ddl-search"), config.DOMAIN);

            chart.hideLoading();

            if (option && typeof option === "object") {
                chart.setOption(option, true);
            }
        }
    });

    // DataSet Setting - node
    $("#range-node").ionRangeSlider({
        min: 0,
        max: 100,
        from: (100 - config.THRESHOLD_NODE),
        type: 'single',
        step: 1,
        postfix: '',
        prettify: false,
        hasGrid: true,
        onFinish: function (obj) {
            config.THRESHOLD_NODE = 100 - obj.from;

            config.DATA_SOURCE.operation = "node";
            config.HIDDEN_LEGEND = chart.getOption().legend[0].selected;
            chart.showLoading();

            var ds = generate_dataset(config.DATA_SOURCE);
            var option = get_option(ds);
            bind_select2(ds, $("#ddl-search"), config.DOMAIN);

            chart.hideLoading();

            if (option && typeof option === "object") {
                chart.setOption(option, true);
            }
        }
    });

    // DataSet Setting - edge
    $("#range-edge").ionRangeSlider({
        min: 0,
        max: 100,
        from: (100 - config.THRESHOLD_EDGE),
        type: 'single',
        step: 1,
        postfix: '',
        prettify: false,
        hasGrid: true,
        onFinish: function (obj) {
            config.THRESHOLD_EDGE = 100 - obj.from;

            config.DATA_SOURCE.operation = "edge";
            config.HIDDEN_LEGEND = chart.getOption().legend[0].selected;
            chart.showLoading();

            var ds = generate_dataset(config.DATA_SOURCE);
            var option = get_option(ds);
            bind_select2(ds, $("#ddl-search"), config.DOMAIN);

            chart.hideLoading();

            if (option && typeof option === "object") {
                chart.setOption(option, true);
            }
        }
    });

    // Graphy Setting - layout
    $("select#ddl-layout").val(config.CHART_TYPE).change(function () {
        if ($(this).val() !== "") {
            $(".config-graph div.config").hide();
            $(".config-graph div.config-" + $(this).val().substring(0, 1)).show();

            $groupby = $("select#ddl-groupby");
            var selected_group = $groupby.val();
            $groupby.empty();

            groups = config.DICT.FIELD[$(this).find("option:selected").text()];
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

            config.CHART_TYPE = $(this).val();
            config.GROUP_BY_FIELD = $groupby.val();

            config.DATA_SOURCE.operation = "layout";
            config.HIDDEN_LEGEND = chart.getOption().legend[0].selected;
            chart.showLoading();

            var ds = generate_dataset(config.DATA_SOURCE);
            var option = get_option(ds);
            bind_select2(ds, $("#ddl-search"), config.DOMAIN);

            chart.hideLoading();

            if (option && typeof option === "object") {
                chart.setOption(option, true);
            }
        }
    });

    // Graphy Setting - layout
    $("input#cb-fix-location").change(function () {
        config.CHART_FIX_LOCATION = $(this).is(':checked');
    });

    // DataSet Setting - group by
    $("select#ddl-groupby").val(config.GROUP_BY_FIELD).change(function () {
        if ($(this).val() !== "") {
            config.GROUP_BY_FIELD = $(this).val();

            if (config.GROUP_BY_FIELD === "community") {
                $(".config-sub-community").show();
            } else {
                $(".config-sub-community").hide();
            }

            config.DATA_SOURCE.operation = "groupby";
            config.HIDDEN_LEGEND = chart.getOption().legend[0].selected;
            chart.showLoading();

            var ds = generate_dataset(config.DATA_SOURCE);
            var option = get_option(ds);
            bind_select2(ds, $("#ddl-search"), config.DOMAIN);

            chart.hideLoading();

            if (option && typeof option === "object") {
                chart.setOption(option, true);
            }
        }
    });

    $("#btn-time-travel").click(function () {
        var url = [location.protocol, '//', location.host,
            '/Nexus/pages/domain-time-travel.html',
            "?domain=", config.DOMAIN
        ].join('');

        window.open(url);
    });
}

function render_chart(filepath, chart) {
    $.get(filepath, function (d, status) {
        console.log(d);
        if (status === "success" && d != null && (d.state === "success" || d.state === "cache") || config.CACHE) {
            if (config.DEBUG && !config.CACHE) {
                console.log(d.state);
                console.log(d.time);
                console.log(d.describe);
            }

            config.DATA_SOURCE = config.CACHE ? d : d.data;

            // # initial the gender vale

            $.each(config.DATA_SOURCE.nodes, function (i, node) {
                if (node.gender == 1) {
                    node.gender = "Male";
                } else if (node.gender == 0) {
                    node.gender = "Female";
                } else {
                    node.gender = "None";
                }
            });

            config.CHART_FIX_LOCATION = false;
            $("input#cb-fix-location").prop('checked', config.CHART_FIX_LOCATION);

            config.DATA_SOURCE.operation = "initial";
            var ds = generate_dataset(config.DATA_SOURCE);
            var option = get_option(ds);
            bind_select2(ds, $("#ddl-search"), config.DOMAIN);

            chart.hideLoading();

            if (option && typeof option === "object") {
                chart.setOption(option, true);
            }
        } else if (status === "success" && d != null && d.state === "exception") {
            alert(d.message);
        }
    });
}