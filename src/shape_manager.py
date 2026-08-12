import cv2
import numpy as np

from src.config import (
    WIDTH,
    HEIGHT,
    TARGET_SIZE,
    MAX_PARTICLES
)


# ============================================================
# ĐỌC ẢNH VÀ TẠO TARGET CHO PARTICLE
# ============================================================

def load_shape_targets(path, seed):

    # Đọc ảnh, giữ cả kênh alpha nếu có
    image = cv2.imread(
        path,
        cv2.IMREAD_UNCHANGED
    )

    if image is None:
        raise FileNotFoundError(
            f"Không đọc được ảnh: {path}"
        )


    # ========================================================
    # RESIZE ẢNH
    # ========================================================

    h, w = image.shape[:2]

    scale = (
        TARGET_SIZE
        / max(w, h)
    )

    new_w = max(
        1,
        int(w * scale)
    )

    new_h = max(
        1,
        int(h * scale)
    )

    image = cv2.resize(
        image,
        (new_w, new_h),
        interpolation=cv2.INTER_AREA
    )


    # ========================================================
    # TẠO MASK
    # ========================================================

    # PNG có nền trong suốt
    if (
        len(image.shape) == 3
        and image.shape[2] == 4
    ):

        bgr = image[:, :, :3]
        alpha = image[:, :, 3]

        mask = alpha > 50


    # Ảnh không có alpha
    elif (
        len(image.shape) == 3
        and image.shape[2] == 3
    ):

        bgr = image

        # Ước lượng màu nền từ 4 góc ảnh
        corners = np.array(
            [
                image[0, 0],
                image[0, -1],
                image[-1, 0],
                image[-1, -1]
            ],
            dtype=np.float32
        )

        background = np.median(
            corners,
            axis=0
        )

        difference = np.linalg.norm(
            image.astype(np.float32)
            - background,
            axis=2
        )

        mask = difference > 35


    else:

        raise ValueError(
            f"Định dạng ảnh không hỗ trợ: {path}"
        )


    # ========================================================
    # LẤY PIXEL THUỘC VỀ HÌNH
    # ========================================================

    ys, xs = np.where(mask)

    if len(xs) == 0:
        raise ValueError(
            f"Không tìm thấy vùng hình trong: {path}"
        )


    # ========================================================
    # CĂN HÌNH RA GIỮA CAMERA
    # ========================================================

    offset_x = (
        WIDTH - new_w
    ) // 2

    offset_y = (
        HEIGHT - new_h
    ) // 2


    # ========================================================
    # CHỌN ĐỦ SỐ PARTICLE
    # ========================================================

    rng = np.random.default_rng(
        seed
    )

    replace = (
        len(xs) < MAX_PARTICLES
    )

    selected = rng.choice(
        len(xs),
        size=MAX_PARTICLES,
        replace=replace
    )

    selected_x = xs[selected]
    selected_y = ys[selected]


    # ========================================================
    # TARGET POSITION
    # ========================================================

    positions = np.column_stack(
        (
            selected_x + offset_x,
            selected_y + offset_y
        )
    ).astype(np.float32)


    # ========================================================
    # TARGET COLOR
    # ========================================================

    colors = bgr[
        selected_y,
        selected_x
    ].astype(np.float32)


    return positions, colors