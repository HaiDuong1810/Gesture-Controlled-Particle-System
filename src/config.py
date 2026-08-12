# ============================================================
# CẤU HÌNH CHUNG
# ============================================================

WIDTH = 860
HEIGHT = 640

MP_WIDTH = 256
MP_HEIGHT = 192

MAX_PARTICLES = 4000
PARTICLE_RADIUS = 1

TARGET_SIZE = 320
CAMERA_DARKNESS = 0.45


# ============================================================
# 4 MẪU HÌNH
# ============================================================

SHAPE_PATHS = {
    1: "assets/shapes/heart.png",
    2: "assets/shapes/butterfly.png",
    3: "assets/shapes/tree.png",
    4: "assets/shapes/earth.png"
}

SHAPE_NAMES = {
    1: "HEART",
    2: "BUTTERFLY",
    3: "TREE",
    4: "EARTH"
}


# ============================================================
# TƯƠNG TÁC PARTICLE
# ============================================================

# 5 ngón -> đẩy
REPEL_RADIUS = 90
REPEL_FORCE = 3.0
SWIPE_FORCE = 0.08


# Pinch -> gom / kéo
GRAB_RADIUS = 180
GRAB_FORCE = 0.95
GRAB_FOLLOW_FORCE = 0.15
GRAB_CLOUD_RADIUS = 22


# Nhận diện pinch
PINCH_THRESHOLD = 0.42


# ============================================================
# TẠO / MORPH SHAPE
# ============================================================

SHAPE_FORCE = 0.008
COLOR_MORPH_SPEED = 0.08


# ============================================================
# CHUYỂN ĐỘNG
# ============================================================

DAMPING = 0.92
MAX_HAND_SPEED = 35


# ============================================================
# CỬ CHỈ CHỌN HÌNH
# ============================================================

GESTURE_HOLD_TIME = 0.7
GESTURE_MAX_SPEED = 16


# ============================================================
# BÚNG TAY -> BREAK
# ============================================================

SNAP_CLOSE_RATIO = 0.48
SNAP_RELEASE_RATIO = 0.85

SNAP_MAX_TIME = 0.50
SNAP_MIN_SPEED = 10
SNAP_COOLDOWN = 0.8

BREAK_FORCE_MIN = 3.0
BREAK_FORCE_MAX = 8.0


# ============================================================
# TRANSFORM SHAPE - MOVE
# ============================================================

# Làm mượt trung điểm giữa hai tay.
# Nhỏ hơn -> mượt hơn nhưng phản hồi chậm hơn.
TRANSFORM_MOVE_SMOOTHING = 0.35


# ============================================================
# TRANSFORM SHAPE - SCALE
# ============================================================

# Làm mượt khoảng cách giữa hai tay.
# Giúp shape không phồng/xẹp liên tục do landmark rung nhẹ.
TRANSFORM_SCALE_SMOOTHING = 0.25


# Giới hạn mức thay đổi scale trong mỗi frame.
TRANSFORM_SCALE_STEP_MIN = 0.97
TRANSFORM_SCALE_STEP_MAX = 1.03


# Giới hạn kích thước tổng thể của shape.
# 1.0 = kích thước gốc.
TRANSFORM_SCALE_MIN = 0.45
TRANSFORM_SCALE_MAX = 2.00


# ============================================================
# TRANSFORM SHAPE - ROTATE
# ============================================================

# Làm mượt góc giữa hai tay.
# Nhỏ hơn -> xoay mượt hơn nhưng phản hồi chậm hơn.
TRANSFORM_ROTATE_SMOOTHING = 0.25


# Giới hạn số độ shape được phép xoay trong mỗi frame.
# Giúp tránh shape giật mạnh khi landmark bị rung.
TRANSFORM_ROTATE_STEP_MAX = 4.0