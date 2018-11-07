# pycape
## Post YOLO Crop and Pose Estimation

This repository is created for our Senior Design Project, Soccer Video Analytics, in conjunction with SporSight LLC.
We worked on this project from February 2018 - November 2018.

This repository is created to enhance the OpenPose Pose Estimations on a multi-object detection view.
Although OpenPose is designed for Multi-Object Detections, it fails to detect people of small sizes (100 pixels and smaller).
To fix this issue, we created this repository.

## Requirements
The requirements for this project are the computed YOLO Detections, and video frames.
The computed YOLO Detections fall in the following form:

- A Folder titled *YOLO*
  - sub folder titled *dets* containing the detections found by YOLO.
    - Each file should be titled {X}.txt, where x represents the detections for that frame.
  - sub folder titled *frames* containing the frames of the video.
    - Each file should be titled {x}.jpg where x represents the frame number.
   
### Detection files
Each of the detection files as mentioned above should follow this format:

  object confidence x1 y1 x2 y2

Example:
person .98 1343 600 1367 640 
person .68 568 230 597 250
person .50 229 450 250 486

Because we limited the output of our YOLO code to only "person"'s detected, we didn't worry about other objects.

## Pipeline
The following describes how the pipeline of this repository works.
1. Supply YOLO dataset
2. run pycape.py with crop mode (more on this later)
3. pass extracted images to OpenPose
4. pass extracted JSON files from OpenPose to pycape repository (more on this later)
5. run pycape.py on export mode

At this point, the keypoints of each frame are extracted and held in one JSON file.
From here we plan to pass these keypoints in to DetectAndTrack, with the bounding boxes. We may pickle these together or read them from the extracted JSON file.

## Folder Structure

### YOLO
This Folder holds the precomputed YOLO detections and frames. 
Folder structure explained above under *requirements*

### cropOutJSON
This folder holds the keypoints as constructed by OpenPose. Currently, will need to be placed in this folder until pipelining is completed, or until all is containerized.
These will be saved in the format: frame{x}player{y}_keypoints.json, where x represents the frame and y represents the player #.

### playerPositions
This folder stores the positions of each player in each frame after being modified and accepted as an actual player to detect.
It reorganizes the values to match what is expected for DetectAndTrack.

### poseInputImages
This folder stores the images cropped by the Crop method. These crops are determinded by the precomputed YOLO detections and are the images that are passed to OpenPose.

### trackingKeypoints
This folder contains the combined keypoints of each player detected on a field. This folder is populated after running the export method in pycape.py. 

### cropImgOut
This folder isn't necessary as it just holds the cropped images from OpenPose. These aren't necessarily needed, because all computation happens based off of the JSON files, not the images.

## Pycape.py

### Class Player

This holds the basic information of each player that is being computed. It stores the following information:

- Player ID: currently not in use, but left just in case for future use.
- x1: first x position of the player (Left-most x position of Bounding Box)
- y1: first y position of the player (Bottom-most position of Bounding Box)
- x2: second x position of the player (Right-most position of Bounding Box)
- y2: second y position of the player (Top-most position of Bounding Box)
- confidence: confidence level of the detected object being a player.

### Class Pycape
Where the methods are found that are ran for exporting images/JSON files.
Variables included in this class are hardcoded to have paths but can be modified via command line arguments:
- numFrames: the number of total frames to run through.
- framePath: the path to the YOLO/frames/
- detectionPath: the path to the YOLO/dets/
- estimatedPath: unused currently.
- currentFrame: The current frame being used.
- fileExt: the extension of the YOLO/frame images.
- playersPerFrame: modified, unused currently.

## Pycape Methods

### getPlayers()
This method is used when the command line argument *--mode crop* is passed.
The purpose of this method is to crop subimages of the original image based off of the YOLO detections.

### exportPlayerAnnotations

