#A Multi-Modal Framework To Teach Robots

Exploring ways to program a robot through demonstrations, gestures, and natural language. 
Programming robots can be time-consuming and expensive.
Often small changes in the behavior of the robot might require hiring a software engineer, reducing the applicability of robots in small businesses and private applications.
Thus, if we would be able to program robots by other means, the applicability of robots would be immensely strengthened.
A user study will be conducted to show if others can teach robots new tasks through the developed techniques.

## Description

Project 3-1 in commission of Maastricht University.

A pre-trained YOLOv5 model is used in combination with a ZED 2 camera for object tracking with 3D coordinates.

A pre-instructed large language model, running on the `gpt-3.5-turbo-1106` model by OpenAI, is used for conversation with the user.

The user records a video of them performing a task.
Afterwards, the user will be shown the robot's interpretation of this task, and how it plans to reproduce it.
The user can talk to an integrated chatbot to fine-tune this interpretation, or choose to re-record the task as many times as needed.

## Getting Started

### Dependencies

Some packages might need up-to-date [C++ compilers](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
If you have an NVIDIA graphics card, make sure to install the latest [CUDA drivers](https://developer.nvidia.com/cuda-downloads), as well as the appropriate CUDA-compatible [PyTorch](https://pytorch.org/get-started/locally/).

Run `pip install requirements.txt` to install all python dependencies.
Additionally, make sure you install the latest [ZED SDK](https://www.stereolabs.com/developers/release) and run the included python script.

### Setup

`detector.py` contains a selection of useful variables:
- `MAX_RECORDING_TIME`: the maximum recording time in seconds.
- `WEIGHTS`: path to a `.pt` file containing weights for a YOLOv5 model.
- `CPU`: set to false if you have a compatible GPU.
- `STATIC_CAMERA`: set to false if you want to move the camera around while recording.
- `SKIP_FRAMES`: set to false if you want to process every single frame.

Additionally, `ui.py` contains the variable `LIVE`, which denotes if a live camera feed should be used.
If a live camera feed is not available, Go to `detector.py` and put some paths to pre-recorded `.svo` files in the `TEST_VIDEOS` list.

If you want to make use of the integrated chatbot, you need to create a new file `secret.py` that contains two variables:
- `key`: an OpenAI API key.
- `org`: your OpenAI organization ID.

### Executing Program

To execute the program, run `main.py`.

## Authors

* Arantxa Buiter Sanchez
* Marco Cattaneo Vittone
* Antoine Dorard
* Gunes Ozmen Bakan
* Diogo Reis Rio
* Thomas Vroom

## License

See `LICENSE`.
