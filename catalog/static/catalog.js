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

function RecordDetail(more_a) {
  var h6 = $(more_a).parents()[0];
  var table = $(h6).next();
  var label = '';
  if($(table).attr('class') == 'closed') {
    $(table).attr('class','open');
    label = '&amp;laquo; Less details';
  } else {
    $(table).attr('class','closed');
    label = 'More details &#187;';
  }
  $(more_a).attr('text',label);
  return false;
}
