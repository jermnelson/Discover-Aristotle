<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8" />
		<title>Colorado College Video Player</title>
		
		<style>
			html, body { margin: 0; padding: 0; height: 100%; overflow: hidden; }
			#player { height: 100%; width: 100%; display: block; margin: 0; padding: 0; }
			object { margin: 0; padding: 0; }
		</style>
	</head>
	<body>
		<a id="player" href="#"></a>
		
		<script src="/scripts/flowplayer-3.2.6.min.js"></script>
		<script src="/scripts/jquery.js"></script>
		<script>
			$(document).ready(function() {
				$('#player')
					.attr('href', '<?php echo 'http://' . $_SERVER['HTTP_HOST']; ?><?php echo (isset($_GET['video']) && $_GET['video']) ? $_GET['video'] : '' ?>');

				flowplayer('player', 'http://releases.flowplayer.org/swf/flowplayer-3.2.7.swf');
			});
		</script>
	</body>
</html>