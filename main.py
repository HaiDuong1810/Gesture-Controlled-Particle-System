import cv2
import numpy as np
import time

from src.config import (
    WIDTH,
    HEIGHT,
    MAX_PARTICLES,
    CAMERA_DARKNESS,
    SHAPE_PATHS,
    SHAPE_NAMES,
    REPEL_RADIUS,
    GRAB_RADIUS,

    TRANSFORM_MOVE_SMOOTHING,

    TRANSFORM_SCALE_SMOOTHING,
    TRANSFORM_SCALE_STEP_MIN,
    TRANSFORM_SCALE_STEP_MAX,

    TRANSFORM_ROTATE_SMOOTHING,
    TRANSFORM_ROTATE_STEP_MAX
)

from src.shape_manager import load_shape_targets
from src.particle_system import ParticleSystem
from src.hand_tracker import HandTracker
from src.gesture_controller import GestureController


# ============================================================
# LOAD TOÀN BỘ SHAPE
# ============================================================

def load_all_shapes():

    shape_targets = {}

    for shape_id, path in SHAPE_PATHS.items():

        shape_targets[shape_id] = load_shape_targets(
            path,
            seed=100 + shape_id
        )

    return shape_targets


# ============================================================
# CHUẨN HÓA GÓC -180 -> 180
# ============================================================

def normalize_angle(angle):

    return (
        (angle + 180.0)
        % 360.0
    ) - 180.0


# ============================================================
# CHUẨN HÓA GÓC ĐƯỜNG NỐI HAI TAY
#
# Hai đầu của đường thẳng có thể đổi vị trí cho nhau.
# Vì vậy góc của đường nối được xem theo chu kỳ 180 độ.
# ============================================================

def normalize_line_angle(angle):

    return (
        (angle + 90.0)
        % 180.0
    ) - 90.0


# ============================================================
# TÍNH CHÊNH LỆCH GÓC NGẮN NHẤT
# ============================================================

def line_angle_difference(
    new_angle,
    old_angle
):

    return (
        (
            new_angle
            - old_angle
            + 90.0
        )
        % 180.0
    ) - 90.0


# ============================================================
# VẼ TRẠNG THÁI TỪNG BÀN TAY
# ============================================================

def draw_hand_status(
    display,
    hand_controls
):

    for control in hand_controls:

        x = control["x"]
        y = control["y"]

        mode = control["mode"]
        label = control["label"]
        fingers = control["fingers"]


        # ====================================================
        # MÀU + BÁN KÍNH THEO MODE
        # ====================================================

        if mode == "REPEL":

            color = (
                0,
                0,
                255
            )

            radius = REPEL_RADIUS


        elif mode == "GRAB":

            color = (
                0,
                255,
                0
            )

            radius = GRAB_RADIUS


        elif mode == "TRANSFORM":

            color = (
                255,
                255,
                0
            )

            radius = 35


        else:

            color = (
                160,
                160,
                160
            )

            radius = 20


        # ====================================================
        # ĐIỂM ĐIỀU KHIỂN
        # ====================================================

        cv2.circle(
            display,
            (x, y),
            8,
            color,
            -1
        )


        # ====================================================
        # VÙNG TÁC ĐỘNG
        # ====================================================

        if mode in (
            "REPEL",
            "GRAB",
            "TRANSFORM"
        ):

            cv2.circle(
                display,
                (x, y),
                radius,
                color,
                1
            )


        # ====================================================
        # THÔNG TIN TAY
        # ====================================================

        cv2.putText(
            display,
            f"{label}: {mode} | {fingers}",
            (
                x - 60,
                max(
                    20,
                    y - 20
                )
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            color,
            1
        )


# ============================================================
# VẼ THÔNG TIN CHUNG
# ============================================================

def draw_hud(
    display,
    fps,
    particle_mode,
    current_shape,
    gesture_candidate,
    gesture_triggered,
    gesture_progress,
    status_message,
    status_until,
    now
):

    # ========================================================
    # PARTICLE
    # ========================================================

    cv2.putText(
        display,
        f"Particles: {MAX_PARTICLES}",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )


    # ========================================================
    # FPS
    # ========================================================

    cv2.putText(
        display,
        f"FPS: {fps:.1f}",
        (20, 55),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )


    # ========================================================
    # MODE
    # ========================================================

    cv2.putText(
        display,
        f"Mode: {particle_mode}",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )


    # ========================================================
    # SHAPE HIỆN TẠI
    # ========================================================

    if current_shape is not None:

        cv2.putText(
            display,
            (
                f"Shape: "
                f"{current_shape} - "
                f"{SHAPE_NAMES[current_shape]}"
            ),
            (20, 105),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2
        )


    # ========================================================
    # TIẾN TRÌNH GIỮ 1 - 4 NGÓN
    # ========================================================

    if (
        gesture_candidate is not None
        and not gesture_triggered
    ):

        cv2.putText(
            display,
            (
                f"Gesture "
                f"{gesture_candidate}: "
                f"{int(gesture_progress * 100)}%"
            ),
            (20, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 255),
            2
        )


    # ========================================================
    # STATUS
    # ========================================================

    if now < status_until:

        cv2.putText(
            display,
            status_message,
            (
                20,
                HEIGHT - 25
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )


# ============================================================
# VẼ THÔNG TIN TRANSFORM
# ============================================================

def draw_transform_status(
    display,
    transform_active,
    transform_points,
    current_scale,
    current_rotation
):

    if not transform_active:
        return


    # ========================================================
    # TRANSFORM MODE
    # ========================================================

    cv2.putText(
        display,
        "TRANSFORM MODE",
        (
            WIDTH // 2 - 100,
            35
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 0),
        2
    )


    if len(transform_points) != 2:
        return


    # ========================================================
    # HAI ĐIỂM PINCH
    # ========================================================

    point_1 = (
        int(transform_points[0][0]),
        int(transform_points[0][1])
    )

    point_2 = (
        int(transform_points[1][0]),
        int(transform_points[1][1])
    )


    # ========================================================
    # ĐƯỜNG NỐI HAI TAY
    # ========================================================

    cv2.line(
        display,
        point_1,
        point_2,
        (255, 255, 0),
        2
    )


    # ========================================================
    # TRUNG ĐIỂM HAI TAY
    # ========================================================

    center_point = (
        int(
            (
                transform_points[0][0]
                + transform_points[1][0]
            ) / 2
        ),
        int(
            (
                transform_points[0][1]
                + transform_points[1][1]
            ) / 2
        )
    )


    cv2.circle(
        display,
        center_point,
        8,
        (255, 255, 0),
        -1
    )


    # ========================================================
    # MOVE + SCALE + ROTATE
    # ========================================================

    cv2.putText(
        display,
        "MOVE + SCALE + ROTATE",
        (
            center_point[0] + 12,
            center_point[1] - 28
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 0),
        2
    )


    # ========================================================
    # SCALE
    # ========================================================

    cv2.putText(
        display,
        f"Scale: {current_scale:.2f}x",
        (
            center_point[0] + 12,
            center_point[1] - 8
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 0),
        1
    )


    # ========================================================
    # ROTATION
    # ========================================================

    cv2.putText(
        display,
        f"Rotation: {current_rotation:.1f} deg",
        (
            center_point[0] + 12,
            center_point[1] + 12
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 0),
        1
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # ========================================================
    # HAND + GESTURE
    # ========================================================

    hand_tracker = HandTracker()
    gesture_controller = GestureController()

    cap = None


    try:

        # ====================================================
        # LOAD SHAPE
        # ====================================================

        shape_targets = load_all_shapes()


        # ====================================================
        # PARTICLE SYSTEM
        # ====================================================

        heart_positions, heart_colors = (
            shape_targets[1]
        )


        particles = ParticleSystem(
            heart_positions,
            heart_colors
        )


        # ====================================================
        # CAMERA
        # ====================================================

        cap = cv2.VideoCapture(0)


        cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            WIDTH
        )


        cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            HEIGHT
        )


        cap.set(
            cv2.CAP_PROP_BUFFERSIZE,
            1
        )


        cap.set(
            cv2.CAP_PROP_FPS,
            30
        )


        if not cap.isOpened():

            print(
                "Không mở được camera!"
            )

            return


        # ====================================================
        # TRẠNG THÁI PARTICLE
        # ====================================================

        particle_mode = "FREE"

        current_shape = None


        # ====================================================
        # TRANSFORM - MOVE
        # ====================================================

        transform_center_smooth = None

        previous_transform_center = None


        # ====================================================
        # TRANSFORM - SCALE
        # ====================================================

        transform_distance_smooth = None

        previous_transform_distance = None

        current_scale = 1.0


        # ====================================================
        # TRANSFORM - ROTATE
        # ====================================================

        transform_angle_smooth = None

        previous_transform_angle = None

        current_rotation = 0.0


        # ====================================================
        # STATUS
        # ====================================================

        status_message = "FREE MODE"

        status_until = 0.0


        # ====================================================
        # FPS
        # ====================================================

        fps = 0.0

        fps_frames = 0

        fps_timer = (
            time.perf_counter()
        )


        # ====================================================
        # MAIN LOOP
        # ====================================================

        while True:

            now = time.perf_counter()


            # =================================================
            # CAMERA
            # =================================================

            success, frame = cap.read()


            if not success:

                print(
                    "Không đọc được camera!"
                )

                break


            if (
                frame.shape[1] != WIDTH
                or frame.shape[0] != HEIGHT
            ):

                frame = cv2.resize(
                    frame,
                    (
                        WIDTH,
                        HEIGHT
                    )
                )


            frame = cv2.flip(
                frame,
                1
            )


            # =================================================
            # HAND TRACKING
            # =================================================

            results = (
                hand_tracker.process(
                    frame
                )
            )


            # =================================================
            # GESTURE
            # =================================================

            gesture_data = (
                gesture_controller.process(
                    results,
                    now
                )
            )


            hand_controls = (
                gesture_data[
                    "hand_controls"
                ]
            )


            detected_hands = (
                gesture_data[
                    "detected_hands"
                ]
            )


            shape_trigger = (
                gesture_data[
                    "shape_trigger"
                ]
            )


            snap_event = (
                gesture_data[
                    "snap_event"
                ]
            )


            gesture_candidate = (
                gesture_data[
                    "gesture_candidate"
                ]
            )


            gesture_triggered = (
                gesture_data[
                    "gesture_triggered"
                ]
            )


            gesture_progress = (
                gesture_data[
                    "gesture_progress"
                ]
            )


            transform_active = (
                gesture_data[
                    "transform_active"
                ]
            )


            transform_points = (
                gesture_data[
                    "transform_points"
                ]
            )


            # =================================================
            # 1 - 4 NGÓN -> SHAPE
            # =================================================

            if shape_trigger is not None:

                current_shape = (
                    shape_trigger
                )


                (
                    new_positions,
                    new_colors

                ) = shape_targets[
                    current_shape
                ]


                particles.set_target(
                    new_positions,
                    new_colors
                )


                particle_mode = "SHAPE"


                # =============================================
                # RESET TRANSFORM CỦA SHAPE MỚI
                # =============================================

                current_scale = 1.0
                current_rotation = 0.0

                transform_center_smooth = None
                previous_transform_center = None

                transform_distance_smooth = None
                previous_transform_distance = None

                transform_angle_smooth = None
                previous_transform_angle = None


                status_message = (
                    f"SHAPE "
                    f"{current_shape}: "
                    f"{SHAPE_NAMES[current_shape]}"
                )


                status_until = (
                    now + 1.2
                )


            # =================================================
            # TRANSFORM
            # MOVE + SCALE + ROTATE
            # =================================================

            if (
                transform_active
                and particle_mode == "SHAPE"
                and len(transform_points) == 2
            ):

                # =============================================
                # 2 ĐIỂM PINCH
                # =============================================

                x1, y1 = (
                    transform_points[0]
                )

                x2, y2 = (
                    transform_points[1]
                )


                # =============================================
                # TRUNG ĐIỂM -> MOVE
                # =============================================

                center_x = (
                    x1 + x2
                ) / 2.0


                center_y = (
                    y1 + y2
                ) / 2.0


                current_center = np.array(
                    [
                        center_x,
                        center_y
                    ],
                    dtype=np.float32
                )


                # =============================================
                # KHOẢNG CÁCH -> SCALE
                # =============================================

                current_distance = float(
                    np.hypot(
                        x2 - x1,
                        y2 - y1
                    )
                )


                # =============================================
                # GÓC HAI TAY -> ROTATE
                # =============================================

                current_angle = float(
                    np.degrees(
                        np.arctan2(
                            y2 - y1,
                            x2 - x1
                        )
                    )
                )


                current_angle = (
                    normalize_line_angle(
                        current_angle
                    )
                )


                # =============================================
                # FRAME ĐẦU TIÊN CỦA TRANSFORM
                # =============================================

                if (
                    transform_center_smooth is None
                    or transform_distance_smooth is None
                    or transform_angle_smooth is None
                ):

                    # MOVE
                    transform_center_smooth = (
                        current_center.copy()
                    )

                    previous_transform_center = (
                        current_center.copy()
                    )


                    # SCALE
                    transform_distance_smooth = (
                        current_distance
                    )

                    previous_transform_distance = (
                        current_distance
                    )


                    # ROTATE
                    transform_angle_smooth = (
                        current_angle
                    )

                    previous_transform_angle = (
                        current_angle
                    )


                # =============================================
                # CÁC FRAME TIẾP THEO
                # =============================================

                else:

                    # =========================================
                    # MOVE
                    # =========================================

                    transform_center_smooth += (
                        current_center
                        - transform_center_smooth
                    ) * TRANSFORM_MOVE_SMOOTHING


                    delta = (
                        transform_center_smooth
                        - previous_transform_center
                    )


                    dx = float(
                        delta[0]
                    )

                    dy = float(
                        delta[1]
                    )


                    particles.move_shape(
                        dx,
                        dy
                    )


                    previous_transform_center = (
                        transform_center_smooth.copy()
                    )


                    # =========================================
                    # SCALE
                    # =========================================

                    transform_distance_smooth += (
                        current_distance
                        - transform_distance_smooth
                    ) * TRANSFORM_SCALE_SMOOTHING


                    if (
                        previous_transform_distance
                        is not None
                        and previous_transform_distance > 1.0
                    ):

                        scale_factor = (
                            transform_distance_smooth
                            / previous_transform_distance
                        )


                        scale_factor = float(
                            np.clip(
                                scale_factor,
                                TRANSFORM_SCALE_STEP_MIN,
                                TRANSFORM_SCALE_STEP_MAX
                            )
                        )


                        current_scale = (
                            particles.scale_shape(
                                scale_factor,
                                float(
                                    transform_center_smooth[0]
                                ),
                                float(
                                    transform_center_smooth[1]
                                )
                            )
                        )


                    previous_transform_distance = (
                        transform_distance_smooth
                    )


                    # =========================================
                    # ROTATE - LÀM MƯỢT GÓC
                    # =========================================

                    angle_to_target = (
                        line_angle_difference(
                            current_angle,
                            transform_angle_smooth
                        )
                    )


                    transform_angle_smooth = (
                        normalize_line_angle(
                            transform_angle_smooth
                            + angle_to_target
                            * TRANSFORM_ROTATE_SMOOTHING
                        )
                    )


                    # =========================================
                    # ROTATE - ĐỘ XOAY TỪ FRAME TRƯỚC
                    # =========================================

                    angle_delta = (
                        line_angle_difference(
                            transform_angle_smooth,
                            previous_transform_angle
                        )
                    )


                    # =========================================
                    # GIỚI HẠN XOAY MỖI FRAME
                    # =========================================

                    angle_delta = float(
                        np.clip(
                            angle_delta,
                            -TRANSFORM_ROTATE_STEP_MAX,
                            TRANSFORM_ROTATE_STEP_MAX
                        )
                    )


                    # =========================================
                    # XOAY SHAPE
                    # =========================================

                    if abs(angle_delta) > 0.001:

                        particles.rotate_shape(
                            angle_delta,
                            float(
                                transform_center_smooth[0]
                            ),
                            float(
                                transform_center_smooth[1]
                            )
                        )


                        current_rotation = (
                            normalize_angle(
                                current_rotation
                                + angle_delta
                            )
                        )


                    previous_transform_angle = (
                        transform_angle_smooth
                    )


            # =================================================
            # THOÁT TRANSFORM
            # =================================================

            else:

                transform_center_smooth = None
                previous_transform_center = None

                transform_distance_smooth = None
                previous_transform_distance = None

                transform_angle_smooth = None
                previous_transform_angle = None


            # =================================================
            # SNAP -> BREAK
            # =================================================

            if snap_event is not None:

                break_x, break_y = (
                    snap_event
                )


                particles.break_apart(
                    break_x,
                    break_y
                )


                particle_mode = "FREE"

                current_shape = None


                # =============================================
                # RESET TRANSFORM
                # =============================================

                current_scale = 1.0
                current_rotation = 0.0

                transform_center_smooth = None
                previous_transform_center = None

                transform_distance_smooth = None
                previous_transform_distance = None

                transform_angle_smooth = None
                previous_transform_angle = None


                status_message = (
                    "SNAP -> BREAK!"
                )


                status_until = (
                    now + 1.2
                )


            # =================================================
            # UPDATE PARTICLES
            # =================================================

            particles.update(
                hand_controls,
                particle_mode
            )


            # =================================================
            # CAMERA TỐI
            # =================================================

            display = (
                frame.astype(
                    np.float32
                )
                * CAMERA_DARKNESS
            ).astype(
                np.uint8
            )


            # =================================================
            # PARTICLES
            # =================================================

            particles.draw(
                display
            )


            # =================================================
            # LANDMARK
            # =================================================

            for hand_landmarks in (
                detected_hands
            ):

                hand_tracker.draw_landmarks(
                    display,
                    hand_landmarks
                )


            # =================================================
            # TRẠNG THÁI TAY
            # =================================================

            draw_hand_status(
                display,
                hand_controls
            )


            # =================================================
            # TRANSFORM HUD
            # =================================================

            draw_transform_status(
                display=display,
                transform_active=transform_active,
                transform_points=transform_points,
                current_scale=current_scale,
                current_rotation=current_rotation
            )


            # =================================================
            # FPS
            # =================================================

            fps_frames += 1


            fps_elapsed = (
                now - fps_timer
            )


            if fps_elapsed >= 0.5:

                fps = (
                    fps_frames
                    / fps_elapsed
                )

                fps_frames = 0
                fps_timer = now


            # =================================================
            # HUD
            # =================================================

            draw_hud(
                display=display,

                fps=fps,

                particle_mode=particle_mode,

                current_shape=current_shape,

                gesture_candidate=gesture_candidate,

                gesture_triggered=gesture_triggered,

                gesture_progress=gesture_progress,

                status_message=status_message,

                status_until=status_until,

                now=now
            )


            # =================================================
            # HIỂN THỊ
            # =================================================

            cv2.imshow(
                "Interactive Particles",
                display
            )


            key = (
                cv2.waitKey(1)
                & 0xFF
            )


            if key == ord("q"):
                break


    # ========================================================
    # BẮT LỖI
    # ========================================================

    except Exception as error:

        print(
            f"Lỗi chương trình: {error}"
        )


    # ========================================================
    # GIẢI PHÓNG
    # ========================================================

    finally:

        if cap is not None:
            cap.release()

        hand_tracker.close()

        cv2.destroyAllWindows()


# ============================================================
# CHẠY
# ============================================================

if __name__ == "__main__":
    main()