use strict;
use warnings;
use Image::Magick;

my $p = Image::Magick->new();

sub fixRatio($$) {
    my ($w, $h) = @_;

    my $ratio = $w > 0.9*$h ? 6/4.0 : 4/6.0;
    print "$ratio w/h: " . $w/$h . "\n";
    if($w/$h > $ratio) {
        # too wide
        print "1 ";
        return $w, $w/$ratio
    } else {
        # too tall
        print "2 ";
        return $h*$ratio, $h
    }
}

my @images = @ARGV;
my $border = 0;
# some day, this will be using GetOpt
if($images[0] =~/^\d+$/) {
    $border = shift(@images);
    print "border: $border\n";
}

foreach my $img (@images) {
    print "*** image $img ***\n";
    my $new=$img;
    $new=~s/o_//;
    $p->Read($img);
    my $w = $p->Get('width');
    my $h = $p->Get('height');

    my $new_w;
    my $new_h;
    ($new_w, $new_h) = fixRatio($w + $border, $h + $border);

    my $xoffset = ($new_w - $w) / 2;
    my $yoffset = ($new_h - $h) / 2;
    print "$img $new $w $h -> $new_w $new_h $xoffset $yoffset\n";
    $p->Extent('width' => $new_w, 'height' => $new_h, 'background' => '#ddd', 'geometry' => "${new_w}x${new_h}-${xoffset}-${yoffset}");
    $p->Write($new);


    @$p = ();
}
