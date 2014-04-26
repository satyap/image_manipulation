#!/usr/bin/ruby

require 'getoptlong'

class ImageAnnotate

  def initialize
    @text = nil
    @input = nil
    @output = nil
    @size = 20
    @orientation = 'top-left-horizontal'
  end
  def cmd_line
    opts = GetoptLong.new(
      ['--text', '-t', GetoptLong::REQUIRED_ARGUMENT],
      ['--inputfile', '-i', GetoptLong::REQUIRED_ARGUMENT],
      ['--outputfile', '-o', GetoptLong::REQUIRED_ARGUMENT],
      ['--textsize', '-s', GetoptLong::REQUIRED_ARGUMENT],
      ['--orientation', '-d', GetoptLong::REQUIRED_ARGUMENT],
      ['--help', '-h', GetoptLong::NO_ARGUMENT],
    )

    opts.each do |opt, arg|
      case opt
      when '--text'
        @text = arg
      when '--inputfile'
        @input = arg
      when '--outputfile'
        @output = arg
      when '--textsize'
        @size = arg
      when '--orientation'
        @orientation = arg
      when '--help'
        help
        exit
      end
    end

    unless @text and @input and @output
      help
      exit
    end

    puts `#{convert} #{@input} #{@output}`
    puts `#{exif}`
  end

  def help
    puts <<-TXT
    #{$0} -t "Text to put on image" -i inputfile -o outputfile [-s 20 -d top-horizontal]
    TXT
  end

  def getwh(file, dim)
    %Q[identify -format "%#{dim}" #{file}]
  end

  def edge_distance(rotate, dim)
    labelimg_d = `#{labelimg rotate} | #{getwh('-', dim)}`.to_i
    in_d = `#{getwh(@input, dim)}`.to_i
    if in_d < labelimg_d
      STDERR.puts "WARN: #{@input} is too small for the text"
    end
    return in_d - labelimg_d
  end

  def convert
    vertical, horizontal, direction = @orientation.split('-')

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
      vgeometry = %Q[+#{edge_distance(rotate, 'h') - 30}]
    end

    case horizontal
    when 'left'
      hgeometry='+30'
    when 'right'
      hgeometry = %Q[+#{edge_distance(rotate, 'w') - 30}]
    end

    return <<-COV.gsub(/\n/, ' ')
    #{labelimg rotate} | composite -compose atop -geometry "#{hgeometry}""#{vgeometry}" -
    COV

  end

  def labelimg(rotate)
    <<-IMG.gsub(/\n/, ' ')
    convert -density 100 -pointsize #{@size} -background '#00000099' -fill white 
    -gravity center 
    -font Times-New-Roman-Bold 
    label:" #{@text} " 
    -strokewidth 8 
    #{rotate}
    miff:- 
      IMG
  end

  def exif
    <<-CMD.gsub(/\n/, ' ')
    exiv2 
    -M"set Exif.Photo.UserComment charset=Ascii #{@text}" 
    -M"set Iptc.Application2.Caption String #{@text}" 
    -M"set Xmp.dc.description lang=\"x-default\" #{@text}" 
    mo #{@output} 
    CMD
  end

end

if __FILE__==$0
  ImageAnnotate.new.cmd_line
end
