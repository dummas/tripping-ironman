#!/usr/bin/env python2

# DCT
from scipy.fftpack import *
# PCA
from pca import *
# file_to_array
from functions import data_to_array
# Naitive matplotlib
import matplotlib
matplotlib.use('WXAgg')
# Another PCA
from matplotlib.mlab import PCA
# Plotting lib
#import matplotlib.pyplot as plt
# 3D Axes
#from mpl_toolkits.mplot3d import Axes3D

# Numpy needed by mlpy
from numpy import *
# Mlpy
import mlpy

#SIGNAL_01 = open('data/data01_n.dat', 'r');
#SIGNAL_02 = open('data/data02_n.dat', 'r');

NUMBER_OF_WINDOWS = 10
NUMBER_OF_ACTIVITY = 2
WINDOW_SIZE = 100
WINDOW_DELAY = 50

SVM_PREDICT_01 = open('data_from_analyzer_01/svm_1.dat', 'w')
SVM_PREDICT_02 = open('data_from_analyzer_01/svm_2.dat', 'w')

ACTIVITY_01 = open('data_from_analyzer_01/activity_1.dat', 'w')
ACTIVITY_02 = open('data_from_analyzer_01/activity_2.dat', 'w')

SIGNAL_DCT_01 = open('data_from_analyzer_01/signal_dct_1.dat', 'w')
SIGNAL_DCT_02 = open('data_from_analyzer_01/signal_dct_2.dat', 'w')

signal_dct_01 = []
signal_dct_02 = []

#output = open('data_from_analyzer/data001.dat', 'w')

#signal_01 = data_to_array( SIGNAL_01 )
#signal_02 = data_to_array( SIGNAL_02 )

for window in range(1, NUMBER_OF_WINDOWS+1):

	for activity in range(1, NUMBER_OF_ACTIVITY+1):
	
		data_file = open('data/data0' + str(activity) + '_n.dat', 'r')
		
		signal = data_to_array ( data_file )
		
		if activity == 1:
			signal_class = 1;
		else:
			signal_class = -1;
			
		training_output_file = open('data_from_analyzer_01/train_data' + str(window) + '.dat', 'a')
		testing_output_file = open('data_from_analyzer_01/test_data' + str(window) + '.dat', 'a')
		
		if window is 1:
		
			if activity == 1:
				signal_dct_01.append( dct ( signal[1:window*WINDOW_SIZE] ) )
			else:
				signal_dct_02.append( dct ( signal[1:window*WINDOW_SIZE] ) )
				
			signal_pca = PCA ( dct ( signal[1:window*WINDOW_SIZE] ) )
		else:
			if activity == 1:
				signal_dct_01.append( dct ( signal[window*WINDOW_SIZE-WINDOW_DELAY:window*WINDOW_SIZE] ) )
			else:
				signal_dct_02.append( dct ( signal[window*WINDOW_SIZE-WINDOW_DELAY:window*WINDOW_SIZE] ) )
			signal_pca = PCA ( dct ( signal[window*WINDOW_SIZE-WINDOW_DELAY:window*WINDOW_SIZE] ) )
			
		for vector in zip ( signal_pca.a.T[0], signal_pca.a.T[1], signal_pca.a.T[2] ):
			if activity == 1:
				print >>ACTIVITY_01, vector[0], vector[1], vector[2]
			else:
				print >>ACTIVITY_02, vector[0], vector[1], vector[2]
				
			print >>training_output_file, str(vector[0]) + '\t' + str(vector[1]) + '\t' + str(vector[2]) + '\t' + str(signal_class)
			print >>testing_output_file, str(vector[0]) + '\t' + str(vector[1]) + '\t' + str(vector[2])
			


# FANCY STUFF
mlx, mly = mlpy.data_fromfile('data_from_analyzer_01/train_data1.dat');

svm = mlpy.Svm(kernel='gaussian', C= 0.9);
svm.compute(mlx, mly)

mltx, mlty = mlpy.data_fromfile('data_from_analyzer_01/train_data1.dat');

for vector in mltx:
	if svm.predict(vector) == 1:
		print >>SVM_PREDICT_01, vector[0], vector[1], vector[2]
	else:
		print >>SVM_PREDICT_02, vector[0], vector[1], vector[2]
		
		
for vector in signal_dct_01:
	print >>SIGNAL_DCT_01, vector[0], vector[1], vector[2]
	
for vector in signal_dct_02:
	print >>SIGNAL_DCT_02, vector[0], vector[1], vector[2]
	
		

#for activity in range(1, NUMBER_OF_ACTIVITY+1):

#	data_file = open('data/data0' + str(activity) + '_n.dat', 'r')
	
#	signal = data_to_array ( data_file )
	
#	if activity == 1:
#		signal_class = 1;
#	else:
#		signal_class = -1;

#	for window in range(1, NUMBER_OF_WINDOWS+1):
	
		#output = open('data_from_analyzer/data0'+ str(activity) +'_' + str(window) + '.dat', 'w')
		
	
#		if window is 1:
			#signal_fft = fft(signal[1:window*WINDOW_SIZE] )
			#signal_pca = PCA( signal_fft )
#			signal_pca = PCA ( dct ( signal[1:window*WINDOW_SIZE] ) )
#		else:
			#signal_fft = fft(signal[window*WINDOW_SIZE-WINDOW_DELAY:window*WINDOW_SIZE] )
			#signal_pca = PCA(  signal_fft )
			#signal_pca = PCA ( dct ( signal[window*WINDOW_SIZE-WINDOW_DELAY:window*WINDOW_SIZE] ) )
		
#		for vector in zip ( signal_pca.a.T[0], signal_pca.a.T[1], signal_pca.a.T[2]):
			#print >>output, abs(vector[0]), abs(vector[1]), abs(vector[2])
#			acc = vector[0] + vector[1] + vector[2]
#			print >>output, str(vector[0]) + '\t' + str(vector[1]) + '\t' + str(vector[2]) + '\t' + str(signal_class)
		
	#print window
	

#PCA_OUTPUT_01 = open('data_from_analyzer/data01.dat', 'w')
#PCA_OUTPUT_02 = open('data_from_analyzer/data02.dat', 'w')



#signal_01_pca = PCA(dct(signal_01[100:200]))
#signal_02_pca = PCA(dct(signal_02[100:200]))

#for vector in zip(signal_01_pca.a.T[0], signal_01_pca.a.T[1], signal_01_pca.a.T[2]):
	#print >>PCA_OUTPUT_01, vector[0], vector[1], vector[2]
	
#for vector in zip(signal_02_pca.a.T[0], signal_02_pca.a.T[1], signal_02_pca.a.T[2]):
	#print >>PCA_OUTPUT_02, vector[0], vector[1], vector[2]

#fig = plt.figure()
#ax = fig.add_subplot(211, projection='3d')
#ay = fig.add_subplot(212, projection='3d')

#ax.scatter(signal_01_pca.a.T[0], signal_01_pca.a.T[1], signal_01_pca.a.T[2])
#ay.scatter(signal_02_pca.a.T[0], signal_02_pca.a.T[1], signal_02_pca.a.T[2])

#plt.show()
