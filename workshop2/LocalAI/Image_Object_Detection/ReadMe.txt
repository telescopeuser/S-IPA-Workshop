==========================================================
python code and local AI module for image object detection
==========================================================

https://github.com/telescopeuser/S-IPA-Workshop/blob/master/workshop2/LocalAI/Image_Object_Detection/object_detection_tutorial-IPA-2018-10-19.ipynb

https://github.com/tensorflow/models/tree/master/research/object_detection
https://github.com/tensorflow/models/blob/master/research/object_detection/object_detection_tutorial.ipynb

https://mybinder.org/
https://github.com/tensorflow/models.git



==========================================================
In case there is error is about:
==========================================================

ImportError Traceback (most recent call last)
in ()
----> 1 from utils import label_map_util
2
3 from utils import visualization_utils as vis_util
......\object_detection\utils\label_map_util.py in ()
20 import tensorflow as tf
21 from google.protobuf import text_format
---> 22 from object_detection.protos import string_int_label_map_pb2
23
24
ImportError: cannot import name 'string_int_label_map_pb2'


==========================================================
Solution:
==========================================================

1	Download protobuf-python-3.6.1.zip from:
	https://github.com/protocolbuffers/protobuf/releases
	
	
2	Unzip then use terminal to install protobuf; Refer to:
	https://pythonprogramming.net/introduction-use-tensorflow-object-detection-api-tutorial/
	
	sudo ./configure
	sudo make check
	sudo make install
	
	
3	Use terminal to setup protobuf; Refer to:
	https://stackoverflow.com/questions/25518701/protobuf-cannot-find-shared-libraries
	
	sudo ldconfig
	export LD_LIBRARY_PATH=/usr/local/lib
	

4	Use terminal to run below command from folder: tensorflow object detection "models/research"
	protoc object_detection/protos/*.proto --python_out=.
