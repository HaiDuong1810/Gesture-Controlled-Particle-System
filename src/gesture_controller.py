import math

from src.config import (
    WIDTH,
    HEIGHT,

    PINCH_THRESHOLD,
    MAX_HAND_SPEED,

    GESTURE_HOLD_TIME,
    GESTURE_MAX_SPEED,

    SNAP_CLOSE_RATIO,
    SNAP_RELEASE_RATIO,
    SNAP_MAX_TIME,
    SNAP_MIN_SPEED,
    SNAP_COOLDOWN
)


# ============================================================
# HÀM TÍNH KHOẢNG CÁCH
# ============================================================

def distance_2d(x1, y1, x2, y2):
    return math.hypot(
        x2 - x1,
        y2 - y1
    )


# ============================================================
# KIỂM TRA MỘT NGÓN CÓ DUỖI KHÔNG
# ============================================================

def finger_is_extended(
    hand_landmarks,
    tip_id,
    pip_id,
    threshold=1.12
):

    wrist = hand_landmarks.landmark[0]
    tip = hand_landmarks.landmark[tip_id]
    pip = hand_landmarks.landmark[pip_id]

    tip_distance = math.hypot(
        tip.x - wrist.x,
        tip.y - wrist.y
    )

    pip_distance = math.hypot(
        pip.x - wrist.x,
        pip.y - wrist.y
    )

    return (
        tip_distance
        > pip_distance * threshold
    )


# ============================================================
# ĐẾM 1 - 4 NGÓN DÙNG CHỌN SHAPE
# KHÔNG TÍNH NGÓN CÁI
# ============================================================

def get_shape_finger_count(hand_landmarks):

    index_up = finger_is_extended(
        hand_landmarks,
        8,
        6
    )

    middle_up = finger_is_extended(
        hand_landmarks,
        12,
        10
    )

    ring_up = finger_is_extended(
        hand_landmarks,
        16,
        14
    )

    pinky_up = finger_is_extended(
        hand_landmarks,
        20,
        18
    )


    # 1 ngón: trỏ
    if (
        index_up
        and not middle_up
        and not ring_up
        and not pinky_up
    ):
        return 1


    # 2 ngón: trỏ + giữa
    if (
        index_up
        and middle_up
        and not ring_up
        and not pinky_up
    ):
        return 2


    # 3 ngón: trỏ + giữa + áp út
    if (
        index_up
        and middle_up
        and ring_up
        and not pinky_up
    ):
        return 3


    # 4 ngón: trỏ + giữa + áp út + út
    if (
        index_up
        and middle_up
        and ring_up
        and pinky_up
    ):
        return 4


    return 0


# ============================================================
# KIỂM TRA NGÓN CÁI MỞ
# ============================================================

def is_thumb_open(hand_landmarks):

    thumb_tip = (
        hand_landmarks.landmark[4]
    )

    index_mcp = (
        hand_landmarks.landmark[5]
    )

    pinky_mcp = (
        hand_landmarks.landmark[17]
    )


    palm_width = math.hypot(
        index_mcp.x - pinky_mcp.x,
        index_mcp.y - pinky_mcp.y
    )


    if palm_width < 0.001:
        return False


    thumb_distance = math.hypot(
        thumb_tip.x - index_mcp.x,
        thumb_tip.y - index_mcp.y
    )


    thumb_ratio = (
        thumb_distance
        / palm_width
    )


    return thumb_ratio > 0.80


# ============================================================
# KIỂM TRA BÀN TAY MỞ ĐỦ 5 NGÓN
# ============================================================

def is_full_open_hand(hand_landmarks):

    return (
        get_shape_finger_count(
            hand_landmarks
        ) == 4

        and

        is_thumb_open(
            hand_landmarks
        )
    )


# ============================================================
# GESTURE CONTROLLER
# ============================================================

class GestureController:

    def __init__(self):

        # Vị trí control point của frame trước
        self.previous_control_points = {}

        # Đầu ngón giữa của frame trước
        self.previous_middle_tips = {}

        # Trạng thái búng tay
        self.snap_states = {}

        # Trạng thái gesture 1 - 4
        self.gesture_candidate = None
        self.gesture_start_time = 0.0
        self.gesture_triggered = False


    # ========================================================
    # RESET GESTURE SHAPE
    # ========================================================

    def reset_shape_gesture(self):

        self.gesture_candidate = None
        self.gesture_start_time = 0.0
        self.gesture_triggered = False


    # ========================================================
    # PHÂN TÍCH KẾT QUẢ MEDIAPIPE
    # ========================================================

    def process(self, results, now):

        hand_controls = []
        detected_hands = []

        current_control_points = {}
        current_middle_tips = {}

        shape_candidates = []

        snap_event = None


        # ====================================================
        # XỬ LÝ TỪNG BÀN TAY
        # ====================================================

        if results.multi_hand_landmarks:

            for i, hand_landmarks in enumerate(
                results.multi_hand_landmarks
            ):

                detected_hands.append(
                    hand_landmarks
                )


                # =============================================
                # LEFT / RIGHT
                # =============================================

                hand_label = f"Hand_{i}"

                if results.multi_handedness:

                    hand_label = (
                        results
                        .multi_handedness[i]
                        .classification[0]
                        .label
                    )


                # =============================================
                # TÂM LÒNG BÀN TAY
                # =============================================

                palm_ids = (
                    0,
                    5,
                    9,
                    13,
                    17
                )

                center_x = 0.0
                center_y = 0.0


                for landmark_id in palm_ids:

                    landmark = (
                        hand_landmarks
                        .landmark[landmark_id]
                    )

                    center_x += landmark.x
                    center_y += landmark.y


                center_x = int(
                    (
                        center_x
                        / len(palm_ids)
                    )
                    * WIDTH
                )

                center_y = int(
                    (
                        center_y
                        / len(palm_ids)
                    )
                    * HEIGHT
                )


                # =============================================
                # LANDMARK QUAN TRỌNG
                # =============================================

                thumb = (
                    hand_landmarks.landmark[4]
                )

                index = (
                    hand_landmarks.landmark[8]
                )

                middle = (
                    hand_landmarks.landmark[12]
                )

                index_mcp = (
                    hand_landmarks.landmark[5]
                )

                pinky_mcp = (
                    hand_landmarks.landmark[17]
                )


                thumb_x = int(
                    thumb.x * WIDTH
                )

                thumb_y = int(
                    thumb.y * HEIGHT
                )


                index_x = int(
                    index.x * WIDTH
                )

                index_y = int(
                    index.y * HEIGHT
                )


                middle_x = int(
                    middle.x * WIDTH
                )

                middle_y = int(
                    middle.y * HEIGHT
                )


                # =============================================
                # ĐỘ RỘNG LÒNG BÀN TAY
                # =============================================

                palm_width = distance_2d(
                    index_mcp.x * WIDTH,
                    index_mcp.y * HEIGHT,

                    pinky_mcp.x * WIDTH,
                    pinky_mcp.y * HEIGHT
                )


                # =============================================
                # PINCH: NGÓN CÁI + NGÓN TRỎ
                # =============================================

                pinch_distance = distance_2d(
                    thumb_x,
                    thumb_y,
                    index_x,
                    index_y
                )


                pinch_ratio = (
                    pinch_distance / palm_width
                    if palm_width > 1
                    else 999
                )


                is_pinching = (
                    pinch_ratio
                    < PINCH_THRESHOLD
                )


                # =============================================
                # ĐẾM SHAPE 1 - 4
                # =============================================

                shape_finger_count = (
                    get_shape_finger_count(
                        hand_landmarks
                    )
                )


                # =============================================
                # KIỂM TRA 5 NGÓN
                # =============================================

                full_open_hand = (
                    is_full_open_hand(
                        hand_landmarks
                    )
                )


                if full_open_hand:

                    display_finger_count = 5

                else:

                    display_finger_count = (
                        shape_finger_count
                    )


                # =============================================
                # CONTROL POINT
                # =============================================

                if is_pinching:

                    control_x = (
                        thumb_x + index_x
                    ) // 2

                    control_y = (
                        thumb_y + index_y
                    ) // 2

                else:

                    control_x = center_x
                    control_y = center_y


                # =============================================
                # TỐC ĐỘ TAY
                # =============================================

                hand_vx = 0
                hand_vy = 0


                if (
                    hand_label
                    in self.previous_control_points
                ):

                    prev_x, prev_y = (
                        self.previous_control_points[
                            hand_label
                        ]
                    )


                    hand_vx = (
                        control_x - prev_x
                    )

                    hand_vy = (
                        control_y - prev_y
                    )


                    hand_vx = max(
                        -MAX_HAND_SPEED,
                        min(
                            MAX_HAND_SPEED,
                            hand_vx
                        )
                    )

                    hand_vy = max(
                        -MAX_HAND_SPEED,
                        min(
                            MAX_HAND_SPEED,
                            hand_vy
                        )
                    )


                hand_speed = math.hypot(
                    hand_vx,
                    hand_vy
                )


                current_control_points[
                    hand_label
                ] = (
                    control_x,
                    control_y
                )


                # =============================================
                # MODE TAY
                # =============================================

                if is_pinching:

                    mode = "GRAB"

                elif full_open_hand:

                    mode = "REPEL"

                else:

                    mode = "IDLE"


                # =============================================
                # 1 - 4 NGÓN -> ỨNG VIÊN SHAPE
                # =============================================

                if (
                    not is_pinching
                    and not full_open_hand
                    and 1 <= shape_finger_count <= 4
                    and hand_speed <= GESTURE_MAX_SPEED
                ):

                    shape_candidates.append(
                        shape_finger_count
                    )


                # =============================================
                # SNAP: NGÓN CÁI + NGÓN GIỮA
                # =============================================

                thumb_middle_distance = (
                    distance_2d(
                        thumb_x,
                        thumb_y,
                        middle_x,
                        middle_y
                    )
                )


                thumb_middle_ratio = (
                    thumb_middle_distance
                    / palm_width

                    if palm_width > 1

                    else 999
                )


                middle_speed = 0


                if (
                    hand_label
                    in self.previous_middle_tips
                ):

                    (
                        prev_middle_x,
                        prev_middle_y
                    ) = self.previous_middle_tips[
                        hand_label
                    ]


                    middle_speed = distance_2d(
                        prev_middle_x,
                        prev_middle_y,
                        middle_x,
                        middle_y
                    )


                current_middle_tips[
                    hand_label
                ] = (
                    middle_x,
                    middle_y
                )


                # =============================================
                # TẠO SNAP STATE
                # =============================================

                if hand_label not in self.snap_states:

                    self.snap_states[
                        hand_label
                    ] = {
                        "armed": False,
                        "armed_time": 0.0,
                        "last_snap": -999.0
                    }


                snap_state = (
                    self.snap_states[
                        hand_label
                    ]
                )


                # =============================================
                # CHUẨN BỊ BÚNG
                # =============================================

                if (
                    thumb_middle_ratio
                    < SNAP_CLOSE_RATIO

                    and

                    now
                    - snap_state["last_snap"]
                    > SNAP_COOLDOWN
                ):

                    if not snap_state["armed"]:

                        snap_state["armed"] = True
                        snap_state["armed_time"] = now


                # =============================================
                # NGÓN GIỮA BẬT RA
                # =============================================

                elif snap_state["armed"]:

                    elapsed = (
                        now
                        - snap_state["armed_time"]
                    )


                    if (
                        thumb_middle_ratio
                        > SNAP_RELEASE_RATIO

                        and

                        middle_speed
                        > SNAP_MIN_SPEED

                        and

                        elapsed
                        <= SNAP_MAX_TIME
                    ):

                        snap_event = (
                            middle_x,
                            middle_y
                        )

                        snap_state["armed"] = False
                        snap_state["last_snap"] = now


                    elif elapsed > SNAP_MAX_TIME:

                        snap_state["armed"] = False


                # =============================================
                # LƯU CONTROL
                # =============================================

                hand_controls.append(
                    {
                        "label": hand_label,

                        "mode": mode,

                        "x": control_x,
                        "y": control_y,

                        "vx": hand_vx,
                        "vy": hand_vy,

                        "fingers":
                            display_finger_count,

                        "shape_fingers":
                            shape_finger_count
                    }
                )


        # ====================================================
        # LƯU FRAME HIỆN TẠI
        # ====================================================

        self.previous_control_points = (
            current_control_points.copy()
        )

        self.previous_middle_tips = (
            current_middle_tips.copy()
        )

        # ====================================================
        # HAI TAY CÙNG PINCH -> TRANSFORM MODE
        # ====================================================

        pinching_controls = [
            control
            for control in hand_controls
            if control["mode"] == "GRAB"
        ]

        transform_active = (
                len(pinching_controls) >= 2
        )

        transform_points = []

        if transform_active:

            # Sắp xếp theo vị trí X để thứ tự 2 tay ổn định hơn
            pinching_controls.sort(
                key=lambda control: control["x"]
            )

            # Chỉ lấy 2 tay đầu tiên
            transform_controls = (
                pinching_controls[:2]
            )

            # Chuyển GRAB -> TRANSFORM
            for control in transform_controls:
                control["mode"] = "TRANSFORM"

                transform_points.append(
                    (
                        control["x"],
                        control["y"]
                    )
                )

            # Khi đang transform:
            # không cho kích hoạt Shape hoặc Snap
            shape_candidates.clear()
            snap_event = None

            self.reset_shape_gesture()


        # Nếu một tay biến mất khi đang chuẩn bị snap
        # thì hủy trạng thái snap của tay đó
        active_labels = set(
            current_control_points.keys()
        )

        for label, state in self.snap_states.items():

            if label not in active_labels:
                state["armed"] = False


        # ====================================================
        # XỬ LÝ GESTURE 1 - 4
        # ====================================================

        detected_shape_gesture = None


        if (
            shape_candidates
            and len(set(shape_candidates)) == 1
        ):

            detected_shape_gesture = (
                shape_candidates[0]
            )


        shape_trigger = None
        gesture_progress = 0.0


        # Không phát hiện gesture hợp lệ
        if detected_shape_gesture is None:

            self.reset_shape_gesture()


        else:

            # Gesture vừa thay đổi
            if (
                self.gesture_candidate
                != detected_shape_gesture
            ):

                self.gesture_candidate = (
                    detected_shape_gesture
                )

                self.gesture_start_time = now
                self.gesture_triggered = False


            else:

                held_time = (
                    now
                    - self.gesture_start_time
                )

                gesture_progress = min(
                    1.0,
                    held_time
                    / GESTURE_HOLD_TIME
                )


                # Giữ đủ thời gian -> tạo hình
                if (
                    not self.gesture_triggered
                    and held_time
                    >= GESTURE_HOLD_TIME
                ):

                    shape_trigger = (
                        self.gesture_candidate
                    )

                    self.gesture_triggered = True


            if self.gesture_triggered:
                gesture_progress = 1.0


        # ====================================================
        # SNAP ƯU TIÊN CAO HƠN SHAPE
        # ====================================================

        if snap_event is not None:

            shape_trigger = None
            gesture_progress = 0.0

            self.reset_shape_gesture()


        # ====================================================
        # TRẢ KẾT QUẢ
        # ====================================================

        return {
            "hand_controls":
                hand_controls,

            "detected_hands":
                detected_hands,

            "shape_trigger":
                shape_trigger,

            "snap_event":
                snap_event,

            "gesture_candidate":
                self.gesture_candidate,

            "gesture_triggered":
                self.gesture_triggered,

            "gesture_progress":
                gesture_progress,

            "transform_active":
                transform_active,

            "transform_points":
                transform_points
        }