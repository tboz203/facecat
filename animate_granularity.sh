#!/bin/sh
#
# Create a animation of varying granularity
#

# Generate initial random image (also  granularity=0 image)
command='convert -size 300x300 xc: +noise random'
echo "$command"

# Ensure final image is 'tilable' makes results better too..
element=" -virtual-pixel tile"
echo "$element"
command+="$element"

# to speed things up - lets limit operaqtions to just the 'G' channel.
element=" -channel G"
echo "$element"
command+="$element"

# generate a sequence of images with varying granularity
b=0.5
for i in $(seq 16);  do
    element=" \\( -clone 0 -blur 0x$b \\)"
    echo "$element"
    command+="$element"
    b=$(convert null: -format "%[fx: $b * 1.3 ]" info:)
done

# normalize and seperate a grayscale image
element=" -normalize  -separate  +channel"
echo "$element"
command+="$element"

# seperate black and white granules in equal divisions of black,gray,white
#command+="  +dither -posterize 3"
element="  -ordered-dither threshold,3"
echo "$element"
command+="$element"

# Set intermedite frame animation delay and infinite loop cycle
element=" -set delay 12"
echo "$element"
command+="$element"

# give a longer pause for the first image
element=" \\( -clone 0 -set delay 50 \\) -swap 0 +delete"
echo "$element"
command+="$element"

# give a longer pause for the last image
element=" \\( +clone -set delay 50 \\) +swap +delete"
echo "$element"
command+="$element"

# make it a patrol cycle (see Animation Modifications)
element=" \\( -clone -2-1 \\)"
echo "$element"
command+="$element"


# final image save
element=" -loop 0 animate_granularity.gif"
echo "$element"
command+="$element"

echo "$command"
eval $command

# chmod 644 animate_granularity.gif
