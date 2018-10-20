import sys
import numpy as np
import math
import argparse
from matplotlib import pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg
from PIL import Image
import os
import errno
import json


# PYCAPE
# Post YOLO Crop And Pose Estimation

# open file and yolo estimations for that file
# crop new images around individual players
# send those images to openpose
# with returned data (JSON), scale back up to original image


class Player:
    player_id = -1
    x1 = -1
    y1 = -1
    x2 = -1
    y2 = -1
    confidence = -1


class Pycape:
    numFrames = 100
    framePath = '../frames'
    detectionPath = '../detections'
    estimatedPath = '../estimations'
    currentFrame = 1
    fileExt = '.jpg'
    playersPerFrame = []

    def getPlayers(self):
        # Open image to show players
        imgFile = self.framePath + '/' + \
            str(self.currentFrame) + '.' + self.fileExt
        print("Current directory: " + os.getcwd())
        img = mpimg.imread(imgFile)

        # Open detections to find bounding boxes
        players = []

        detFile = self.detectionPath + '/' + \
            str(self.currentFrame) + '.txt'

        fp = open(str(detFile))
        writeFile = 'frame' + str(self.currentFrame) + 'players.txt'
        f = open(writeFile, "a")
        try:
            line = fp.readline()
            cnt = 0
            while line:

                line = line.split(' ', 1)[1]
                playerStats = line.split()
                p = Player()
                p.confidence = playerStats[0]
                p.x1 = playerStats[1]
                p.y1 = playerStats[2]
                p.x2 = playerStats[3]
                p.y2 = playerStats[4]

                # Check for pixel dimensions. if too large, lets remove this detection.
                # if p.x2 - p.x2 < 400 and p.y2 - p.y1 < 400:
                players.append(p)
                f.write(p.x1 + ' ' + p.y1 + ' ' + p.x2 + ' ' + p.y2 + '\n')
          

                line = fp.readline()
                cnt += 1
        finally:
            fp.close()
            f.close()
            # append amount of players found in each frame.
            self.playersPerFrame[self.currentFrame] = cnt

        num = 0
        cwd = os.getcwd()
        for p in players:

            img2 = Image.open(cwd + '/' + imgFile)
            cropped_image = img2.crop(
                (float(p.x1) - 25.0, float(p.y1) - 25.0, float(p.x2) + 25.0, float(p.y2) + 25.0))

            bufferDirectory = cwd + '/poseInputImages'

            if num == 0:
                try:
                    # Create target Directory
                    os.mkdir(bufferDirectory)
                    print("Directory poseinputimages Created ")
                except OSError as e:
                    if e.errno == errno.EEXIST:
                        print('Directory not created.')
                    else:
                        raise

            os.chdir(bufferDirectory)

            cropped_image.save(str('frame' +
                                   str(self.currentFrame) + 'player' + str(num) + '.' + self.fileExt))
            num += 1
            os.chdir(cwd)
            fp.close()


    def plotPlayersToOriginal(self):
        # Newer method to plot player positions relative to original frame image.
        #
        # Open the original frame, the openpose json positions, and the frame{x}players.txt file which corresponds with which detections 
        # passed to openpose (in order).
        
        # Image of the entire field.
        imageFile = 'YOLO/frames/' + str(self.currentFrame) + '.' + self.fileExt

        # x1 y1 x2 y2 positions of each player passed to openPose
        playerPositionFile = os.getcwd() + '/playerPositions/frame' + str(self.currentFrame) + 'players.txt'
        
        img = mpimg.imread(imageFile)
        fp = open(playerPositionFile, "r")
        #plt.imshow(img)
        plt.show()
        try:
            # read each player position line.
            line = fp.readline()
            cnt = 0
            while line:

                playerStats = line.split()
                
                # for each player, open its keypoints file.
                openposeDets = 'cropOutJSON/frame' + str(self.currentFrame) + 'player' + str(cnt) + '_keypoints.json'
                # read data in from posefile.
                with open(openposeDets, "r") as read_file:
                    data = json.load(read_file)
                # Parse through keypoint file to gather xy info for each limb. 
                #print data
                if len(data['people']) != 0:
                    it = iter(data['people'][0]['pose_keypoints_2d'])
                    for x in it:
                        try:
                            # Repurpose its position with comparison to where on the main image it is.
                            # include 25 pixel buffer added.
                            #print 'player stats: x value: ' + playerStats[0]

                            x1 = int(x)
                            y1 = int(next(it))
                            if x1 == 0 and y1 == 0:
                                next(it)
                                continue
                            #print 'x before adjustment: ' + x1
                            x1 = x1 - 25
                            x1 = x1 + int(playerStats[0])

                            
                            #print 'y before adjustment: ' + y1
                            y1 = y1 - 25
                            y1 = y1 + int(playerStats[1])

                            #print 'x1: ' + str(x1) + ' y1: ' + str(y1)
                            plt.scatter([x1], [y1])  # x1 and y1
                            #plt.imshow(img)
                            
                            next(it)  # skip over confidence level       
                        except:
                            StopIteration
                            print 'error', sys.exc_info()[0]
                
                else:
                    print 'No openpose detection found on' +  openposeDets
                
                line = fp.readline()
                cnt += 1
        finally:
            fp.close()
            print 'closed player position file.'
        plt.imshow(img)
        plt.show()

    def plotPlayers(self):
        # Currently this method is written to open the individually cropped images of openpose and plot the annotated points.
        # This is done simply to make sure the points are plotting properly.
        # Now we need to apply simple math to plot the points of the players from the cropped images to the original image.
        # Currently going to write this in a different method to not mess with current output.

        # Also, this currently expects data (idx, p, and i) to be pulled from an array that says how mny people are in each frame.
        # Although this works now, this isn't a good approach since the videos will be cropped, passed to openpose and THEN this plot
        # function can be called. So to fix this, There is outputted informaiton named frame{x}players where x is the frame. This info
        # includes line by line x1, y1, x2, y2 data on all players passed to openpose.

        # Therefore for the newer method, we should open the original frame, the frame{x}players file, and the openpose JSON files
        # and combine and properly plot the players positions on there.
        for idx, p in enumerate(self.playersPerFrame):
            for i in range(0,p):
                print 'frame:' + str(idx)
                print 'player' + str(i)
                # Open cropped image to plot points onto 
                imgFile = os.getcwd() + '/poseInputImages/frame' + \
                    str(idx) + 'player' + str(i) + '.jpg'
                img = mpimg.imread(imgFile)

                plt.imshow(img)

                directory = os.getcwd()
                # open annotation file to find key points.
                poseFile = directory + '/cropOutJSON/' + 'frame' + \
                    str(idx) + 'player' + str(i) + '_keypoints.json'

                # read data in from posefile.
                with open(poseFile, "r") as read_file:
                    data = json.load(read_file)

                if len(data['people']) != 0:
                    it = iter(data['people'][0]['pose_keypoints_2d'])
                    for x in it:
                        try:
                            #print (x, next(it))
                            plt.scatter([x], [next(it)])  # x1 and y1
                            next(it)  # confidence level       
                        except:
                            StopIteration
                
                #plt.show()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--framePath', required=True)
    parser.add_argument('-d', '--detectionPath', required=True)
    parser.add_argument('-n', '--numFrames', required=True)
    parser.add_argument('-e', '--ext', required=True)

    parsed = parser.parse_args()
    pycape = Pycape()

    pycape.framePath = str(parsed.framePath)
    pycape.detectionPath = str(parsed.detectionPath)
    pycape.numFrames = parsed.numFrames
    pycape.fileExt = str(parsed.ext)
    pycape.currentFrame = 2
    pycape.playersPerFrame = [0,0,0,0,0,0,0,0,0,0,0]

    # for i in range(1, 11):
    #     pycape.currentFrame = i
    #     pycape.getPlayers()

    pycape.plotPlayersToOriginal()


# Will only run if this file is called as primary file
if __name__ == "__main__":
    main()
