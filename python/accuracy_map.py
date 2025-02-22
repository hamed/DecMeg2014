"""DecMeg2014 example code.

This code creates a simple sensor maps from the data of a given
subject. The value at each location is the cross-validated accuracy.

Copyright Emanuele Olivetti 2014, BSD license, 3 clauses.
"""

import numpy as np
from scipy.io import loadmat
from sklearn.linear_model import LogisticRegression
from sklearn.cross_validation import cross_val_score
import matplotlib.pyplot as plt
from topography import topography
    
if __name__ == '__main__':

    subject = 1
    cv = 5 # numbers of fold of cross-validation

    clf = LogisticRegression(random_state=0)

    filename = 'data/train_subject%02d.mat' % subject
    print "Loading %s" % filename
    data = loadmat(filename, squeeze_me=True)
    X = data['X']
    y = data['y']

    print "Loading channels name."
    channel_name = np.loadtxt('../additional_files/Vectorview-all.lout', skiprows=1, usecols=(5,), delimiter='\t', dtype='S')

    print "Computing cross-validated accuracy for each channel."
    score_channel = np.zeros(X.shape[1])
    for channel in range(X.shape[1]):
        print "Channel %d (%s) :" % (channel, channel_name[channel]),
        X_channel = X[:,channel,:].copy()
        X_channel -= X_channel.mean(0)
        X_channel = np.nan_to_num(X_channel / X_channel.std(0))
        scores = cross_val_score(clf, X_channel, y, cv=cv, scoring='accuracy')
        score_channel[channel] = scores.mean()
        print score_channel[channel]

    print
    print "Plotting."
    plt.interactive(True)

    print "Loading channels coordinates."
    coords_xy = np.loadtxt('../additional_files/Vectorview-all.lout', skiprows=1, usecols=(1,2))
    plt.figure()
    topography(score_channel, coords_xy[:,0], coords_xy[:,1])
    plt.title("Classification Accuracy at each Channel")

    print
    print "Channels with highest accuracy:",
    n_best = 3
    best_channels = np.argsort(score_channel)[-n_best:][::-1]
    print best_channels
    print "Plotting the average signal of each class."
    X_best_face = (X[:,best_channels,:][y==1]).mean(0) * 1.0e15
    X_best_scramble = (X[:,best_channels,:][y==0]).mean(0) * 1.0e15
    X_best_face_std = (X[:,best_channels,:][y==1]).std(0) * 1.0e15
    X_best_scramble_std = (X[:,best_channels,:][y==0]).std(0) * 1.0e15
    time = np.linspace(-0.5, 1.0, 375)
    plt.figure()
    for i, channel in enumerate(best_channels):
        plt.subplot(n_best,1,i+1)
        plt.plot(time, X_best_face[i], 'r-')
        plt.plot(time, X_best_scramble[i], 'b-')
        plt.axis('tight')
        plt.text(0.6, X_best_face[i].max(), str(i+1)+') '+str(channel_name[channel])+' = '+("%0.2f" % score_channel[channel]), bbox=dict(facecolor='white', alpha=1.0))
        if i == (len(best_channels) - 1):
            plt.xlabel('Time (sec)')
            
        if i == (len(best_channels) / 2):
            plt.ylabel('Magnetic Field (fT)')

    # highlight best channels:
    plt.figure()
    v=np.zeros(306)
    v[best_channels] = np.arange(n_best) + 1
    topography(v, coords_xy[:,0], coords_xy[:,1])

    print
    print "Plotting magnetometer map."
    mag_indexes = np.array([cn[-1]=='1' for cn in channel_name], dtype=np.bool)
    plt.figure()
    topography(score_channel[mag_indexes], coords_xy[mag_indexes,0], coords_xy[mag_indexes,1])
    plt.title("Classification Accuracy at each Magnetometer")


    print "Computing cross-validated accuracy for each pair of gradiometers."
    # Here follows a somewhat involved :) but general code to pair
    # gradiometers according to their name:
    # grad_indexes = np.array([cn[-1]!='1' for cn in channel_name], dtype=np.bool)
    # triplet_name = sorted(set([cn[:-1] for cn in channel_name]))
    # grad_pair_name = [filter(lambda cn: cn.startswith(tn), channel_name[grad_indexes]) for tn in triplet_name]
    # grad_pair_idx = [[np.where(channel_name==grad1)[0][0], np.where(channel_name==grad2)[0][0]] for grad1, grad2 in grad_pair_name]

    # The previous code is equivalent to:
    grad_pair_idx = np.array((range(0,306,3), range(1,306,3))).T

    score_grad_pair = np.zeros(len(grad_pair_idx))
    for i, (channel1, channel2) in enumerate(grad_pair_idx):
        print "Channels %d (%s), %d (%s) :" % (channel1, channel_name[channel1], channel2, channel_name[channel2]),
        X_grad_pair = np.hstack([X[:, channel1 ,:], X[:, channel2 ,:]])
        X_grad_pair -= X_grad_pair.mean(0)
        X_grad_pair = np.nan_to_num(X_grad_pair / X_grad_pair.std(0))
        scores = cross_val_score(clf, X_grad_pair, y, cv=cv, scoring='accuracy')
        score_grad_pair[i] = scores.mean()
        print score_grad_pair[i]

    print
    print "Plotting gradiometers map."
    plt.figure()
    topography(score_grad_pair, coords_xy[mag_indexes,0], coords_xy[mag_indexes,1])
    plt.title("Classification Accuracy at each Pair of Gradiometers")
    
    # plt.show()

