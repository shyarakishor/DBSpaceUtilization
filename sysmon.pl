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
my $from_date       = $q->param('fromdate') || $filedata->{fromdate};
my $to_date         = $q->param('todate') || $filedata->{todate};
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
                                                                y => $value
                                                            };
                                                        # }
                                                }
                                                elsif ( $graph_frequency =~ /hour/i ) {
                                                    push @$final_data_array, {
                                                        x => "new Date($y, $m, $d, $hour,0,0)",
                                                        y => $value
                                                    };
                                                }
                                                else {
                                                        push @$final_data_array, {
                                                                x => "new Date($y, $m, $d)",
                                                                y => $value
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
                                                                y => $value
                                                        };
                                                # }
                                        }
                                        elsif ( $graph_frequency =~ /hour/i ) {
                                            push @$final_data_array, {
                                                x => "new Date($y, $m, $d, $hour,0,0)",
                                                y => $value
                                            };
                                        }
                                        else {
                                                push @$final_data_array, {
                                                        x => "new Date($y, $m, $d)",
                                                        y => $value
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
$data_json =~ s/\"//g;
##generate template

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
<script type="text/javascript" src="https://cdn.jsdelivr.net/jquery/latest/jquery.min.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/momentjs/latest/moment.min.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/daterangepicker/daterangepicker.min.js"></script>
<link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/daterangepicker/daterangepicker.css" />
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

.graph_frequency {
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
  <label for="lname">Start Date Time:</label><br>
  <input type="text" class="fromdate" id="fromdate" name="fromdate" value=""><br>
  <label for="lname">End Date Time:</label><br>
  <input type="text" class="todate" id="todate" name="todate" value=""><br><br>
  <input class="signin" type="submit" value="Submit">
</form> 
</div>
</body>
BODY
print <<FOOTER;
<footer>
<script type='text/javascript'>
jQuery(function() {
  jQuery('.fromdate').daterangepicker({
    singleDatePicker: true,
    timePicker: true,
    timePicker24Hour: true,
    locale: {
      format: 'MM/DD/YYYY HH:mm'
    }
  });
  jQuery('.todate').daterangepicker({
    singleDatePicker: true,
    timePicker: true,
    timePicker24Hour: true,
    locale: {
      format: 'MM/DD/YYYY HH:mm'
    }
  });
});

function check_validation() {
    var graph_frequency = jQuery('#graph_frequency').val();
    var fromdate = jQuery('#fromdate').val();
    var todate = jQuery('#todate').val();

    var date1=fromdate.split(' ')[0];
    var date2=todate.split(' ')[0];

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
