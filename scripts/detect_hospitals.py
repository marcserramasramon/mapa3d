import cv2
import numpy as np

def detect_dots(image_path):
    print(f"Loading {image_path}...")
    img = cv2.imread(image_path)
    if img is None:
        print("Error: Could not load image.")
        return

    # Strategy 1: Simple Thresholding (dark dots on light bg)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    dots_thresh = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 5: # Lowered threshold
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                dots_thresh.append((cX, cY))
    
    print(f"Threshold found {len(dots_thresh)} dots.")
    
    # Strategy 2: Red Color Detection (if dots are red)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 70, 50])
    upper_red2 = np.array([180, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 + mask2
    
    contours_red, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    dots_red = []
    for cnt in contours_red:
        area = cv2.contourArea(cnt)
        if area > 5:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                dots_red.append((cX, cY))
            
    print(f"Red color found {len(dots_red)} dots.")
    
    # Decide which to use
    final_dots = []
    if len(dots_red) >= 7:
        print("Using red dots.")
        final_dots = dots_red
    elif len(dots_thresh) >= 7:
        print("Using threshold dots.")
        final_dots = dots_thresh
    else:
        print("Taking union of unique dots...")
        # dumb union
        final_dots = list(set(dots_thresh + dots_red))
        
    # Sort by X to have West->East conceptual mapping? 
    # Or just return raw and I map them.
    # Map logic: 
    # HAV (West): Lowest X?
    # HJT (East): Highest X?
    # BCN and Metro: Cluster?
    
    final_dots.sort(key=lambda p: p[0])

    print(f"Final Count: {len(final_dots)}")
    for i, (x, y) in enumerate(final_dots):
        print(f"Dot {i}: ({x}, {y})")

if __name__ == "__main__":
    detect_dots("map_dots.png")
