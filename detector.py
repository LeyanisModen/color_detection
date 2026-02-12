import cv2
import numpy as np

def get_limits(color):
    # Adjusted values based on initial feedback
    
    # Yellow - Increase Saturation to avoid light wood
    if color == 'yellow':
        lowerLimit = np.array([20, 150, 150], dtype=np.uint8)
        upperLimit = np.array([30, 255, 255], dtype=np.uint8)
    
    # Blue - Narrowed to avoid overlap with purple
    elif color == 'blue':
        lowerLimit = np.array([100, 150, 50], dtype=np.uint8)
        upperLimit = np.array([130, 255, 255], dtype=np.uint8)
        
    # Green
    elif color == 'green':
        lowerLimit = np.array([40, 50, 50], dtype=np.uint8)
        upperLimit = np.array([80, 255, 255], dtype=np.uint8)
        
    # Orange - Drastically increased Saturation/Value to ignore cardboard/wood
    elif color == 'orange':
        lowerLimit = np.array([10, 180, 150], dtype=np.uint8)
        upperLimit = np.array([25, 255, 255], dtype=np.uint8)
        
    # Pink/Purple - Widened range downwards to catch the "blueish" purple card
    elif color == 'pink':
        lowerLimit = np.array([135, 100, 50], dtype=np.uint8)
        upperLimit = np.array([170, 255, 255], dtype=np.uint8)

    # Red
    elif color == 'red':
        lowerLimit = np.array([0, 150, 100], dtype=np.uint8)
        upperLimit = np.array([10, 255, 255], dtype=np.uint8)

    else:
        lowerLimit = np.array([0, 0, 0], dtype=np.uint8)
        upperLimit = np.array([0, 0, 0], dtype=np.uint8)
        
    return lowerLimit, upperLimit

def main():
    cap = cv2.VideoCapture(0)
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    colors_to_detect = ['red', 'green', 'blue', 'yellow', 'orange', 'pink']
    
    # Increased min_area to ignore smaller noise
    min_area = 1000 

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        blurred = cv2.GaussianBlur(hsv, (5, 5), 0)

        for color_name in colors_to_detect:
            lower, upper = get_limits(color_name)
            mask = cv2.inRange(blurred, lower, upper)
            
            if color_name == 'red':
                lower2 = np.array([170, 150, 100], dtype=np.uint8)
                upper2 = np.array([180, 255, 255], dtype=np.uint8)
                mask2 = cv2.inRange(blurred, lower2, upper2)
                mask = mask + mask2

            # More aggressive morphology
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.erode(mask, kernel, iterations=2) # Increased iterations to kill noise
            mask = cv2.dilate(mask, kernel, iterations=2)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                area = cv2.contourArea(cnt)
                
                if area > min_area:
                    x, y, w, h = cv2.boundingRect(cnt)
                    # Filter by aspect ratio to ensure it's somewhat rectangular/card-like
                    aspect_ratio = float(w)/h
                    # Cards are usually ~1.6 or ~0.6, allow some rotation
                    if 0.2 < aspect_ratio < 4.0: 
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(frame, color_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        cv2.imshow('Detector', frame)

        # Handle 'q' AND the window close button (X)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if cv2.getWindowProperty('Detector', cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
