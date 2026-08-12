import numpy as np
import math

from src.config import (
    WIDTH,
    HEIGHT,
    PARTICLE_RADIUS,

    REPEL_RADIUS,
    REPEL_FORCE,
    SWIPE_FORCE,

    GRAB_RADIUS,
    GRAB_FORCE,
    GRAB_FOLLOW_FORCE,
    GRAB_CLOUD_RADIUS,

    SHAPE_FORCE,
    COLOR_MORPH_SPEED,

    DAMPING,

    BREAK_FORCE_MIN,
    BREAK_FORCE_MAX,

    TRANSFORM_SCALE_MIN,
    TRANSFORM_SCALE_MAX
)


# ============================================================
# RANDOM GENERATOR
# ============================================================

RNG = np.random.default_rng()


# ============================================================
# PARTICLE SYSTEM
# ============================================================

class ParticleSystem:

    def __init__(
        self,
        initial_targets,
        initial_colors
    ):

        count = len(initial_targets)


        # ====================================================
        # VỊ TRÍ BAN ĐẦU
        # ====================================================

        self.positions = np.empty(
            (count, 2),
            dtype=np.float32
        )

        self.positions[:, 0] = RNG.uniform(
            0,
            WIDTH,
            count
        )

        self.positions[:, 1] = RNG.uniform(
            0,
            HEIGHT,
            count
        )


        # ====================================================
        # VẬN TỐC
        # ====================================================

        self.velocities = np.zeros(
            (count, 2),
            dtype=np.float32
        )


        # ====================================================
        # TARGET
        # ====================================================

        self.targets = (
            initial_targets
            .astype(np.float32)
            .copy()
        )


        # ====================================================
        # MÀU
        # ====================================================

        self.colors = (
            initial_colors
            .astype(np.float32)
            .copy()
        )

        self.target_colors = (
            initial_colors
            .astype(np.float32)
            .copy()
        )


        # ====================================================
        # SCALE HIỆN TẠI
        # ====================================================

        self.current_scale = 1.0


        # ====================================================
        # OFFSET KHI GRAB
        # ====================================================

        angles = RNG.uniform(
            0,
            2 * math.pi,
            count
        )

        radii = (
            GRAB_CLOUD_RADIUS
            * np.sqrt(
                RNG.random(count)
            )
        )

        self.grab_offsets = np.column_stack(
            (
                np.cos(angles) * radii,
                np.sin(angles) * radii
            )
        ).astype(np.float32)


    # ========================================================
    # ĐỔI TARGET HÌNH
    # ========================================================

    def set_target(
        self,
        new_targets,
        new_colors
    ):

        self.targets[:] = (
            new_targets
        )

        self.target_colors[:] = (
            new_colors
        )


        # Shape mới trở về kích thước gốc
        self.current_scale = 1.0


        # Giảm quán tính của shape trước
        self.velocities *= 0.45


    # ========================================================
    # DI CHUYỂN TOÀN BỘ SHAPE
    # ========================================================

    def move_shape(
        self,
        dx,
        dy
    ):

        # ====================================================
        # BIÊN HIỆN TẠI CỦA SHAPE
        # ====================================================

        min_x = float(
            np.min(
                self.targets[:, 0]
            )
        )

        max_x = float(
            np.max(
                self.targets[:, 0]
            )
        )

        min_y = float(
            np.min(
                self.targets[:, 1]
            )
        )

        max_y = float(
            np.max(
                self.targets[:, 1]
            )
        )


        # ====================================================
        # GIỚI HẠN DỊCH THEO X
        # ====================================================

        dx = float(
            np.clip(
                dx,
                -min_x,
                (WIDTH - 1) - max_x
            )
        )


        # ====================================================
        # GIỚI HẠN DỊCH THEO Y
        # ====================================================

        dy = float(
            np.clip(
                dy,
                -min_y,
                (HEIGHT - 1) - max_y
            )
        )


        # ====================================================
        # DỊCH TOÀN BỘ TARGET
        # ====================================================

        self.targets[:, 0] += dx
        self.targets[:, 1] += dy


    # ========================================================
    # SCALE TOÀN BỘ SHAPE
    # ========================================================

    def scale_shape(
        self,
        scale_factor,
        center_x,
        center_y
    ):

        # ====================================================
        # SCALE MỚI
        # ====================================================

        requested_scale = (
            self.current_scale
            * scale_factor
        )


        # ====================================================
        # GIỚI HẠN SCALE TỔNG
        # ====================================================

        new_scale = float(
            np.clip(
                requested_scale,
                TRANSFORM_SCALE_MIN,
                TRANSFORM_SCALE_MAX
            )
        )


        if self.current_scale <= 0:
            self.current_scale = 1.0


        # ====================================================
        # SCALE THỰC SỰ ĐƯỢC ÁP DỤNG
        # ====================================================

        actual_factor = (
            new_scale
            / self.current_scale
        )


        if abs(
            actual_factor - 1.0
        ) < 0.0001:

            return self.current_scale


        # ====================================================
        # TÂM SCALE
        # ====================================================

        center = np.array(
            [
                center_x,
                center_y
            ],
            dtype=np.float32
        )


        # ====================================================
        # VECTOR TỪ TÂM ĐẾN PARTICLE TARGET
        # ====================================================

        relative = (
            self.targets
            - center
        )


        # ====================================================
        # SCALE
        # ====================================================

        scaled_targets = (
            center
            + relative * actual_factor
        )


        # ====================================================
        # GIỮ SHAPE TRONG MÀN HÌNH
        # ====================================================

        min_x = float(
            np.min(
                scaled_targets[:, 0]
            )
        )

        max_x = float(
            np.max(
                scaled_targets[:, 0]
            )
        )

        min_y = float(
            np.min(
                scaled_targets[:, 1]
            )
        )

        max_y = float(
            np.max(
                scaled_targets[:, 1]
            )
        )


        shift_x = 0.0
        shift_y = 0.0


        if min_x < 0:

            shift_x = (
                -min_x
            )


        elif max_x > WIDTH - 1:

            shift_x = (
                (WIDTH - 1)
                - max_x
            )


        if min_y < 0:

            shift_y = (
                -min_y
            )


        elif max_y > HEIGHT - 1:

            shift_y = (
                (HEIGHT - 1)
                - max_y
            )


        # ====================================================
        # DỊCH CẢ SHAPE NẾU SCALE LÀM VƯỢT BIÊN
        # ====================================================

        scaled_targets[:, 0] += (
            shift_x
        )

        scaled_targets[:, 1] += (
            shift_y
        )


        # ====================================================
        # LƯU TARGET MỚI
        # ====================================================

        self.targets[:] = (
            scaled_targets
        )


        # ====================================================
        # LƯU SCALE HIỆN TẠI
        # ====================================================

        self.current_scale = (
            new_scale
        )


        return self.current_scale


    # ========================================================
    # ROTATE TOÀN BỘ SHAPE
    # ========================================================

    def rotate_shape(
        self,
        angle_degrees,
        center_x,
        center_y
    ):

        # ====================================================
        # NẾU GÓC QUÁ NHỎ THÌ KHÔNG CẦN XOAY
        # ====================================================

        if abs(angle_degrees) < 0.0001:
            return


        # ====================================================
        # ĐỘ -> RADIAN
        # ====================================================

        angle_radians = math.radians(
            angle_degrees
        )


        cos_angle = math.cos(
            angle_radians
        )

        sin_angle = math.sin(
            angle_radians
        )


        # ====================================================
        # TÂM XOAY
        # ====================================================

        center = np.array(
            [
                center_x,
                center_y
            ],
            dtype=np.float32
        )


        # ====================================================
        # VECTOR TỪ TÂM XOAY ĐẾN TARGET
        # ====================================================

        relative = (
            self.targets
            - center
        )


        x = relative[:, 0]
        y = relative[:, 1]


        # ====================================================
        # CÔNG THỨC XOAY 2D
        #
        # Vì trục Y của OpenCV hướng xuống dưới nên
        # góc dương sẽ tương ứng với chiều xoay trên màn hình.
        # ====================================================

        rotated_x = (
            x * cos_angle
            - y * sin_angle
        )

        rotated_y = (
            x * sin_angle
            + y * cos_angle
        )


        rotated_targets = np.column_stack(
            (
                rotated_x,
                rotated_y
            )
        ).astype(
            np.float32
        )


        # ====================================================
        # ĐƯA TRỞ LẠI TỌA ĐỘ MÀN HÌNH
        # ====================================================

        rotated_targets += (
            center
        )


        # ====================================================
        # KIỂM TRA BIÊN SAU KHI XOAY
        # ====================================================

        min_x = float(
            np.min(
                rotated_targets[:, 0]
            )
        )

        max_x = float(
            np.max(
                rotated_targets[:, 0]
            )
        )

        min_y = float(
            np.min(
                rotated_targets[:, 1]
            )
        )

        max_y = float(
            np.max(
                rotated_targets[:, 1]
            )
        )


        shift_x = 0.0
        shift_y = 0.0


        # ====================================================
        # BIÊN TRÁI / PHẢI
        # ====================================================

        if min_x < 0:

            shift_x = (
                -min_x
            )


        elif max_x > WIDTH - 1:

            shift_x = (
                (WIDTH - 1)
                - max_x
            )


        # ====================================================
        # BIÊN TRÊN / DƯỚI
        # ====================================================

        if min_y < 0:

            shift_y = (
                -min_y
            )


        elif max_y > HEIGHT - 1:

            shift_y = (
                (HEIGHT - 1)
                - max_y
            )


        # ====================================================
        # KHÔNG CLIP TỪNG PARTICLE
        #
        # Dịch cả shape để giữ nguyên hình dạng.
        # ====================================================

        rotated_targets[:, 0] += (
            shift_x
        )

        rotated_targets[:, 1] += (
            shift_y
        )


        # ====================================================
        # LƯU TARGET SAU KHI XOAY
        # ====================================================

        self.targets[:] = (
            rotated_targets
        )


    # ========================================================
    # UPDATE TOÀN BỘ PARTICLE
    # ========================================================

    def update(
        self,
        hand_controls,
        particle_mode
    ):

        pos = self.positions
        vel = self.velocities


        # ====================================================
        # SHAPE MODE
        # ====================================================

        if particle_mode == "SHAPE":

            vel += (
                self.targets - pos
            ) * SHAPE_FORCE


            self.colors += (
                self.target_colors
                - self.colors
            ) * COLOR_MORPH_SPEED


        # ====================================================
        # TƯƠNG TÁC VỚI TỪNG BÀN TAY
        # ====================================================

        for control in hand_controls:

            mode = control["mode"]

            hand_x = float(
                control["x"]
            )

            hand_y = float(
                control["y"]
            )

            hand_vx = float(
                control["vx"]
            )

            hand_vy = float(
                control["vy"]
            )


            # =================================================
            # REPEL
            # =================================================

            if mode == "REPEL":

                dx = (
                    pos[:, 0]
                    - hand_x
                )

                dy = (
                    pos[:, 1]
                    - hand_y
                )


                distance_sq = (
                    dx * dx
                    + dy * dy
                )


                mask = (
                    (distance_sq > 1.0)
                    &
                    (
                        distance_sq
                        <
                        REPEL_RADIUS
                        * REPEL_RADIUS
                    )
                )


                if np.any(mask):

                    distance = np.sqrt(
                        distance_sq[mask]
                    )


                    strength = (
                        REPEL_RADIUS
                        - distance
                    ) / REPEL_RADIUS


                    vel[mask, 0] += (
                        (
                            dx[mask]
                            / distance
                        )
                        * strength
                        * REPEL_FORCE

                        +

                        hand_vx
                        * strength
                        * SWIPE_FORCE
                    )


                    vel[mask, 1] += (
                        (
                            dy[mask]
                            / distance
                        )
                        * strength
                        * REPEL_FORCE

                        +

                        hand_vy
                        * strength
                        * SWIPE_FORCE
                    )


            # =================================================
            # GRAB
            # =================================================

            elif mode == "GRAB":

                target_x = (
                    hand_x
                    + self.grab_offsets[:, 0]
                )

                target_y = (
                    hand_y
                    + self.grab_offsets[:, 1]
                )


                dx = (
                    target_x
                    - pos[:, 0]
                )

                dy = (
                    target_y
                    - pos[:, 1]
                )


                distance_sq = (
                    dx * dx
                    + dy * dy
                )


                mask = (
                    (distance_sq > 1.0)
                    &
                    (
                        distance_sq
                        <
                        GRAB_RADIUS
                        * GRAB_RADIUS
                    )
                )


                if np.any(mask):

                    distance = np.sqrt(
                        distance_sq[mask]
                    )


                    strength = (
                        GRAB_RADIUS
                        - distance
                    ) / GRAB_RADIUS


                    strength = (
                        0.25
                        + strength * 0.75
                    )


                    vel[mask, 0] += (
                        (
                            dx[mask]
                            / distance
                        )
                        * strength
                        * GRAB_FORCE

                        +

                        hand_vx
                        * strength
                        * GRAB_FOLLOW_FORCE
                    )


                    vel[mask, 1] += (
                        (
                            dy[mask]
                            / distance
                        )
                        * strength
                        * GRAB_FORCE

                        +

                        hand_vy
                        * strength
                        * GRAB_FOLLOW_FORCE
                    )


        # ====================================================
        # DAMPING
        # ====================================================

        vel *= DAMPING


        # ====================================================
        # CẬP NHẬT VỊ TRÍ
        # ====================================================

        pos += vel


        # ====================================================
        # GIỮ PARTICLE TRONG MÀN HÌNH
        # ====================================================

        left = (
            pos[:, 0] < 0
        )

        right = (
            pos[:, 0] >= WIDTH
        )

        top = (
            pos[:, 1] < 0
        )

        bottom = (
            pos[:, 1] >= HEIGHT
        )


        if np.any(left):

            pos[left, 0] = 0
            vel[left, 0] *= -0.5


        if np.any(right):

            pos[right, 0] = (
                WIDTH - 1
            )

            vel[right, 0] *= -0.5


        if np.any(top):

            pos[top, 1] = 0
            vel[top, 1] *= -0.5


        if np.any(bottom):

            pos[bottom, 1] = (
                HEIGHT - 1
            )

            vel[bottom, 1] *= -0.5


    # ========================================================
    # BREAK TOÀN BỘ PARTICLE
    # ========================================================

    def break_apart(
        self,
        break_x,
        break_y
    ):

        dx = (
            self.positions[:, 0]
            - break_x
        )

        dy = (
            self.positions[:, 1]
            - break_y
        )


        distance = np.sqrt(
            dx * dx
            + dy * dy
        )


        safe_distance = np.where(
            distance < 1.0,
            1.0,
            distance
        )


        nx = (
            dx
            / safe_distance
        )

        ny = (
            dy
            / safe_distance
        )


        # ====================================================
        # PARTICLE ĐÚNG TẠI TÂM BREAK
        # ====================================================

        zero_mask = (
            distance < 1.0
        )


        if np.any(zero_mask):

            angles = RNG.uniform(
                0,
                2 * math.pi,
                np.count_nonzero(
                    zero_mask
                )
            )

            nx[zero_mask] = (
                np.cos(angles)
            )

            ny[zero_mask] = (
                np.sin(angles)
            )


        # ====================================================
        # LỰC PHÁ HÌNH
        # ====================================================

        force = RNG.uniform(
            BREAK_FORCE_MIN,
            BREAK_FORCE_MAX,
            len(self.positions)
        )


        noise = RNG.uniform(
            -2,
            2,
            size=(
                len(self.positions),
                2
            )
        ).astype(np.float32)


        self.velocities[:, 0] += (
            nx * force
        )

        self.velocities[:, 1] += (
            ny * force
        )

        self.velocities += (
            noise
        )


    # ========================================================
    # VẼ TOÀN BỘ PARTICLE
    # ========================================================

    def draw(
        self,
        frame
    ):

        # ====================================================
        # TỌA ĐỘ PIXEL
        # ====================================================

        xs = np.rint(
            self.positions[:, 0]
        ).astype(np.int32)


        ys = np.rint(
            self.positions[:, 1]
        ).astype(np.int32)


        xs = np.clip(
            xs,
            0,
            WIDTH - 1
        )


        ys = np.clip(
            ys,
            0,
            HEIGHT - 1
        )


        # ====================================================
        # MÀU PARTICLE
        # ====================================================

        colors = np.clip(
            self.colors,
            0,
            255
        ).astype(np.uint8)


        # ====================================================
        # VẼ TÂM PARTICLE
        # ====================================================

        frame[
            ys,
            xs
        ] = colors


        # ====================================================
        # VẼ THÊM 4 PIXEL XUNG QUANH
        # ====================================================

        if PARTICLE_RADIUS >= 1:

            offsets = (
                (-1, 0),
                (1, 0),
                (0, -1),
                (0, 1)
            )


            for ox, oy in offsets:

                xx = np.clip(
                    xs + ox,
                    0,
                    WIDTH - 1
                )


                yy = np.clip(
                    ys + oy,
                    0,
                    HEIGHT - 1
                )


                frame[
                    yy,
                    xx
                ] = colors