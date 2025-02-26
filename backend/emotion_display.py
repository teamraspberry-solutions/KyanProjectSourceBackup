import cairo
import numpy as np
import cv2
import time
import threading
import random

class EmotionDisplay:
    def __init__(self):
        """Initialize the Cairo-based display."""
        self.width, self.height = 240, 120  # Display size
        self.current_emotion = "neutral"
        self.running = True
        self.lock = threading.Lock()
        self.eyes_open = True

        self.display_thread = threading.Thread(target=self.run_display, daemon=True)
        self.blink_thread = threading.Thread(target=self.blink_loop, daemon=True)

        self.display_thread.start()
        self.blink_thread.start()
 
    def create_face(self, emotion="neutral", eyes_open=True):
        """Creates an expressive robotic face using Cairo."""
        surface = cairo.ImageSurface(cairo.FORMAT_RGB24, self.width, self.height)
        ctx = cairo.Context(surface)

        # Set background to black
        ctx.set_source_rgb(0, 0, 0)
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.fill()

        # Eye properties
        eye_width, eye_height = (35, 20) if eyes_open else (35, 5)
        eye_color = (1, 1, 1) if eyes_open else (0, 0, 0)
        left_eye = (50, 35)
        right_eye = (160, 35)
        mouth_color = (1, 1, 1)

        # Define mouth coordinates and shapes
        mouth_shapes = {
            "happy": [(100, 95), (110, 105), (120, 108), (130, 105), (140, 95)],
            "sad": [(100, 105), (110, 95), (120, 92), (130, 95), (140, 105)],
            "angry": [(100, 100), (140, 90)],
            "surprised": [(110, 85, 130, 105)],
            "neutral": [(110, 95), (130, 95)]
        }
        mouth_coords = mouth_shapes.get(emotion, mouth_shapes["neutral"])

        # Draw eyes
        ctx.set_source_rgb(*eye_color)
        ctx.rectangle(left_eye[0], left_eye[1], eye_width, eye_height)
        ctx.fill()
        ctx.rectangle(right_eye[0], right_eye[1], eye_width, eye_height)
        ctx.fill()

        # Draw mouth
        ctx.set_source_rgb(*mouth_color)
        ctx.set_line_width(3)
        if emotion == "surprised":
            x, y, x2, y2 = mouth_coords[0]
            ctx.arc((x + x2) / 2, (y + y2) / 2, 10, 0, 2 * 3.1415)
            ctx.fill()
        else:
            ctx.move_to(*mouth_coords[0])
            for coord in mouth_coords[1:]:
                ctx.line_to(*coord)
            ctx.stroke()

        return surface

    def run_display(self):
        """Continuously updates the display."""
        while self.running:
            with self.lock:
                surface = self.create_face(self.current_emotion, self.eyes_open)

            self.show_image(surface)
            time.sleep(0.1)

        # Ensure window closes properly when loop ends
        self.force_close_window()

    def blink_loop(self):
        """Handles blinking at random intervals."""
        while self.running:
            time.sleep(random.uniform(3, 5))
            with self.lock:
                self.eyes_open = False
            self.update_display()
            time.sleep(0.25)
            with self.lock:
                self.eyes_open = True
            self.update_display()

    def update_display(self):
        """Updates the display with the current emotion."""
        if self.running:
            surface = self.create_face(self.current_emotion, self.eyes_open)
            self.show_image(surface)

    def show_image(self, surface):
        """Displays the face using Cairo and OpenCV."""
        buf = surface.get_data()
        image_np = np.ndarray(shape=(self.height, self.width, 4), dtype=np.uint8, buffer=buf)

        # Convert to BGR for OpenCV
        image_np = cv2.cvtColor(image_np, cv2.COLOR_BGRA2BGR)
        cv2.imshow("Kyan Face Display", image_np)

        # Process window events
        if not self.running:
            cv2.waitKey(500)  # Give it 500ms to close
        else:
            cv2.waitKey(1)  # Small delay to keep the window responsive


    def set_emotion(self, emotion):
        """Updates the displayed emotion."""
        with self.lock:
            self.current_emotion = emotion
            self.eyes_open = True
        print(f"Emotion changed to: {emotion}")
        self.update_display()  # Immediately update display

    def stop_display(self):
        """Stops the display and closes all threads cleanly within 1 second."""
        self.running = False  # Stop loops

        # Ensure all threads terminate before closing
        self.display_thread.join(timeout=1)
        self.blink_thread.join(timeout=1)

        # Force OpenCV to close immediately
        self.force_close_window()

    def force_close_window(self):
        """Forcefully closes the display window."""
        cv2.destroyAllWindows()
        cv2.waitKey(1)  # Ensure OpenCV processes the closure


if __name__ == "__main__":
    display = EmotionDisplay()

    time.sleep(3)
    display.set_emotion("happy")
    time.sleep(3)
    # display.stop_display()  # Should close within 1 second

    display.set_emotion("angry")
    time.sleep(3)
    display.set_emotion("sad")
    time.sleep(3)
    display.set_emotion("surprised")
    time.sleep(5)

    display.stop_display()
