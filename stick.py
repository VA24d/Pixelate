import cv2
import numpy as np
from ultralytics import YOLO
import sys


# --- USER SETTINGS ---
INPUT_VIDEO_PATH = '1.mp4'  # Make sure this file exists!
OUTPUT_VIDEO_PATH = 'output_final.mp4'

# Time Clipping (Seconds)
START_TIME = 865.0     # Start time (e.g., 5.0 for 5 seconds in)
END_TIME = 925.0      # End time (e.g., 15.0 or None for end of video)

# Visuals
TARGET_FPS = 60           # 60fps for smooth stick movement
SMOOTHING = 0.6           # 0.1 (smooth/laggy) -> 0.9 (fast/jittery)
STICK_COLOR = (255, 255, 255) # White
THICKNESS = 3

# Pastel Background Settings
PASTEL_BLUR = (75, 75)    # Smoothing strength (Must be odd numbers)
PASTEL_SAT_CAP = 90       # Lower = paler colors
PASTEL_VAL_FLOOR = 160    # Higher = brighter background

class PoseSmoother:
    """ smooths jittery AI detection using Exponential Moving Average """
    def __init__(self, alpha=0.5):
        self.alpha = alpha
        self.prev_landmarks = None

    def update(self, current_landmarks):
        if not current_landmarks:
            return self.prev_landmarks # Return last known good pose if detection fails
        
        if self.prev_landmarks is None:
            self.prev_landmarks = current_landmarks
            return current_landmarks

        smoothed = []
        for i, lm in enumerate(current_landmarks):
            prev = self.prev_landmarks[i]
            # EMA Filter: New = Alpha * Current + (1-Alpha) * Previous
            new_x = self.alpha * lm.x + (1 - self.alpha) * prev.x
            new_y = self.alpha * lm.y + (1 - self.alpha) * prev.y
            new_z = self.alpha * lm.z + (1 - self.alpha) * prev.z
            new_vis = self.alpha * lm.visibility + (1 - self.alpha) * prev.visibility
            
            smoothed.append(type(lm)(x=new_x, y=new_y, z=new_z, visibility=new_vis))

        self.prev_landmarks = smoothed
        return smoothed

def create_pastel_bg(image):
    """ Converts anime frame to abstract pastel background """
    # Heavy blur to remove details
    blurred = cv2.GaussianBlur(image, PASTEL_BLUR, 0)
    # Convert to HSV to clamp saturation and value
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    s[s > PASTEL_SAT_CAP] = PASTEL_SAT_CAP       # Cap saturation
    v[v < PASTEL_VAL_FLOOR] = PASTEL_VAL_FLOOR   # Floor brightness
    final_hsv = cv2.merge([h, s, v])
    return cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

def draw_stick_figure(image, landmarks):
    if not landmarks: return
    h, w, _ = image.shape
    connections = mp.solutions.pose.POSE_CONNECTIONS
    
    # Draw Bones
    for start_idx, end_idx in connections:
        start = landmarks[start_idx]
        end = landmarks[end_idx]
        if start.visibility > 0.3 and end.visibility > 0.3:
            pt1 = (int(start.x * w), int(start.y * h))
            pt2 = (int(end.x * w), int(end.y * h))
            cv2.line(image, pt1, pt2, STICK_COLOR, THICKNESS, cv2.LINE_AA)

    # Draw Joints
    for lm in landmarks:
        if lm.visibility > 0.3:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(image, (cx, cy), 4, STICK_COLOR, -1, cv2.LINE_AA)

def interpolate_landmarks(start_lms, end_lms, fraction):
    """ Generates a 'fake' pose between two real poses """
    if not start_lms or not end_lms: return start_lms or end_lms
    interp_lms = []
    for i in range(len(start_lms)):
        s, e = start_lms[i], end_lms[i]
        ix = s.x + (e.x - s.x) * fraction
        iy = s.y + (e.y - s.y) * fraction
        iz = s.z + (e.z - s.z) * fraction
        iv = s.visibility + (e.visibility - s.visibility) * fraction
        interp_lms.append(type(s)(x=ix, y=iy, z=iz, visibility=iv))
    return interp_lms

def main():
    print("--- Initializing MediaPipe ---")
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=2)
    smoother = PoseSmoother(alpha=SMOOTHING)

    cap = cv2.VideoCapture(INPUT_VIDEO_PATH)
    if not cap.isOpened():
        print(f"CRITICAL ERROR: Could not open {INPUT_VIDEO_PATH}")
        sys.exit()

    # Video Properties
    orig_fps = cap.get(cv2.CAP_PROP_FPS)
    if orig_fps == 0: orig_fps = 24 # Fallback if unknown
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Time Clipping
    start_frame = int(START_TIME * orig_fps)
    end_frame = int(END_TIME * orig_fps) if END_TIME else total_frames
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    
    print(f"Video Loaded: {width}x{height} @ {orig_fps}fps")
    print(f"Processing range: {START_TIME}s to {END_TIME if END_TIME else 'End'}s")

    # Output Setup (Double Width for Side-by-Side)
    out_width = width * 2
    # NOTE: 'avc1' is better for Mac. 'mp4v' is better for Windows/Linux.
    fourcc = cv2.VideoWriter_fourcc(*'avc1') 
    out = cv2.VideoWriter(OUTPUT_VIDEO_PATH, fourcc, TARGET_FPS, (out_width, height))

    prev_frame_img = None
    prev_landmarks = None
    frame_count = 0

    print("--- Starting Processing (Press 'q' in window to cancel) ---")

    while cap.isOpened():
        current_frame_idx = cap.get(cv2.CAP_PROP_POS_FRAMES)
        if current_frame_idx >= end_frame:
            break

        success, frame = cap.read()
        if not success:
            break

        # 1. Detect & Smooth
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(img_rgb)
        
        raw_landmarks = results.pose_landmarks.landmark if results.pose_landmarks else None
        curr_landmarks = smoother.update(raw_landmarks)

        # Buffer Priming
        if prev_frame_img is None:
            prev_frame_img = frame
            prev_landmarks = curr_landmarks
            continue

        # 2. Interpolate & Render Loop
        # We generate multiple output frames for every single input frame to hit 60fps
        frames_to_generate = int(TARGET_FPS / orig_fps)
        
        # Pre-calculate background once per input frame to save speed
        pastel_bg = create_pastel_bg(prev_frame_img) 

        for i in range(frames_to_generate):
            fraction = i / frames_to_generate
            
            # Create 'In-Between' Skeleton
            interp_lms = interpolate_landmarks(prev_landmarks, curr_landmarks, fraction)
            
            # Draw Stickman on Pastel BG (Make a copy so we don't draw over same BG twice)
            final_stick_frame = pastel_bg.copy()
            draw_stick_figure(final_stick_frame, interp_lms)

            # Combine Side-by-Side [Original | Stick]
            combined = np.hstack((prev_frame_img, final_stick_frame))

            # Display & Save
            cv2.imshow('Real-time Preview', combined)
            out.write(combined)
            
            # Frame limiting logic for preview
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Interrupted by user.")
                cap.release()
                out.release()
                cv2.destroyAllWindows()
                sys.exit()

        # Update buffers
        prev_frame_img = frame
        prev_landmarks = curr_landmarks
        
        # Progress Log
        frame_count += 1
        if frame_count % 10 == 0:
            pct = ((current_frame_idx - start_frame) / (end_frame - start_frame)) * 100
            print(f"Progress: {pct:.1f}% completed")

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Done! Saved to {OUTPUT_VIDEO_PATH}")

if __name__ == "__main__":
    main()