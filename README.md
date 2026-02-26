# Color Detection & Decoding System

## Overview
This project implements a computer vision system using **OpenCV** to detect specific colored cards in a video feed and interpret their arrangement as a unique code.

The system is designed to work in industrial/construction environments (e.g., concrete backgrounds) and detects cards at a distance of ~3 meters.

## Features
- **Multi-Color Detection**: Identifies Pink, Green, Blue, Yellow, Orange, and Purple cards.
- **Robustness**: Filters out background noise (wood/concrete) using HSV thresholding and morphological operations.
- **Geometric Decoding**: Interprets a 4-card pattern based on their relative positions:
    1.  **Top**
    2.  **Left**
    3.  **Bottom**
    4.  **Right**
- **Visual Feedback**: Draws bounding boxes, labels, and the decoding sequence directly on the video feed.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd color_detection
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### 1. Calibration (Optional)
If lighting conditions change, use the calibration tool to find the best HSV values for your cards.
```bash
python calibration.py
```
-   Use the sliders to isolate the card color from the background.
-   Update the `get_limits()` function in `detector.py` with the new values.

### 2. Running the Detector
Start the main detection system:
```bash
python detector.py
```
-   **'q'**: Quit the application.

## Color Code Logic
The system looks for exactly **4 cards**. It sorts them geometrically to form a sequence:
`[Top Card] - [Left Card] - [Bottom Card] - [Right Card]`

Example:
If you have:
-   Yellow at the top
-   Green on the left
-   Blue at the bottom
-   Orange on the right

The output code will be: **YELLOW - GREEN - BLUE - ORANGE**

### Combinatorics & Capacity
With **6 available colors** and **4 positions**, assuming **no repeated colors** on a single module, the system supports:
$$ P(6, 4) = 6 \times 5 \times 4 \times 3 = 360 \text{ unique codes} $$

**Note on Adjacency**:
In the physical assembly, adjacent modules must share the same color on their joining sides (e.g., the "Right" color of Module A must match the "Left" color of Module B). While this constrains the *global* arrangement, the system can simply identify up to 360 unique module types based on their local color pattern.
