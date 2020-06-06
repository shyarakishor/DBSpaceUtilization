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
use Template qw(process);;
use JSON;
use Data::Dumper;
##################################################

# Version Info ###################################
my $VERSION = "1.0.0";
##################################################

my $q = new CGI;
print $q->header;

my $config_file = $q->param('config_file');
my $action = $q->param('action');

#################
# Config Values #
#################
my $CONFIG_FILE = "$base_dir/resources/$config_file";

# Load Config Data #######################################
my $filedata = LoadFile($CONFIG_FILE);

##check params
if ( !defined $action || $action =~ /^\s*$/i ) {
    &display_form();
    exit;
}


my $header_title    = $filedata->{header_title};
my $csv_file        = $filedata->{file};
my $from_date       = $q->param('fromdate').' '.$q->param('fromtime') || $filedata->{fromdate};
my $to_date         = $q->param('todate').' '.$q->param('totime') || $filedata->{todate};
my $graph_frequency = $q->param('graph_frequency') || $filedata->{graph_frequency};
my $footer_hash     = $filedata->{footer};

####Read CSV File and Collect Lines
my $csv_lines = [];
my $fh = FileHandle->new;
if ( $fh->open("< $csv_file") ) {
        while (my $line = $fh->getline()) {
                chomp($line);
                push @$csv_lines, $line;
        }
        $fh->close;
}
else {
        print "Cannot open $csv_file";
        die;
}
####Read CSV File and Collect Lines END

if ( $from_date && $from_date !~ /^\s*$/ ) {
        $from_date = &check_convert_date_format( $from_date );
}
if ( $to_date && $to_date !~ /^\s*$/ ) {
        $to_date   = &check_convert_date_format( $to_date );
}

my $months_day = {
        '01' => 31,
        '02' => 28,
        '03' => 31,
        '04' => 30,
        '05' => 31,
        '06' => 30,
        '07' => 31,
        '08' => 31,
        '09' => 30,
        '10' => 31,
        '11' => 30,
        '12' => 31
};

##start read and prepare Graph
my $final_data_array = [];
if( scalar @$csv_lines ) {
        foreach my $line ( @$csv_lines ) {
                $line = &trim_space( $line );

                my ( $date_time, $value ) = split(',', $line);

                if( $date_time ) {
                        if ( $from_date !~ /^\s*$/ && $to_date !~ /^\s*$/ ) {
                                $date_time = &check_convert_date_format( $date_time );

                                if ( $date_time ge $from_date && $date_time le $to_date ) {

                                        my ( $date, $hour ) = $date_time =~ /(.*?)\s+(.*)/;
                                        $hour =~ s/(.*?):.*/$1/g;

                                        if ( $date ) {
                                                $date  = &trim_space( $date );

                                                my ( $m, $d, $y ) = $date =~ /(\d+)\/(\d+)\/(\d+)/;
                                                $m -= 1;
                                                my $new_date = sprintf('%02d', $m).'/'.sprintf('%02d', $d).'/'.sprintf('%02d', $y);

                                                $value = &trim_space( $value );

                                                if ( $graph_frequency =~ /Month/i ) {
                                                        if ( $y % 4 == 0 ) {
                                                            $months_day->{'02'} = 29;
                                                        }

                                                        my $month_last_date = sprintf('%04d', $y).'-'.sprintf('%02d', $m).'-'.sprintf('%02d', $d);
                                                        my $current_date = sprintf('%04d', $y).'-'.sprintf('%02d', $m).'-'.$months_day->{sprintf('%02d', $m)};
                                                        # if ( $current_date eq $month_last_date ) {
                                                            push @$final_data_array, {
                                                                x => "new Date($y, $m, $d)",
                                                                y => $value,
                                                                toolTipContent => $date_time.': '.$value
                                                            };
                                                        # }
                                                }
                                                elsif ( $graph_frequency =~ /hour/i ) {
                                                    push @$final_data_array, {
                                                        x => "new Date($y, $m, $d, $hour,0,0)",
                                                        y => $value,
                                                        toolTipContent => $date_time.': '.$value
                                                    };
                                                }
                                                else {
                                                        push @$final_data_array, {
                                                                x => "new Date($y, $m, $d)",
                                                                y => $value,
                                                                toolTipContent => $date_time.': '.$value
                                                        };
                                                }
                                        }
                                }
                        }
                        else {
                                my ( $date, $hour ) = $date_time =~ /(.*?)\s+(.*)/;
                                $hour =~ s/(.*?):.*/$1/g;
                                if ( $date ) {
                                        $date  = &trim_space( $date );
                                        $value = &trim_space( $value );

                                        my ( $m, $d, $y ) = $date =~ /(\d+)\/(\d+)\/(\d+)/;
                                        $m -= 1;
                                        my $new_date = sprintf('%02d', $m).'/'.sprintf('%02d', $d).'/'.sprintf('%02d', $y);

                                        if ( $graph_frequency =~ /Month/i ) {
                                                if ( $y % 4 == 0 ) {
                                                        $months_day->{'02'} = 29;
                                                }

                                                my $two_digit_month = sprintf('%02d', $m+1);
                                                my $month_last_date = sprintf('%04d', $y).'-'.sprintf('%02d', $m).'-'.sprintf('%02d', $d);
                                                my $current_date = sprintf('%04d', $y).'-'.sprintf('%02d', $m).'-'.$months_day->{$two_digit_month};

                                                # if ( $current_date eq $month_last_date ) {
                                                        # print $month_last_date.'---'.$current_date."\n";
                                                        push @$final_data_array, {
                                                                x => "new Date($y, $m, $d)",
                                                                y => $value,
                                                                toolTipContent => $date_time.': '.$value
                                                        };
                                                # }
                                        }
                                        elsif ( $graph_frequency =~ /hour/i ) {
                                            push @$final_data_array, {
                                                x => "new Date($y, $m, $d, $hour,0,0)",
                                                y => $value,
                                                toolTipContent => $date_time.': '.$value
                                            };
                                        }
                                        else {
                                                push @$final_data_array, {
                                                        x => "new Date($y, $m, $d)",
                                                        y => $value,
                                                        toolTipContent => $date_time.': '.$value
                                                };
                                        }
                                        # push @$final_data_array, {
                                        #       x => "new Date($y, $m, $d)",
                                        #       y => $value
                                        # };
                                }
                        }
                }
        }
}

my $data_json = to_json( $final_data_array );
$data_json =~ s/"x":"(.*?)"/x:$1/g;
$data_json =~ s/"y":"(.*?)"/y:$1/g;
$data_json =~ s/"toolTipContent"/toolTipContent/g;
# $data_json =~ s/\"//g;
##generate template
# print $data_json;

my $config_template = {
        INCLUDE_PATH => $base_dir."/Templates",  # or list ref
        INTERPOLATE  => 1,               # expand "$var" in plain text
        POST_CHOMP   => 1,               # cleanup whitespace
        PRE_PROCESS  => '',              # prefix each template
        EVAL_PERL    => 1,               # evaluate Perl code blocks
};
my $obj_template = undef;
eval {
        $obj_template = Template->new($config_template);
};
if ( $@ ) {
        print $@;
}

##feeddata in template
my $template_hash = {};
my $interval = 0;
my $interval_type = '';
if ( $graph_frequency =~ /Day/i ) {
        $template_hash->{'value_format_string'} = 'MM/DD/YYYY';
        $interval_type = 'day';
        $interval = 1;
}
elsif ( $graph_frequency =~ /Month/i ) {
        $template_hash->{'value_format_string'} = 'MMM';
        $interval_type = 'month';
        $interval = 1;
}
elsif ( $graph_frequency =~ /Year/i ) {
        $template_hash->{'value_format_string'} = 'YYYY';
        $interval_type = 'year';
        $interval = 1;
}
elsif ( $graph_frequency =~ /Week/i ) {
        $template_hash->{'value_format_string'} = 'DDD';
}
elsif ( $graph_frequency =~ /Hour/i ) {
    $template_hash->{'value_format_string'} = "HH:00";
    $interval_type = "hour";
    $interval = 1;
}
else {
        $template_hash->{'value_format_string'} = 'MM/DD/YYYY';
}

$template_hash->{'final_data_array'}    = $final_data_array;
$template_hash->{'data_json'}    = $data_json;
$template_hash->{'footer_hash'}  = $footer_hash;
$template_hash->{'header_title'} = $header_title;

# Template::process({'linechart.html'}, $template_hash) || die "Template process failed: ", $obj_template->error(), "\n";

##trim
sub trim_space {
        my $line = shift;

        $line =~ s/^\s+//g;
        $line =~ s/\s+$//g;

        return $line;
}

sub check_convert_date_format {
        my $date_string = shift;

        my ( $m, $d, $y, $hh, $mm ) = $date_string =~ /(\d+)\/(\d+)\/(\d+)\s+(\d+):(\d+)/;
        if ( length($y) == 2 ) {
                $y = '20'.$y;
        }

        my $new_date = sprintf('%02d', $m).'/'.sprintf('%02d', $d).'/'.sprintf('%02d', $y).' '.sprintf('%02d', $hh).':'.sprintf('%02d', $mm);

        return $new_date;
}

sub display_form {
print <<HEADER;
<!DOCTYPE HTML>
<html>
<head>
<link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
<script src='https://code.jquery.com/jquery-1.12.4.js'></script>
    <script src='https://code.jquery.com/ui/1.12.1/jquery-ui.js'></script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {
  font-family: Arial, Helvetica, sans-serif;
}

* {
  box-sizing: border-box;
}

/* Add padding to containers */
.container {
  padding: 16px;
  background-color: white;
}

/* Full-width input fields */
input[type=text], input[type=password] {
  width: 20%;
  padding: 15px;
  margin: 5px 0 22px 0;
  display: inline-block;
  border: none;
  background: #f1f1f1;
}

.graph_frequency, .fromtime, .totime {
    width: 20%;
  padding: 15px;
  margin: 5px 0 22px 0;
  display: inline-block;
  border: none;
  background: #f1f1f1;
}

input[type=text]:focus, input[type=password]:focus {
  background-color: #ddd;
  outline: none;
}

/* Overwrite default styles of hr */
hr {
  border: 1px solid #f1f1f1;
  margin-bottom: 25px;
}
.signin {
  background-color: #f1f1f1;
  text-align: center;
}
</style>
</head>
HEADER
print <<BODY;
<body>
 <div class="container">
<form action="sysmon.pl?config_file=$config_file" onsubmit="return check_validation();" method="POST">
    <input type="hidden" name="action" value="graph" />
    <input type="hidden" name="config_file" value="$config_file" />
  <label for="fname">Graph Freuency:</label><br>
  <select class="graph_frequency" name="graph_frequency" id="graph_frequency">
    <option value="hour">Hour</option>
    <option value="day">Day</option>
    <option value="month">Month</option>
    <option value="year">Year</option>
  <select><br>
  <label for="lname">Start Date & Time:</label><br>
  <input type="text" class="fromdate" id="fromdate" name="fromdate" value="">
  <select class="fromtime" name="fromtime" id="fromtime">
    <option value="00:00" selected>00:00</option>
    <option value="01:00">01:00</option>
    <option value="02:00">02:00</option>
    <option value="03:00">03:00</option>
    <option value="04:00">04:00</option>
    <option value="05:00">05:00</option>
    <option value="06:00">06:00</option>
    <option value="07:00">07:00</option>
    <option value="08:00">08:00</option>
    <option value="09:00">09:00</option>
    <option value="10:00">10:00</option>
    <option value="11:00">11:00</option>
    <option value="12:00">12:00</option>
    <option value="13:00">13:00</option>
    <option value="14:00">14:00</option>
    <option value="15:00">15:00</option>
    <option value="16:00">16:00</option>
    <option value="17:00">17:00</option>
    <option value="18:00">18:00</option>
    <option value="19:00">19:00</option>
    <option value="20:00">20:00</option>
    <option value="21:00">21:00</option>
    <option value="22:00">22:00</option>
    <option value="23:00">23:00</option>
    <option value="24:00">24:00</option>
  <select><br>
  <label for="lname">End Date & Time:</label><br>
  <input type="text" class="todate" id="todate" name="todate" value="">
  <select class="totime" name="totime" id="totime">
    <option value="00:00">00:00</option>
    <option value="01:00">01:00</option>
    <option value="02:00">02:00</option>
    <option value="03:00">03:00</option>
    <option value="04:00">04:00</option>
    <option value="05:00">05:00</option>
    <option value="06:00">06:00</option>
    <option value="07:00">07:00</option>
    <option value="08:00">08:00</option>
    <option value="09:00">09:00</option>
    <option value="10:00">10:00</option>
    <option value="11:00">11:00</option>
    <option value="12:00">12:00</option>
    <option value="13:00">13:00</option>
    <option value="14:00">14:00</option>
    <option value="15:00">15:00</option>
    <option value="16:00">16:00</option>
    <option value="17:00">17:00</option>
    <option value="18:00">18:00</option>
    <option value="19:00">19:00</option>
    <option value="20:00">20:00</option>
    <option value="21:00">21:00</option>
    <option value="22:00">22:00</option>
    <option value="23:00">23:00</option>
    <option value="24:00" selected>24:00</option>
  <select><br><br>
  <input class="signin" type="submit" value="Submit">
</form>
</div>
</body>
BODY
print <<FOOTER;
<footer>
<script type='text/javascript'>
jQuery(function() {
  

  jQuery(document).ready(function() {
    jQuery('#fromdate').datepicker();
    jQuery( "#fromdate" ).datepicker( "option", "dateFormat", "mm/dd/yy" );
    jQuery('#todate').datepicker();
    jQuery( "#todate" ).datepicker( "option", "dateFormat", "mm/dd/yy" );
});
});

function check_validation() {
    var graph_frequency = jQuery('#graph_frequency').val();
    var fromdate = jQuery('#fromdate').val();
    var todate = jQuery('#todate').val();

    var date1=fromdate;
    var date2=todate;

    var dates1 = new Date(date1);
    var dates2 = new Date(date2);
    var diffDays = parseInt((dates2 - dates1) / (1000 * 60 * 60 * 24), 10);

    if ( graph_frequency == 'hour' ) {
        if ( date1 != date2 ) {
            alert("For Graph Frequency Hour Start and End date should be same");
            return false;
        }
    }
    if ( graph_frequency == 'day' ) {
        if ( date1 == date2 ) {
            alert("For Graph Frequency Day Start and End date should not be same");
            return false;
        }
        if ( diffDays > 15 ) {
            alert("For Graph Frequency Day Start and End date should not be more then 15 days");
            return false;
        }
    }
    if ( graph_frequency == 'month' ) {
        if ( date1 == date2 ) {
            alert("For Graph Frequency Month Start and End date should not be same");
            return false;
        }
        if ( diffDays < 31 ) {
            alert("For Graph Frequency Month Start and End date should be more then 30 days");
            return false;
        }
    }
    return true;
}
</script>
</footer>
</html>
FOOTER
}

print <<HEADER;
<!DOCTYPE HTML>
<html>
<head>
</head>
HEADER
print <<BODY;
<body>
<div style='text-align: center;'>
<p style='margin: 5px 25px 0 25px; color: $template_hash->{footer_hash}->{color};font-weight: $template_hash->{footer_hash}->{color}; font-size: $template_hash->{footer_hash}->{size}'>$template_hash->{header_title}</p>
</div>
<div id='chartContainer' style='height: 300px; width: 100%;'>
</div>
</body>
BODY
print <<FOOTER;
<footer>
<div style='text-align: center;'>
<p style='margin: 5px 25px 0 25px; color: $template_hash->{footer_hash}->{color};font-weight: $template_hash->{footer_hash}->{color}; font-size: $template_hash->{footer_hash}->{size}'>FromDate: $from_date & ToDate: $to_date - $template_hash->{footer_hash}->{text}</p>
</div>
<script type='text/javascript' src='https://canvasjs.com/assets/script/canvasjs.min.js'></script></head>
<script type='text/javascript'>
var chart = new CanvasJS.Chart('chartContainer',
    {
      animationEnabled: true,
      zoomEnabled: true,
      markerEnabled: true,
      axisX: {
        interval: $interval,
        intervalType: '$interval_type',
        valueFormatString: '$template_hash->{value_format_string}'
      },
      axisY:{
        interval:10,
        suffix: "%",
        maximum: 100,
        includeZero: false
      },
      data: [
      {
        type: 'line',
        markerType: 'circle',
        markerSize: 10,
        dataPoints: $template_hash->{data_json}
      }
      ]
    });
    chart.render();
</script>
</footer>
</html>
FOOTER
