import cv2
import numpy as np
from ultralytics import YOLO
import sys


# --- USER SETTINGS ---
INPUT_VIDEO_PATH = '1.mp4'  # Make sure this file exists!
OUTPUT_VIDEO_PATH = 'output_multi_stick.mp4'

# Time Clipping (Seconds)
START_TIME = 865.0     # Start time (e.g., 5.0 for 5 seconds in)
END_TIME = 925.0      # End time (e.g., 15.0 or None for end of video)

# Visuals
TARGET_FPS = 30  # Lowered to 30 temporarily as processing is heavy
THICKNESS = 4    # Slightly thicker lines for colored visibility

# Keypoint connections (Standard COCO Skeleton)
SKELETON_CONNECTIONS = [
    (5, 7), (7, 9),       # Left Arm
    (6, 8), (8, 10),      # Right Arm
    (11, 13), (13, 15),   # Left Leg
    (12, 14), (14, 16),   # Right Leg
    (5, 6),               # Shoulders
    (11, 12),             # Hips
    (5, 11), (6, 12),     # Torso
    (0, 1), (0, 2),       # Eyes to Nose
    (1, 3), (2, 4)        # Ears
]

def create_stylized_background(image):
    """ 
    Creates a high-contrast, painterly version of the original frame.
    Uses Bilateral Filtering and CLAHE.
    """
    # 1. Bilateral Filter (Edge-preserving smoothing)
    # d=diameter of pixel neighborhood, sigmaColor/Space=filter strength
    painted = cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)

    # 2. Enhance Contrast using LAB color space
    # Convert BGR to LAB
    lab = cv2.cvtColor(painted, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)

    # Merge back and convert to BGR
    merged_lab = cv2.merge((cl, a, b))
    final_bg = cv2.cvtColor(merged_lab, cv2.COLOR_LAB2BGR)
    
    # Optional: Slight dark overlay to make brightly colored stick figures pop
    overlay = np.full(final_bg.shape, (30, 30, 30), dtype=np.uint8)
    final_bg = cv2.addWeighted(final_bg, 0.8, overlay, 0.2, 0)
    
    return final_bg

def get_character_color(original_frame, bbox):
    """
    Samples the center area of a character's bounding box to find their dominant color.
    """
    h, w, _ = original_frame.shape
    x1, y1, x2, y2 = map(int, bbox)

    # Ensure box is within frame boundaries
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, h)

    # Crop to the center 50% of the bounding box to avoid background noise
    cx1 = int(x1 + (x2-x1) * 0.25)
    cy1 = int(y1 + (y2-y1) * 0.25)
    cx2 = int(x2 - (x2-x1) * 0.25)
    cy2 = int(y2 - (y2-y1) * 0.25)

    crop = original_frame[cy1:cy2, cx1:cx2]

    # Fallback if crop is empty (e.g., character barely on screen)
    if crop.size == 0: return (200, 200, 200) 

    # Calculate mean BGR color of the crop
    avg_color = np.mean(crop, axis=(0, 1))
    
    # Boost saturation slightly to make stick figures pop
    color_uint8 = np.array([[avg_color]], dtype=np.uint8)
    hsv = cv2.cvtColor(color_uint8, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    s = cv2.add(s, 50) # Increase saturation
    v = cv2.add(v, 30) # Increase brightness
    final_hsv = cv2.merge((h, s, v))
    final_bgr = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)[0][0]

    return tuple(map(int, final_bgr))

def draw_skeleton(image, keypoints, color):
    h, w, _ = image.shape
    # Draw Lines
    for idx1, idx2 in SKELETON_CONNECTIONS:
        if idx1 >= len(keypoints) or idx2 >= len(keypoints): continue
        pt1, pt2 = keypoints[idx1], keypoints[idx2]
        # Lowered confidence threshold slightly for better connectivity
        if pt1[2] > 0.3 and pt2[2] > 0.3:
            pos1 = (int(pt1[0]), int(pt1[1]))
            pos2 = (int(pt2[0]), int(pt2[1]))
            cv2.line(image, pos1, pos2, color, THICKNESS, cv2.LINE_AA)

    # Draw Joints (slightly brighter than lines)
    joint_color = [min(c + 30, 255) for c in color]
    for pt in keypoints:
        if pt[2] > 0.3:
            pos = (int(pt[0]), int(pt[1]))
            cv2.circle(image, pos, THICKNESS+2, joint_color, -1, cv2.LINE_AA)

def main():
    print("Loading YOLOv8 Pose Model (this may take a moment)...")
    # Using 'yolov8m-pose.pt' (Medium) instead of 'n' (Nano) for better accuracy
    # It will download automatically if you don't have it.
    model = YOLO('yolov8m-pose.pt') 

    cap = cv2.VideoCapture(INPUT_VIDEO_PATH)
    if not cap.isOpened(): sys.exit("Error opening video.")

    orig_fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    start_frame = int(START_TIME * orig_fps)
    end_frame = int(END_TIME * orig_fps) if END_TIME else int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    # Mac use 'avc1', Windows use 'mp4v'
    fourcc = cv2.VideoWriter_fourcc(*'avc1') 
    # Outputting single width now, as side-by-side is too heavy with this processing
    out = cv2.VideoWriter(OUTPUT_VIDEO_PATH, fourcc, TARGET_FPS, (width, height))

    print("Processing... (This will be slower due to heavy image processing)")

    while cap.isOpened():
        curr_frame_idx = cap.get(cv2.CAP_PROP_POS_FRAMES)
        if curr_frame_idx >= end_frame: break
        success, frame = cap.read()
        if not success: break

        # 1. Generate High-Contrast Stylized BG
        stylized_bg = create_stylized_background(frame)
        stick_canvas = stylized_bg.copy()

        # 2. Run YOLO Tracking
        results = model.track(frame, persist=True, verbose=False, tracker="bytetrack.yaml")
        
        if results[0].boxes is not None and results[0].keypoints is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            all_keypoints = results[0].keypoints.data.cpu().numpy()
            
            # Loop through each detected person
            for i, person_kpts in enumerate(all_keypoints):
                # Get the bounding box for this person to sample color
                bbox = boxes[i]
                char_color = get_character_color(frame, bbox)
                
                # Draw their specific skeleton with their specific color
                draw_skeleton(stick_canvas, person_kpts, char_color)

        # 3. Preview & Save (Single view for performance)
        cv2.imshow('Ultimate Stickman', stick_canvas)
        out.write(stick_canvas)

        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("Done.")

if __name__ == "__main__":
    main()