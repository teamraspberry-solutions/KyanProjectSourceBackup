import cv2
import numpy as np
from PIL import Image, ImageDraw
import time
import threading
import random

class EmotionDisplay:
    def __init__(self):
        """Initialize display parameters."""
        self.width, self.height = 240, 120  # Display size
        self.current_emotion = "neutral"
        self.target_emotion = "neutral"  # Track target emotion for smooth transition
        self.running = True
        self.lock = threading.Lock()
        self.eyes_open = True

        # Flags to manage the threads
        self.display_thread_running = True
        self.blink_thread_running = True

        self.display_thread = threading.Thread(target=self.run_display, daemon=True)
        self.display_thread.start()

        self.blink_thread = threading.Thread(target=self.blink_loop, daemon=True)
        self.blink_thread.start()

    def create_face(self, emotion="neutral", eyes_open=True):
        """Creates an expressive robotic face."""
        face = Image.new("RGB", (self.width, self.height), "black")
        draw = ImageDraw.Draw(face)

        # Eye properties
        eye_size = (35, 20) if eyes_open else (35, 5)
        eye_color = "white" if eyes_open else "black"
        left_eye = (50, 35)
        right_eye = (160, 35)
        mouth_color = "white"

        # Define mouth coordinates and shapes for different emotions
        emotion_mouth_shapes = {
            "happy": [(100, 95), (110, 105), (120, 108), (130, 105), (140, 95)],
            "sad": [(100, 105), (110, 95), (120, 92), (130, 95), (140, 105)],
            "angry": [(100, 100), (140, 90)],
            "surprised": [(110, 85, 130, 105)],
            "neutral": [(110, 95), (130, 95)],
        }
        mouth_coords = emotion_mouth_shapes.get(emotion, emotion_mouth_shapes["neutral"])

        # Draw eyes
        draw.rectangle([left_eye, (left_eye[0] + eye_size[0], left_eye[1] + eye_size[1])], fill=eye_color)
        draw.rectangle([right_eye, (right_eye[0] + eye_size[0], right_eye[1] + eye_size[1])], fill=eye_color)

        # Draw mouth
        if emotion == "surprised":
            draw.ellipse(mouth_coords[0], fill=mouth_color)
        else:
            draw.line(mouth_coords, fill=mouth_color, width=3)

        return face
    
    def run_display(self):
        """Continuously updates the display."""
        while self.display_thread_running:
            with self.lock:
                face_image = self.create_face(self.current_emotion, self.eyes_open)
            self.show_image(face_image)
            time.sleep(0.1)  # Delay for a smooth display refresh

        # Explicitly destroy any OpenCV windows once the display thread ends
        cv2.destroyAllWindows()

    def blink_loop(self):
        """Handles blinking at random intervals."""
        while self.blink_thread_running:
            time.sleep(random.uniform(3, 5))
            with self.lock:
                self.eyes_open = False
            self.update_display()
            time.sleep(0.25)
            with self.lock:
                self.eyes_open = True
            self.update_display()

    def transition_to_emotion(self, new_emotion, duration=1.0):
        """Smoothly transitions to a new emotion."""
        frames = int(duration * 30)  # Assuming 30 FPS, adjust as needed
        for frame in range(frames):
            # Smoothly interpolate between the current and new emotion
            with self.lock:
                self.current_emotion = self.interpolate_emotion(self.current_emotion, new_emotion, frame, frames)

            # Update the display to show the transition
            self.update_display()
            time.sleep(1 / 30)  # Sleep for the duration of one frame (30 FPS)

        # Ensure we finish on the target emotion
        with self.lock:
            self.current_emotion = new_emotion
        self.update_display()

    def interpolate_emotion(self, start_emotion, end_emotion, frame, total_frames):
        """Interpolates between two emotions. For simplicity, we'll focus on mouth shapes."""
        # Linear interpolation of emotions (you can add more complex logic here)
        if frame == total_frames - 1:
            return end_emotion
        return start_emotion  # For simplicity, direct transition. Add more complexity if needed.

    def update_display(self):
        """Updates the display with the current emotion."""
        face_image = self.create_face(self.current_emotion, self.eyes_open)
        self.show_image(face_image)

    def show_image(self, image):
        """Displays the face using OpenCV."""
        # Convert the Pillow image to a NumPy array
        face_np = np.array(image)
        # Convert RGB (Pillow) to BGR (OpenCV)
        face_cv = cv2.cvtColor(face_np, cv2.COLOR_RGB2BGR)
        # Display the image
        cv2.imshow("Kyan Face Display", face_cv)
        # Refresh the window immediately, this ensures it updates without waiting for a keypress
        cv2.waitKey(1)

    def set_emotion(self, emotion):
        """Updates the displayed emotion immediately."""
        with self.lock:
            self.current_emotion = emotion
            self.eyes_open = True
        print(f"Emotion changed to: {emotion}")
        self.update_display()

    def stop_display(self):
        """Stops the display properly."""
        self.display_thread_running = False
        self.blink_thread_running = False

        # Wait for threads to finish safely before exiting
        self.display_thread.join()
        self.blink_thread.join()

        # Now that threads are joined, we can safely destroy OpenCV windows
        cv2.destroyAllWindows()
        print("Emotion Display Stopped")
