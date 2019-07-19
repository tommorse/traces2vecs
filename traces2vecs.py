#!/usr/bin/python
# traces2vecs.py
# Tom Morse updated on 20180227.  Originial from 20120314
# This program is for converting traces in a graph to an approximation
# of those traces as vectors whose values are the values on the axes of 
# the figure.  It relies on the user having access to inkscape, a free
# application available on all platforms: www.inkscape.org
# traces2vecs.py accepts as input a postscript file and writes
# NEURON (that could easily be converted to matlab/octave style vectors 
# by chopping off the first two lines) of the traces in the graph.
# This postscript file is assumed to be the result of importing
# a research paper's figure (as a tif) into a new inkscape figure and then
# editing the figure by selecting the "Bezier or straight line" path tool (shift-f6)
# and then left clicking to start and add points to a polygon, the right
# click will finish the line without adding additional points past the last left click.
# When done tracing the curves, select the background image by first selecting the
# select arrow and then clicking anywhere on the background except where you created lines.
# Press the delete key to delete the background image.  Then select
# file -> save and
# type or click a file name with ps (postscript) extension.  When the file is saved the pixel values
# of all the points will be written as text at the end of the file.
# Important:
# The first three or four points you click will need to be the axis
# traces2vecs.py assumes that the first three or four points 
# (at the end of the postscript
# file) delimit the axis by tracing
# the (x,y) points on the axis:
# (ignored x, y_axis_max), (x_axis_min,y_axis_min), (x_axis_max,ignored y) or if 4 points
# (ignored x, y_axis_max), (ignored x, y_axis_min), 
#  (x_axis_min, ignored y), (x_axis_max, ignored y)
# The order of the mouse clicks on the max y, (0,0), max x axis is important
# because the values of these points are user pre-supplied in a data file
# called axis_limits.dat whose first line is the y_axis_max and the second
# line is y_axis_extreme.  traces2vecs.py uses the linear transformation created
# by using axis_limits.dat and the pixel values recorded on the first three
# clicks.
# The output files are given the names traceX.dat where
# trace0.dat should reflect the values in axis_limits.dat and
# traceX with X from 1 to the number of traces are the subsequent traces.


""" usage:
 traces2vecs.py input.ps
 Running assumes axis_limits.dat exists in the current dir and has four lines:
 the max y value (the yvalue where your first click will be)
 the min y value (the y value where your second click will be
 the min x value (the x value where your second click will be)
 the max x value (the x value where your third click will be)
 which are the paper's scale values.
 Please click on three or four points on the axes as your first poly line 
 corresponding to the max y, min y, min x, max x points on the axes.
 (If the min y and  min x point occur at the same point you only need 
 to click 3 points).
 Recall that in inkscape, after importing your figure as a tif, select
 polyline (e) in the left tool column, and then left click to add a point,
 right click to end a line without adding new points.
 When done, select file -> save, and save your file as e.g., input.ps which then
 you will supply as shown in the first line in this help.  Finally you can
 import the traceX.dat files into matlab or excel by lopping off the first two
 lines of each, or you can read them into NEURON afer setting the first line in
 the read_lines.hoc file to the appropriate number and executing nrngui read_lines.hoc.
"""

# note that the extreme points on the axis are called max below
# and that each point has an x,y value, e.g. the first point
#
# Variables with suffix pix are pixel values, otherwise they are
# the "graphed" values, i.e. correspond to the numbers on the graph tic marks or scales
#

import os
import sys
import numpy as np
input_ps_name = ""
if (len(sys.argv)!=2):
  print "I notice no inkscape output file was supplied as an argument - I will look later for one..."
else:
  input_ps_name = sys.argv[1]
  print input_ps_name
  #
  # read in the values from the axis limits file
  print("Opening "+input_ps_name +" for finding your manually entered")
  print("axis clicks (top y, origin, left x) and subsequent traces.\n")

fid=0 # file id for inkscape file given global scope for later analysis

try:
  axis_limits_file = open( "axis_limits.dat","r")
except:
    print("Couldn't open axis_limits.dat file")
    print("This file needs to be in the current directory and")
    print("contains:\nthe max y value\nthe min y value\nthe min x value")
    print("the max x value\n(on seperate lines)\n")
    print("These user supplied numbers are the paper figures values corresponding to your")
    print("first three mouse clicks on the figure (high y axis, origin, far right x axis)")
    print("Then traces2vecs.py will use the pixel values as returned by inkscape matched")
    print("to the above axis_limits user supplied data to transform the subsequent curves.")
    exit(1)

  # another possibility would be to use while (fgets(buf,1000, axis_limits_file)!=NULL) {}
axis_limits_array=axis_limits_file.readlines()

global y_axis_max_y, y_axis_min_y, x_axis_min_x, x_axis_max_x 
y_axis_max_y = eval(axis_limits_array[0])
y_axis_min_y = eval(axis_limits_array[1])
x_axis_min_x = eval(axis_limits_array[2])
x_axis_max_x = eval(axis_limits_array[3])

print("From axis_limits.dat:\n")
print("y_axis_max_y = "+str(y_axis_max_y)+"\ny_axis_min_y = "+str(y_axis_min_y)+\
  "\nx_axis_min_x = "+str(x_axis_min_x)+"\nx_axis_max_x = "+str(x_axis_max_x))

found_inkscape_file=0 # 0 is false: set true if find an inkscape file
if (len(sys.argv)>1):
  try:
    fid=open(sys.argv[1],"r")
    found_inkscape_file=-1 # set true
  except:
    print("Couldn't open "+sys.argv[1]+" file")
    print("This file needs to be in the current directory/specified path")
    exit(1)
else:
  print "No inkscape file supplied as input."
  print "I am going to look for an inkscape file"
  files=os.listdir(".")
  for f in files:
    if (f[-3:]=='.ps'):
      try:
        print "*** Found one!: Using "+f+" as inkscape file (to read)."
        fid=open(f,"r")
        found_inkscape_file=-1
      except:
        print("For some reason could not open an inkscape file, "+f+", I found")
        exit(1)
      break
if (~found_inkscape_file):
  print ("Wasn't supplied or couldn't find an inkscape (.ps) file in current directory.")
  exit(1)
# print 
start_position=0
file_data=fid.readlines()
line_starts=[] # a list of the indicies that lines start in the supplied file
for i in range(len(file_data)):
  # print "Checking: "+file_data[i]
  if " cm" in file_data[i]: # 20180226 I noticed that lines start after " cm"
    # print "found an MLine at line "+str(i)
    start_position=i+1
    line_starts.append(start_position)

# now have the starting position for the pixel lines: convert them all into a list of traces

def parse_a_line(index):
  parsed_path=[]# a path is a trace in the graph (can be axes or data)
  i=index
  line_text=''
  while i< len(file_data):
    line_text=line_text + file_data[i][:-1]
    if 'S' in line_text:
     break
    i = i + 1
  points_text = line_text.split(' m ')  
  points_text_list = points_text[0].split(' ')
  point_float_list=[float(x) for x in points_text_list]
  parsed_path.append(point_float_list)
  # now add the other [x,y] points
  other_points_text = points_text[1].split('S')[0].split(' l ')[:-1]
  for x in other_points_text:
    xlist=x.split(' ')
    parsed_path.append([eval(xlist[0]), eval(xlist[1])])
  return parsed_path

traces=[] # will be list of lists of m vectors x,y coordinates, e.g.:
# traces=[ [ [x00,y00],[x01,y01],[x02,y02],[x03,y03] ],
# [ [x10,y10],[x11,y11],[x12,y12],[x13,y13],...,[x1n,y1n] ],
#  ...
# [ [xm0,ym0],[xm1,ym1],[xm2,ym2],[xm3,ym3],...,[xmn,ymn] ] ]

for index in line_starts:
  traces.append(parse_a_line(index))

# the above has parsed the postscript file into a list of traces:
# traces[0] is the clicks on the axes
# traces[1] is the first trace
# ...
# traces[m] contains the last trace
# Note: the traces can all be different sizes (different numbers of pairs of points)

if len(traces)<2:
  print('Surprisingly there were ',len(traces),' traces where')
  print('at least 2 were expected (The axes and at least one data line).')
  print('traces = ', repr(traces))
  quit()
  
axes_num_of_clicks=len(traces[0])

yaxis_xvec=traces[0][0][0]
yaxis_yvec=traces[0][0][1]
if (axes_num_of_clicks==3):
  origin_xvec=traces[0][1][0]
  origin_yvec=traces[0][1][1]
  xaxis_xvec=traces[0][2][0]
  xaxis_yvec=traces[0][2][1]
  #
  # now have the pixel values for the top y, origin, left x axes so
  # need to combine them with the read-in figure scale values 
  #
  print "Using your inkscape 'first three clicks' line for the axis values:\n"
  print "yaxis max: ",yaxis_xvec, ", ", yaxis_yvec
  print "origin:    ",origin_xvec, ", ", origin_yvec
  print "xaxis max: ",xaxis_xvec, ", ", xaxis_yvec
  #x_fig = ((x_axis_max_x-x_axis_min_x)/(x_axis_pix_max - x_axis_pix_origin))*(x_pix - x_axis_pix_origin)
  #y_fig = ((y_axis_max_y-y_axis_min_y)/(y_axis_pix_max - y_axis_pix_origin))*(y_pix - y_axis_pix_origin)
  
  x_axis_pix_max = xaxis_xvec
  x_axis_pix_origin = origin_xvec
  
  y_axis_pix_max = yaxis_yvec
  y_axis_pix_origin = origin_yvec
elif (axes_num_of_clicks==4):
  ignore_xvec=traces[0][1][0]
  origin_yvec=traces[0][1][1]
  origin_xvec=traces[0][2][0]
  ignore_yvec=traces[0][2][1]
  xaxis_xvec =traces[0][3][0]
  xaxis_yvec =traces[0][3][1]
  #
  # now have the pixel values for the top y, origin, left x axes so
  # need to combine them with the read-in figure scale values 
  #
  print "Using your inkscape 'first four clicks' line for the axis values:\n"
  print "yaxis max: ",yaxis_xvec, ", ", yaxis_yvec
  print "xaxis min, yaxis_min:    ",origin_xvec, ", ", origin_yvec
  print "xaxis max: ",xaxis_xvec, ", ", xaxis_yvec
  #x_fig = ((x_axis_max_x-x_axis_min_x)/(x_axis_pix_max - x_axis_pix_origin))*(x_pix - x_axis_pix_origin)
  #y_fig = ((y_axis_max_y-y_axis_min_y)/(y_axis_pix_max - y_axis_pix_origin))*(y_pix - y_axis_pix_origin)
  
  x_axis_pix_max = xaxis_xvec
  x_axis_pix_origin = origin_xvec  # actually min xvalue
  
  y_axis_pix_max = yaxis_yvec
  y_axis_pix_origin = origin_yvec  # actually min yvalue
else:
  print "I am confused by your first line being "+str(axes_num_of_clicks)
  print "Please either click on three or four points to enter axes."
  print "See documentation for more help."
  exit(1)

def x_pix2x_fig(x_pix):
  # converts a pixel x-coordinate to a figure x coordintate
  # note that without float below it is possible that integer arithmatic will corrupt the calculation
  return (float(x_axis_max_x-x_axis_min_x)/(x_axis_pix_max - x_axis_pix_origin))*(x_pix - x_axis_pix_origin)+x_axis_min_x

def y_pix2y_fig(y_pix):
  # note that without float below it is possible that integer arithmatic will corrupt the calculation
  return (float(y_axis_max_y-y_axis_min_y)/(y_axis_pix_max - y_axis_pix_origin))*(y_pix - y_axis_pix_origin)+y_axis_min_y

if (axes_num_of_clicks==3):
  print "confirmation run of conversions x_pix2xfig, y_pix2y_fig:"
  print "upper y axis: "+str(x_pix2x_fig(yaxis_xvec))+", "+str(y_pix2y_fig(yaxis_yvec))
  print "graph origin: "+str(x_pix2x_fig(origin_xvec))+", "+str(y_pix2y_fig(origin_yvec))
  print "right x axis: "+str(x_pix2x_fig(xaxis_xvec))+", "+str(y_pix2y_fig(xaxis_yvec))
else:
  print "confirmation run of conversions x_pix2xfig, y_pix2y_fig:"
  print "upper y axis: "+str(x_pix2x_fig(yaxis_xvec))+", "+str(y_pix2y_fig(yaxis_yvec))
  print "lower y axis: "+str(x_pix2x_fig(ignore_xvec))+", "+str(y_pix2y_fig(origin_yvec))
  print "left x axis: "+str(x_pix2x_fig(origin_xvec))+", "+str(y_pix2y_fig(ignore_yvec))
  print "right x axis: "+str(x_pix2x_fig(xaxis_xvec))+", "+str(y_pix2y_fig(xaxis_yvec))

for X in range(len(traces)): # iterate over the number of traces
  filename="trace"+repr(X)+".dat"
  file=open(filename,"w")
  file.write("label: trace"+repr(X)+"\n")
  file.write(repr(len(traces[X]))+"\n")
  for i in range(len(traces[X])):
    file.write(repr(x_pix2x_fig(traces[X][i][0]))+" "+repr(y_pix2y_fig(traces[X][i][1]))+"\n")
  file.close()
print("Success!")
