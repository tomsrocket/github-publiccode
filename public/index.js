$(() => {
  $('#gridContainer').dxDataGrid({
    dataSource: 'public-code-list.json',
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
    columns: [
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
        caption: 'Latest Commit',
        dataField: 'pa',
        width: 100
      },
      {
        caption: 'Watchers',
        dataField: 'w',
        width: 50,
      },
      {
        caption: 'Contributors',
        dataField: 'cont',
        width: 100,
      },
      {
        caption: 'Size',
        dataField: 's',
        width: 60
      },
      {
        dataField:'name',
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
        width: 100
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
        caption: 'Picture',
        dataField: 'logo',
        width: 90,
        cellTemplate(container, options) {
          $('<div>').addClass("im")
            .append($('<img>', { src: options.value }))
            .appendTo(container);
        }
      },
      {
        caption: 'Project URL',
        dataField: 'url',
        cellTemplate(container, options) {
          $('<a>', {href: options.value})
            .append( options.value )
            .appendTo(container);
        },
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
