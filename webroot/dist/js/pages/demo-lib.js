function init_demo(keyword, chart) {
    if (keyword != undefined) {
        // control-dashboard script
        $("#control-dashboard").load("../shared/control-dashboard.html", function () {
            $(this).css("height", window.innerHeight - $(".main-header").outerHeight());

            // hardcode for network problems and take action
            $("#panel-optimate .card-comments").click(function () {
                $("#panel-optimate .card-footer").show();
                $("#panel-optimate .card-body").hide();
                var uc_name = $(this).prop("id").split('-')[1];
                $("#panel-optimate #pnl-" + uc_name).show(500);
            });

            $("#panel-optimate #issue-uc0").click(function () {
                config.DOMAIN = 'intelligent+enterprise';
                config.CHART_TYPE = 'force';
                config.GROUP_BY_FIELD = 'networktype';
                config.THRESHOLD_NODE = 100 - 80;
                config.THRESHOLD_EDGE = 100 - 80;
                config.MODE_SHOW_LABEL = 0;
                config.THRESHOLD_SHOW_LABEL = 70;
                config.HIDDEN_LEGEND = {};
                debug = false;

                chart.showLoading();

                var ds = generate_dataset(config.DATA_SOURCE);
                var option = get_option(ds);

                chart.hideLoading();

                if (option && typeof option === "object") {
                    chart.setOption(option, true);
                }
            });

            $("#panel-optimate #pnl-uc0 #btn-ignore").click(function () {
                $("#panel-optimate #pnl-uc0 .attachment-block>img").prop("src",
                    "../dist/img/usercase0_active.png");

                config.HIDDEN_LEGEND = {};
                config.HIDDEN_LEGEND['Brokers'] = false;

                chart.setOption({
                    legend: [{
                        selected: config.HIDDEN_LEGEND
                    }]
                }, false);
            });

            $("#panel-optimate #pnl-uc0 #btn-action").click(function () {
                $("#panel-optimate #pnl-uc0 .attachment-block>img").prop("src",
                    "../dist/img/usercase0.png");

                config.HIDDEN_LEGEND = {};
                config.HIDDEN_LEGEND['Brokers'] = true;

                chart.setOption({
                    legend: [{
                        selected: config.HIDDEN_LEGEND
                    }]
                }, false);
            });

            $("#panel-optimate #issue-uc1").click(function () {
                //http://127.0.0.1/nexus/pages/domain-viewer.html?domain=intelligent+enterprise&type=f&group=functionalarea
                //&date=2018-08-01&node=70&edge=100&label=0&nocates=Communications,Development,Finance,General%20Management%20%26%20Admin,Human%20Resources,None,Services,Education%20and%20Knowledge%20Services,Information%20Technology
                config.DOMAIN = 'intelligent+enterprise';
                config.CHART_TYPE = 'force';
                config.GROUP_BY_FIELD = 'functionalarea';
                config.THRESHOLD_NODE = 100 - 99;
                config.THRESHOLD_EDGE = 100 - 99;
                config.MODE_SHOW_LABEL = 0;
                config.THRESHOLD_SHOW_LABEL = 70;
                config.HIDDEN_LEGEND = {};
                config.HIDDEN_LEGEND['Communications'] = false;
                config.HIDDEN_LEGEND['Development'] = false;
                config.HIDDEN_LEGEND['Finance'] = false;
                config.HIDDEN_LEGEND['General Management & Admin'] = false;
                config.HIDDEN_LEGEND['Human Resources'] = false;
                config.HIDDEN_LEGEND['None'] = false;
                config.HIDDEN_LEGEND['Services'] = false;
                config.HIDDEN_LEGEND['Education and Knowledge Services'] = false;
                config.HIDDEN_LEGEND['Information Technology'] = false;
                debug = false;

                chart.showLoading();

                var ds = generate_dataset(config.DATA_SOURCE);
                var option = get_option(ds);
                bind_select2(ds, $("#ddl-search"), config.DOMAIN);

                chart.hideLoading();

                if (option && typeof option === "object") {
                    chart.setOption(option, true);
                }
            });

            $("#panel-optimate #pnl-uc1 #btn-ignore").click(function () {
                $("#panel-optimate #pnl-uc1 .attachment-block>img").prop("src",
                    "../dist/img/usercase1.png");
            });

            $("#panel-optimate #pnl-uc1 #btn-action").click(function () {
                chart.showLoading();

                $("#panel-optimate #pnl-uc1 .attachment-block>img").prop("src",
                    "../dist/img/usercase1_active.png");

                var ds = generate_dataset(config.DATA_SOURCE);
                ds.links.push({
                    "source": "I806541",
                    "target": "I828442",
                    "weight": 1000,
                    "lineStyle": {
                        "normal": {
                            "curveness": 0.2,
                            "width": 5,
                            "opacity": 0.5,
                            "color": "#28a745"
                        }
                    }
                });
                ds.links.push({
                    "source": "I075614",
                    "target": "I828442",
                    "weight": 1000,
                    "lineStyle": {
                        "normal": {
                            "curveness": 0.2,
                            "width": 3,
                            "opacity": 0.5,
                            "color": "#28a745"
                        }
                    }
                });
                var option = get_option(ds);
                option.series[0].focusNodeAdjacency = true;
                // option.series[0].tooltip = {
                //     formatter: function (param) {
                //         if (param.dataType == 'edge') {
                //             if (param.data.weight == 1000) {
                //                 return '<p>A closer collaboration between <br /> <span class="badge bg-primary">Mandy Lin (74.03)</span> and <span class="badge bg-primary">Emily Loggenberg (91.24)</span> <br />will increase the collaboration structure by 20%</p>'
                //             }
                //         } else if (param.dataType == 'node') {
                //             return get_tooltips(param).join('');
                //         }
                //     }
                // }

                bind_select2(ds, $("#ddl-search"), config.DOMAIN);

                chart.hideLoading();

                if (option && typeof option === "object") {
                    chart.setOption(option, true);
                }
            });

            $("#panel-optimate #issue-uc2").click(function () {
                //http://127.0.0.1/Nexus/pages/domain-viewer.html?domain=intelligent+enterprise&type=c&group=functionalarea&node=100&edge=100&label=0
                config.DOMAIN = 'intelligent+enterprise';
                config.CHART_TYPE = 'force';
                config.GROUP_BY_FIELD = 'functionalarea';
                config.THRESHOLD_NODE = 100 - 99;
                config.THRESHOLD_EDGE = 100 - 0;
                config.MODE_SHOW_LABEL = 0;
                config.THRESHOLD_SHOW_LABEL = 70;
                config.HIDDEN_LEGEND = {};
                debug = false;

                chart.showLoading();

                var ds = generate_dataset(config.DATA_SOURCE);
                var option = get_option(ds);
                bind_select2(ds, $("#ddl-search"), config.DOMAIN);

                chart.hideLoading();

                if (option && typeof option === "object") {
                    chart.setOption(option, true);
                }
            });

            $("#panel-optimate #pnl-uc2 #btn-ignore").click(function () {
                $("#panel-optimate #pnl-uc2 .attachment-block>img").prop("src",
                    "../dist/img/usercase2.png");
            });

            $("#panel-optimate #pnl-uc2 #btn-action").click(function () {
                $("#panel-optimate #pnl-uc2 .attachment-block>img").prop("src",
                    "../dist/img/usercase2_active.png");

                config.CHART_TYPE = 'circular';
                //config.THRESHOLD_NODE = 100 - 0;
                //config.THRESHOLD_EDGE = 100 - 99;

                // var node = 0;
                // var sim = setInterval(function () {
                //     config.THRESHOLD_NODE = 100 - node;
                //     var ds = generate_dataset(config.DATA_SOURCE);
                //     var option = get_option(ds);

                //     if (option && typeof option === "object") {
                //         chart.setOption(option, true);
                //     }

                //     $("span#simulate-date").text(ds.nodes.length);
                //     node += 3;

                //     if (node >= 80) {
                //         clearInterval(sim);
                //     }
                // }, 800);

                var edge = 0;
                var sim = setInterval(function () {
                    $("span#simulate-date").text(edge);
                    config.THRESHOLD_EDGE = 100 - edge;
                    var ds = generate_dataset(config.DATA_SOURCE);
                    var option = get_option(ds);

                    if (option && typeof option === "object") {
                        chart.setOption(option, true);
                    }

                    $("span#simulate-date").text(ds.links.length);
                    edge += 5;

                    if (edge >= 100) {
                        clearInterval(sim);
                    }
                }, 300);
            });

            $("#panel-optimate #issue-uc4").click(function () {
                //http://127.0.0.1/Nexus/pages/domain-viewer.html?domain=intelligent+enterprise&type=n&group=functionalarea&node=43&edge=100&label=0&nocates=None,Information%20Technology,Human%20Resources,General%20Management%20%26%20Admin,Finance,Communications,Services
                config.DOMAIN = 'intelligent+enterprise';
                config.CHART_TYPE = 'none';
                config.GROUP_BY_FIELD = 'functionalarea';
                config.THRESHOLD_NODE = 100 - 43;
                config.THRESHOLD_EDGE = 100 - 99;
                config.MODE_SHOW_LABEL = 0;
                config.THRESHOLD_SHOW_LABEL = 70;
                config.HIDDEN_LEGEND = {};
                config.HIDDEN_LEGEND['Communications'] = false;
                config.HIDDEN_LEGEND['Finance'] = false;
                config.HIDDEN_LEGEND['General Management & Admin'] = false;
                config.HIDDEN_LEGEND['Human Resources'] = false;
                config.HIDDEN_LEGEND['None'] = false;
                config.HIDDEN_LEGEND['Services'] = false;
                config.HIDDEN_LEGEND['Education and Knowledge Services'] = false;
                config.HIDDEN_LEGEND['Information Technology'] = false;
                debug = false;

                chart.showLoading();

                var ds = generate_dataset(config.DATA_SOURCE);
                var option = get_option(ds);
                bind_select2(ds, $("#ddl-search"), config.DOMAIN);

                chart.hideLoading();

                if (option && typeof option === "object") {
                    chart.setOption(option, true);
                }
            });
        });

        // control-api-panel script
        $("#control-api-panel").load("../shared/control-api-panel.html", function () {
            $(this).css("height", window.innerHeight - $(".main-header").outerHeight());

            $(".pnl-api-describe").click(function () {
                $(this).siblings(".pnl-api-debug").toggle(500);
            });

            $("#btn-api-communities").click(function () {
                //  http://10.178.200.23/Nexus/pages/domain-viewer.html?domain=blockchain&type=f&group=community&date=&node=100&edge=80&label=0&nocates=000066,000046,000020,000014,000059,000072,000147,000036,000050,000010,000128,000028,000187,000207,000064,000034,000000,000145,000255,000029,000061,000011,000263,000103,000053,000075,000124,000143,000016,000071,000212,000189,000242,000044,000154,000164,000038,000089,000047,000022,000045,000188,000137,000015,000127,000041,000173,000232,000112,000208,000084,000025,000146,000151,000169,000219,000247,000031,000195,000249,000098,000194,000006,000198,000018,000120,000150,000133,000106,000008,000177,000091,000213,000191,000087,000121,000217,000017,000057,000019,000027,000001,000258,000206,000160,000069,000185,000156,000074,000032,000238,000115,000051,000253,000210,000095,000021,000054,000205,000003,000267,000042,000155,000063,000265,000117,000193,000088,000199,000167,000237,000203,000181,000082,000241,000068,000170,000048,000109,000013,000246,000184,000076,000108,000218,000257,000158,000090,000119,000111,000080,000039,000043,000126,000009,000026,000132,000153,000007,000142,000097,000101,000196,000165,000122,000157,000261,000005,000070,000171,000104,000135,000130,000055,000190,000129,000002,000224,000062,000244,000123,000085,000118,000180,000225,000243,000141,000168,000215,000102,000086,000073,000248,000152,000202,000216,000037,000114,000235,000159,000200,000256,000067,000035,000140,000222,000092,000148,000214,000096,000049,000172,000183,000204,000227,000083,000033,000116,000251,000110,000236,000100,000260,000245,000058,000182,000240,000012,000134,000094,000081,000099,000250,000056,000197,000004,000024,000065,000138,000163,000264,000233,000030,000078,000220,000079,000192,000231,000175,000139,000144,000229,000186,000131,000211,000209,000105,000162,000174,000040,000179,000226,000176,000149,000125,000136,000221,000161,000230,000228,000077,000266,000223,000254,000178,000234,000262,000201,000060,000113,000259,000093,000107,000166,000252,000239,None
                config.DOMAIN = 'blockchain';
                config.CHART_TYPE = 'force';
                config.GROUP_BY_FIELD = 'community';
                config.THRESHOLD_NODE = 100 - 100;
                config.THRESHOLD_EDGE = 100 - 80;
                config.MODE_SHOW_LABEL = 0;
                config.THRESHOLD_SHOW_LABEL = 70;

                var str_nocates =
                    "000066,000046,000020,000014,000059,000072,000147,000036,000050,000010,000128,000028,000187,000207,000064,000034,000000,000145,000255,000029,000061,000011,000263,000103,000053,000075,000124,000143,000016,000071,000212,000189,000242,000044,000154,000164,000038,000089,000047,000022,000045,000188,000137,000015,000127,000041,000173,000232,000112,000208,000084,000025,000146,000151,000169,000219,000247,000031,000195,000249,000098,000194,000006,000198,000018,000120,000150,000133,000106,000008,000177,000091,000213,000191,000087,000121,000217,000017,000057,000019,000027,000001,000258,000206,000160,000069,000185,000156,000074,000032,000238,000115,000051,000253,000210,000095,000021,000054,000205,000003,000267,000042,000155,000063,000265,000117,000193,000088,000199,000167,000237,000203,000181,000082,000241,000068,000170,000048,000109,000013,000246,000184,000076,000108,000218,000257,000158,000090,000119,000111,000080,000039,000043,000126,000009,000026,000132,000153,000007,000142,000097,000101,000196,000165,000122,000157,000261,000005,000070,000171,000104,000135,000130,000055,000190,000129,000002,000224,000062,000244,000123,000085,000118,000180,000225,000243,000141,000168,000215,000102,000086,000073,000248,000152,000202,000216,000037,000114,000235,000159,000200,000256,000067,000035,000140,000222,000092,000148,000214,000096,000049,000172,000183,000204,000227,000083,000033,000116,000251,000110,000236,000100,000260,000245,000058,000182,000240,000012,000134,000094,000081,000099,000250,000056,000197,000004,000024,000065,000138,000163,000264,000233,000030,000078,000220,000079,000192,000231,000175,000139,000144,000229,000186,000131,000211,000209,000105,000162,000174,000040,000179,000226,000176,000149,000125,000136,000221,000161,000230,000228,000077,000266,000223,000254,000178,000234,000262,000201,000060,000113,000259,000093,000107,000166,000252,000239,None";

                var arr = str_nocates.split(',');
                if (arr.length > 0) {
                    for (var i in arr) {
                        var cate = decodeURIComponent(arr[i]);
                        config.HIDDEN_LEGEND[cate] = false;
                    }
                }

                config.CACHE = false;

                chart.showLoading();

                var ds = generate_dataset(config.DATA_SOURCE);
                var option = get_option(ds);
                bind_select2(ds, $("#ddl-search"), config.DOMAIN);

                chart.hideLoading();

                if (option && typeof option === "object") {
                    chart.setOption(option, true);
                    $("button#btn-search-reset").click();
                }
            });

            $("#btn-api-broker").click(function () {
                config.DOMAIN = 'blockchain';
                config.CHART_TYPE = 'circular';
                config.GROUP_BY_FIELD = 'networktype';
                config.THRESHOLD_NODE = 100 - 100;
                config.THRESHOLD_EDGE = 100 - 80;
                config.MODE_SHOW_LABEL = 0;
                config.THRESHOLD_SHOW_LABEL = 70;
                config.HIDDEN_LEGEND = {};
                config.CACHE = false;

                chart.showLoading();

                var ds = generate_dataset(config.DATA_SOURCE);
                var option = get_option(ds);

                bind_select2(ds, $("#ddl-search"), config.DOMAIN);

                chart.hideLoading();

                if (option && typeof option === "object") {
                    chart.setOption(option, true);

                    // highlight [Brokers] Raimund Gross (D032728)

                    // var selected = $('#ddl-search').find('option[text="[Brokers] Raimund Gross (D032728)"]').val();
                    // alert(selected);
                    $("#ddl-search").val(24);
                    $("#ddl-search").trigger("change");
                }
            });
        });
    }

}