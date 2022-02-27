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
        caption: 'Release Date',
        dataField: 'date',
        width: 100
      },
      {
        caption: 'Status',
        dataField: 'stat',
        width: 80
      },
      {
        caption: 'Application Type',
        dataField: 'type',
        width: 120
      },
      {
        dataField:'name',
        caption: 'Software Name',
        cellTemplate(container, options) {
          $('<b>')
            .append( options.value )
            .appendTo(container);
        },
        width: 250

      },
      {
        caption: 'Language(s)',
        dataField: 'lang',
        width: 80
      },
      {
        caption: 'Maintained by',
        dataField: 'mnt',
        width: 90
      },
      {
        caption: 'License',
        dataField: 'l',
        width: 110
      },
      {
        caption: 'Platform',
        dataField: 'p',
        width: 90
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
        width: 80
      }
      ],
  });
});
