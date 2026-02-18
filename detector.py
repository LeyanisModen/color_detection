import cv2
import numpy as np
import math

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

def get_card_position(detections):
    """
    Sorts 4 detected cards into Top, Left, Bottom, Right positions.
    detections: list of (x, y, w, h, color_name, center_x, center_y)
    Returns: list [TopColor, LeftColor, BottomColor, RightColor]
    """
    if len(detections) != 4:
        return None

    # Sort by Y coordinate (Center Y)
    # The one with min Y is TOP
    # The one with max Y is BOTTOM
    sorted_by_y = sorted(detections, key=lambda k: k[6])
    top_card = sorted_by_y[0]
    bottom_card = sorted_by_y[-1]
    
    # The remaining two are Left and Right
    remaining = [d for d in detections if d != top_card and d != bottom_card]
    
    # Sort remaining by X coordinate (Center X)
    sorted_by_x = sorted(remaining, key=lambda k: k[5])
    left_card = sorted_by_x[0]
    right_card = sorted_by_x[-1]

    return [top_card, left_card, bottom_card, right_card]

def main():
    cap = cv2.VideoCapture(0)
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)

    colors_to_detect = ['red', 'green', 'blue', 'yellow', 'orange', 'pink']
    
    min_area = 1000 

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        blurred = cv2.GaussianBlur(hsv, (5, 5), 0)
        
        detections = [] # Store all detections in this frame

        for color_name in colors_to_detect:
            lower, upper = get_limits(color_name)
            mask = cv2.inRange(blurred, lower, upper)
            
            if color_name == 'red':
                lower2 = np.array([170, 150, 100], dtype=np.uint8)
                upper2 = np.array([180, 255, 255], dtype=np.uint8)
                mask2 = cv2.inRange(blurred, lower2, upper2)
                mask = mask + mask2

            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.erode(mask, kernel, iterations=2) 
            mask = cv2.dilate(mask, kernel, iterations=2)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                area = cv2.contourArea(cnt)
                
                if area > min_area:
                    x, y, w, h = cv2.boundingRect(cnt)
                    aspect_ratio = float(w)/h
                    
                    if 0.2 < aspect_ratio < 4.0: 
                        # Calculate center
                        cx = x + w // 2
                        cy = y + h // 2
                        
                        detections.append((x, y, w, h, color_name, cx, cy))
                        
                        # Draw bounding box (visual feedback)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(frame, color_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Logic to decode the pattern
        # We need exactly 4 cards to form a code
        if len(detections) >= 4:
            # If more than 4, take the 4 largest? or 4 closest? 
            # For now, let's take the 4 largest areas (simplest assumption)
            # Area is w*h
            detections.sort(key=lambda k: k[2]*k[3], reverse=True)
            top_4 = detections[:4]
            
            ordered = get_card_position(top_4)
            if ordered:
                # [Top, Left, Bottom, Right]
                code_text = f"CODE: {ordered[0][4].upper()} - {ordered[1][4].upper()} - {ordered[2][4].upper()} - {ordered[3][4].upper()}"
                
                # Draw the code on screen
                cv2.putText(frame, code_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                
                # Draw lines connecting them to visualize the diamond
                pts = np.array([[ordered[0][5], ordered[0][6]], 
                                [ordered[3][5], ordered[3][6]],
                                [ordered[2][5], ordered[2][6]],
                                [ordered[1][5], ordered[1][6]]], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], True, (255, 255, 0), 2)

        # Resize for display (so it fits on a non-4K monitor)
        display_frame = cv2.resize(frame, (1280, 720))
        cv2.imshow('Detector', display_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if cv2.getWindowProperty('Detector', cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
