/**
 * Colorado College
 * by White Whale Web Services
 * http://whitewhale.net
 */

var dotBulletsAvailable = 3,
    homepageTimeout,
    homepageFired = false,
    openNav = false;



$(document).ready(function() {
	addCalendarIcons();
	addRandomSubnavigationBullets();
	startNavigationCollapse();
	startPlaceholder();
	startLeftScrapbookScatter();
	startIECSSFixes();
	startWebFontFix();
	startSlideshows();
	startHomepage();
	startQuickAccess();
	startVideoPlayer();
	startBlockTextFitting();
	startBlockFeatureFeature();
	startProgramBrowser();
	startLightboxes();
	startLibrarySearchBoxes();
});


function startWebFontFix() {
	// Chrome on Windows cannot handle the web font because in its version,
	// it is missing an apostrophe — rather than showing it as the default
	// font, it shows the entire line as the default font, not cool; to fix
	// this, we're replacing apostrophes with a non-web-font version
   if (BrowserDetect.browser == 'Chrome' && BrowserDetect.OS == 'Windows') {
		$('*')
			.filter(function() {
				return /neofill/i.test($(this).css('font-family')) && $(this).parents('#main-navigation').length == 0;
			})
			.each(function() {
				// replace apostrophes
				$(this).html($(this).html().replace(/([^>])(?:'|’)([^<])/ig, '$1<span class="no-web-fonts">’</span>$2'));
			});
	}
	
	if (BrowserDetect.browser == 'Opera') {
		$('*')
			.filter(function() {
				return /neofill/i.test($(this).css('font-family')) && $(this).parents('#main-navigation').length == 0;
			})
			.each(function() {
				// replace apostrophes
				$(this).html($(this).html().replace(/([^>])(?:'|’)([^<])/ig, '$1<span class="no-web-fonts">’</span>$2'));

				// replace brackets
				$(this).html($(this).html().replace(/(?:{)/ig, '('));
				$(this).html($(this).html().replace(/(?:})/ig, ')'));
			});
	}
}

/**
 * Adds calendar icons to calendar sidebar items
 */
function addCalendarIcons() {
	var day;
	
	// sidebar
	$('.calendar li')
		.each(function(n) {
			// parse for the date			
			day = $(this).find('em').eq(0).text().match(/([0-9]{1,2})(?:st|nd|rd|th)/i)[1];
			
			// only add icon if we found the day
			if (day) {
				$(this)
					.prepend('<span class="date">' + day + '</span>')
					.addClass('with-icon');
			}
		});
	
	// event-detail header
	$('#events.details #content header')
		.each(function(n) {
			// parse for the date
			day = $(this).find('time').eq(0).text().match(/([0-9]{1,2})(?:, [0-9]{4})/i)[1];
			
			if (day) {
				$('<span>' + day + '</span>').insertBefore($(this).find('hgroup'));
				$(this).addClass('with-icon');
			}
		});
}


/**
 * Adds randomized hand-drawn bullets to subnavigation calendar items
 */
function addRandomSubnavigationBullets() {
	var random, previousRandom = 0;
	
	if ($('#subnavigation').length) {
		$('#subnavigation li')
			.each(function(n) {
				// make a random number in the allowed range
				random = Math.round((Math.random() * (dotBulletsAvailable - 1)) + 1);

				// to ensure we don't get the same bullet twice in a row
				while (dotBulletsAvailable > 1 && random == previousRandom) {
					random = Math.round((Math.random() * (dotBulletsAvailable - 1)) + 1);
				}

				previousRandom = random;
				$(this).addClass('dot' + random);
			});
	}
}


/**
 * Collapses the navigation if appropriate, adds triggers to expand
 */
function startNavigationCollapse() {
	var header = $('#header'),
	    navList = $('#header ul li ul'),
	    openNav = $('#openNav').val();
	
	if (!$('header.collapsed').length) { return; }  // this page is not a collapsed page

	// initiate collapse CSS
	// header.css('height', '78px').data('nav-is-collapsed', true);
	// navList.css('top', '160px');
	
	if (openNav == "true") {
		header.css('height', '209px').data('nav-is-collapsed', false);
		navList.css('top', '0px');
	} else {
		header.css('height', '78px').data('nav-is-collapsed', true);  
		navList.css('top', '160px');
	}
	
	$('#header h5')
		.bind('click', function() {
			// $('#header').data('nav-is-collapsed') is a state-holder
			// for the navigation, we can't use .toggle() since the click
			// events are spread between many ULs
			if (header.data('nav-is-collapsed')) {
				// already collapsed, expand
				header
					.data('nav-is-collapsed', false)
					.stop()
					.animate({'height': '209px'}, 400, 'easeOutBack');
				$('#header h5').css('cursor', 'default');
				navList.each(function(n) {
					// the delay here sets up a fan-like animation
					$(this).stop().delay(50 * n).animate({'top': 0}, 600, 'easeOutBack');
				});
			} else {
				header
					.data('nav-is-collapsed', true)
					.stop()
					.animate({'height': '78px'}, 700, 'easeInOutBack');
				$('#header h5').css('cursor', 'pointer');
				navList.each(function(n) {
					$(this).stop().delay(50 * n).animate({'top': '160px'}, 600, 'easeOutQuad');
				});
			}
		})
		.css('cursor', 'pointer');  // usability cue
}


/**
 * Starts placeholder on all input boxes
 */
function startPlaceholder() {
	$('input[type="text"]').placeholder();
}


/**
 * Scatters left-scrapbook photos a little
 */
function startLeftScrapbookScatter() {
	var basePositions = [ 0, 17, 34 ].shuffle();
	
	$('.left-scrapbook img').each(function(n) {
		var nudge = Math.round(Math.random() * 12) - 6,   // ±6px
		    basePosition = parseInt(basePositions[n % basePositions.length], 10),
		    newMarginRight = basePosition + Math.round(nudge);
		
		$(this).css('margin-right', newMarginRight + 'px');
	});
}


/**
 * Applies styles to certain elements that can't comprehend CSS3
 */
function startIECSSFixes() {
	$('aside.left-scrapbook img:nth-child(6n-4)').addClass('ie-bring-to-front');
	
	$('aside.scrunched img:nth-child(6n-4)').removeClass('ie-bring-to-front');
	$('aside.scrunched img:first-child').addClass('ie-bring-to-front');
	
	$('#block-feature .block-selector li:nth-child(4n)').addClass('ie-remove-margin');
}


/**
 * Sets up and starts Flowplayer
 */
function startVideoPlayer() {
	$('aside.video a, #homepage a.video').each(function(e) {
		// check for a youtube link
		if ($(this).attr('href').match(/youtube\.com/i)) {
			$(this)
				.fancybox({
					type: 'iframe',
					href: 'http://www.youtube.com/embed/' + $(this).attr('href').match(/v=([0-9a-zA-Z_\-]+)&?/i)[1],
					height: 349,
					width: 425,
					transitionIn: 'elastic',
					transitionOut: 'elastic',
					centerOnScroll: true,
					overlayColor: '#292c34',
					overlayOpacity: 0.6,
					padding: 6
				});
		
		// check for a vimeo link
		} else if ($(this).attr('href').match(/vimeo\.com/i)) {
			$(this)
			.fancybox({
				type: 'iframe',
				href: 'http://player.vimeo.com/video/' + $(this).attr('href').match(/com\/([0-9]+)\??/i)[1] + '?title=0&portrait=0&color=ffffff',
				height: 300,
				width: 400,
				transitionIn: 'elastic',
				transitionOut: 'elastic',
				centerOnScroll: true,
				overlayColor: '#292c34',
				overlayOpacity: 0.6,
				padding: 6
			});
		
		// this is a normal, uploaded video, use the local player
		} else {
			$(this)
				.fancybox({
					type: 'iframe',
					href: '/assets/player.php?video=' + $(this).attr('href'),
					scrolling: 'no',
					transitionIn: 'elastic',
					transitionOut: 'elastic',
					centerOnScroll: true,
					overlayColor: '#292c34',
					overlayOpacity: 0.6,
					padding: 6
				});			
		}
	});
}



/**
 * Mimics placeholder in browsers that don't support it
 */
$.fn.extend({ // add plugins
	placeholder: function(options) { // bootstrap HTML5 placeholder attributes for browsers that don't support it
		options = options || {};
		var s = {
			style:options.style || 'placeholder', // the class to add when the element is operating as a placeholder
			clear:options.clear || false // the elements which, when clicked, should wipe the placeholder
		};
		return this.each(function() { // with each matched element
			var self = $(this);
			if (this.placeholder && 'placeholder' in document.createElement(this.tagName)) return; // if the browser supports placeholders for this element, abort
			if (self.data('placeholder')) { // if a placeholder has already been set on this element
				return; // abort to avoid double-binding
			}
			self.data('placeholder',true); // flag this element as having a placeholder, so we'll never double-bind
			var placeholder = self.attr('placeholder') || '',
			clear = function() { // to clear the placeholder
				if (self.val()==placeholder) { // if the text is the placeholder
					self.removeClass(s.style).val(''); // blank the text and remove the placeholder style
				}
			};
			self
				.focus(clear)
				.blur(function() {
					var val = self.val();
					if (!val||val==placeholder) { // if there's no text, or the text is the placeholder
						self.addClass(s.style).val(placeholder); // set the text to the placeholder and add the style
					}
				}).blur(); // and do it now
				self.parents('form').submit(clear);
				$(s.clear).click(clear);
		});
	}
});


/**
 * Slideshows
 */
function startSlideshows() {
	$('aside.slideshow')
		.find('a.more-info')
			.css('display', 'block')
			.click(function(e) {
				e.preventDefault();
				e.stopPropagation();
			})
		.end()
		.each(function(i) {
			var items = $(this).find('li'),
			    list = $(this).find('ul'),
			    areaWidth = list.width(),
			    areaHeight = list.height(),
				 ranges = {
					'moveLeft': {
						'top': {
							'start': ((areaHeight/2) * -1) - 30,
							'end': ((areaHeight/2) * -1) - 10
						},
						'left': {
							'start': ((areaWidth/2) * -1) - 30,
							'end': ((areaWidth/2) * -1) - 10
						},
						'rotate': {
							'start': -30,
							'end': -10
						}
					},
					'moveRight': {
						'top': {
							'start': ((areaHeight/2) * -1) - 30,
							'end': ((areaHeight/2) * -1) - 10
						},
						'left': {
							'start': (areaWidth/2) + 10,
							'end': (areaWidth/2) + 30
						},
						'rotate': {
							'start': 10,
							'end': 30
						}
					}
				 };
			
			list.data('lowest-z-index', 50000);
			list.data('ranges', ranges);
			
			items.each(function(n) {
				var item = $(this),
				    itemWidth = item.width(),
				    itemHeight = item.height(),
				    newZIndex = 50000 - n,
				    newLeft = Math.round((areaWidth - itemWidth) / 2),
				    newTop = Math.round((areaHeight - itemHeight) / 2);
				
				list.data('lowest-z-index', newZIndex);

				$(this)
					.css('left', newLeft)
					.css('top', newTop)
					.data('order', n)
					.data('returnLeftValue', newLeft)
					.data('returnTopValue', newTop)
					.css('z-index', newZIndex);  // way up
			});
		});
	
	
	$('aside.slideshow ul')
		.css('cursor', 'pointer')
		.each(function(k) {
			$(this)
				.click(function(e) {
					var items = $(this).find('li'),
					    highestZIndex = 0,
					    currentItem,
					    range,
					    useLeft,
					    useTop,
					    useRotate;

					items.each(function(n) {
						if ($(this).css('z-index') > highestZIndex) {
							highestZIndex = $(this).css('z-index');
							currentItem = $(this);
						}
					});
					
					// move front-most pic
					range = (currentItem.css('z-index') % 2) ? $(this).data('ranges').moveLeft : $(this).data('ranges').moveRight;
				   useLeft = range.left.start + (Math.random() * (Math.abs(range.left.start - range.left.end))),
				   useTop = range.top.start + (Math.random() * (Math.abs(range.top.start - range.top.end))),
				   useRotate = (BrowserDetect.browser == 'Chrome' || BrowserDetect.browser == 'Safari') ? 0 : range.rotate.start + (Math.random() * (Math.abs(range.rotate.start - range.rotate.end)));
								
					currentItem
						.animate({
							'top': useTop,
							'left': useLeft,
							'rotate': useRotate
						}, 215, 'easeOutCubic', function() {
							var updateZIndex = $(this).parents('ul').data('lowest-z-index') - 1;
							$(this).parents('ul').data('lowest-z-index', updateZIndex);
							$(this).css('z-index', updateZIndex);
							
							$(this)
								.animate({
									'top': $(this).data('returnTopValue'),
									'left': $(this).data('returnLeftValue'),
									'rotate': 0
								}, 255, 'easeInQuad');
						});
				})
				.dblclick(function(e) {
					e.preventDefault();
					return false;
				});
		});
}


/**
 * Homepage picture moving
 */
function startHomepage() {
	if (!$('#homepage').length) {
		return;
	}
	
	// animation
	// -------------------------------------------------------------------------
	$('a.left, a.right')
		.each(function(n) {
			$(this)
				.data('startingLeft', $(this).css('left'))
				.data('startingTop', $(this).css('top'));
		});
		
	homepageTimeout = setTimeout(function() {
		moveHomepageImages();
	}, 3000);
	
	$('a.image, a.video').mouseenter(function() {
		clearTimeout(homepageTimeout);
		moveHomepageImages();
	});
	
	// captions
	// -------------------------------------------------------------------------
	$('#homepage a.left, #homepage a.right')
		.fancybox({
			titlePosition: 'over',
			cyclic: true,
			transitionIn: 'elastic',
			transitionOut: 'elastic',
			centerOnScroll: true,
			overlayColor: '#292c34',
			overlayOpacity: 0.6,
			padding: 6
		});
}


/**
 * Turning on QuickAccess
 */
function startQuickAccess() {
	$('aside.quick-search input.quick-search, #gateway .quick-search input')
		.quickaccess({
			links: '.quick-links a',
			maxResults: 5
		});
	
	// position qa_results
	positionPageQA();
	$(window).resize(function() {
		positionPageQA();
	});
	
	$('#header form .text-box input')
		.quickaccess({
			links: '.quick-links a',
			maxResults: 5,
			results: '#page_qa_results'
		});
}


/**
 * Positions the page-level QuickAccess
 */
function positionPageQA() {
	$('#page_qa_results')
		.css('top', parseInt($('#header form .text-box input').offset().top, 10) + $('#header form .text-box input').height() + 10)
		.css('right', $(window).width() - parseInt($('#header form .text-box input').offset().left, 10) - $('#header form .text-box input').width() - 8);
}



/**
 * Triggers the homepage images to move
 */
function moveHomepageImages() {
	if (homepageFired) {
		return;
	}
	
	homepageFired = true;
	
	$('.left.position-ne').animate({'left': '-=260' }, 500, 'easeOutCirc');
	$('.left.position-nw').animate({'left': '-=60' }, 500, 'easeOutCirc');
	$('.left.position-sw').animate({'left': '-=140' }, 500, 'easeOutCirc');
	$('.left.position-se').animate({'left': '-=190' }, 500, 'easeOutCirc');
	$('.right.position-ne').animate({'left': '+=80' }, 500, 'easeOutCirc');
	$('.right.position-nw').animate({'left': '+=190' }, 500, 'easeOutCirc');
	$('.right.position-sw').animate({'left': '+=257' }, 500, 'easeOutCirc');
	$('.right.position-se').animate({'left': '+=100' }, 500, 'easeOutCirc');
}


/**
 * Attempts to fit the block text onto one line
 */
function startBlockTextFitting() {
	var currentBlock = $('#block .current-block'),
	    blockText = currentBlock.text();
	
	currentBlock.css('visibility', 'hidden').prepend('<span>' + blockText + '</span>');
	
	// adjusts text to fit as large as possible but be on one line
	do {
		currentBlock
			.css('font-size', parseInt(currentBlock.css('font-size'), 10) - 1);
	} while (currentBlock.height() > parseInt(currentBlock.css('font-size'), 10) * 1.1);
	
	currentBlock
		.css('font-size', parseInt(currentBlock.css('font-size'), 10) * 0.9)
		.css('visibility', 'visible');
}


/**
 * Makes the feature section for block feature page
 */
function startBlockFeatureFeature() {
	if (!$('#block-feature').length) {
		return;
	}
	
	var tabs = $('<ul id="tabs"></ul>'),
	    visuals = $('<ul id="visuals"></ul>'),
	    featuredCourseList = $('<div id="featured-courses"><h4>Featured Courses</h4></div>');

	// create a playground for tab area
	$('.block-highlights hgroup')
		.after('<div id="feature-highlights"></div>');

	// create tabs
	$('ul.featured-courses')
		.children('li')
		.each(function(i) {
			var visualItem = $('<li></li>'),  
			    tabItem = $('<li></li>')
			    backgroundImage = $(this).children('img').attr('src');
			
			// visuals
			visualItem
				.css('background-image', 'url(' + backgroundImage + ')')
				.append('<div class="description">' + $(this).children('.description').html() + '</div>')
				.attr('id', 'visual-' + i);			
			visuals.append(visualItem);
			
			// tabs
			tabItem
				.html('<a href="#">' + $(this).children('h3').html() + '</a>')
				.data('trigger-id', i);
			tabs.append(tabItem);
			featuredCourseList.append(tabs);
		});
	
	$('#feature-highlights')
		.append(visuals)
		.append(featuredCourseList)
		.append('<span class="clear"></span>');
	
	$('.featured-courses').css('display', 'none');
	
	// we need a reference point for swapping z-indexes
	$('#feature-highlights #tabs').data('tabsLastZIndex', 10);
	
	$('#feature-highlights #tabs a')
		.click(function(e) {
			var index = $(this).parent().data('trigger-id'),
			    newZIndex = $('#feature-highlights #tabs').data('tabsLastZIndex');

			$('#feature-highlights #tabs').data('tabsLastZIndex', newZIndex + 1);

			$('#feature-highlights #tabs li')
				.each(function(i) {
					if ($(this).data('trigger-id') == index) {
						$(this).addClass('on');
						$('#visual-' + $(this).data('trigger-id')).stop().fadeTo(600, 1).css('z-index', newZIndex);
					} else {
						$(this).removeClass('on');
						$('#visual-' + $(this).data('trigger-id')).stop().fadeTo(600, 0);
					}
				});
			
			return false;
		});
	
	
	$('#feature-highlights #tabs li:first-child a').click();
}


/**
 * Drop-down action for the program browser
 */
function startProgramBrowser() {
	$('#program-browser p')
		.toggle(
			function(e) {
				$(this)
					.parents('#program-browser')
					.find('.programs')
						.slideDown(500, 'easeOutCubic');
			},
			function(e) {
				$(this)
					.parents('#program-browser')
					.find('.programs')
						.slideUp(500, 'easeOutCubic');					
			}
		);
}


/**
 * Adds fancybox lightbox to all links with the class "lightbox"
 */
function startLightboxes() {
	$('a.lightbox').fancybox({
		titlePosition: 'over',
		cyclic: true,
		transitionIn: 'elastic',
		transitionOut: 'elastic',
		centerOnScroll: true,
		overlayColor: '#292c34',
		overlayOpacity: 0.6,
		padding: 6
	});
}


/**
 * Starts the library drop downs
 */
function startLibrarySearchBoxes() {
	if (!$('#search-library, #searchbox').length)  { return; }
	
	$('input[type="button"]')
		.click(function() {
			var searchForm = $(this).parents('form');
			var searchBox = searchForm.find('.search-types');

			searchBox.css('display', (searchBox.css('display') == 'block') ? 'none' : 'block');
		})
		.each(function(i) {
			positionSearchTypeDropDown($(this));
		});
	
	$('.search-types a')
		.click(function(e) {
			e.preventDefault();
		
			$(this)
				.parents('form')  // update search button value
					.find('input[type="submit"]').val('Search ' + $(this).text())
				.end()
					.find('.search-types')  // hide drop down
					.css('display', 'none')
				.end()
					.find('input[name="search-type"]')
					.val($(this).data('searchtype'));
			
			positionSearchTypeDropDown($(this).parents('form').find('input[type="button"]'));
			
			return false;
		});
}

/**
 * Positions the search type drop down on library pages
 */
function positionSearchTypeDropDown(el) {
	var formWidth = el.parents('form').width();
	
	el
		.parents('form')
		.find('.search-types')
			.css({
				top: parseInt(el.position().top, 10) + el.height() + 17,
				right: formWidth - (parseInt(el.position().left, 10) + el.width() + parseInt(el.css('padding-right'), 10) + parseInt(el.css('padding-left'), 10) + 2)
			});
}



/**
 * Browser detection, used to fix web fonts unfortunately
 * source: http://www.quirksmode.org/js/detect.html
 */
var BrowserDetect = {
	init: function () {
		this.browser = this.searchString(this.dataBrowser) || "An unknown browser";
		this.version = this.searchVersion(navigator.userAgent)
			|| this.searchVersion(navigator.appVersion)
			|| "an unknown version";
		this.OS = this.searchString(this.dataOS) || "an unknown OS";
	},
	searchString: function (data) {
		for (var i=0;i<data.length;i++)	{
			var dataString = data[i].string;
			var dataProp = data[i].prop;
			this.versionSearchString = data[i].versionSearch || data[i].identity;
			if (dataString) {
				if (dataString.indexOf(data[i].subString) != -1)
					return data[i].identity;
			}
			else if (dataProp)
				return data[i].identity;
		}
	},
	searchVersion: function (dataString) {
		var index = dataString.indexOf(this.versionSearchString);
		if (index == -1) return;
		return parseFloat(dataString.substring(index+this.versionSearchString.length+1));
	},
	dataBrowser: [
		{
			string: navigator.userAgent,
			subString: "Chrome",
			identity: "Chrome"
		},
		{ 	string: navigator.userAgent,
			subString: "OmniWeb",
			versionSearch: "OmniWeb/",
			identity: "OmniWeb"
		},
		{
			string: navigator.vendor,
			subString: "Apple",
			identity: "Safari",
			versionSearch: "Version"
		},
		{
			prop: window.opera,
			identity: "Opera"
		},
		{
			string: navigator.vendor,
			subString: "iCab",
			identity: "iCab"
		},
		{
			string: navigator.vendor,
			subString: "KDE",
			identity: "Konqueror"
		},
		{
			string: navigator.userAgent,
			subString: "Firefox",
			identity: "Firefox"
		},
		{
			string: navigator.vendor,
			subString: "Camino",
			identity: "Camino"
		},
		{		// for newer Netscapes (6+)
			string: navigator.userAgent,
			subString: "Netscape",
			identity: "Netscape"
		},
		{
			string: navigator.userAgent,
			subString: "MSIE",
			identity: "Explorer",
			versionSearch: "MSIE"
		},
		{
			string: navigator.userAgent,
			subString: "Gecko",
			identity: "Mozilla",
			versionSearch: "rv"
		},
		{ 		// for older Netscapes (4-)
			string: navigator.userAgent,
			subString: "Mozilla",
			identity: "Netscape",
			versionSearch: "Mozilla"
		}
	],
	dataOS : [
		{
			string: navigator.platform,
			subString: "Win",
			identity: "Windows"
		},
		{
			string: navigator.platform,
			subString: "Mac",
			identity: "Mac"
		},
		{
			   string: navigator.userAgent,
			   subString: "iPhone",
			   identity: "iPhone/iPod"
	    },
		{
			string: navigator.platform,
			subString: "Linux",
			identity: "Linux"
		}
	]

};
BrowserDetect.init();



/**
 * Adds shuffle functionality to Arrays
 * source: http://javascript.about.com/library/blshuffle.htm
 */
Array.prototype.shuffle = function() {
	var s = [];
	while (this.length) {
		s.push(this.splice(Math.random() * this.length, 1));
	}
	while (s.length) {
		this.push(s.pop());
	}
	return this;
}