import cv2
import numpy as np
import random


WIDTH = 640
HEIGHT = 480

MAX_PARTICLES = 4000
PARTICLE_RADIUS = 1

IMAGE_PATH = "../assets/shapes/heart.png"


class Particle:
    def __init__(self, target_x, target_y, color):
        self.x = random.uniform(0, WIDTH)      # Vị trí ban đầu ngẫu nhiên
        self.y = random.uniform(0, HEIGHT)

        self.target_x = target_x               # Vị trí đích
        self.target_y = target_y

        self.color = color                     # Màu của hạt

    def update(self):
        self.x += (self.target_x - self.x) * 0.06   # Bay dần về đích
        self.y += (self.target_y - self.y) * 0.06

    def draw(self, canvas):
        cv2.circle(
            canvas,
            (int(self.x), int(self.y)),
            PARTICLE_RADIUS,
            self.color,
            -1,
            cv2.LINE_AA
        )


image = cv2.imread(IMAGE_PATH, cv2.IMREAD_UNCHANGED)

if image is None:
    print("Không đọc được ảnh!")
    exit()

# Thu nhỏ ảnh để vừa màn hình
target_size = 320
h, w = image.shape[:2]

scale = target_size / max(w, h)
new_w = int(w * scale)
new_h = int(h * scale)

image = cv2.resize(
    image,
    (new_w, new_h),
    interpolation=cv2.INTER_AREA
)

points = []

# Nếu ảnh có kênh alpha (PNG trong suốt)
if len(image.shape) == 3 and image.shape[2] == 4:
    for y in range(new_h):
        for x in range(new_w):
            b, g, r, a = image[y, x]

            if a > 50:
                points.append((x, y, (int(b), int(g), int(r))))

# Nếu ảnh chỉ có 3 kênh màu
elif len(image.shape) == 3 and image.shape[2] == 3:
    for y in range(new_h):
        for x in range(new_w):
            b, g, r = image[y, x]

            # Bỏ nền đen nếu có
            if not (b < 10 and g < 10 and r < 10):
                points.append((x, y, (int(b), int(g), int(r))))

# Giới hạn số particle
if len(points) > MAX_PARTICLES:
    points = random.sample(points, MAX_PARTICLES)

offset_x = (WIDTH - new_w) // 2
offset_y = (HEIGHT - new_h) // 2

# Tạo danh sách particle
particles = []

for x, y, color in points:
    target_x = x + offset_x
    target_y = y + offset_y
    particles.append(Particle(target_x, target_y, color))


while True:
    canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

    for particle in particles:
        particle.update()
        particle.draw(canvas)

    cv2.putText(
        canvas,
        f"Particles: {len(particles)}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.imshow("Particle Shape Test", canvas)

    key = cv2.waitKey(16) & 0xFF   # ~60 FPS

    if key == ord("q"):
        break

cv2.destroyAllWindows()