import cv2
import numpy as np
import time
import tkinter as tk
from tkinter import ttk

# --- GUI for Color Selection ---
def select_cloak_color():
    selected = []

    def submit():
        selected.append(color_var.get())
        root.destroy()

    root = tk.Tk()
    root.title("Choose Cloak Color")
    root.geometry("300x120")

    ttk.Label(root, text="Select the color of your cloak:").pack(pady=10)
    color_var = tk.StringVar(value="Blue")
    colors = ["Blue", "Red", "Green"]
    dropdown = ttk.Combobox(root, values=colors, textvariable=color_var, state="readonly")
    dropdown.pack(pady=5)
    ttk.Button(root, text="Start Cloak", command=submit).pack(pady=10)

    root.mainloop()
    return selected[0] if selected else None

# --- HSV Ranges ---
def get_hsv_range(color_name):
    if color_name == "Blue":
        return np.array([90, 50, 50]), np.array([130, 255, 255])
    elif color_name == "Red":
        # Red has two ranges due to HSV wrap-around
        return [(np.array([0, 120, 70]), np.array([10, 255, 255])),
                (np.array([170, 120, 70]), np.array([180, 255, 255]))]
    elif color_name == "Green":
        return np.array([40, 50, 50]), np.array([90, 255, 255])
    else:
        raise ValueError("Invalid color selected")

# --- Capture Background ---
def create_background(cap, num_frames=30):
    print("Capturing background. Please move out of frame.")
    backgrounds = []
    for i in range(num_frames):
        ret, frame = cap.read()
        if ret:
            backgrounds.append(frame)
        else:
            print(f"Warning: Could not read frame {i+1}/{num_frames}")
        time.sleep(0.1)
    if backgrounds:
        return np.median(backgrounds, axis=0).astype(np.uint8)
    else:
        raise ValueError("Could not capture any frames for background")

# --- Create Mask ---
def create_mask(frame, hsv_range):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    if isinstance(hsv_range, list):
        # For red: combine both HSV ranges
        mask1 = cv2.inRange(hsv, hsv_range[0][0], hsv_range[0][1])
        mask2 = cv2.inRange(hsv, hsv_range[1][0], hsv_range[1][1])
        mask = cv2.bitwise_or(mask1, mask2)
    else:
        lower, upper = hsv_range
        mask = cv2.inRange(hsv, lower, upper)
    
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8), iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, np.ones((3, 3), np.uint8), iterations=1)
    return mask

# --- Cloak Effect ---
def apply_cloak_effect(frame, mask, background):
    mask_inv = cv2.bitwise_not(mask)
    fg = cv2.bitwise_and(frame, frame, mask=mask_inv)
    bg = cv2.bitwise_and(background, background, mask=mask)
    return cv2.add(fg, bg)

# --- Main Function ---
def main():
    print("OpenCV version:", cv2.__version__)

    selected_color = select_cloak_color()
    if not selected_color:
        print("No color selected. Exiting.")
        return

    hsv_range = get_hsv_range(selected_color)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    try:
        background = create_background(cap)
    except ValueError as e:
        print(f"Error: {e}")
        cap.release()
        return

    print("Starting main loop. Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            time.sleep(1)
            continue

        mask = create_mask(frame, hsv_range)
        result = apply_cloak_effect(frame, mask, background)

        cv2.imshow('Invisible Cloak', result)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
