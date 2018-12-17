var config = {
	'THRESHOLD_USER': null,
	'THRESHOLD_LV': 4,
	'THRESHOLD_S_LV': 3,
	'THRESHOLD_F_LV': 2,
	'API_SERVER_PATH': 'http://10.58.78.253:8001/profile/'
};

$(function () {
	$("#ddl-search").empty().select2({
		ajax: {
			url: function (params) {
				return config.API_SERVER_PATH + params.term;
			},
			dataType: 'json',
			delay: 500,
			processResults: function (d) {
				console.log(d.data);
				return {
					results: d.data
				};
			}
		},
		minimumInputLength: 3
	}).change(function () {
		config.THRESHOLD_USER = $(this).val();
	});

	$("#btn-generate").click(function () {
		//people-network.html?user=i345795&lv=5&slv=5&follow=true
		if (config.THRESHOLD_USER != null) {
			var url = "people-network.html";
			url = url.concat("?user=", config.THRESHOLD_USER, "&lv=", config.THRESHOLD_LV);

			if (config.THRESHOLD_S_LV > 0) {
				url = url.concat("&slv=", config.THRESHOLD_S_LV);
			}

			if (config.THRESHOLD_F_LV > 0) {
				url = url.concat("&follow=true&flv=", config.THRESHOLD_F_LV);
			}

			url = url.concat("&debug=", !$("#cb-debug").is(':checked'));

			window.location.href = url;
		} else {
			alert('Please choose an employee');
		}
	});

	$("#range-lv").ionRangeSlider({
		min: 1,
		max: 6,
		from: 4,
		onFinish: function (obj) {
			config.THRESHOLD_LV = obj.from;
			config.THRESHOLD_S_LV = Math.round(obj.from / 1.5);
			config.THRESHOLD_F_LV = 0;

			$("#range-s-lv").data("ionRangeSlider").update({
				from: config.THRESHOLD_S_LV,
				max: obj.from
			});

			$("#range-f-lv").data("ionRangeSlider").update({
				from: config.THRESHOLD_F_LV,
				max: obj.from
			});
		}
	});
	$("#range-s-lv").ionRangeSlider({
		min: 0,
		max: 6,
		from: 3,
		onFinish: function (obj) {
			config.THRESHOLD_S_LV = obj.from;
		}
	});
	$("#range-f-lv").ionRangeSlider({
		min: 0,
		max: 6,
		from: 2,
		onFinish: function (obj) {
			config.THRESHOLD_F_LV = obj.from;
		}
	});
});