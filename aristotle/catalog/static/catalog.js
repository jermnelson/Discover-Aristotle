function DisplayAdvSearch(search_a) {
  $('#adv-searchbox').attr('style','display:inline');
  $('#basic-searchbox').attr('style','display:none');
  $(search_a).attr('text','Basic Search');
}


function DisplayBasicSearch(search_a) {
  $('#adv-searchbox').attr('style','display:none');
  $('#basic-searchbox').attr('style','display:inline');
  $(search_a).attr('text','Advanced Search');
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

function DisplayRows(row_count_select) {
 var new_row_count = $(row_count_select).attr('value');
 $('#solr_rows').attr('value',new_row_count);
 document.forms['catalog_search'].submit();

}

function DisplaySearch(search_a) {
   if($(search_a).attr('text') == 'Basic Search') {
      DisplayBasicSearch(search_a);
   }
   if($(search_a).attr('text') == 'Advanced Search') {
      DisplayAdvSearch(search_a);
   }

}

function FilterByFacet(facet,value) {
 $('#catalog_search').append('<input type="hidden" name="fq" value="' + facet + ':' + value + '">');
 document.forms['catalog_search'].submit();

}

function handleResultPaginateClick(new_page_index,pagination_container) {
  var data = 'func=search&search-type=' + $("input[name~='search-type']").val();
  data += '&page_index=' + new_page_index;
  data += '&rows=' + $("#solr_rows").val();
  $("input[name~='q']").each(
    function(i,v) {
     data += '&q=' + $(v).val();
  });
  $("input[name~='fq']").each(
    function(i,v) {
      data += '&fq=' + $(v).val();
  });
  $.ajax({
      type: 'get',
       url: '/catalog/rpc',
      data: data,
   success: function(responseText) {
      $('.results-list').remove();
      $('#main-content').attr('innerHTML',responseText);
    }
   });

  return false;
}

function NextPage(num_found) {
 var next_rows = $('#solr_start').attr('value') + $('#solr_rows').attr('value');
 if(next_rows < num_found) {
   $('#solr_start').attr('value',next_rows);
   document.forms['catalog_search'].submit()
 }
}

function PreviousPage() {
 var previous_rows = $('#solr_start').attr('value') - $('#solr_rows').attr('value');
 if(previous_rows >= 0) {
    $('#solr_start').attr('value',previous_rows);
 } else {
   $('#solr_start').attr('value',0);
 }
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
  
function ShowSearchHistory() {
 if($('#search-history').attr('display') == 'none') {
   $('#search-history').attr('display','block');
 } else {
   $('#search-history').attr('display','none');
 }
}
