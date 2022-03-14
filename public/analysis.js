$(() => {

  function drawCommunityHealth(data) {
    var dataSource = [
      {icon: 'critical', desc: 'More than one indicator is critical', val: 0, color:'red'},
      {icon: 'risky', desc: 'Danger: One indicator is critial', val: 0},
      {icon: 'ok', desc: 'At least two subobtimal indicators', val: 0},
      {icon: 'good', desc: 'Only one subobtimal indicator', val: 0},
      {icon: 'very good', desc: 'All indicators green', val: 0, color:'green'},
    ]

    $.each( data, function( key, val ) {
      const rating = val['rt'].substr(1);
      const nr_worst = (rating.match(/1/g)||[]).length;
      const nr_bad = (rating.match(/2/g)||[]).length;
      if (nr_worst > 1) {dataSource[0]['val']++}
      else if (nr_worst > 0) {dataSource[1]['val']++}
      else if (nr_bad > 1) {dataSource[2]['val']++}
      else if (nr_bad == 1) {dataSource[3]['val']++}
      else {dataSource[4]['val']++}
    });
    console.debug(dataSource)

    $('#pie2').dxPieChart({
      type: 'doughnut',
      palette: ['#540202','#AB3131','#EDE0A6','#799163', '#507B58'],
      dataSource,
      title: 'Community Health Rating',
      tooltip: {
        enabled: true,
        customizeTooltip(arg) {
          return {
            text: `${arg.point.data.desc}\n ${arg.valueText} repositories (${(arg.percent * 100).toFixed(2)}%)`,
          };
        },
      },
      legend: {
        visible: false,
      },
      export: {
        enabled: true,
      },
      series: [{
        argumentField: 'icon',
        label: {
          visible: true,
          customizeText(point) {
            return `${point.argumentText}: ${(point.percent * 100).toFixed(2)}%`;
          },
          connector: {
            visible: true,
          },
        },
      }],
    });
  }

  function drawBarChart(target, data, fieldName, title, color) {
    var results = {};
    var total = 0;
    $.each( data, function( key, val ) {
      const rkey = val[fieldName];
      total++;
      if (!results[rkey]) {
        results[rkey] = 1;
      } else {
        results[rkey]++
      }
    });
    console.debug(results)

    var dataSource = [];
    var other = 0;
    var count = 0;
    (Object.keys(results).sort(function(a,b){return results[a]-results[b]})).reverse().forEach(function(result) {
      if (count++<20) {
        dataSource.push({name: result, val: results[result],p: (results[result]/total)});
      } else {
        other+=results[result];
      }
    });
    dataSource.push({name: "Other", val: other, p: (other/total)});

    console.debug("total", total, dataSource)

    $(target).dxChart({
      dataSource: dataSource.reverse(),
      rotated: true,
      title: title,
      tooltip: {
        enabled: true,
        customizeTooltip(arg) {
          return {
            text: `${arg.valueText} repositories (${(arg.point.data['p'] * 100).toFixed(2)}%)`,
          };
        },
      },
      legend: {
        visible: false
      },
      series: {
        argumentField: 'name',
        valueField: 'val',
        color: color,
        type: 'bar'
      },
    });

  }

  function drawSoftwareType(data) {
    var results = {};
    $.each( data, function( key, val ) {
      const rkey = val['type'];
      if (!results[rkey]) {
        results[rkey] = 1;
      } else {
        results[rkey]++
      }
    });

    var dataSource = [];
    var other = 0;
    var count = 0;
    (Object.keys(results).sort(function(a,b){return results[a]-results[b]})).reverse().forEach(function(result) {
      if (count++<10) {
        dataSource.push({name: result, val: results[result]});
      } else {
        other+=results[result];
      }
    });
    dataSource.push({name: "Other", val: other});

    console.debug(dataSource)

    $('#pie4').dxPieChart({
      type: 'doughnut',
      palette: 'Soft Pastel',
      dataSource,
      title: 'Software Type',
      tooltip: {
        enabled: true,
        customizeTooltip(arg) {
          return {
            text: `${arg.argument}: ${arg.valueText} (${(arg.percent * 100).toFixed(2)}%)`,
          };
        },
      },
      legend: {
        visible: false,
      },
      export: {
        enabled: true,
      },
      series: [{
        argumentField: 'name',
        label: {
          visible: true,
          customizeText(point) {
            return `${point.argumentText}: ${(point.percent * 100).toFixed(2)}%`;
          },
          connector: {
            visible: true,
          },
        },
      }],
    });
  }

  function drawCategories(data) {
    var results = {};
    $.each( data, function( key, val ) {
      const entries = val['cat'];
      if (Array.isArray(entries)) {
        entries.forEach(function(rkey){
          if (!results[rkey]) {
            results[rkey] = 1;
          } else {
            results[rkey]++
          }
        });
      }
    });
    var dataSource = [];
    var other = 0;
    var count = 0;
    (Object.keys(results).sort(function(a,b){return results[a]-results[b]})).reverse().forEach(function(result) {
      dataSource.push({text: result, weight: results[result]});
    });
    $('#pie5').jQCloud(dataSource);
  }

  $.getJSON( "public-code-list.json", function( data ) {

    drawBarChart('#pie1', data, 'l', 'Top Programming Languages', '#7565a4');
    drawCommunityHealth(data)
    drawBarChart('#pie3', data, 'lgl', 'Top Licenses', '#456c68');
    drawSoftwareType(data);
    drawCategories(data);

  });






});
