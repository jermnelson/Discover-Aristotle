/**
 * Copyright (c) White Whale Web Services (http://www.whitewhale.net/)
 * but free for any use, with or without modification
 *
 * Version 1.3.4 (2010-10-31)
 *
 * Usage: $('.inputselector').quickaccess(settingsObject);
 * 	where .inputselector selects the container for the search input (so when the element has no other function than quickaccess it isn't shown) OR the search input itself
 *	settingsObject may contain:
 *  links : the selector for the links that are to be searched (i.e. '#linkslist a' or 'a.quickaccess')
 *    To organize results into categories, selector may be an array of objects (i.e. [{selector:'#mammals a',title:'Mammals',className:'mammals'},{selector:'#reptiles a',title:'Reptiles',className:'reptiles'}])
 *  results : the container in which the results will be placed (default:they'll be placed in a .qa_results created immediately after the search box)
 *	forceSelect : when true, an autocomplete option will always be selected; disable, for instance, if you'd like the quickaccess box to also function as a typical search box (default:true)
 *	onSubmit(event,selected) : callback function for when the user hits the enter/return key; by default, this will take them to the selected link (args: the keypress event and the currently selected result)
 *  placeholder : set the HTML5 placeholder attribute on the input (default: none)
 *  maxResults : the maximum number of results to show at any one time (default : 10)
 *  tooMany : the message to show when there are more matching results than maxResults (default : 'Keep typing...')
 *  noneFound : the message to show when no results are found (default : 'No matches found.')
 *  focus : true/false; should the search element grab focus upon page initialization? (default : false)
 *  sort : true/false; should the search results be alphabetized? (default : false)
 *  removeDuplicates : true/false; should duplicate URLs be allowed in the results? (default : false) 
 * Example: $('#quicksearch').quickaccess({selector:'#offices li a', maxResults:10,noneFound:'Sorry, no matching links were found.'});
 **/

(function($){
	$.fn.extend({
		quickaccess  :   function(options) {
			this.each(function() { // for each specified input
				var self = $(this),
					qa = {},
					s = $.extend({ // initialize the settings with their defaults
						links		: '.qa_links a',
						results		: null,
						forceSelect	: true,
						onSubmit	: function(e,selected) { if(selected.length) { e.preventDefault(); window.location=selected.eq(0).find('a').attr('href'); } },
						maxResults	: 10,
						placeholder : null,
						tooMany		: 'Keep typing...',
						noneFound	: 'No matches found.',
						focus		: false,
						sort		: false,
						removeDuplicates : false
					},options);

				if(self.is('input[type=text],textarea')) qa.search=self; // if the specified item is an input element, use it
				else qa.search = $('<input type="text" class="qa_search_query"/>').prependTo(self); // otherwise, add an input inside of it
				
				if(s.placeholder) qa.search.attr('placeholder',s.placeholder); // if a placeholder is specified, add it
				
				if(s.results) qa.results=$(s.results).eq(0); // select the specified container
				else qa.results = $('<div class="qa_results"></div>').insertAfter(qa.search); // otherwise, create a new container
				
				qa.results.addClass('qa_blur'); // initialize the blurred state

				qa.message = $('<div class="qa_message"></div>').appendTo(qa.results).hide(); // create a message div

				var toSpace = new RegExp(/[,\-_\s&\/\\]+/g), // regexp for elements that should become spaces
					toRemove = new RegExp(/[^a-zA-Z 0-9]+/g); // regexp for elements that should be removed

				if(typeof s.links=='string') { // if the selector is not an array of categories
					qa.categories = [{selector:s.links}]; // make it one
				} else { // otherwise
					qa.categories = s.links; // use the selectors as categories
				}

				$.each(qa.categories,function(index,category) { // with each category
					qa.categories[index].results = $('<div class="qa_category'+index+' qa_category'+(category.className ? ' '+category.className : '')+'">'+(category.title ? '<div class="qa_category_title">'+category.title+'</div>' : '')+'</div>').appendTo(qa.results); // append the category div
					qa.categories[index].results_list = $('<ul class="qa_results_list"><li></li></ul>').appendTo(qa.categories[index].results); // and its results list
					qa.categories[index].links = new Array(); // array to store all links
					$(category.selector).each(function() { // with each item
						qa.categories[index].links.push({ // add it to the array
							title : $(this).text(), // the "title"
							keywords : (this.innerHTML).toLowerCase().replace('&amp;','and').replace(toSpace,' ').replace(toRemove,''), // keyword for matching against
							href : $(this).attr('href'),
							category : index
						});					
					});
					if(s.sort) qa.categories[index].links.sort(function(a,b) { // alphabetize
						var la = a.title.toLowerCase(), // toLowerCase for case-insensitive sort; we use a new variable name due to IE bug
							lb = b.title.toLowerCase(); // ditto
						return (la==lb ? 0 : (la>lb? 1 : -1));
					});
					qa.categories[index].matches = qa.categories[index].links; // initialize the set as containing all links
				});

				qa.category_divs = qa.results.find('.qa_category'); // store the set of all the category divs
				qa.results_lists = qa.results.find('.qa_results_list'); // store the set of all results lists

				qa.results_items = $([]); // create an empty jQuery object for the results items

				qa.search.attr('autocomplete','off').keyup(function() { // on each keypress, filter the links
					var raw = $(this).val(),
						query = $.trim(raw.toLowerCase().replace(toSpace,' ').replace(toRemove,'')), // grab query, sanitize it
						subquery; 
					if(query==qa.lastquery) return; // do nothing if the query is unchanged
					if(!query.length || raw == $(this).attr('placeholder')) {
						qa.lastquery='';
						qa.results_lists.html('<li></li>');
						qa.results.addClass('qa_noquery');
						return;
					} else qa.results.removeClass('qa_noquery');
					if(!qa.lastquery||query.indexOf(qa.lastquery)!=0) {  // if this query is NOT a subset of the last query
						$.each(qa.categories,function(index) { // for each category
							qa.categories[index].matches = qa.categories[index].links; // reinitialize the matches and search on all terms
						});
						subquery = query;
					} else subquery = query.substring(query.lastIndexOf(' ')+1,query.length); // otherwise, since this query IS a subset of the last query, no need to search the last query's terms
					qa.lastquery=query;
					var count = 0;
					$.each(subquery.split(' '),function() { // filter the result for each word in the query
						var search = this;
						$.each(qa.categories,function(index) { // for each category
							qa.categories[index].matches = $.grep(qa.categories[index].matches,function(item) { return (' ' + item.keywords).indexOf(' ' + search)>=0; }); // filter out the non-matching links
							count+=qa.categories[index].matches.length;
						});
					});
					var query_exp = new RegExp('(\\b' + raw.replace(toRemove,'.').replace(/\s/g,'|\\b') +')','ig'); // for highlighting the query terms (we compile this before emptying the list for performance)

					qa.message.empty().hide(); // hide the message
					qa.results_lists.empty(); // empty all the results lists
					qa.category_divs.removeClass('qa_nonefound'); // remove none found classes from the categories
					qa.results.removeClass('qa_toomany').removeClass('qa_nonefound'); // and the too many none found class from the main list

					if(count>s.maxResults) qa.message.html(s.tooMany).show().parent().addClass('qa_toomany'); // if there are too many matches, add the message and class
					else if(count==0) {
						qa.message.html(s.noneFound).show().parent().addClass('qa_nonefound'); // if there are no matches, add the message and class
						if(qa.categories.length>1) qa.results_lists.html('<li class="qa_message">'+s.noneFound+'</li>').parent().addClass('qa_nonefound'); // if there's more than one category, add an individual message for each
					} else { // if the matches are just right
						$.each(qa.categories,function(index) { // for each category
							if(!qa.categories[index].matches.length) qa.categories[index].results_list.html('<li class="qa_message">'+s.noneFound+'</li>').parent().addClass('qa_nonefound'); // if there are no matches for this list, add the message and class
							else { // otherwise, if there are matches
								$.each(qa.categories[index].matches,function(i,item) { // with each item
									if(!s.removeDuplicates||!qa.categories[index].results_list.find('a').filter(function() { return $(this).attr('href')==item.href; }).length) { // if duplicates are okay or if there are no duplicates
										qa.categories[index].results_list.append('<li><a href="'+item.href+'">'+(' ' + item.title).replace(query_exp,'<span class="qa_highlight">$1</span>')+'</a></li>'); // list the match, with highlighting
									}
								});
							}
						});
						qa.results_items = qa.results.find('.qa_results_list li:not(.qa_message)'); // store all the items
						if(s.forceSelect) qa.results_items.eq(0).addClass('qa_selected'); // force select the first match
					}
				}).keydown(function(e) { // capture special keys on keydown
					switch(e.keyCode) {
						case 38: // up arrow
							e.preventDefault();
							var selected = qa.results.find('.qa_selected'),
								index = qa.results_items.index(selected);
							selected.removeClass('qa_selected');
							if(index>0) qa.results_items.eq(index-1).addClass('qa_selected');
							else if(s.forceSelect) qa.results_items.eq(qa.results_items.length-1).addClass('qa_selected');
							break;
						case 40: // down arrow
							e.preventDefault();
							var selected = qa.results.find('.qa_selected'),
								index = qa.results_items.index(selected);
							selected.removeClass('qa_selected');
							if(index<qa.results_items.length-1) qa.results_items.eq(index+1).addClass('qa_selected');
							else if(s.forceSelect) qa.results_items.eq(0).addClass('qa_selected');
							break;
						case 13: // enter/return
							var selected = qa.results.find('.qa_selected');
							s.onSubmit.apply(self,[e,selected]);
							break;
					}
				}).focus(function() {
					qa.results.removeClass('qa_blur');
				}).blur(function() {
					setTimeout(function() { qa.results.addClass('qa_blur'); },200); // after 200ms, add the blur class; we use a delay in case the user has clicked in that area
				});

				qa.search.keyup(); // run search in case field is pre-populated (e.g. in Firefox)

				if(s.focus) qa.search.focus(); // put cursor in search box
				
			});

			return this; // return original element for chaining
		}
	});

})(jQuery);