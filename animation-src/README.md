### Requirements
* GIMP (http://gimp.org)
* ImageMagick convert (http://imagemagick.org/script/convert.php)

### Preparing animation frames
* Open cbox-wifi-animation.xcf in GIMP
* Prepare adaptations / additions to each frame as needed
* use "Export as" to save each frame in the corresponding subdirectory (in alphabetical order)

### Commands in order to make two animations:
* Chrome:
```
cd cbox-animation-chrome
convert -fuzz 1% -delay 1x3 -loop 0 *.png -coalesce -layers OptimizeTransparency cbox-wifi-animation.gif
```
* Safari:
```
cd cbox-animation-ios
convert -fuzz 1% -delay 1x3 -loop 0 *.png -coalesce -layers OptimizeTransparency cbox-wifi-animation-ios.gif`
```
