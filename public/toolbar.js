$(() => {

  const drawer = $('#drawer').dxDrawer({
    opened: false,
    //height: 400,
    closeOnOutsideClick: true,
    template() {
      const $list = $('<div>').width(200).addClass('panel-list');

      return $list.dxList({
        dataSource:  [
          { id: 1, text: 'Project list', icon: 'product', url: 'index.html' },
          { id: 2, text: 'Analysis charts', icon: 'money', url: 'analysis.html'}
        ],
        hoverStateEnabled: false,
        focusStateEnabled: false,
        activeStateEnabled: false,
        elementAttr: { class: 'dx-theme-accent-as-background-color' },
        selectionMode: "single",
        onSelectionChanged: function(e) {
            location.href = e.addedItems[0].url;
            drawer.hide();
        }
      });
    },
  }).dxDrawer('instance');

  $('#toolbar').dxToolbar({
    items: [{
      widget: 'dxButton',
      location: 'before',
      height: 100,
      options: {
        icon: 'menu',
        onClick() {
          drawer.toggle();
        },
      },
    }, {
      location: 'center',
      locateInMenu: 'never',
      template() {
        return $("<div class='toolbar-label'><b>OSS Developer Community Health Analysis for Publiccode Github Repositories</b></div>");
      },
    }],
  });
});
