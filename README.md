# Gesture-Controlled Particle System

A real-time interactive particle system controlled by hand gestures using **MediaPipe**, **OpenCV**, and **NumPy**.

The application tracks one or two hands through a webcam and allows the user to interact with thousands of particles using natural hand gestures. Particles can morph into predefined shapes, be grabbed, repelled, broken apart, moved, scaled, and rotated in real time.

---

## Demo

![Gesture-Controlled Particle System Demo](assets/demo/demo_small.gif)

## Features

* Real-time hand tracking with MediaPipe
* 4000 interactive particles rendered with NumPy
* Particle morphing into predefined images
* One-hand particle interaction
* Two-hand shape transformation
* Smooth gesture detection and motion
* Real-time FPS display
* Webcam-based interaction
* No custom AI model training required

---

## Gesture Controls

| Gesture                                  | Action                  |
| ---------------------------------------- | ----------------------- |
| ☝️ 1 finger                              | Create Heart shape      |
| ✌️ 2 fingers                             | Create Butterfly shape  |
| 3 fingers                                | Create Tree shape       |
| 4 fingers                                | Create Earth shape      |
| 🖐️ 5 fingers                            | Repel nearby particles  |
| 🤏 Thumb + Index                         | Grab and drag particles |
| 🫰 Finger snap                           | Break the current shape |
| 🤏 + 🤏 Two-hand pinch                   | Activate Transform Mode |
| Move both pinched hands                  | Move the entire shape   |
| Increase/decrease distance between hands | Scale the shape         |
| Rotate the line between both hands       | Rotate the shape        |

---

## Shape Presets

The project currently includes four particle shapes:

1. ❤️ Heart
2. 🦋 Butterfly
3. 🌳 Tree
4. 🌍 Earth

Shape images are stored inside:

```text
assets/shapes/
```

---

## Technologies

* Python
* OpenCV
* MediaPipe
* NumPy

Main package versions used during development:

```text
mediapipe==0.10.21
numpy==1.26.4
opencv-contrib-python==4.11.0.86
```

Python 3.11 is recommended.

---

## Project Structure

```text
Gesture-Controlled-Particle-System/
│
├── assets/
│   └── shapes/
│       ├── butterfly.png
│       ├── earth.png
│       ├── heart.png
│       └── tree.png
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── gesture_controller.py
│   ├── hand_tracker.py
│   ├── particle_system.py
│   └── shape_manager.py
│
├── tests/
│   └── particle_test.py
│
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

---

## Module Overview

### `main.py`

Main entry point of the application.

It handles:

* Webcam capture
* Main application loop
* Gesture processing
* Particle updates
* Shape transformation
* HUD rendering
* FPS display

### `src/config.py`

Contains configuration values such as:

* Window size
* Particle count
* Gesture thresholds
* Grab and repel radius
* Shape morph settings
* Transform smoothing
* Scale limits
* Rotation settings

### `src/hand_tracker.py`

Handles MediaPipe hand tracking.

Responsibilities include:

* Processing webcam frames
* Detecting up to two hands
* Returning hand landmarks
* Drawing hand landmarks

### `src/gesture_controller.py`

Interprets hand landmarks and converts them into gestures.

Supported interactions include:

* Finger counting
* Shape selection
* Pinch detection
* Grab
* Repel
* Finger snap detection
* Two-hand Transform Mode

### `src/particle_system.py`

Controls the particle simulation.

It handles:

* Particle positions
* Particle velocity
* Shape targets
* Color morphing
* Grab interaction
* Repel interaction
* Break effect
* Shape movement
* Shape scaling
* Shape rotation

Particle operations are mainly implemented using **NumPy vectorization** for better real-time performance.

### `src/shape_manager.py`

Loads shape images and converts valid image pixels into particle target positions and colors.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/HaiDuong1810/Gesture-Controlled-Particle-System.git
```

Move into the project directory:

```bash
cd Gesture-Controlled-Particle-System
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```cmd
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

---

## Run the Project

Make sure a webcam is connected and available.

Run:

```bash
python main.py
```

The application will open the webcam window and start detecting hand gestures.

Press:

```text
Q
```

to close the application.

---

## How It Works

The application uses **MediaPipe Hands** to detect hand landmarks from each webcam frame.

The detected landmarks are analyzed by the gesture controller to determine the current hand gesture.

For example:

```text
Hand landmarks
      ↓
Gesture detection
      ↓
GRAB / REPEL / SHAPE / BREAK / TRANSFORM
      ↓
Particle target or velocity update
      ↓
NumPy particle simulation
      ↓
OpenCV rendering
```

Particles are stored in NumPy arrays rather than thousands of individual Python objects.

This allows operations such as movement, attraction, repulsion, morphing, scaling, and rotation to be applied efficiently to thousands of particles at once.

---

## Two-Hand Transform Mode

When both hands perform a pinch gesture simultaneously, the application switches from normal `GRAB` interaction to `TRANSFORM` mode.

Three properties are calculated from the two pinch points.

### Move

The midpoint between both hands controls the position of the shape.

```text
🤏 -------- ❤️ -------- 🤏
             ↑
          midpoint
```

Moving both hands together moves the complete shape.

### Scale

The distance between both hands controls the size of the shape.

```text
🤏   ❤️   🤏
```

Moving the hands farther apart enlarges the shape.

Moving the hands closer together reduces its size.

### Rotate

The angle of the line connecting the two pinch points controls the rotation of the shape.

```text
🤏 -------- 🤏
```

can become:

```text
🤏
   \
    \
     🤏
```

and the particle shape rotates accordingly.

Smoothing and per-frame limits are used to reduce jitter caused by small variations in hand landmark detection.

---

## Performance

The system is designed for real-time interaction.

Current implementation includes:

* Approximately 4000 particles
* NumPy-based vectorized particle calculations
* Reduced-resolution frames for MediaPipe processing
* Lightweight particle rendering
* Motion smoothing for hand gestures
* Separate modules for particle physics and gesture processing

Actual FPS depends on the webcam, CPU, and system configuration.

---

## Requirements

Recommended environment:

* Python 3.11
* Webcam
* Windows, macOS, or Linux
* Adequate lighting for reliable hand detection

For better gesture recognition:

* Keep both hands visible to the webcam
* Avoid very dark environments
* Avoid placing hands too close to the edge of the frame
* Keep the hand clearly separated from the background when possible

---

## Possible Future Improvements

Possible extensions include:

* Custom shapes drawn by the user
* Particle trails
* Vortex effects
* Shockwave effects
* Additional gesture controls
* More particle presets
* Dynamic color effects
* Save screenshots or recordings
* Full-screen visualization mode
* Improved gesture stabilization
* GPU-based particle rendering

---

## Author

Developed by **HaiDuong1810**.

GitHub project:

`HaiDuong1810/Gesture-Controlled-Particle-System`

---

## Acknowledgements

This project uses:

* MediaPipe for real-time hand landmark detection
* OpenCV for webcam processing and visualization
* NumPy for efficient particle calculations
