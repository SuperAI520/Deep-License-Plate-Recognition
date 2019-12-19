# Automatic License Plate Recognition API

Accurate, fast and easy to use API for license plate recognition. Trained on data from over 100 countries and regions around the world. The core of our license plate detection system is based on state of the art deep neural networks architectures.

Integrate with our ALPR API in a few lines of code. Get an easy to use JSON response with the number plate value of vehicles and the bounding boxes.

<p align="center">
  <img src="assets/demo.jpg">
</p>

  - [Reading License Plates from Images](#reading-license-plates-from-images)
    - [Lookups For a Specific Region](#lookups-for-a-specific-region)
    - [Process Multiple Files (Batch Mode)](#process-multiple-files-batch-mode)
    - [Running the ALPR Locally (SDK)](#running-the-alpr-locally-sdk)
  - [Automatic Image Transfer](#automatic-image-transfer)
  - [Code Samples](#code-samples)
  - [Number Plate Recognition on a Video](#number-plate-recognition-on-a-video)


## Reading License Plates from Images

Get your API key from [Plate Recognizer](https://platerecognizer.com/). Replace **MY_API_KEY** with your API key and run the following command:

```
pip install requests
python plate_recognition.py --api-key MY_API_KEY /path/to/vehicle.jpg
```

The **result** includes the bounding `box`es (rectangle around object) and the `plate` value for each plate. The JSON output can easily be consumed by your application.

```javascript
[
  {
    "version": 1,
    "results": [
      {
        "box": {
          "xmin": 85,
          "ymin": 85,
          "ymax": 211,
          "xmax": 331
        },
        "plate": "ABC123",
        "score": 0.904,
        "dscore": 0.92
      }
    ],
    "filename": "car.jpg"
  }
]
```


### Lookups For a Specific Region

You can match the license plate patterns of a specific region.

`python plate_recognition.py --api-key MY_API_KEY --regions fr --regions it /path/to/car.jpg`



### Process Multiple Files (Batch Mode)

You can also run the license plate reader on many files at once. To run the script on all the images of a directory, use:

`python plate_recognition.py --api-key MY_API_KEY /path/to/car1.jpg /path/to/car2.jpg /path/to/trucks*.jpg`

<br><br><br>

### [Running the ALPR Locally (SDK)](docker/)

To use a locally hosted sdk, pass the url to the docker container as follows:

`python plate_recognition.py  --sdk-url http://localhost:8080 /path/to/vehicle.jpg`

<br><br><br>

## Automatic Image Transfer

Monitor a folder and automatically process images (Cloud or SDK) as they are added. It can also forward the results to our parking management service [Parkpow](https://parkpow.com/).

To get started: `python transfer.py --help`

<br><br><br>

## Code Samples

See sample projects to use the API in [C++](cpp/), [C#](csharp/) or [Java](java/). View how to integrate with other languages in our [documentation](http://docs.platerecognizer.com/#introduction).

<br><br><br>

## Number Plate Recognition on a Video

To do ANPR on videos, you will also need to **install OpenCV**. Here are the [installation](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_setup/py_setup_in_windows/py_setup_in_windows.html) instructions. Those 2 python packages are also needed:

```
pip install requests
pip install pillow
```

The script `alpr_video.py` lets you perform license plate recognition on a video file. It looks at each frame of the video and reads license plates. If you are only interested in one part of the video, you may use the `--start` and `--end` arguments. Additionally, you can use the `--skip` argument to read 1 in every N frames. It will speed up the analysis of large videos. Here's an example:

`python alpr_video.py --api MY_API_KEY --start 900 --end 2000 --skip 3 /path/to/cars.mp4`

OpenCV is also capable of reading **live video streams**. See this [page](https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_gui/py_video_display/py_video_display.html) for an example.

<br><br><br>

## Number Plate Recognition from a Live Camera stream
Follow the instructions above to **install OpenCv** including the installation of dependancies `requests` and `pillow`. Then run the script as shown below.

`python anpr_camera_stream.py --camera RTSP_STREAM_URL --api-key MY_TOKEN --regions fr --output /path/to/save.csv`
Run:
`python anpr_campera_stream.py --help` for usage.

For testing purposes when you dont have a camera, you can install [CamOn Live Streaming app](https://play.google.com/store/apps/details?id=com.miv.rtspcamera) from the google play store and use its RTSP url to stream your mobile phone's camera.


---
Have questions?  [Let us know](https://platerecognizer.com/contact) how we can help.

Provided by Plate Recognizer, a subsidiary of [ParkPow](https://parkpow.com/).
