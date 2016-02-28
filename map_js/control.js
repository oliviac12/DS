var info = L.control();

info.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
    this.update();
    return this._div;
};

info.update = function (props) {
    this._div.innerHTML = '<h4> housing and transportation costs as a percent of income for renters</h4>' +  (props ?
        '<b>' + props.tracts + '</b><br />' + props.ht_rent + '%'
        : 'Hover over a state');
};

info.addTo(map);
