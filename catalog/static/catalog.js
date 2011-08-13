function DisplayAdvSearch(search_a) {
  alert('In adv search');
  $('#adv-searchbox').attr('display','block');
  $('#basic-searchbox').attr('display','none');
  $(search_a).attr('text','Basic Search');
  $(search_a).attr('onclick','DisplayBasicSearch(this)');
}

function DisplayFacet(facet_a) {
 // Cycle through and close other facets
 var h5 = $(facet_a).children()[0];
 var ul = $(facet_a).next();
 if($(h5).attr('class') == 'closed') {
   $(h5).attr('class','');
   $(ul).attr('class','open');
 } else {
   $(h5).attr('class','closed');
   $(ul).attr('class','closed');
 }
 return false;
}

function FilterByFacet(facet,value) {
 $('#catalog_search').append('<input type="hidden" name="fq" value="' + facet + ':' + value + '">');
 document.forms['catalog_search'].submit();

}

function RecordDetail(more_a) {
  var h6 = $(more_a).parents()[0];
  var table = $(h6).next();
  var label = '';
  if($(table).attr('class') == 'closed') {
    $(table).attr('class','open');
    label = '<< Less details';
  } else {
    $(table).attr('class','closed');
    label = 'More details >>';
  }
  $(more_a).attr('text',label);
  return false;
}

function RemoveTerm(li_id) {
  $('#' + li_id).remove();
  document.forms['catalog_search'].submit();
}
  

