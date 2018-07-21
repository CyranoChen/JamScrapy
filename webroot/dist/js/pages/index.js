function load_detail_panel(container, data) {
    if (data) {
        $pnl_describe = container.find("div.describe");
        $pnl_more = container.find("div.more");

        var entity_html = $("#pnl-context .card-body li.active a").html();

        $pnl_describe.find(".card-title").html(entity_html);
        $pnl_more.find(".card-title").html(data.detail.title.toUpperCase());

        $pnl_describe.find(".card-body").empty().append("<ul></ul>");
        $.each(data.describe, function (i, entity) {
            $pnl_describe.find(".card-body > ul").append("<li>" + entity + "</li>");
        });

        $pnl_more.find(".card-body").empty().append("<p>" + data.detail.content + "</p>");
        $pnl_more.find(".card-body").append("<ul></ul>");
        $.each(data.detail.points, function (i, entity) {
            $pnl_more.find(".card-body > ul").append("<li>" + entity + "</li>");
        });

        $pnl_describe.find(".btn-more").click(function () {
            $('#pnl-detail .describe').hide();
            $('#pnl-detail .more').fadeIn();
        });

        $pnl_more.find(".btn-back").click(function () {
            $('#pnl-detail .more').hide();
            $('#pnl-detail .describe').fadeIn();
        });

        container.show();
    } else {
        container.hide();
    }
}

function render_chart(chart, chart_type) {
    chart.setOption({
        series: [{
            layout: chart_type
        }]
    }, false);
}

$(function () {
    $("#container").css("height", window.innerHeight);

    var dom = document.getElementById("container");
    var chart = echarts.init(dom);
    chart.showLoading();

    $.get("../data/dataset-blockchain-t0-n60-l75.json", function (dataset, status) {
      if (status === "success" && dataset != null) {
        console.log(dataset);

        // 遍历节点，计算分类汇总与坐标
        dataset.nodes.forEach(function (node) {
          node.symbolSize = node.value / 6 + 1;
        });

        var option = {
          tooltip: {
            show: false,
          },
          series: [{
            id: 'people',
            type: 'graph',
            layout: 'force',
            zlevel: 100,
            force: {
              initLayout: 'circular',
              edgeLength: 20, // 边的两个节点之间的距离，这个距离也会受 repulsion。支持设置成数组表达边长的范围，此时不同大小的值会线性映射到不同的长度。值越大则长度越长。
              repulsion: 50, // 支持设置成数组表达斥力的范围，此时不同大小的值会线性映射到不同的斥力。值越大则斥力越大。default: 50
              gravity: 0.05 //节点受到的向中心的引力因子。该值越大节点越往中心点靠拢。default: 0.1
            },
            circular: {
              rotateLabel: true
            },
            draggable: false, // 节点是否可拖拽，只在使用力引导布局的时候有用
            animation: true,
            roam: false, // 是否开启鼠标缩放和平移漫游。默认不开启。如果只想要开启缩放或者平移，可以设置成 'scale' 或者 'move'。设置成 true 为都开启
            focusNodeAdjacency: false, // 节点hover时显示连接节点与边
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
              label: {
                show: false
              },
              edgeLabel: {
                show: false
              }
            }
          }]
        };

        chart.hideLoading();

        if (option && typeof option === "object") {
          chart.setOption(option, true);
        }
      }
    });

    $.getJSON("../data/dataset-index.json", function (data, status) {
        if (status === "success" && data != null) {
            //console.log(data);

            var entity_name = $("#pnl-context .card-body li.active").text().trim();
            load_detail_panel($("#pnl-detail"), data[entity_name]);

            $("#pnl-context .card .card-body ul li").click(function () {
                if ($(this).attr("class") != "active") {
                    $("#pnl-context .card .card-body ul li").removeClass("active");
                    $(this).addClass("active");
                    
                    var name = $(this).text().trim();
                    render_chart(chart, data[name].chart);
                    load_detail_panel($("#pnl-detail"), data[name]);
                }
            });
        }
    });

    $("#pnl-context .col-md-12 h2").click(function () {
        $("#pnl-context .card").hide();
        $(this).parent(".col-md-12").find(".card").show(200);
    });
});