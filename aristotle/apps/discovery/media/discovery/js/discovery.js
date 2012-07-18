function AddCartItem(anchor_tag,record_id) {
  var data = 'record_id=' + record_id;
  $.ajax({
      type: 'get',
       url: '/catalog/cart/add',
      data: data,
   success: function(responseText) {
       // Should change icon and text to Drop
       var anchor_html = "DropCartItem(this,'" + record_id + "'," + true + ')"';
       $(anchor_tag).removeClass('label-success').addClass('label-important');
       $(anchor_tag).attr('onclick',anchor_html);
       $(anchor_tag).html('<i class="icon-minus-sign icon-white"></i>');
    }
   });
}

function CartToRefworks(session_id) {
  var refworks_url = 'http://www.refworks.com/express/expressimport.asp?vendor=iii&filter=RefWorks%20Tagged%20Format&url=http%3A//' + window.location.host + '/catalog/cart/refworks?session=' + session_id;
  window.open(refworks_url);
}


function ChangeSearchBookText(btn_text) {
 $("#searchby").html(btn_text);
 $("#searchby").val(btn_text);
 var search_char = btn_text.charAt(0);
 switch(search_char) {
  case 'A':
   $('#search-type').val("author_search");
   break;
  case 'J':
   $('#search-type').val("title_search");
   break;
  case 'K':
   $('#search-type').val("search");
   break;
  case 'S':
   $('#search-type').val("subject_search");
   break;
  case 'T':
   $('#search-type').val("title_search");
 }
}

function DropCartItem(anchor_tag,record_id,keep) {
  var data = 'record_id=' + record_id;
  $.ajax({
      type: 'get',
       url: '/catalog/cart/drop',
      data: data,
   success: function(responseText) {
       // Should change icon and text to Drop
       if(keep) {
         var anchor_html = "AddCartItem(this,'" + record_id + "'" + ')';
         $(anchor_tag).removeClass('label-important').addClass('label-success');
         $(anchor_tag).attr('onclick',anchor_html);
         $(anchor_tag).attr('title','Remove Record from cart');
         $(anchor_tag).html('<i class="icon-plus-sign icon-white"></i>');
       } else {
         $(anchor_tag).parent().remove();
       }
    }
   });
}

function DisplayAdvSearch(search_a) {
  $('#adv-searchbox').attr('style','display:inline');
  $('#basic-searchbox').attr('style','display:none');
  $(search_a).text('Basic Search');
  
}


function DisplayBasicSearch(search_a) {
  $('#adv-searchbox').attr('style','display:none');
  $('#basic-searchbox').attr('style','display:inline');
  $(search_a).text('Advanced Search');
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

function DisplayItems(more_dd) {
  $("dd").attr('style','');
  $(more_dd).remove();
}

function DisplayRows(row_count_select) {
 var new_row_count = $(row_count_select).attr('value');
 $('#solr_rows').attr('value',new_row_count);
 document.forms['catalog_search'].submit();

}

function DisplaySearch(search_a) {
   var label = $(search_a).text();
   if(label == 'Basic Search') {
      DisplayBasicSearch(search_a);
   }
   if(label == 'Advanced Search') {
      DisplayAdvSearch(search_a);
   }

}

function EmailCart() {
  var email_addr = prompt('Please enter your email');
  var data = 'email=' + email_addr;
  $.ajax({
     type: 'get',
      url: '/catalog/cart/email',
     data: data,
    success: function(responseText) {
          alert(responseText);
     }
    });
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


function ProcessSearchQuery() {
  var new_q = $('#book-search').value();
  new_q += set_fieldname("field1");
  new_q += set_fieldname("field2");
  new_q += set_fieldname("field3");
  $('#book-search').attr('value',new_q);
  //document.forms['catalog_search'].submit();
}

function set_fieldname(field_stem) {
  var search_type = "input[name~='" + field_stem + "_type']";
  var search_phrase = "input[name~='" + field_stem + "_phrase']";
  var search_operator = "input[name~='" + field_stem + "_operator']";

  var output = ' ';
  if ($(search_type).value()) {
    output += $(search_type).value() + ':' + $(search_phrase).value();
  } else {
    output += $(search_phrase).value();
  }
  if (output.length > 2) {
    output += ' ' + $(search_operator).value();
  }
 return output;
}


function PrintCart() {
  var print_window = window.open('/catalog/cart/print','_blank','fullscreen=yes');
  print_window.print();
}

function ShowCart(session_id) {
   var data = '';
   $.ajax({
      type: 'get',
       url: '/catalog/cart',
      data: data,
   success: function(responseText) {
        var output = '<button class="btn" onclick="PrintCart()"><i class="icon-print"></i> Print</button>';
        output += '<button class="btn" onclick="EmailCart()"><i class="icon-envelope"></i> Email</button>';
        output += '<button class="btn" onclick=';
        output += "'CartToRefworks(";
        output += '"' + session_id + '"';
        output += ")'><i class='icon-share'></i> Export to RefWorks</button><ol>";
        var results = eval(responseText);
        for(row in results) {
           var record = results[row];
           if(record.id) {
             output += '<li><a href="/catalog/record/' + record.id + '"><em>';
             output += record.full_title + '</em></a>.';
             if(record.format) {
                output += record.format + ' ';
             }
             if(record.callnum) {
               output += record.callnum + ' at ';
             }

             if(record.location) {
                output +=  record.location;
             }
             output += '. <a class="btn btn-mini btn-danger" onclick="DropCartItem(this,' + "'" + record.id + "'," + false + ')">';
             output += 'Remove</a>';
           }
           
        }
        output += '</ol>';
        $('#cart-dlg-contents').html(output);
    }
   });

}
