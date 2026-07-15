# Simple hit-spark particles.
import random
from scene import fill, rect


class Sparks:
    def __init__(self):
        self.particles = []

    def spawn(self, x, y, count=8):
        for _ in range(count):
            self.particles.append({
                'x': x,
                'y': y,
                'vx': random.uniform(-120, 120),
                'vy': random.uniform(20, 180),
                'life': random.uniform(0.2, 0.45),
                'size': random.uniform(3, 6),
            })

    def update_and_draw(self, dt):
        gravity = -400
        alive = []
        for p in self.particles:
            p['life'] -= dt
            if p['life'] <= 0:
                continue
            p['vy'] += gravity * dt
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt

            fill(1, 0.9, 0.4, min(1.0, p['life'] * 3))
            rect(p['x'], p['y'], p['size'], p['size'])
            alive.append(p)
        self.particles = alive
