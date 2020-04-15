#!/usr/bin/perl -w

use strict;
# Dependencies ###################################
use FileHandle qw();
use File::Basename qw();
use Cwd qw();
my $base_dir;
my $relative_path;
BEGIN {
   $relative_path = './';
   $base_dir = Cwd::realpath(File::Basename::dirname(__FILE__) . '/' . $relative_path);
}
# Dependencies ####################################
use lib "$base_dir/lib64/perl5";
use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser) ;
use YAML::XS qw(LoadFile Load);
##################################################

# Version Info ###################################
my $VERSION = "1.1.0";
##################################################


package ASE;
sub new {
	my $class = shift;
	my $web_url = shift;
    my $home_button = shift;
	my $nav = shift;
	my $self = {};
    $self->{web_url} = $web_url;
	$self->{home_button} = $home_button;
	$self->{nav} = $nav;
	return bless $self;
}

#changes to READ from stdin
#MK - 18 Feb 2020 
sub executequery {
	my $self = shift;
	my $scriptfile = shift;
	my $resultfile = shift;

	# Execute Query ###############################
	my $cmd="$scriptfile" ;	

	# Read Result File ###############################
	my $OS_ERROR;
	open(IN,"$cmd |") or die "can't run command '$cmd',$OS_ERROR\n"; 
	my @items = ();
	while (my $line = <IN>) {
		chomp($line);
		$line = $self->trimwhitespace($line);
		push(@items, $line);
	}
	close(IN);
	my $CHILD_ERROR;
	die "$cmd returned error: $CHILD_ERROR \n" if $CHILD_ERROR;


	return @items;
}


sub executeasequery {
	my $self = shift;
	my $scriptfile = shift;
	my $resultfile = shift;
	my $script_args = shift;
	my $OS_ERROR;
	my $CHILD_ERROR;

	# Execute Query ###############################
	my $cmd = "$scriptfile $script_args";	

	open(IN,"$cmd |") or die "can't run command '$cmd',$OS_ERROR\n";

	# Read Result File ###############################
	my @aseitems = ();
	while (my $line = <IN>) {
		chomp($line);
		$line = $self->trimwhitespace($line);
		push(@aseitems, $line);
	}
	$self->{aseitems} = \@aseitems;
	close(IN);
	my $CHILD_ERROR;
	die "$cmd returned error: $CHILD_ERROR \n" if $CHILD_ERROR;

}
sub executescript {
	my $self = shift;
	my $q = shift;
	my $scriptfile = shift;
	my $resultfile = shift;
	my $row_number = shift;

	my @param_keys = $q->param;
	my $arglist = "";
	for my $param (@param_keys) {
		my $value = $q->param("$param");
		if ($param =~ m/(.)+_field/) {	
		} elsif ($param eq 'Action' || $param eq 'Nav' || $param !~ m/(.)+_${row_number}_(\d)+/) {
			next;
		}
		
		$arglist = "$arglist \"$value\"";
	}

	# Execute Query #################################
	my $cmd = "$scriptfile $arglist";
	
	# Read Result File ##############################
	my $result = "";
	my $OS_ERROR;
	open(IN,"$cmd |") or die "can't run command '$cmd',$OS_ERROR\n";
	
	my $line = <IN>; 
	chomp($line);

	$result = $line;

	close(IN);
	my $CHILD_ERROR;
	die "$cmd returned error: $CHILD_ERROR \n" if $CHILD_ERROR;
				
	print "<span id='status-result'>$result</span>\n";
}

sub trimwhitespace {
	my $self = shift;
	my $stringtotrim = shift;

	$stringtotrim =~ s/^\s+//g;
	$stringtotrim =~ s/\s+$//g;

	return $stringtotrim;
}

# Display Methods ########################################################
sub displayerror {
	my $self = shift;
	my $message = shift;
	print <<MESSAGE
	<p>Error: $message</p>
MESSAGE
}
sub displayheader {
	my $self = shift;
	my $title = shift;
	my $subtitle = shift;
	my $menu_font = shift;
	my $timeout_mins = 1;

print <<HEADER;
<!DOCTYPE html>
<html>
<head>
   <title>$subtitle</title>
   <meta charset="iso-8859-1">
   <meta http-equiv="X-UA-Compatible" content="IE=edge">
   <link rel='stylesheet' href='//code.jquery.com/ui/1.12.1/themes/dark-hive/jquery-ui.css'>
   <style type="text/css">
   body {
      background-color: #fff;
      padding: 0;
	  margin: 0;
   }
   div.outer {
     min-height: 400px;
	 min-width: 326px;
   }
   span#title-text {
     color: #fff;
     font-size: 24pt;
     font-family: Verdana, Arial, Helvetica, sans-serif;
     font-weight: bold;
     padding: 0 10px 0 10px;
   }
   span#sub-title-text {
     color: #214888;
     font-size: 18pt;
     font-family: Verdana, Arial, Helvetica, sans-serif;
     font-weight: bold;
     padding: 10px 25px 10px 25px;
     display: block;
   }
   div#home-button {
	 float: right;
     padding: 10px 25px 10px 25px;
   }
   div.header-row {
     background-color: #214888;
     color: #fff;
      width: 100%;
      display: block;
      float: left;
      border: 1px dotted green;
   }
   div.sub-header-row {
	  width: 100%;
	  display: block;
      float: left
   }
   
   div.header-row a {
     color: #fff;
	 padding: 0 10px 0 10px; 
   }
   div#menurow {
     background-color: #000;
     visibility: hidden;
   }
   table.inner {
     border: 1px solid #eee;
     margin: 25px 25px 10px 25px;
   }
   table.inner li {
     max-width: 800px;
   }
   form {
	  padding: 10px;
   }
   input, label {
      margin: 3px;
      padding: 3px 10px 5px 10px;
   }
   label {
	  width: 75px;
      font-weight: bold;
	  text-align: right;
   }
   input {
	  border-radius: 6px;     
   }
   input.text {
      width: auto;
   }
   input.number,
   input.list {
      width: 50;
   }
   input.date {
      width: 80px;
   }
   input.text {
      text-align: left;
   }
   input.number {
	  text-align: right;
   }
   .column-label {
      padding: 2px 5px 2px 5px;
	  border: 2px solid #aaa;
   }
   td {
      margin: 0;
   }
   th {
	  font-family: Verdana, Arial, Helvetica, sans-serif;
	  padding: 2px 10px 2px 10px;
      text-align: left;
   }
   p.error {
	  color: #f00;
   }
   table.display-table {
      border-top: 1px solid #eee;
      border-right: 1px solid #eee;
   }
   table.display-table th,
   table.display-table td {
      border-left: 1px solid #eee;
	  border-bottom: 1px solid #eee;
   }
   a:hover {
      font-weight: bold;
   }
   a, a:visited {
	   color: #4286f4;
   }
   a#glossary_button:hover {
      text-decoration: underline;
	  cursor: pointer
   }
   td.query-field input {
	  width: 275px;
   }
   td {
      font-size: 12pt;
	  font-family: Arial, Helvetica, sans-serif;
   }
   tr.even-row {
      background-color: #eee;
   }
   tr.odd-row {
      background-color: #fff;
   }
   td#stat-graph-col {
      background-color: #fefefe;
   }
   td.edit-box {
      text-align: center;
      white-space: nowrap;
   }
   td.edit-box input {
	  margin: 0 10px 0 0;
   }
   td.edit-box label {
	  text-align: left;
   }
   .ui-menu-item-wrapper {
      background: #fff;
      color: #000;
   }
   div#menurow .ui-menu-item-wrapper {
      background: #000;
      color: #fff;
   }
   div#logout-button {
      float: right;
      margin: 0 25px 0 25px;
   }
   
   div.report {
	  font-family: 11pt monospace, sans-serif;
	  border: 1px solid #eee;
	  background-color: #f6f8fa;
   }
   .bold-text {
      font-weight: bold;
   }
   input.execute-button {
	  min-width: 90px;
   }
   .ui-menu-item-wrapper {
     font-size: $menu_font !important;
   }
   .ui-menu-icons .ui-menu-item-wrapper {
     padding-left: .5em;
   }
   div#menurow tr {
     white-space: nowrap;
   }
   .noclose .ui-dialog-titlebar-close
   {
     display:none;
   }
   </style>
	<!-- MK : Tooltip CSS - Added 13/Feb/2020 -->
	<style>
	.tooltip {
	  position: relative;
	  display: inline-block;
	  #border-bottom: 1px dotted black;
	}
	.tooltip .tooltiptext {
	  visibility: hidden;
	  width: 300px;
	  background-color: black;
	  color: #fff;
	  text-align: center;
	  border-radius: 6px;
	  padding: 5px 0;
	  position: absolute;
	  z-index: 1;
	  top: 150%;
	  left: 50%;
	  margin-left: -150px;
	}
	.tooltip .tooltiptext::after {
	  content: "";
	  position: absolute;
	  bottom: 100%;
	  left: 50%;
	  margin-left: -5px;
	  border-width: 5px;
	  border-style: solid;
	  border-color: transparent transparent black transparent;
	}
	.tooltip:hover .tooltiptext {
	  visibility: visible;
	}
	<!-- Tooltip CSS 13/Feb/2020 - done -->
	</style>
   <script src='https://code.jquery.com/jquery-1.12.4.js'></script>
   <script src='https://code.jquery.com/ui/1.12.1/jquery-ui.js'></script>
   <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.7.2/Chart.bundle.min.js"></script>
   <script>
		function getCookie(key) {
            var keyValue = document.cookie.match("(^|;) ?" + key + "=([^;]*)(;|\$)");
            return keyValue ? keyValue[2] : null;
        }
		function setCookie(key, value) {
      	    var expires = new Date();
        	expires.setTime(expires.getTime() + ($timeout_mins * 1000));
        	document.cookie = key + '=' + value + ';expires=' + expires.toUTCString();
      	}
   </script>
</head>
<body>
<div class="outer">
HEADER
;
   if ($self->{nav} eq '1') {
	print <<HEADERTITLE
   <div class='header-row'>
      <span id="title-text">$title</span>
   </div>
HEADERTITLE
;
   }
}

sub displaysubheader {
	my $self = shift;
	my $header_text = shift;

    print "<div class='sub-header-row'>";
    if ($self->{nav} ne "1") {
      print "<div id='home-button'><a href='$self->{home_button}' >Home</a></div>";
    }

	print <<SUBHEADER
	  <span id="sub-title-text">$header_text</span>
   </div>
SUBHEADER
;
}
sub displaymenusection {
	my $self = shift;
	my @menu = shift;

	if ($self->{nav} ne "1") {
		return;
    }

	print <<MENUHEADER
    <script src='https://code.jquery.com/jquery-1.12.4.js'></script>
	<script src='https://code.jquery.com/ui/1.12.1/jquery-ui.js'></script>
	<div id='menurow'>
    <table><tr>
MENUHEADER
;

	my $depth = 0;
	$self->displaymenu(\@menu, $depth);
	
	print <<MENUEND
    </tr></table>
	</div>
	<script>
		jQuery("ul.ssc-menu").each(function () {
			jQuery(this).menu();
            jQuery(this).menu("option", "position", { my: "left top", at: "center bottom"});
		})
		jQuery("div#menurow").css("visibility","visible");
	</script>
MENUEND
;	
}
sub displaymenu {
	my $self = shift;
	my $menu_ptr = shift;
	my @menu = @{$menu_ptr};
	my $depth = shift;

	my $listcount = 0;
	my $listmax = 0;
	while (my $menu_item = $menu[0][$listmax]) {
		$listmax++;
	}
	while (my $menu_item = $menu[0][$listcount]) {
		my $item_name = $menu_item->{name} ;
		my $item_type = $menu_item->{type};
		if (lc $item_type eq 'menu') {
			my @menuitems = $menu_item->{items};
			if ($depth == 0) {
				print "<td><ul class='ssc-menu'>\n";
				print "<li><div>$item_name</div>\n";
				$self->displaymenu(\@menuitems, $depth + 1);
				print "</li>\n";
				print "</ul></td>\n";
			} else {
                if ($listcount == 0) {
					print "<ul class='ssc-menu'>\n";
                }
				print "<li><div>$item_name</div>\n";
				$self->displaymenu(\@menuitems, $depth + 1);
				print "</li>\n";

				if ($listcount == $listmax-1) {
					print "</ul>\n";
				}
			}
		} elsif (lc $item_type eq 'link') {
			my $link = $menu_item->{url};
			if ($depth == 0) {
				print "<ul class='ssc-menu'>\n";
				print "<li><div><a href='$link'>$item_name</a></div></li>\n";
				print "</ul>\n";
			} else {
                if ($listcount == 0) {	
					print "<ul>\n";
				}
				print "<li><div><a href='$link'>$item_name</a></div></li>\n";
				if ($listcount == $listmax-1) {
					print "</ul>\n";
				}
			}
		}
		$listcount++;
	}
}

# MK - 13/Feb/2020 Export To CSV - Function Added 
# MK - 13/Feb/2020 Sends HTML headers for download as CSV
sub displayexportheaderForCSV {
	my $self = shift;
	print "Content-Type:application/x-download\n";
	print "Content-Disposition:attachment;filename=file.csv\n\n";
}
#MK - 13/Feb/2020 Export header code complete

#MK - 13/Feb/2020 Original Source Function - Was used for showing HTML Export - Not In Use.
sub displayexportheader {
	my $self = shift;

print <<HEADER;
<!DOCTYPE html>
<html>
<head>
   <title>Export</title>
   <meta charset="iso-8859-1">
   <meta http-equiv="X-UA-Compatible" content="IE=edge">
   <link rel='stylesheet' href='//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css'>
   <style type="text/css">
   body {
      background-color: #fff;
   }
   h1 {
      color: #666699;
	  font-family: Verdana, Arial, Helvetica, sans-serif;
	  padding: 0 10px 0 10px; 
   }
   td.table-heading {
      border: 1px solid #eee;
   }
   table.outer {
      width: 710px;  
      border: none;
   }
   form {
	  padding: 10px;
   }
   input, label {
      margin: 3px;
      padding: 3px 10px 5px 10px;
   }
   label {
	  width: 75px;
      font-weight: bold;
	  text-align: right;
   }
   input {
	  border-radius: 6px;     
   }
   input.text,
   input.number,
   input.list {
      width: 50px;
   }
   input.date {
      width: 80px;
   }
   input.text {
      text-align: left;
   }
   input.number {
	  text-align: right;
   }
   .column-label {
      padding: 2px 5px 2px 5px;
	  border: 2px solid #aaa;
   }
   .column-label,
   table.inner {
	  min-width: 710px;
	  border-top-left-radius: 6px;
  	  border-top-right-radius: 6px;
	  border-bottom-left-radius: 6px;
  	  border-bottom-right-radius: 6px;
      background: white;	
   }
   table.inner {
      box-shadow: 1px 2px 4px rgba(0, 0, 0, .5);
   }
   td {
      margin: 0;
   }
   th {
	  font-family: Verdana, Arial, Helvetica, sans-serif;
	  padding: 2px 10px 2px 10px;
   }
   th.table-header,
   tr.header-row {
      background-color: #4286f4;
      color: #fff;
	  font-size: 14pt;
      text-align: center;
   }
   tr {
	  white-space: nowrap;
   }
   p.error {
	  color: #f00;
   }
   table.display-table {
      border-right: 1px solid #eee;
   }
   table.display-table td {
      border-left: 1px solid #eee;
	  border-bottom: 1px solid #eee;
   }
   a:hover {
      font-weight: bold;
   }
   a, a:visited {
	   color: #4286f4;
   }
   a#glossary_button:hover {
      text-decoration: underline;
	  cursor: pointer
   }
   td.query-field input {
	  width: 275px;
   }
   td {
      font-size: 12pt;
	  font-family: Arial, Helvetica, sans-serif;
   }
   tr.even-row {
      background-color: #eee;
   }
   tr.odd-row {
      background-color: #fff;
   }
   td#stat-graph-col {
      background-color: #fefefe;
   }
   td.edit-box {
      text-align: center;
      white-space: nowrap;
   }
   td.edit-box input {
	  margin: 0 10px 0 15px;
   }
   td.edit-box label {
	  text-align: left;
   }
   div#logout-button {
      float: right;
      margin: 0 25px 0 25px;
   }
   
   div.report {
	  font-family: 11pt monospace, sans-serif;
	  border: 1px solid #eee;
	  background-color: #f6f8fa;
   }
   .bold-text {
      font-weight: bold;
   }
   input.execute-button {
	  min-width: 90px;
   }
   </style>
   <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.7.2/Chart.bundle.min.js"></script>
   <script>
		function getCookie(key) {
            var keyValue = document.cookie.match("(^|;) ?" + key + "=([^;]*)(;|\$)");
            return keyValue ? keyValue[2] : null;
        }
		function setCookie(key, value) {
      	    var expires = new Date();
        	expires.setTime(expires.getTime() + 1000);
        	document.cookie = key + '=' + value + ';expires=' + expires.toUTCString();
      	}
   </script>
</head>
<body>
<div id="logout-button"><a href="javascript:window.close()" >close</a></div>
HEADER
;
}

#MK - 13/Feb/2020 Export to CSV - Added
sub renderQueryResultAsCSV {
	my $self = shift;
	my $q = shift;
	my $column_ptr = shift;
	my $dbquery_script = shift;
	my $query_result = shift;

	my @columns = @{$column_ptr};
	my $column_count = 0;
	my @columnNames = ();
	while (my $column = $columns[0][$column_count]) {
		push(@columnNames,$column->{name});
		$column_count++;
	}

	print join(',',@columnNames),"\r\n";
	# build args to pass to db query script
	my @param_keys = $q->param;
	my $arglist = "";
	for my $param (@param_keys) {
		if ($param eq 'Action') {
			next;
		}elsif ($param eq 'Nav') {
			next;
		} 
		elsif ($param eq 'debug') {
			$self->{debugmode} = 1;
			next;
		}
		my $value = $q->param("$param");
	
		# Separate 
		if ($param eq "AIT") {
			my @tokens = split /,/, $value;
			$value = $tokens[0];
			$value = $self->trimwhitespace($value);
		}
		$arglist = "$arglist \"$value\"";
	}

	$self->executeasequery($dbquery_script, $query_result, $arglist);

	#Print CSV to browser output.
	my @aseitems = @{$self->{aseitems}};
	for my $ase (@aseitems) {
		print $ase;
		print "\r\n";
	}
}

#MK - 13/Feb/2020 - Method used earlier for export as HTML  - not in use.
sub displayquerytable {
	my $self = shift;
	my $q = shift;
	my $column_ptr = shift;
	my $dbquery_script = shift;
	my $query_result = shift;

	print "<table class='display-table'><tr class='export-row' id='row_0'>";
	my @columns = @{$column_ptr};
	$self->{column_types} = ();
	my %column_types;
	my $column_count = 0;
	while (my $column = $columns[0][$column_count]) {
		my $column_arg = $column->{name};
		$column_arg =~ s/\s/_/g;
		$self->displayheadercolumn($column->{name}, $column_count);
		$self->{column_types}{$column_count} = $column->{type};
		$column_count++;
	}

	# build args to pass to db query script
	my @param_keys = $q->param;
	my $arglist = "";
	for my $param (@param_keys) {
		if ($param eq 'Action') {
			next;
		} elsif ($param eq 'debug') {
			$self->{debugmode} = 1;
			next;
		}
		my $value = $q->param("$param");
	
		# Separate 
		if ($param eq "AIT") {
			my @tokens = split /,/, $value;
			$value = $tokens[0];
			$value = $self->trimwhitespace($value);
		}
		$arglist = "$arglist \"$value\"";
	}
	$self->executeasequery($dbquery_script, $query_result, $arglist);
	print "</tr>";
	my @aseitems = @{$self->{aseitems}};
	my $row_counter = 0;
	my $column_counter = 0;
	for my $ase (@aseitems) {
		$column_counter = 0;
		my $rowid = $row_counter + 1;
		print "<tr class='export-row' id='row_$rowid'>";
		for my $i (0..($column_count-1)) {
			my @tokens = split /,/, $ase;
			$self->displaylabelcolumnread($tokens[$i], $rowid, $i);
			$column_counter++;
		}
		print "</tr>";
		$row_counter++;
	}
	print "</table>";
}
sub displayasedisplaytable {
	my $self = shift;
	my $q = shift;
	my $column_ptr = shift;
	my $dbquery_script = shift;
	my $query_result = shift;

	print "<table><tr><td><form id='table-form' action='$self->{web_url}' method='get'><table class='display-table'><tr class='export-row' id='row_0'>";
    if ($self->{nav} eq "1") {
		print "<input id='nav' type='hidden' name='Nav' value='$self->{nav}'>";
    }
	my @columns = @{$column_ptr};
	$self->{column_types} = ();
	my %column_types;
	my $column_count = 0;
	while (my $column = $columns[0][$column_count]) {
		my $column_arg = $column->{name};
		$column_arg =~ s/\s/_/g;
		$self->displayheadercolumn($column->{name}, $column_count);
		$self->{column_types}{$column_count} = $column->{type};
		$column_count++;
	}
	print <<ADJUSTHEADER
	<script>
		jQuery(document).ready(function() {
			jQuery("th#title-header").attr('colspan', $column_count);
		});
	</script>
ADJUSTHEADER
;
	# build args to pass to db query script
	my @param_keys = $q->param;
	my $arglist = "";
	for my $param (@param_keys) {
		if ($param eq 'Action') {
			next;
        } elsif ($param eq 'Nav') {
			next;
		} elsif ($param eq 'debug') {
			$self->{debugmode} = 1;
			next;
		}
		my $value = $q->param("$param");
	
		# Separate 
		if ($param eq "AIT") {
			my @tokens = split /,/, $value;
			$value = $tokens[0];
			$value = $self->trimwhitespace($value);
		}
		print "<input type='hidden' name='${param}_field' value='$value'>\n";
		$arglist = "$arglist \"$value\"";
	}
	$self->executeasequery($dbquery_script, $query_result, $arglist);
	print "</tr>";
	my @aseitems = @{$self->{aseitems}};
	my $row_counter = 0;
	my $column_counter = 0;
	for my $ase (@aseitems) {
		$column_counter = 0;
		my $rowid = $row_counter + 1;
		print "<tr class='export-row' id='row_$rowid'>";
		for my $i (0..($column_count-1)) {
			my @tokens = split /,/, $ase;
			$self->displaylabelcolumnread($tokens[$i], $rowid, $i);
			$column_counter++;
		}
		print "</tr>";
		$row_counter++;
	}
	print "</table></form></td></tr></table>";
}
sub displayasetable {
	my $self = shift;
	my $q = shift;
	my $column_ptr = shift;
	my $dbquery_script = shift;
	my $query_result = shift;

	print "<table id='inner' class='inner'><tr><td><form id='table-form' action='$self->{web_url}' method='get'><table><tr>";
    if ($self->{nav} eq "1") {
		print "<input id='nav' type='hidden' name='Nav' value='$self->{nav}'>";
    }
	
	my @columns = @{$column_ptr};
	$self->{column_types} = ();
	my %column_types;
	my $column_count = 0;
	while (my $column = $columns[0][$column_count]) {
		my $column_arg = $column->{name};
		$column_arg =~ s/\s/_/g;
		$self->displayheadercolumn($column->{name}, $column_count);
		$self->{column_types}{$column_count} = $column->{type};
		$column_count++;
		if ($column_count == 1) {
			$self->displayheadercolumn("", $column_count);
		}
	}


	print <<ADJUSTHEADER
	<script>
		jQuery(document).ready(function() {
			jQuery("th#title-header").attr('colspan', $column_count);
		});
	</script>
ADJUSTHEADER
;
	# build args to pass to db query script
	my @param_keys = $q->param;
	my $arglist = "";
	my $mode = "";
	for my $param (@param_keys) {
		if ($param eq 'Action') {
		 	$mode = $q->param('Action');
			next;
        } elsif ($param eq 'Nav') {
			next;
		} elsif ($param eq 'debug') {
			$self->{debugmode} = 1;
			next;
		}
		my $value = $q->param("$param");
	
		# Separate 
		if ($param eq "AIT") {
			my @tokens = split /,/, $value;
			$value = $tokens[0];
			$value = $self->trimwhitespace($value);
		}
		print "<th><input type='hidden' name='${param}_field' value='$value'></th>\n";
		$arglist = "$arglist \"$value\"";
	}
	$self->executeasequery($dbquery_script, $query_result, $arglist);
	print "</tr>";
	my @aseitems = @{$self->{aseitems}};
	my $row_counter = 0;
	my $column_counter = 0;
	for my $ase (@aseitems) {
		$column_counter = 0;
		if (lc $mode eq "create" && $row_counter == 0) {
			print "<tr id='entry_$row_counter'>";
			for my $i (0..($column_count-1)) {
				if ($self->{column_types}{$i} eq 'text') {
					my $column_size = $columns[0][$i]->{size};
					$self->displaytextcolumn("", "text_${row_counter}_$i", $column_size);
					if ($column_counter == 0) {
						$self->displaysavebutton($row_counter, $column_count);
					}
				} elsif ($self->{column_types}{$i} eq 'number') {
					my $precision = $columns[0][$i]->{precision};
					$self->displaynumbercolumn("", "number_${row_counter}_$i", $precision);
				} elsif ($self->{column_types}{$i} eq 'list') {
					my $listcolumn = $columns[0][$i];
					$self->displaylistcolumn($listcolumn->{values}, "", "list_${row_counter}_$i", $row_counter);
				} elsif ($self->{column_types}{$i} eq 'date') {
					$self->displaydatecolumn("", "date_${row_counter}_$i");
				}
				$column_counter++;
			}
			print "</tr>";
			$row_counter++;
			$column_counter = 0;
		}
		print "<tr id='entry_$row_counter'>";
		for my $i (0..($column_count-1)) {
			my @tokens = split /,/, $ase;
			if ($self->{column_types}{$i} eq 'text') {
				my $column_size = $columns[0][$i]->{size};
				$self->displaytextcolumn($tokens[$i], "text_${row_counter}_$i", $column_size);
				if ($column_counter == 0) {
					$self->displayeditbutton($row_counter, $column_count);
				}
			} elsif ($self->{column_types}{$i} eq 'number') {
				my $precision = $columns[0][$i]->{precision};
				$self->displaynumbercolumn($tokens[$i], "number_${row_counter}_$i", $precision);
			} elsif ($self->{column_types}{$i} eq 'list') {
				my $listcolumn = $columns[0][$i];
				$self->displaylistcolumn($listcolumn->{values}, $tokens[$i], "list_${row_counter}_$i", $row_counter);
			} elsif ($self->{column_types}{$i} eq 'date') {
				$self->displaydatecolumn($tokens[$i], "date_${row_counter}_$i");
			}
			$column_counter++;
		}
		print "</tr>";
		$row_counter++;
	}
	print "</table></form></td></tr></table>";
}
sub submitaseform {
	my $self = shift;
	my $q = shift;
	my @fields = shift;
	my $errormessage = shift;
	
	print <<PLANHEADER
    <table>
	<tr class='odd-row'>
	<td colspan='3'>
	<form id='field_form' action='$self->{web_url}' method='get'>
		<input id='execaction' type='hidden' name='Action'>
		<script src='https://code.jquery.com/jquery-1.12.4.js'></script>
		<script src='https://code.jquery.com/ui/1.12.1/jquery-ui.js'></script>
		<table>
PLANHEADER
;
	$self->{action} = $q->param('Action');
    if ($self->{nav} eq "1") {
		print "<input id='nav' type='hidden' name='Nav' value='$self->{nav}'>";
    }
	
	my $fieldcount = 0;
	while (my $field = $fields[0][$fieldcount]) {
		my $fieldarg = $field->{name};
		$fieldarg =~ s/\s/_/g;
		my $value = $q->param("${fieldarg}_field");

		$self->hiddenfield($field->{name}, $value, $fieldarg);	
		
		$fieldcount++;
	}


	if (length($errormessage) > 0) {
		print "<tr><td><p class='error'>$errormessage</p></td></tr>";
	}

	print <<PLANEND
	</table>
    <script>
		jQuery("input#execaction").attr("value", "Update");
		jQuery("#field_form").submit();
    </script>
	</form>
	</td>
	</tr>
    </table>
PLANEND
;	
}
sub displayaseform {
	my $self = shift;
	my $q = shift;
	my @fields = shift;
	my $errormessage = shift;
	
	print <<PLANHEADER
    <table>
	<tr class='odd-row'>
	<td colspan='3'>
	<form id='field_form' action='$self->{web_url}' method='get'>
		<input id='execaction' type='hidden' name='Action'>
		<script src='https://code.jquery.com/jquery-1.12.4.js'></script>
		<script src='https://code.jquery.com/ui/1.12.1/jquery-ui.js'></script>
		<table>
PLANHEADER
;
	$self->{action} = $q->param('Action');
    if ($self->{nav} eq "1") {
		print "<input id='nav' type='hidden' name='Nav' value='$self->{nav}'>";
    }
	
	my $fieldcount = 0;
	while (my $field = $fields[0][$fieldcount]) {
		my $fieldarg = $field->{name};
		$fieldarg =~ s/\s/_/g;
		my $value = $q->param("$fieldarg");

		if ($field->{type} eq 'datetime') {
			$self->displaydatefield($field->{name}, $value, $fieldarg, $fieldcount);	
		} elsif ($field->{type} eq 'list') {
			my @results = {};
			if (defined $field->{values}) {
				@results = @{$field->{values}};
			} elsif (defined $field->{query}) {
				@results = $self->executequery($field->{query}, $field->{results});
			}
			$self->displaylistfield($field->{name}, \@results, $value, $fieldarg, $fieldcount);
		}
		
		$fieldcount++;
	}


	if (length($errormessage) > 0) {
		print "<tr><td><p class='error'>$errormessage</p></td></tr>";
	}

	print <<PLANEND
	</table>
	</form>
	</td>
	</tr>
    </table>
PLANEND
;	
}
sub displayheadercolumn {
	my $self = shift;
	my $value = shift;
	my $column = shift;
	print "<th class='table-header' id='col_${column}'>$value</th>";	
}
sub displaylabelcolumnread {
	my $self = shift;
	my $value = shift;
	my $row = shift;
	my $column = shift;
	
	#MK - 13/Feb/2020 Tooltip - Integration - Text Column above size > 50 will be truncated to 50 and shown as ...
	#MK - 13/Feb/2020 on mouse over tooltip is displayed
	if(length($value) <= 50) {
		print "<td class='export-column' id='col_${column}'>$value";
		print "</td>";
	} else {
		print "<td class='export-column' id='col_${column}'><div class='tooltip'>".substr( $value, 0, 50 )."...";
		print "<span class='tooltiptext'>$value";		
		print "</span></div></td>";
	}
	#MK - 13/Feb/2020 - Tooltip Integration complete
	
}
sub displaylabelcolumn {
	my $self = shift;
	my $value = shift;
	my $arg = shift;
	
	print "<td><label class='column-label' id='$arg'>$value</label><input type='hidden' name='$arg' value='$value'>";
	print "</td>";
}
sub displaytextcolumn {
	my $self = shift;
	my $value = shift;
	my $arg = shift;
	my $column_size = shift;
	my $tabidx = shift;

	if ($column_size eq "") {
		print "<td><input class='text' tabindex='$tabidx' type='text' id='$arg' name='$arg' value='$value' disabled></td>";	
	} else {
		print "<td><input style='width: $column_size' class='text' tabindex='$tabidx' type='text' id='$arg' name='$arg' value='$value' disabled></td>";	
	}
}
sub displaynumbercolumn {
	my $self = shift;
	my $value = shift;
	my $arg = shift;
	my $precision = shift;
	my $tabidx = shift;

	if ($value eq "") {
		$value = "0";
	}

	print "<td><input class='number' tabindex='$tabidx' type='text' id='$arg' name='$arg' value='$value' disabled></td>";	 print <<NUMBERFORMAT
	<script>
	jQuery(document).ready(function() {
		var num = $value;
		jQuery('#$arg').val(num.toFixed($precision));
	});
	</script>
NUMBERFORMAT
;
}
sub displaydatecolumn {
	my $self = shift;
	my $value = shift;
	my $arg = shift;
	print <<DATEFIELDJQ
	<td class='inner-table'>
		<input class='date' type='text' id='$arg' name='$arg' value='$value' placeholder='mm-dd-yyyy' disabled>
		<script type='text/javascript'>
		jQuery(document).ready(function() {
			jQuery('#$arg').datepicker();
				jQuery('#$arg').datepicker('option','dateFormat','mm-dd-yy');
				if ("$value" != "") {
					jQuery('#$arg').datepicker('setDate', new Date('$value'));
				}
			});
		</script>
	</td>
DATEFIELDJQ
;
}
sub displaylistcolumn {
	my $self = shift;
	my $values = shift;
	my $value = shift;
	my $arg = shift;
	my $tabidx = shift;

	print <<LISTFIELD
	<td class='inner-table'>
		<select name='$arg' id='$arg' value='$value' disabled>
LISTFIELD
;
	my @values = @{$values};
	for my $i (@values) {
		$i = $self->trimwhitespace($i);
		$value = $self->trimwhitespace($value);
		if ("$i" eq "$value") {
			print "<option selected>$i</option>\n";
		} else {
			print "<option>$i</option>\n";
		}
	}
	print <<FIELDMIDDLE
	   </select>
	</td>
FIELDMIDDLE
;
}
sub displaysavebutton {
	my $self = shift;
	my $row_number = shift;
	my $column_count = shift;

	print <<CREATEMODEBUTTONTOP
	<td class='edit-box'>
    <span class='edit-box' id='editsave_$row_number'>
    </span>
    <script>
        function enable_create_mode_$row_number(rowcount) {
			var column_count = "$column_count";
            var field_ids = {};
CREATEMODEBUTTONTOP
;
		for my $i (0..($column_count-1)) {
			if ($self->{column_types}{$i} eq 'text') {	
				print "field_ids[$i] = \"text_${row_number}_$i\";\n"; 		
			} elsif ($self->{column_types}{$i} eq 'label') {
				print "field_ids[$i] = \"text_${row_number}_$i\";\n"; 		
			} elsif ($self->{column_types}{$i} eq 'list') {
				print "field_ids[$i] = \"list_${row_number}_$i\";\n"; 		
			} elsif ($self->{column_types}{$i} eq 'date') {
				print "field_ids[$i] = \"date_${row_number}_$i\";\n"; 		
			} elsif ($self->{column_types}{$i} eq 'number') {
				print "field_ids[$i] = \"number_${row_number}_$i\";\n"; 		
			} elsif ($self->{column_types}{$i} eq 'edit') {
				print "field_ids[$i] = \"edit_${row_number}\";\n";
			}
        }	
	print <<CREATEBUTTONEND
			for (var i = 0; i < column_count; i++) {
				jQuery("#" + field_ids[i]).removeAttr('disabled');
			}
			jQuery("input#editsave_$row_number").css("visibility","hidden");
			jQuery("input.edit_buttons").each(function() {
				jQuery(this).attr("disabled","");
			});
			jQuery("span#editsave_$row_number").html("<input id='action_$row_number' type='hidden' name='Action' value='create_$row_number'><input id='save_$row_number' type='submit' value='Save'><input id='cancel_$row_number' type='button' value='Cancel'>");
			jQuery("#cancel_$row_number").click(function() {
				jQuery("input#execaction").attr("value", "Update");
				jQuery("#field_form").submit();
			});
		}
 
		jQuery(document).ready(function() {
			enable_create_mode_$row_number($row_number);
		});
	</script>
	</td>
CREATEBUTTONEND
;
}
	
sub displayeditbutton {
	my $self = shift;
	my $row_number = shift;
	my $column_count = shift;

	print <<EDITMODEBUTTONTOP
	<td class='edit-box'>
    <span class='edit-box' id='editsave_$row_number'>
	<input class='edit_buttons' id='edit_$row_number' type='button' value='Upd'>
	<input class='delete_buttons' id='delete_$row_number' type='button' value='Del'>
    </span>
	<script>
        function delete_row_$row_number(rowcount) {
            var fieldtype = "input#$self->{column_types}{0}_${row_number}_0";
            var fieldvalue = jQuery(fieldtype).val();
			jQuery("span#editsave_$row_number").append("<input id='action_$row_number' type='hidden' name='Action' value='delete_$row_number'>");
			jQuery("#delete_$row_number").val("Are you sure you want to delete " + fieldvalue);
			jQuery("#delete_$row_number").dialog({
			  title: "Confirmation",
              open: function() {
              },
              closeOnEscape: true,
              beforeClose: function(event, ui) {
					jQuery("span#editsave_$row_number").append("<input class='delete_buttons' id='delete_$row_number' type='button' value='Del'>");
					jQuery("input#delete_$row_number").click(function() {
						delete_row_$row_number($row_number);
        			});
			  },
			  resizable: false,
			  height: "auto",
			  width: "auto",
			  modal: true,
			  buttons: {
				"Delete": function() {
					remove_entry_$row_number();
					jQuery(this).dialog("close");
				},
				Cancel: function() {
					jQuery(this).dialog("close");
				}
			  }
			});
        }
        function enable_editmode_$row_number(rowcount) {
			var column_count = "$column_count";
            var field_ids = {};
EDITMODEBUTTONTOP
;
		for my $i (0..($column_count-1)) {
			if ($self->{column_types}{$i} eq 'text') {	
				print "field_ids[$i] = \"text_${row_number}_$i\";\n"; 		
			} elsif ($self->{column_types}{$i} eq 'label') {
				print "field_ids[$i] = \"text_${row_number}_$i\";\n"; 		
			} elsif ($self->{column_types}{$i} eq 'list') {
				print "field_ids[$i] = \"list_${row_number}_$i\";\n"; 		
			} elsif ($self->{column_types}{$i} eq 'date') {
				print "field_ids[$i] = \"date_${row_number}_$i\";\n"; 		
			} elsif ($self->{column_types}{$i} eq 'number') {
				print "field_ids[$i] = \"number_${row_number}_$i\";\n"; 		
			} elsif ($self->{column_types}{$i} eq 'edit') {
				print "field_ids[$i] = \"edit_${row_number}\";\n";
			}
        }	
	print <<EDITBUTTONEND
			//Enable all fields and save values
			for (var i = 0; i < column_count; i++) {
				jQuery("#" + field_ids[i]).removeAttr('disabled');
                var fieldvalue = jQuery("#" + field_ids[i]).val();
				var fieldidx = "undo_${row_number}_" + i;
				jQuery("tr#entry_$row_number").append("<input type='hidden' id='" + fieldidx + "' name='" + fieldidx + "' value='" + fieldvalue + "'>");
			}
			jQuery("input#editsave_$row_number").css("visibility","hidden");
			jQuery("input.edit_buttons").each(function() {
				jQuery(this).attr("disabled","");
			});
			jQuery("span#editsave_$row_number").html("<input id='action_$row_number' type='hidden' name='Action' value='update_$row_number'><input id='save_$row_number' type='button' value='Save'><input id='cancel_$row_number' type='button' value='Cancel'>");
            jQuery("input#cancel_$row_number").click(function() {
				for (var i = 0; i < column_count; i++) {
					var fieldidx = "undo_${row_number}_" + i;
				    var fieldvalue = jQuery("#" + fieldidx).val();
					jQuery("#" + fieldidx).remove();
					jQuery("#" + field_ids[i]).val(fieldvalue);
					save_cancel_$row_number(field_ids);
				}
			});
			jQuery("input#save_$row_number").click(function() {
				var form = jQuery("form#table-form");
				var url = form.attr('action');
				jQuery.ajax({
                    type: "POST",
					url: url,
					data: form.serialize(),
					error: function(xhr, status, errorThrown) {
						alert("Error: " + xhr.statusText);
					},
					success: function(data) {
						var container = document.createElement("div");
						jQuery(container).html(data);
						var value = jQuery(container).find('span#status-result');
						jQuery("div#status-footer").html(data);
					    save_cancel_$row_number(field_ids);						
                    }
				});
			});
		}
        function save_cancel_$row_number(field_ids) {
			var column_count = "$column_count";
			jQuery("input#action_$row_number").remove();
			jQuery("input#save_$row_number").remove();
			jQuery("input#cancel_$row_number").remove();
			for (var i = 0; i < column_count; i++) {
			   jQuery("#" + field_ids[i]).attr('disabled',"");
			}	
			jQuery("span#editsave_$row_number").html("<input class='edit_buttons' id='edit_$row_number' type='button' value='Upd'><input class='delete_buttons' id='delete_$row_number' type='button' value='Del'>");
			jQuery("input.edit_buttons").each(function() {
				jQuery(this).removeAttr("disabled");
			});
			jQuery("input#edit_$row_number").click(function() {
				enable_editmode_$row_number($row_number);	
			});
			jQuery("input#delete_$row_number").click(function() {
				delete_row_$row_number($row_number);
        	});
        }
        function remove_entry_$row_number() {
			var form = jQuery("form#table-form");
			var url = form.attr('action');
			jQuery.ajax({
            	type: "POST",
				url: url,
				data: form.serialize(),
				error: function(xhr, status, errorThrown) {
					alert("Error: " + xhr.statusText);
				},
				success: function(data) {
					var container = document.createElement("div");
					jQuery(container).html(data);
					var value = jQuery(container).find('span#status-result');
					jQuery("div#status-footer").html(value);
					jQuery("input#action_$row_number").remove();
					jQuery("tr#entry_$row_number").remove();
				}
			});
        }
		jQuery("input#edit_$row_number").click(function() {
			enable_editmode_$row_number($row_number);	
		});
        jQuery("input#delete_$row_number").click(function() {
			delete_row_$row_number($row_number);
        });
	</script>
	</td>
EDITBUTTONEND
;
}
sub hiddenfield {
	my $self = shift;
	my $value = shift;
	my $arg = shift;

	print <<DATEFIELD
	<tr>
	<td>
		<input  type='hidden' name='$value' value='$arg'>
    </td>
    </tr>
DATEFIELD
;
}	
sub displaydatefield {
	my $self = shift;
	my $label = shift;
	my $value = shift;
	my $arg = shift;
	my $tabidx = shift;

	print <<DATEFIELD
	<tr>
	<td>
		<label>$label: </label>
	</td>
	<td class='inner-table'>
		<input tabindex='$tabidx' type='text' id='datefield$tabidx' name='$arg' placeholder='dd-mm-yyyy'>
		<select name='${arg}H' id='hourfield$tabidx'>
DATEFIELD
;
	my $hourcount = 0;
	while ($hourcount < 24) {
		my $formatted = sprintf("%02d", $hourcount);
		print "<option>$formatted</option>";
		$hourcount++;
	}
	print "</select>";
	print "<select name='${arg}M' id='minutefield$tabidx'>";
	my $minutecount = 0;
	while ($minutecount <= 59) {
		my $formatted = sprintf("%02d", $minutecount);
		print "<option>$formatted</option>";
		$minutecount++;
	} 

	print <<DATEFIELDJQ
	</select>
	<script type='text/javascript'>
		jQuery(document).ready(function() {
			jQuery('#datefield$tabidx').datepicker();
				jQuery('#datefield$tabidx').datepicker('option','dateFormat','mm-dd-yy');
				jQuery('#$arg').datepicker('setDate', new Date('$value'));
			});
		</script>
	</td>
DATEFIELDJQ
;
}

sub displaylistfield {
	my $self = shift;
	my $label = shift;
	my $values = shift;
	my $value = shift;
	my $arg = shift;
	my $tabidx = shift;

	print <<LISTFIELD
	<tr>
	<td>
		<label>$label: </label>
	</td>
	<td class='query-field'>
		<input name='${arg}' id='${arg}$tabidx' value='$value'>
LISTFIELD
;
	my @items = @{$values};
	print "<script>\n";
	print " var items_$tabidx = [";
	for my $item_value (@items) {
		print "\"$item_value\",";
	}
	print " \"\"];\n";
	print "</script>\n";
	print <<FIELDMIDDLE
		<script>
    		jQuery("#${arg}$tabidx").autocomplete({
				minLength: 0,
      			source: items_$tabidx
    		}).bind('focus', function(){ jQuery(this).autocomplete("search"); } );
  		</script>
	</td>
FIELDMIDDLE
;
	if ($tabidx == 0) {
		$self->displayquerybutton($tabidx + 2);
		$self->displayupdatebutton($tabidx + 3);
		$self->displaycreatebutton($tabidx + 4);
		$self->displayexportbutton($tabidx + 5);
	}
	print <<FIELDEND
	</tr>
FIELDEND
;
}

sub displayquerybutton {
	my $self = shift;
	my $tabindex = shift;

	print <<DISPLAYBUTTON
	<td>
	<input class='execute-button' id='query_$tabindex' type='button' value='Query'>
	<script>
	jQuery("input#query_$tabindex").click(function() {
		jQuery("input#execaction").attr("value", "QUERY");
		jQuery("#field_form").submit();
	});
	</script>
    </td>
DISPLAYBUTTON
;
}
sub displayupdatebutton {
	my $self = shift;
	my $tabindex = shift;

	print <<DISPLAYBUTTON
	<td>
	<input class='execute-button' id='update_$tabindex' type='button' value='Update'>
	<script>
	jQuery("input#update_$tabindex").click(function() {
		jQuery("input#execaction").attr("value", "Update");
		jQuery("#field_form").submit();
	});
	</script>
    </td>
DISPLAYBUTTON
;
}
sub displaycreatebutton {
	my $self = shift;
	my $tabindex = shift;

	print <<DISPLAYBUTTON
	<td>
	<input class='execute-button' id='create_$tabindex' type='button' value='Create'>
	<script>
	jQuery("input#create_$tabindex").click(function() {
		jQuery("input#execaction").attr("value", "Create");
		jQuery("#field_form").submit();
	});
	</script>
    </td>
DISPLAYBUTTON
;
}
sub displayexportbutton {
	my $self = shift;
	my $tabindex = shift;

	print <<DISPLAYBUTTONTOP
	<td>
	<input class='execute-button' id='export_$tabindex' type='button' value='Export' disabled>
	<script>
    jQuery("input#export_$tabindex").click(function() {
		jQuery("input#execaction").attr("value", "Export");
		jQuery("#field_form").attr("target","_newtab");
		jQuery("#field_form").submit();
		jQuery("#field_form").removeAttr("target","_newtab");
	});
DISPLAYBUTTONTOP
;
	if ($self->{action} eq 'QUERY') {
		print <<ENABLEEXPORT
		jQuery('input#export_$tabindex').removeAttr('disabled');
ENABLEEXPORT
;
	}
	
	print <<DISPLAYBUTTONEND
	</script>
    </td>
DISPLAYBUTTONEND
;
}


sub displayfilterheader {
	my $self = shift;
	
	print <<FILTERHEADER
<span class='datefilter'>Date Filter</span>
FILTERHEADER
}

sub displayfilterform {
	my $self = shift;
	my $servername = shift;
	my $startdate = shift;
	my $starthour = shift;
	my $startminute = shift;
	my $enddate = shift;
	my $endhour = shift;
	my $endminute = shift;
	my $errormsg = shift;

	print <<FILTERSTART	
    <table id='inner' class='inner'>
	<tr class='odd-row'>
	<td colspan="3">
	<form action='$self->{web_url}' method='get'>
    <table>
    <tr>
      <td>
	    <label>Start Date: </label>
      </td>
      <td>
FILTERSTART
;
    if ($self->{nav} eq "1") {
		print "<input id='nav' type='hidden' name='Nav' value='$self->{nav}'>";
    }
	
		
      	print "<input tabindex='1' type='text' id='startdatepicker' name='Start_Date' value='$startdate' placeholder='dd-mm-yyyy'>";
		print "<select name='Start_DateH' id='starthourpicker'>";
	

		my $hourcount = 0;
		while ($hourcount < 24) {
			my $formated = sprintf("%02d", $hourcount);
			if ($starthour eq $formated) {
				print "<option selected>$formated</option>";					
			} else {
   				print "<option>$formated</option>";
			}
			$hourcount++;
		}
   		print "</select>";

		print "<select name='Start_DateM' id='startminutepicker'>";
		my $minutecount = 0;
		while ($minutecount < 59) {
			my $formated = sprintf("%02d", $minutecount);
			if ($startminute eq $formated) {
				print "<option selected>$formated</option>";
			} else {
   				print "<option>$formated</option>";
			}
			$minutecount++;
		}
   		print "</select>";
	
	print <<FILTERSUBMIT
      </td>
      <td>
	   <input tabindex="3" type="submit" value="Filter">
      </td>
    </tr>
  	<tr>
      <td>
        <label>End Date: </label>
      </td>
      <td>
FILTERSUBMIT
;
     	print "<input tabindex='2' type='text' id='enddatepicker' name='End_Date' value='$enddate' placeholder='dd-mm-yyyy'>";
		print "<select name='End_DateH' id='endhourpicker'>";

		my $hourcount = 0;
		while ($hourcount < 24) {
			my $formated = sprintf("%02d", $hourcount);
			if ($endhour eq $formated) {
				print "<option selected>$formated</option>";
			} else {
   				print "<option>$formated</option>";
			}
			$hourcount++;
		}
   		print "</select>";

		print "<select name='End_DateM' id='endminutepicker'>";
		my $minutecount = 0;
		while ($minutecount < 59) {
			my $formated = sprintf("%02d", $minutecount);
			if ($endminute eq $formated) {
				print "<option selected>$formated</option>";
			} else {
   				print "<option>$formated</option>";
			}
			$minutecount++;
		}
   		print "</select>";

	print <<FILTERHIDDEN
      </td>
      <td>
		
        <input type="hidden" name="Action" value="SUMMARY">
		<input type="hidden" name="Server_Name" value="$servername">
      </td>
      <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
      <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
      <script type="text/javascript">
         jQuery(document).ready(function() {
	       jQuery('#startdatepicker').datepicker();
	       jQuery('#startdatepicker').datepicker("option","dateFormat","mm-dd-yy");
	       jQuery('#enddatepicker').datepicker();
	       jQuery('#enddatepicker').datepicker("option","dateFormat","mm-dd-yy");
         });
      </script>
    </tr>
FILTERHIDDEN
;

	if (defined $errormsg) {
	
		print <<FILTERERRORMSG
	<tr>
	<td colspan="3">
FILTERERRORMSG
;
		print "<p class='error'>$errormsg</p>";

	print <<FILTERERROREND
</td>
</tr>
FILTERERROREND
}

	print <<FILTERFORMEND
</table>
</form>
</td>
</tr>
</table>
FILTERFORMEND
;
}

sub getYearFromString {
	my $self = shift;
	my $datestr = shift;

	my $yearstr = $datestr;
	$yearstr =~ s/-\d\d-\d\d\s\d\d:\d\d$//g;

	return $yearstr;
}
sub getMonthFromString {
	my $self = shift;
	my $datestr = shift;

	my $monthstr = $datestr;	
	$monthstr =~ s/-\d\d\s\d\d:\d\d$//g;	
	$monthstr =~ s/^\d\d\d\d-//g;

	return $monthstr;
}
sub getDayFromString {
	my $self = shift;
	my $datestr = shift;
	
	my $daystr = $datestr;
	$daystr =~ s/\s\d\d:\d\d$//g;
	$daystr =~ s/^\d\d\d\d-\d\d-//g;
	
	return $daystr;
}
sub getHourFromString {
	my $self = shift;
	my $datestr = shift;

	my $hourstr = $datestr;
	$hourstr =~ s/:\d\d$//g;
	$hourstr =~ s/^\d\d\d\d-\d\d-\d\d\s//g;

	return $hourstr;
}
sub getMinuteFromString {
	my $self = shift;
	my $datestr = shift;

	my $minutestr = $datestr;
	$minutestr =~ s/$//g;
	$minutestr =~ s/^\d\d\d\d-\d\d-\d\d\s\d\d://g;

	return $minutestr;
}

sub displayfooter {
	my $self = shift;
	my $footer = shift;
	print <<EOL
    </div>
	<div style='width: 100%; border-bottom: 1px solid #eee'></div>
	<div id='status-footer'></div>
	<p style='margin: 5px 25px 0 25px;color: $footer->{color};font-weight: $footer->{style}; font-size: $footer->{size}'>$footer->{text}</p>
</body>
</html>
EOL
}

###########################################################################
package main;

my $q = CGI->new;

my $config_file = $q->param('config_file');

#################
# Config Values #
#################
my $CONFIG_FILE = "$base_dir/resources/$config_file";

# Load Config Data #######################################	
my $filedata = YAML::XS::LoadFile($CONFIG_FILE);
my $menufile = $filedata->{home};
my $home_button = $filedata->{home_button};
my $subheader_text = $filedata->{header_title};
my $query_script = $filedata->{query_script};
my $query_result = $filedata->{query_result};
my $create_script = $filedata->{create_script};
my $create_result = $filedata->{create_result};
my $update_script = $filedata->{update_script};
my $update_result = $filedata->{update_result};
my $delete_script = $filedata->{delete_script};
my $delete_result = $filedata->{delete_result};
my @fields = $filedata->{fields};
my @columns = $filedata->{columns};
my $footer_text = $filedata->{footer};

my $menudata = YAML::XS::LoadFile($menufile);
my $header_text = $menudata->{header_title};
my @menu = $menudata->{menu};
my $fontsizemenu = $menudata->{font_size};
#########################################################

my $my_url = $q->url( -relative => 1 );
my @args = $q->param;


my $mode = $q->param('Action');
my $nav = $q->param('Nav');

my $aseapp = ASE->new($my_url, $home_button, $nav);
my $argcount = scalar @args;
if ($argcount <= 1) {
	print $q->header();
	$aseapp->displayheader($header_text, $subheader_text, $fontsizemenu);
	$aseapp->displaymenusection(@menu);
	$aseapp->displaysubheader($subheader_text);
	$aseapp->displayaseform($q, @fields);
	$aseapp->displayfooter($footer_text);
} else {
	if (lc $mode eq "update" || lc $mode eq "create") {
		print $q->header();
		$aseapp->displayheader($header_text, $subheader_text, $fontsizemenu);
		$aseapp->displaymenusection(@menu);
		$aseapp->displaysubheader($subheader_text);
		$aseapp->displayaseform($q, @fields);
		$aseapp->displayasetable($q, \@columns, $query_script, $query_result);
		$aseapp->displayfooter($footer_text);
	} elsif (lc $mode eq "query") {
		print $q->header();
		$aseapp->displayheader($header_text, $subheader_text, $fontsizemenu);
		$aseapp->displaymenusection(@menu);
		$aseapp->displaysubheader($subheader_text);
		$aseapp->displayaseform($q, @fields);
		$aseapp->displayasedisplaytable($q, \@columns, $query_script, $query_result);
		$aseapp->displayfooter($footer_text);
    } elsif ($mode =~ m/delete_(\d)+/) {
		print $q->header();
		my $row_number = $mode;
		$aseapp->executescript($q, $delete_script, $delete_result, $row_number);
    } elsif ($mode =~ m/update_(\d)+/) {
		print $q->header();
		my $row_number = $mode;
		$row_number  =~ s/update_//;
		$aseapp->executescript($q, $update_script, $update_result, $row_number);		
    } elsif ($mode =~ m/create_(\d)+/) {
		print $q->header();
		my $row_number = $mode;
		$row_number  =~ s/create_//;
		$aseapp->executescript($q, $create_script, $create_result, $row_number);		
		$aseapp->submitaseform($q, @fields);
	} elsif (lc $mode eq 'export') {
		#MK - 13/Feb/2020 - Comment export header.
		#MK - 13/Feb/2020 - Add 
		$aseapp->displayexportheaderForCSV();
		$aseapp->renderQueryResultAsCSV($q, \@columns, $query_script, $query_result);
		#MK - 13/Feb/2020 - New method displayexportheaderForCSV called.
		
	}
}