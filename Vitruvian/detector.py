import base64
from datetime import timedelta
import enum
import torch
import numpy as np
import cv2
from flask import Flask, render_template, Response,request
# import PushupModel as pm
import logging
import sys
import time
from ml import Classifier
from ml import Movenet
from ml import MoveNetMultiPose
from ml import Posenet
import math
from typing import List, Tuple ,NamedTuple
import numpy as np
from PIL import Image

app = Flask(__name__,template_folder='./templates')

# 解决缓存刷新问题
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)


# 添加header解决跨域
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
    return response

class BodyPart(enum.Enum):
  """Enum representing human body keypoints detected by pose estimation models."""
  NOSE = 0
  LEFT_EYE = 1
  RIGHT_EYE = 2
  LEFT_EAR = 3
  RIGHT_EAR = 4
  LEFT_SHOULDER = 5
  RIGHT_SHOULDER = 6
  LEFT_ELBOW = 7
  RIGHT_ELBOW = 8
  LEFT_WRIST = 9
  RIGHT_WRIST = 10
  LEFT_HIP = 11
  RIGHT_HIP = 12
  LEFT_KNEE = 13
  RIGHT_KNEE = 14
  LEFT_ANKLE = 15
  RIGHT_ANKLE = 16

class Point(NamedTuple):
  """A point in 2D space."""
  x: float
  y: float

class Rectangle(NamedTuple):
  """A rectangle in 2D space."""
  start_point: Point
  end_point: Point

class KeyPoint(NamedTuple):
  """A detected human keypoint."""
  body_part: BodyPart
  coordinate: Point
  score: float

class Person(NamedTuple):
  """A pose detected by a pose estimation model."""
  keypoints: List[KeyPoint]
  bounding_box: Rectangle
  score: float
  id: int = None

# map edges to a RGB color
KEYPOINT_EDGE_INDS_TO_COLOR = {
    (0, 1): (147, 20, 255),
    (0, 2): (255, 255, 0),
    (1, 3): (147, 20, 255),
    (2, 4): (255, 255, 0),
    (0, 5): (147, 20, 255),
    (0, 6): (255, 255, 0),
    (5, 7): (147, 20, 255),
    (7, 9): (147, 20, 255),
    (6, 8): (255, 255, 0),
    (8, 10): (255, 255, 0),
    (5, 6): (0, 255, 255),
    (5, 11): (147, 20, 255),
    (6, 12): (255, 255, 0),
    (11, 12): (0, 255, 255),
    (11, 13): (147, 20, 255),
    (13, 15): (147, 20, 255),
    (12, 14): (255, 255, 0),
    (14, 16): (255, 255, 0)
}

# A list of distictive colors
COLOR_LIST = [
    (47, 79, 79),
    (139, 69, 19),
    (0, 128, 0),
    (0, 0, 139),
    (255, 0, 0),
    (255, 215, 0),
    (0, 255, 0),
    (0, 255, 255),
    (255, 0, 255),
    (30, 144, 255),
    (255, 228, 181),
    (255, 105, 180),
]

def visualize(
    image: np.ndarray,
    list_persons: List[Person],
    keypoint_color: Tuple[int, ...] = None,
    keypoint_threshold: float = 0.05,
    instance_threshold: float = 0.1,
) -> np.ndarray:
  """Draws landmarks and edges on the input image and return it.

  Args:
    image: The input RGB image.
    list_persons: The list of all "Person" entities to be visualize.
    keypoint_color: the colors in which the landmarks should be plotted.
    keypoint_threshold: minimum confidence score for a keypoint to be drawn.
    instance_threshold: minimum confidence score for a person to be drawn.

  Returns:
    Image with keypoints and edges.
  """
  for person in list_persons:
    if person.score < instance_threshold:
      continue

    keypoints = person.keypoints
    bounding_box = person.bounding_box

    # Assign a color to visualize keypoints.
    if keypoint_color is None:
      if person.id is None:
        # If there's no person id, which means no tracker is enabled, use
        # a default color.
        person_color = (0, 255, 0)
      else:
        # If there's a person id, use different color for each person.
        person_color = COLOR_LIST[person.id % len(COLOR_LIST)]
    else:
      person_color = keypoint_color

    # Draw all the landmarks
    for i in range(len(keypoints)):
      if keypoints[i].score >= keypoint_threshold:
        cv2.circle(image, keypoints[i].coordinate, 2, person_color, 4)

    # Draw all the edges
    for edge_pair, edge_color in KEYPOINT_EDGE_INDS_TO_COLOR.items():
      if (keypoints[edge_pair[0]].score > keypoint_threshold and
          keypoints[edge_pair[1]].score > keypoint_threshold):
        cv2.line(image, keypoints[edge_pair[0]].coordinate,
                keypoints[edge_pair[1]].coordinate, edge_color, 2)

    # Draw bounding_box with multipose
    if bounding_box is not None:
      start_point = bounding_box.start_point
      end_point = bounding_box.end_point
      cv2.rectangle(image, start_point, end_point, person_color, 2)
      # Draw id text when tracker is enabled for MoveNet MultiPose model.
      # (id = None when using single pose model or when tracker is None)
      if person.id:
        id_text = 'id = ' + str(person.id)
        cv2.putText(image, id_text, start_point, cv2.FONT_HERSHEY_PLAIN, 1,
                    (0, 0, 255), 1)

  return image

def keep_aspect_ratio_resizer(
    image: np.ndarray, target_size: int) -> Tuple[np.ndarray, Tuple[int, int]]:
  """Resizes the image.

  The function resizes the image such that its longer side matches the required
  target_size while keeping the image aspect ratio. Note that the resizes image
  is padded such that both height and width are a multiple of 32, which is
  required by the model. See
  https://tfhub.dev/google/tfjs-model/movenet/multipose/lightning/1 for more
  detail.

  Args:
    image: The input RGB image as a numpy array of shape [height, width, 3].
    target_size: Desired size that the image should be resize to.

  Returns:
    image: The resized image.
    (target_height, target_width): The actual image size after resize.

  """
  height, width, _ = image.shape
  if height > width:
    scale = float(target_size / height)
    target_height = target_size
    scaled_width = math.ceil(width * scale)
    image = cv2.resize(image, (scaled_width, target_height))
    target_width = int(math.ceil(scaled_width / 32) * 32)
  else:
    scale = float(target_size / width)
    target_width = target_size
    scaled_height = math.ceil(height * scale)
    image = cv2.resize(image, (target_width, scaled_height))
    target_height = int(math.ceil(scaled_height / 32) * 32)

  padding_top, padding_left = 0, 0
  padding_bottom = target_height - image.shape[0]
  padding_right = target_width - image.shape[1]
  # add padding to image
  image = cv2.copyMakeBorder(image, padding_top, padding_bottom, padding_left,
                            padding_right, cv2.BORDER_CONSTANT)
  return image, (target_height, target_width)

# model = Model()  # Then in here instantiate your model
# model.load_state_dict(torch.load(ospath.join(os.getcwd()+'/weights/last.pt')))  # Then load your model's weights.

# hunchback

def gen_frames_hunchback2(img):
  # cap = cv2.VideoCapture(0)
  estimation_model='movenet_thunder'
  tracker_type='bounding_box'
  classification_model='pose_classifier'
  label_file='pose_labels.txt'
  # camera_id=0
  # width=800
  # height=1600
  # Notify users that tracker is only enabled for MoveNet MultiPose model.
  if tracker_type and (estimation_model != 'movenet_multipose'):
    logging.warning(
        'No tracker will be used as tracker can only be enabled for '
        'MoveNet MultiPose model.')

  # Initialize the pose estimator selected.
  if estimation_model in ['movenet_lightning', 'movenet_thunder']:
    pose_detector = Movenet(estimation_model)
  elif estimation_model == 'posenet':
    pose_detector = Posenet(estimation_model)
  elif estimation_model == 'movenet_multipose':
    pose_detector = MoveNetMultiPose(estimation_model, tracker_type)
  else:
    sys.exit('ERROR: Model is not supported.')

  # Variables to calculate FPS
  counter, fps = 0, 0
  start_time = time.time()

  # Start capturing video input from the camera
  # cap = cv2.VideoCapture(camera_id)
  # cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
  # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

  # Visualization parameters
  row_size = 30  # pixels
  left_margin = 24  # pixels
  text_color = (0, 0, 255)  # red
  font_size = 2
  font_thickness = 2
  classification_results_to_show = 3
  fps_avg_frame_count = 10
  keypoint_detection_threshold_for_classifier = 0.1
  classifier = None

  # Initialize the classification model
  if classification_model:
    classifier = Classifier(classification_model, label_file)
    classification_results_to_show = min(classification_results_to_show,
                                          len(classifier.pose_class_names))
  # Continuously capture images from the camera and run inference
  img = img.split(',');
  img = img[1];
  img_data = base64.b64decode (img)
  parr = np.frombuffer (img_data, np.uint8)
  img_np = cv2. imdecode (parr, cv2. IMREAD_COLOR)
  img = cv2.resize(img_np, (800, 480))
 

  counter += 1
  img = cv2.flip(img, 1)

  if estimation_model == 'movenet_multipose':
    # Run pose estimation using a MultiPose model.
    list_persons = pose_detector.detect(img)
  else:
    # Run pose estimation using a SinglePose model, and wrap the result in an
    # array.
    list_persons = [pose_detector.detect(img)]

  # Draw keypoints and edges on input image
  img = visualize(img, list_persons)

  if classifier:
    # Check if all keypoints are detected before running the classifier.
    # If there's a keypoint below the threshold, show an error.
    person = list_persons[0]
    min_score = min([keypoint.score for keypoint in person.keypoints])
    if min_score < keypoint_detection_threshold_for_classifier:
      error_text = 'Some keypoints are not detected.'
      text_location = (left_margin, 2 * row_size)
      cv2.putText(img, error_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                  font_size, text_color, font_thickness)
      error_text = 'Make sure the person is fully visible in the camera.'
      text_location = (left_margin, 3 * row_size)
      cv2.putText(img, error_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                  font_size, text_color, font_thickness)
    else:
        # Run pose classification
      prob_list = classifier.classify_pose(person)

        # Show classification results on the image
      for i in range(classification_results_to_show):
        class_name = prob_list[i].label
        probability = round(prob_list[i].score, 2)
        result_text = class_name + ' (' + str(probability) + ')'
        text_location = (left_margin, (i + 2) * row_size)
        cv2.putText(img, result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                    font_size, text_color, font_thickness)

  # Calculate the FPS
  if counter % fps_avg_frame_count == 0:
    end_time = time.time()
    fps = fps_avg_frame_count / (end_time - start_time)
    start_time = time.time()

  # Show the FPS
  fps_text = 'FPS = ' + str(int(fps))
  text_location = (left_margin, row_size)
  cv2.putText(img, fps_text, text_location, cv2.FONT_HERSHEY_PLAIN,
              font_size, text_color, font_thickness)
    
  # cv2.imshow(estimation_model, image)
  # ret, image = cap.read() #640 x 480
  ret, buffer = cv2.imencode('.jpg', img)
  frame = buffer.tobytes()
  yield (b'data:image/jpeg;base64,' + base64.b64encode(frame))
  
  cv2.destroyAllWindows()

model = torch.hub.load('ultralytics/yolov5', 'custom',
                       path='yolov5/runs/train/exp9/weights/best.pt', force_reload=True)


def gen_frames_mask2(img):
    img = img.split(',');
    img = img[1];
    img_data = base64.b64decode (img)
    parr = np.frombuffer (img_data, np.uint8)
    img_np = cv2. imdecode (parr, cv2. IMREAD_COLOR)
    img = cv2.resize(img_np, (800, 480))
    result = model(img)
    result = np.squeeze(result.render())            
    try:
        ret, buffer = cv2.imencode('.jpg', result)
        frame = buffer.tobytes()
        yield (b'data:image/jpeg;base64,' + base64.b64encode(frame))
    except Exception as e:
        pass
    cv2.destroyAllWindows()

# yoga----------------------------------------------------------------------------------
model_yoga = torch.hub.load('ultralytics/yolov5', 'custom',
                       path='yolov5/runs/train/exp5/weights/best.pt', force_reload=True)

def gen_frames_yoga2(img):
    img = img.split(',');
    img = img[1];
    img_data = base64.b64decode (img)
    parr = np.frombuffer (img_data, np.uint8)
    img_np = cv2. imdecode (parr, cv2. IMREAD_COLOR)
    img = cv2.resize(img_np, (800, 480))
    result = model_yoga(img)
    result = np.squeeze(result.render())            
    try:
        ret, buffer = cv2.imencode('.jpg', result)
        frame = buffer.tobytes()
        yield (b'data:image/jpeg;base64,' + base64.b64encode(frame))
    except Exception as e:
        pass
    cv2.destroyAllWindows()
# pushup--------------------------------------------------------------------------------
# def gen_frames_pushup2(img):
    detector = pm.poseDetector()
    count = 0
    direction = 0
    form = 0
    feedback = "Fix Form"
    
    img = img.split(',');
    img = img[1];
    img_data = base64.b64decode (img)
    parr = np.frombuffer (img_data, np.uint8)
    img_np = cv2. imdecode (parr, cv2. IMREAD_COLOR)
    img = cv2.resize(img_np, (800, 480))


    img = detector.findPose(img, False)
    lmList = detector.findPosition(img, False)
    # print(lmList)
    if len(lmList) != 0:
        elbow = detector.findAngle(img, 11, 13, 15)
        shoulder = detector.findAngle(img, 13, 11, 23)
        hip = detector.findAngle(img, 11, 23,25)
            
        #Percentage of success of pushup
        per = np.interp(elbow, (90, 160), (0, 100))
            
        #Bar to show Pushup progress
        bar = np.interp(elbow, (90, 160), (380, 50))

        #Check to ensure right form before starting the program
        if elbow > 160 and shoulder > 60 and hip > 160:
            form = 1
        
        #Check for full range of motion for the pushup
        if form == 1:
            if per == 0:
                if elbow <= 90 and hip > 160:
                    feedback = "Up, B!"
                    if elbow <=80 and hip >168:
                        feedback="Up, A!"
                    if direction == 0:
                        count += 0.5
                        direction = 1
                else:
                    feedback = "Fix Form, Grade C!"
                        
            if per == 100:
                if elbow > 160 and shoulder > 40 and hip > 160:
                    feedback = "Down"
                    if direction == 1:
                        count += 0.5
                        direction = 0
                else:
                    feedback = "Fix Form"
                         # form = 0
            # print(count)
            
            #Draw Bar
        if form == 1:
            cv2.rectangle(img, (580, 50), (600, 380), (0, 255, 0), 3)
            cv2.rectangle(img, (580, int(bar)), (600, 380), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, f'{int(per)}%', (565, 430), cv2.FONT_HERSHEY_PLAIN, 2,
                        (255, 0, 0), 2)


            #Pushup counter
        cv2.rectangle(img, (0, 380), (100, 480), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, str(int(count)), (25, 455), cv2.FONT_HERSHEY_PLAIN, 5,
                    (255, 0, 0), 5)
            
        #Feedback 
        cv2.rectangle(img, (500, 0), (640, 40), (255, 255, 255), cv2.FILLED)
        cv2.putText(img, feedback, (500, 40), cv2.FONT_HERSHEY_PLAIN, 2,
                    (0, 255, 0), 2)

            
    ret, buffer = cv2.imencode('.jpg', img)
    frame = buffer.tobytes()
    yield (b'data:image/jpeg;base64,' + base64.b64encode(frame))

    cv2.destroyAllWindows()


@app.route('/video_mask',methods=['POST','GET'])
def video_mask():
    #Video streaming route. Put this in the src attribute of an img tag
    img=request.values['img']
    return Response(gen_frames_mask2(img), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_yoga',methods=['POST','GET'])
def video_yoga():
    img=request.values['img']
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames_yoga2(img), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/video_pushup',methods=['POST','GET'])
# def video_pushup():
#     img=request.values['img']
#     #Video streaming route. Put this in the src attribute of an img tag
#     return Response(gen_frames_pushup2(img), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/viedo_hunchback',methods=['POST','GET'])
def video_hunchback():
    img=request.values['img']
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames_hunchback2(img), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/mask',methods=['POST','GET'])
def mask():
    """Video streaming home page."""
    return render_template('mask.html')
#----------------------------------------------------------------------------

@app.route('/yoga',methods=['POST','GET'])
def yoga():
    """Video streaming home page."""
    return render_template('yoga.html')

#----------------------------------------------------------------------------
@app.route('/pushup',methods=['POST','GET'])
def pushup():
    """Video streaming home page."""
    return render_template('pushup.html')


   
@app.route('/hunchback',methods=['POST','GET'])
def hunchback():
    """Video streaming home page."""
    return render_template('hunchback.html')
  
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5005, debug=True)
