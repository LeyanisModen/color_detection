import cv2
import numpy as np

def nothing(x):
    pass

def main():
    cap = cv2.VideoCapture(0)
    
    # Create a window
    cv2.namedWindow('image')

    # Create trackbars for color change
    # Hue is from 0-179 for Opencv
    cv2.createTrackbar('HMin', 'image', 0, 179, nothing)
    cv2.createTrackbar('SMin', 'image', 0, 255, nothing)
    cv2.createTrackbar('VMin', 'image', 0, 255, nothing)
    cv2.createTrackbar('HMax', 'image', 179, 179, nothing)
    cv2.createTrackbar('SMax', 'image', 255, 255, nothing)
    cv2.createTrackbar('VMax', 'image', 255, 255, nothing)

    # Set default value for Max HSV trackbars
    cv2.setTrackbarPos('HMax', 'image', 179)
    cv2.setTrackbarPos('SMax', 'image', 255)
    cv2.setTrackbarPos('VMax', 'image', 255)

    # Initialize to some reasonable starting values
    cv2.setTrackbarPos('HMin', 'image', 0)
    cv2.setTrackbarPos('SMin', 'image', 0)
    cv2.setTrackbarPos('VMin', 'image', 0)

    print("Use sliders to adjust HSV values.")
    print("Press 'q' to quit.")
    
    while(1):
        ret, frame = cap.read()
        if not ret:
            break

        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # get current positions of all trackbars
        hMin = cv2.getTrackbarPos('HMin', 'image')
        sMin = cv2.getTrackbarPos('SMin', 'image')
        vMin = cv2.getTrackbarPos('VMin', 'image')
        hMax = cv2.getTrackbarPos('HMax', 'image')
        sMax = cv2.getTrackbarPos('SMax', 'image')
        vMax = cv2.getTrackbarPos('VMax', 'image')

        # Set minimum and maximum HSV values to display
        lower = np.array([hMin, sMin, vMin])
        upper = np.array([hMax, sMax, vMax])

        # Create HSV Image and threshold into a range.
        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(frame, frame, mask=mask)

        # Print if there is a change in HSV value
        # (Optional: can just look at sliders)

        cv2.imshow('image', result)
        cv2.imshow('original', frame)
        
        if cv2.waitKey(10) & 0xFF == ord('q'):
            print(f"Final Values: Lower=[{hMin}, {sMin}, {vMin}], Upper=[{hMax}, {sMax}, {vMax}]")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
