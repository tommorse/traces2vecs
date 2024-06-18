This is the readme.txt for traces2vecs.py, a python program by Tom
Morse that converts traces from a paper figure
into NEURON vectors. 20190719, 20180227, 20120314, 20120308.

SUMMARY:

First import a tif (or jpg, png, etc.) figure into inkscape to
manually create (by clicking) polylines (many point lines) which trace
over the curves you would like as vectors in NEURON. Save this
inkscape file, and then secondly run traces2vecs.py which will read
the new inkscape file and create the NEURON vector files. Then you can
edit read_traces.hoc to set the number of traces present, and then run
read_traces.hoc under NEURON to see your traces graphed in NEURON.

DETAILED DIRECTIONS:

1) Open Inkscape

2) import your tiff: File -> import (then browse to and open your
image file (doesn't have to be tiff))

3) Conveniently view your image: select File -> Document properties ->
(+ box next to) Resize page to content -> Resize page to drawing or
selection. Close document properties window

Use the middle mouse button to center the drawing, and then hold the
control key down while using the scrool bar to zoom the drawing so
that it is as big as possible on your screen to increase the accuracy
of the pixels reported from your clicks on the image.

4) select "Bezier and straight line path". (In my version of inkscape,
in the left hand toolbar it is the 11th tool down from the top and the
9th tool up from the bottom).

5) Calibrate by clicking on the axes of the graph:

In the following you will need to click on where you know what the
value of the coordinate on the axis is.  That pretty much means you
need to click on a tic mark unless you are clicking on the ends of
scale bars, in which case you can make up the absolute values of the
scale bar ends (when you create the axis_limits.dat file later - see
below), however the relative difference between the scale bar ends
needs to be the value reported for the figure.  Left click on the top
of the y-axis, then the bottom of the y axis. If there is an x-axis
left click on the minimum and then the maximum points (that have known
values, such as on tic marks). Finish with a right click (anywhere).

If the bottom of the y axis (frequently the origin) is the same as the
left most part of the x axis, then left click on the right most point
on the x axis.  Then right click to finish writing the path (right
click does not add a point). Note that if you are clicking on scale
bars that look like a backwards L then just enter a negative number
for the last number in axis_limits.dat, or a number that is less than
the first x axis number (the min and max x's are permuted; see below).

6) Add all the traces: Add each line (sometimes called a trace) from
the graph by repeating this method:

a) left click data points (usually from left to right)

b) Right click to finish the path (doesn't add any points)

7) Delete the background image: Change the tool to the selection arrow
(the top tool in the left hand tool bar) and select the background
image by clicking on it anywhere other than where you have drawn
lines. Delete the background image by pressing the delete key.

8) Select File->Save from the menu to save as a ps file.

9) Prepare the axis_limits.dat file to contain max y, min y, min x,
max x on four different lines.
These values need to be entered by hand and should match the values
that the points you clicked on the axes or scale bars of the graph
represented.

10) Run
traces2vec.py yourfilename.ps

11) Examine the traces created, traceX.dat.
You can delete the first two lines of these files and use them in
matlab or excel

If successful, the program will create traceX.dat, vectors files
suitable for reading into NEURON, where trace0.dat is the axes, and
trace1.dat, trace2.dat, ... are the traces your subsequently supplied with
mouse clicked polylines.

In the example folder I supply a sample NEURON program,
read_traces.hoc, that will read your traces into NEURON and graph them
after you set the value of the number of traces in the first line of
read_traces.hoc.

