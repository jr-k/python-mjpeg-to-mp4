import time
import cv2
import datetime
import urllib.request
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from multiprocessing import Manager, Process

# Configuration
STREAM_URL = 'http://your_mjpeg_stream.com'
SNAPSHOT_EVERY_X_SECONDS = 5
SNAPSHOT_OUTPUT = "snapshot.jpg"
SEGMENT_EVERY_X_SECONDS = 10
SEGMENT_OUTPUT = "cam1_{timestamp}.mp4"

# Init
stream = urllib.request.urlopen(STREAM_URL)
bytes = bytes()
img_array = []
fontpath = "./FreeSans.ttf"
font = ImageFont.truetype(fontpath, 16)
last_ts_snapshot = 0
last_ts_segment = 0
i = 0

def processFrames(vidname, frames):
	out = cv2.VideoWriter(vidname, cv2.VideoWriter_fourcc(*'H264'), 10, (800,600))
	for i in range(len(frames)):
		out.write(frames[i])
	out.release()

# Run
while True:
	bytes += stream.read(1024)
	a = bytes.find(b'\xff\xd8')
	b = bytes.find(b'\xff\xd9')
	if a != -1 and b != -1:
		i += 1
		# print("frame " + str(i))
		jpg = bytes[a:b+2]
		bytes = bytes[b+2:]
		image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
		# image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
		cv2.rectangle(image, (0, 0), (170, 20), (255, 255, 255), -1)
		img_pil = Image.fromarray(image)
		draw = ImageDraw.Draw(img_pil)
		ts = time.time()
		st = datetime.datetime.fromtimestamp(ts).strftime('%d.%m.%Y %H:%M:%S')
		draw.text((10, 0), st, font=font, fill=(0, 0, 0, 1))
		image = np.array(img_pil)
		img_array.append(image)

		if ts - last_ts_snapshot >= SNAPSHOT_EVERY_X_SECONDS:
			print("Prepare snapshot")
			cv2.imwrite(SNAPSHOT_OUTPUT, image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
			last_ts_snapshot = ts

		if ts - last_ts_segment >= SEGMENT_EVERY_X_SECONDS:
			tsmark = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')
			vidname = SEGMENT_OUTPUT.replace('{timestamp}', tsmark)
			print("Prepare video " + vidname)
			p = Process(target=processFrames, args=(vidname, img_array))
                        p.start()
			img_array = []
			last_ts_segment = ts

		# cv2.imshow('i', image)
		# if cv2.waitKey(1) == 27:
		# 	break



