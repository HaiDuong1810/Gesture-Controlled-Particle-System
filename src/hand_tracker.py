import cv2
import mediapipe as mp

from src.config import (
    MP_WIDTH,
    MP_HEIGHT
)


# ============================================================
# HAND TRACKER
# ============================================================

class HandTracker:

    def __init__(self):

        # MediaPipe Hands
        self.mp_hands = mp.solutions.hands

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=0,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        # Dùng để vẽ landmark
        self.mp_draw = (
            mp.solutions.drawing_utils
        )


    # ========================================================
    # NHẬN DIỆN BÀN TAY
    # ========================================================

    def process(self, frame):

        # Resize nhỏ trước khi đưa vào MediaPipe
        mp_frame = cv2.resize(
            frame,
            (
                MP_WIDTH,
                MP_HEIGHT
            ),
            interpolation=cv2.INTER_AREA
        )

        # OpenCV BGR -> RGB
        rgb_frame = cv2.cvtColor(
            mp_frame,
            cv2.COLOR_BGR2RGB
        )

        # MediaPipe chỉ cần đọc frame
        rgb_frame.flags.writeable = False

        results = self.hands.process(
            rgb_frame
        )

        rgb_frame.flags.writeable = True

        return results


    # ========================================================
    # VẼ LANDMARK
    # ========================================================

    def draw_landmarks(
        self,
        frame,
        hand_landmarks
    ):

        self.mp_draw.draw_landmarks(
            frame,
            hand_landmarks,
            self.mp_hands.HAND_CONNECTIONS
        )


    # ========================================================
    # GIẢI PHÓNG MEDIAPIPE
    # ========================================================

    def close(self):

        self.hands.close()