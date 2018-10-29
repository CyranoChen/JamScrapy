function bind_button(chart) {
	$("#pnl-brand").css("top", (window.innerHeight - $("#pnl-brand").height()) / 2.5).fadeIn(3000);

	// $("#pnl-brand a#btn-domains").click(function () {
	// 	chart.setOption({
	// 		series: [{
	// 			layout: (chart.getOption().series[0].layout == "force" ? "circular" : "force")
	// 		}]
	// 	}, false);
	// });
}

$(function () {
	$("#container").css("height", window.innerHeight);

	var dom = document.getElementById("container");
	var chart = echarts.init(dom);
	chart.showLoading();

	$.get("../data/dataset-blockchain-t0-n60-l80.json", function (dataset, status) {
		if (status === "success" && dataset != null) {

			// 遍历节点，计算分类汇总与坐标
			dataset.nodes.forEach(function (node) {
				node.symbolSize = node.value / 6 + 1;
			});

			dataset.nodes.sort(function (a, b) {
				return a.categoryid - b.categoryid;
			});

			console.log(dataset);

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
						edgeLength: 25, // 边的两个节点之间的距离，这个距离也会受 repulsion。支持设置成数组表达边长的范围，此时不同大小的值会线性映射到不同的长度。值越大则长度越长。
						repulsion: 50, // 支持设置成数组表达斥力的范围，此时不同大小的值会线性映射到不同的斥力。值越大则斥力越大。default: 50
						gravity: 0.1 //节点受到的向中心的引力因子。该值越大节点越往中心点靠拢。default: 0.1
					},
					circular: {
						rotateLabel: true
					},
					width: 1600,
					height: 800,
					draggable: false, // 节点是否可拖拽，只在使用力引导布局的时候有用
					animation: true,
					roam: false, // 是否开启鼠标缩放和平移漫游。默认不开启。如果只想要开启缩放或者平移，可以设置成 'scale' 或者 'move'。设置成 true 为都开启
					focusNodeAdjacency: false, // 节点hover时显示连接节点与边
					silent: true,
					label: {
						normal: {
							show: false
						}
					},
					categories: dataset.categories,
					data: dataset.nodes,
					edges: dataset.links,
					lineStyle: {
						color: 'source',
						opacity: 0.3
					}
				}]
			};

			if (option && typeof option === "object") {
				chart.hideLoading();
				chart.setOption(option, true);
			}

			bind_button(chart);
		}
	});
});