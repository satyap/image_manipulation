#!/usr/bin/ruby

require 'getoptlong'

opts = GetoptLong.new(
    ['--text', '-t', GetoptLong::REQUIRED_ARGUMENT],
    ['--inputfile', '-i', GetoptLong::REQUIRED_ARGUMENT],
    ['--outputfile', '-o', GetoptLong::REQUIRED_ARGUMENT],
    ['--textsize', '-s', GetoptLong::REQUIRED_ARGUMENT],
    ['--orientation', '-d', GetoptLong::REQUIRED_ARGUMENT],
    ['--help', '-h', GetoptLong::NO_ARGUMENT],
)

def help
    puts <<-TXT
    #{$0} -t "Text to put on image" -i inputfile -o outputfile [-s 20 -d top-horizontal]
    TXT
end

def getwh(infile, dim)
    %Q[identify -format "%#{dim}" #{infile}]
end

def edge_distance(rotate, size, text, dim, infile)
    labelimg_d = `#{labelimg size, text, rotate} | #{getwh('-', dim)}`.to_i
    in_d = `#{getwh(infile, dim)}`.to_i
    if in_d < labelimg_d
        STDERR.puts "WARN: #{infile} is too small for the text"
    end
    return in_d - labelimg_d
end

def convert(size, orientation, text, infile)
    vertical, horizontal, direction = orientation.split('-')

    case direction
    when 'horizontal'
        rotate = ''
    when 'vertical'
        rotate = '-rotate 90'
    end

    case vertical
    when 'top'
        vgeometry='+30'
    when 'bottom'
        vgeometry = %Q[+#{edge_distance(rotate, size, text, 'h', infile) - 30}]
    end

    case horizontal
    when 'left'
        hgeometry='+30'
    when 'right'
        hgeometry = %Q[+#{edge_distance(rotate, size, text, 'w', infile) - 30}]
    end

    <<-COV.gsub(/\n/, ' ')
    #{labelimg size, text, rotate} | composite -compose atop -geometry "#{hgeometry}""#{vgeometry}" -
    COV

end

def labelimg(size, text, rotate)
    <<-IMG.gsub(/\n/, ' ')
convert -density 100 -pointsize #{size} -background '#00000099' -fill white 
-gravity center 
-font Times-New-Roman-Bold 
label:" #{text} " 
-strokewidth 8 
#{rotate}
miff:- 
IMG
end

def exif(label, outfile)
    <<-CMD.gsub(/\n/, ' ')
    exiv2 
    -M"set Exif.Photo.UserComment charset=Ascii #{label}" 
    -M"set Iptc.Application2.Caption String #{label}" 
    -M"set Xmp.dc.description lang=\"x-default\" #{label}" 
    mo #{outfile} 
    CMD
end

text = nil
input = nil
output = nil
size = 20
orientation = 'top-left-horizontal'

opts.each do |opt, arg|
    case opt
    when '--text'
        text = arg
    when '--inputfile'
        input = arg
    when '--outputfile'
        output = arg
    when '--textsize'
        size = arg
    when '--orientation'
        orientation = arg
    when '--help'
        help
        exit
    end
end

unless text and input and output
    help
    exit
end

puts "#{convert size, orientation, text, input} #{input} #{output}"
puts exif(text, output)
puts `#{convert size, orientation, text, input} #{input} #{output}`
puts `#{exif(text, output)}`

__END__
#qual=$4
#[ "$qual" == "" ] && qual=70
size=$4
if [ "$size" = "" ]
    then size=20
    fi

    # convert -list font | grep -i times|grep Font:

    convert -density 100 -pointsize $size -background '#00000099' -fill white \
        -gravity center \
        -font Times-New-Roman-Bold \
        label:" $1 " \
        -strokewidth 8 \
        miff:-| \
        composite -compose atop -geometry "+30""+30" - "$2" $3

    #convert $3 -set caption "$1" \
    #-set comment "$1" \
    #-set label "$1" \
    #$3

    exiv2 \
        -M"set Exif.Photo.UserComment charset=Ascii $1" \
        -M"set Iptc.Application2.Caption String $1" \
        -M"set Xmp.dc.description lang=\"x-default\"  $1" \
        mo $3

    #-geometry "+13""+20" \
    echo $2 pointsize $size
    #convert $2 -box '#00000066' \
    #-fill '#00000066' -border "-15" \
    #-pointsize 18 -fill white -font Helvetica \
    #-gravity NorthWest -annotate "+10+10" " $1" $3

    #echo Quality: $qual
