import cv2
import mediapipe as mp
import math
import time
import threading
from database.database import KyanDatabase  # Assuming the database.py is in the same directory

class FocusTracker:
    def __init__(self):
        # Initialize Mediapipe Pose and Face Mesh
        self.mp_pose = mp.solutions.pose
        self.mp_face_mesh = mp.solutions.face_mesh
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.face_mesh = self.mp_face_mesh.FaceMesh(refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        
        # Initialize database connection
        self.db = KyanDatabase()

        # Webcam setup
        self.cap = cv2.VideoCapture(0)

        # Retrieve the latest session_id
        self.db.cursor.execute("SELECT session_id FROM session ORDER BY start_time DESC LIMIT 1")
        result = self.db.cursor.fetchone()

        self.stop_event = threading.Event()  # Add stop event

        if result is None:
            print("No active session found!")
            self.cap.release()
            cv2.destroyAllWindows()

        self.session_id = result[0]  # Get the latest session ID

    def calculate_distance(self, point1, point2):
        return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

    def check_eye_openness(self, landmarks):
        left_eye_top = landmarks[159]
        left_eye_bottom = landmarks[145]
        right_eye_top = landmarks[386]
        right_eye_bottom = landmarks[374]

        left_eye_open = self.calculate_distance(left_eye_top, left_eye_bottom)
        right_eye_open = self.calculate_distance(right_eye_top, right_eye_bottom)
        return (left_eye_open + right_eye_open) / 2

    def check_focus(self, face_landmarks, pose_landmarks):
        # Face landmarks
        nose = face_landmarks[1]  # Nose tip
        left_eye = face_landmarks[33]
        right_eye = face_landmarks[263]
        eye_openness = self.check_eye_openness(face_landmarks)

        # Pose landmarks
        left_shoulder = pose_landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = pose_landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

        # Conditions
        face_straight = abs(left_eye.x - right_eye.x) > 0 and left_eye.x < nose.x < right_eye.x
        shoulders_level = abs(left_shoulder.y - right_shoulder.y) < 0.15
        upright_posture = self.calculate_distance(left_shoulder, right_shoulder) > 0.25
        eyes_open = eye_openness > 0.01  # Threshold for detecting open eyes

        # Weighted scoring
        score = 0
        if face_straight: score += 0.4
        if shoulders_level: score += 0.3
        if upright_posture: score += 0.2
        if eyes_open: score += 0.1

        return score >= 0.7  # Threshold to decide focus

    def track_focus(self, session_id):
        while self.cap.isOpened() and not self.stop_event.is_set():
            ret, frame = self.cap.read()
            if not ret:
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_results = self.face_mesh.process(rgb_frame)
            pose_results = self.pose.process(rgb_frame)

            isFocused = False
            if face_results.multi_face_landmarks and pose_results.pose_landmarks:
                face_landmarks = face_results.multi_face_landmarks[0].landmark
                pose_landmarks = pose_results.pose_landmarks.landmark
                isFocused = self.check_focus(face_landmarks, pose_landmarks)

                # Draw face mesh
                for landmarks in face_results.multi_face_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(frame, landmarks, self.mp_face_mesh.FACEMESH_TESSELATION)

                # Draw pose (upper body only)
                mp.solutions.drawing_utils.draw_landmarks(frame, pose_results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

            # Insert focus data into the database every 30 seconds
            self.db.insert_focus_tracker(self.session_id, isFocused)

            # Display status
            color = (0, 255, 0) if isFocused else (0, 0, 255)
            cv2.putText(frame, f"Focused: {isFocused}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            cv2.imshow("Focus Tracker", frame)

            if cv2.waitKey(1) & 0xFF == ord('q') or self.stop_event.is_set():
                break

            # Wait 30 seconds before checking focus again
            time.sleep(15)

        # Update session end time after the loop
        self.db.cursor.execute("UPDATE session SET end_time = CURRENT_TIMESTAMP WHERE session_id = ?", (self.session_id,))
        self.db.conn.commit()

        self.cap.release()


    def stop(self):
        """Stops focus tracking and releases the camera."""
        self.stop_event.set()  
        self.cap.release()  
