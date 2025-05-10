#!/usr/bin/perl

use strict;
use warnings;
use Image::EXIF;
use Data::Dumper;

my @files=@ARGV;
#my $pattern = shift(@files);
my $prefix = shift(@files);
#my $nomatch = '.' x (4-length($nummatch));
#print "$nomatch, $nummatch \n";

foreach my $f (@files) {
    my $exif = new Image::EXIF; # reset EXIF
    my $time='';
    my $shortdate=$f;
    $shortdate=~s/\..*//;
    $exif->file_name($f);
    my $info = $exif->get_all_info;
    #print Dumper($info);
    my $date = $info->{'other'}->{'Image Generated'};
    unless($date) {
      $date = $info->{'other'}->{'Image Modified'};
    }
    if(!$date || ($date eq '' && $f =~ /IMG-.*-WA/)) { # whatsapp image
      my @date = (split(/-/, $f));
      my $time = substr(@date[2], 2,4);
      $date = "@date[1] $time";
    }
    #print "$date\n";
    if($date) {
        $date =~ s/://g;
        ($date,$time) = split(/\s+/, $date);
        $time=substr($time,0,4);
        $shortdate = substr($date,4);
    }
    my $file = $prefix . $shortdate . $time . '.jpg';
    #$file=~s/dscn$nomatch($nummatch).jpg/$1/i;

    print "ruby ~/ruby/image_manipulation/annotate/annotate.rb \\\n";
    print "    -t \" $date - \" \\\n    -i $f -o $file\n";
#    print "bins_edit -y $date -t \"\" -d \"\" $file\n\n";
    print <<EOF;
cat <<EOT > $file.xml
<?xml version="1.0" encoding="UTF-8"?><image><description>
      <field name="description"> </field>
      <field name="title"> </field>
      <field name="date"> $date </field>
   </description> <bins> </bins> <exif> </exif> </image>
EOT
EOF

}
