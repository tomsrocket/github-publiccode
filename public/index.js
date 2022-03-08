$(() => {

  $('#legend').append('<div><b>Status:</b> 🔵production, 🟢stable, 🟡other, 🟠beta, 🔴development</div>');
  $('#legend').append('<div><b>Maintained by:</b> 💰contractor, 👤internal, 👫community, 🥷individual, 👾other');
  $('#legend').append('<div><b>Columns:</b> ⭐ Nr. of stars, 💻 Nr. of contributions, 👥 Nr. of contributors, 📅 Days since latest commit');
  $('#legend').append('<div><b>Rating:</b> 🌕 very good .. 🌖 good .. 🌗 ok ..  🌘 risky .. 🌑 bad');

  function getRatingSymbol(position, rating) {
    const number = rating.charAt(position)
    icon = "🌧"
    switch (number) {
      case "1": icon ="🌑"; break;
      case "2": icon ="🌘"; break;
      case "3": icon ="🌗"; break;
      case "4": icon ="🌖"; break;
      case "5": icon ="🌕"; break;
    }
    return icon
  }
  function getRatingColor(position, rating) {
    const number = rating.charAt(position)
    if (number == 1) { return '#ffddee'; }
    if (number == 2) { return '#ffeedd'; }
  }

  $('#gridContainer').dxDataGrid({
    dataSource: 'public-code-list.json?v=0.5',
    rowAlternationEnabled: true,
    showBorders: true,
    paging: {
      pageSize: 25,
    },
    pager: {
      showPageSizeSelector: true,
      allowedPageSizes: [10, 25, 50, 100],
    },
    headerFilter: { visible: true },
    filterRow: { visible: true },
    summary: {
      totalItems: [{
        column: 'name',
        summaryType: 'count',
      }],
    },
    onCellPrepared: function(row) {
      const c = row.column.caption
      if (row.rowType != "data") { return; }
      if (c.startsWith('📅')) { row.cellElement.css("background-color", getRatingColor(1, row.data["rt"])); }
      if (c.startsWith('💻')) { row.cellElement.css("background-color", getRatingColor(2, row.data["rt"])); }
      if (c.startsWith('👥')) { row.cellElement.css("background-color", getRatingColor(3, row.data["rt"])); }
    },
    columns: [
      {
        caption: 'Rating',
        dataField: 'rt',
        width: 50
      },
      {
        caption: 'Status',
        dataField: 'stat',
        width: 26,
        cellTemplate(container, options) {
          var icon = "🟡"
          switch (options.value) {
            case "stable": icon = "🟢";break;
            case "beta": icon = "🟠";break;
            case "development": icon ="🔴";break;
            case "production": icon = "🔵";break;
          }
          $('<span title="'+options.value+'">' + icon + '</span>')
            .appendTo(container);
        },
      },
      {
        caption: 'Release Date',
        dataField: 'date',
        width: 90
      },
      {
        caption: '⭐ Stars',
        dataField: 'w',
        width: 60,
        cellTemplate(container, options) {
          $('<span>' + options.value + '</span>').append(getRatingSymbol(0, options.data["rt"]))
            .appendTo(container);
        },
      },
      {
        caption: '📅 Days since latest commit',
        dataField: 'pa',
        width: 60,
        color: {argb:'FF00FF00'},
        cellTemplate(container, options) {
          $('<span>' + options.value + '</span>').append(getRatingSymbol(1, options.data["rt"]))
            .appendTo(container);
        },
      },
      {
        caption: '💻 Contributions',
        dataField: 'cb',
        width: 60,
        cellTemplate(container, options) {
          $('<span>' + options.value + '</span>').append(getRatingSymbol(2, options.data["rt"]))
            .appendTo(container);
        },
      },
      {
        caption: '👥 Contributors',
        dataField: 'c',
        width: 60,
        cellTemplate(container, options) {
          $('<span>' + options.value + '</span>').append(getRatingSymbol(3, options.data["rt"]))
            .appendTo(container);
        },
      },
      {
        caption: 'Contributor types',
        dataField: 'cn',
        width: 70,
      },
      {
        caption: 'Project URL',
        dataField: 'r',
        cellTemplate(container, options) {
          $('<a>', {href: options.data["url"]})
            .append( options.data['rg'] + "/" + options.value )
            .appendTo(container);
        },
      },
      {
        dataField:'n',
        caption: 'Software Name',
        cellTemplate(container, options) {
          var is_a_fork = ""
          if (options.data["f"]) {
            is_a_fork = "🍴"
          }
          $('<b>')
            .append( is_a_fork + options.value  )
            .appendTo(container);
        },
        width: 250
      },
      {
        caption: 'Organisation (=Github Repo Owner)',
        dataField: 'rg',
        width: 110,
        cellTemplate(container, options) {
          logo = options.data["av"]
          $('<div>').addClass("im")
            .append($('<img>', { src: logo }))
            .append(options.value)
            .appendTo(container);
        }
      },
      {
        caption: 'Maintained by',
        dataField: 'mnt',
        width:26,
        cellTemplate(container, options) {
          var maintainer = "👾"
          switch (options.data["mnt"]) {
            case "community": maintainer = "👫";break;
            case "internal": maintainer = "👤";break;
            case "individual": maintainer = "🥷";break;
            case "contract": maintainer = "💰";break;
          }
          maintainer = '<span title="'+options.data["mnt"]+'">' + maintainer + '</span>'
          $(maintainer)
            .appendTo(container);
        },
      },
      {
        caption: 'Language',
        dataField: 'l',
        width: 90
      },
      {
        caption: 'Platform',
        dataField: 'p',
        width: 90
      },
      {
        caption: 'Description',
        dataField: 'd',
      },
      {
        caption: 'Language(s)',
        dataField: 'lang',
        width: 60
      },
      {
        caption: 'YAML',
        dataField: 'src',
        cellTemplate(container, options) {
          $('<a>', {href: options.value})
            .append( "&gt;&gt;" )
            .appendTo(container);
        },
        width: 50
      }
      ],
  });
});
