function LoadTitles(alpha) {
  LoadFacet('title',alpha);
}

function LoadSubject(subject) {
  LoadFacet('subject',subject);
}

function LoadFacet(facet_type,value,csrf_token) {
  var data = 'func=loadFacet&type=' + facet_type + '&value=' + value;
  $.ajax({
     type: 'get',
      url: '/grx/rpc',
     data: data,
  success: function(response) {
    facet_json = eval(response);
    alert(facet_json);
    $('#default-tab').attr('innerHTML',facet_json);
    }
  });
}
