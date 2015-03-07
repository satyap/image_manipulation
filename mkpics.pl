#!/usr/bin/perl

use strict;
use warnings;
use Image::EXIF;
use Data::Dumper;

my @files=@ARGV;
#my $pattern = shift(@files);
my $prefix = shift(@files);
my $exif = new Image::EXIF;
#my $nomatch = '.' x (4-length($nummatch));
#print "$nomatch, $nummatch \n";

foreach my $f (@files) {
    my $time='';
    my $shortdate=$f;
    $shortdate=~s/\..*//;
    $exif->file_name($f);
    my $info = $exif->get_all_info;
    #print Dumper($info);
    my $date = $info->{'other'}->{'Image Generated'};
#    print "$date\n";
    if($date) {
        $date =~ s/://g;
        ($date,$time) = split(/\s+/, $date);
        #print Dumper($info);
        $time=substr($time,0,4);
        $shortdate = substr($date,4);
    }
    my $file = $prefix . $shortdate . $time . '.jpg';
    #$file=~s/dscn$nomatch($nummatch).jpg/$1/i;

    print "ruby ~/ruby/image_manipulation/annotate/annotate.rb -t \"$date - \" -i $f -o $file\n";
    print "bins_edit -y $date -t \"\" -d \"\" $file\n\n";
             
}
