import cv2
import pyautogui
from gaze_tracking import GazeTracking

# Initialize gaze tracking
gaze = GazeTracking()
webcam = cv2.VideoCapture(0)  # Use laptop's default camera

# Get screen size
screen_width, screen_height = pyautogui.size()
mouse_speed = 50  # Adjust speed of mouse movement

while True:
    # Capture frame from webcam
    _, frame = webcam.read()

    # Process frame
    gaze.refresh(frame)

    # Get current mouse position
    mouse_x, mouse_y = pyautogui.position()

    # Check gaze direction
    if gaze.is_right():
        print("Looking Right")
        pyautogui.moveRel(mouse_speed, 0, duration=0.1)  # Move right

    elif gaze.is_left():
        print("Looking Left")
        pyautogui.moveRel(-mouse_speed, 0, duration=0.1)  # Move left

    elif gaze.is_center():
        print("Looking Center")

    # Blink detection for mouse click
    if gaze.is_blinking():
        print("Blink detected (Click!)")
        pyautogui.click()

    # Show webcam feed with gaze tracking overlay
    frame = gaze.annotated_frame()
    cv2.imshow("Eye Tracking", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release resources
webcam.release()
cv2.destroyAllWindows()
