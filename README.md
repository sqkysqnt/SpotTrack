# SpotTrack

SpotTrack is a real-time face detection project using FastAPI, OpenCV, and Coral Edge TPU. The video feed is displayed on a webpage with the ability to toggle the color of the bounding box around detected faces.

## Features

- Real-time face detection using Coral Edge TPU
- Web interface to display the video feed
- Toggle bounding box color between orange and green

## Requirements

- Python 3.7+
- Coral Edge TPU
- OpenCV
- FastAPI
- Uvicorn
- aiymakerkit

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/your-repo-name.git
    cd your-repo-name
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Run the application:
    ```sh
    python3 app.py
    ```

4. Open your browser and go to `http://localhost:8000` to view the video feed.

## Usage

- Click the "Toggle Color" button to change the color of the bounding box around detected faces.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

