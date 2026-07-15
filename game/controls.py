# On-screen touch controls: left/right on the bottom-left,
# jump + attack on the bottom-right.
from scene import fill, stroke, rect, text


class Button:
    def __init__(self, label):
        self.label = label
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0

    def contains(self, point):
        return (self.x <= point.x <= self.x + self.w and
                self.y <= point.y <= self.y + self.h)

    def draw(self):
        fill(1, 1, 1, 0.15)
        stroke(1, 1, 1, 0.4)
        rect(self.x, self.y, self.w, self.h)
        text(self.label, font_size=24,
             x=self.x + self.w / 2, y=self.y + self.h / 2)


class Controls:
    def __init__(self, btn_size=70, btn_spacing=20):
        self.btn_size = btn_size
        self.btn_spacing = btn_spacing

        self.left_btn = Button('<')
        self.right_btn = Button('>')
        self.jump_btn = Button('^')
        self.attack_btn = Button('x')
        self.buttons = [self.left_btn, self.right_btn,
                        self.jump_btn, self.attack_btn]

        # touch_id -> button, so touch_ended releases the right hold
        self.active_touches = {}

    def layout(self, scene):
        s = self.btn_size
        m = self.btn_spacing

        self.left_btn.x, self.left_btn.y = m, m
        self.right_btn.x, self.right_btn.y = m + s + m, m
        self.attack_btn.x, self.attack_btn.y = scene.size.w - m - s, m
        self.jump_btn.x, self.jump_btn.y = scene.size.w - m - s - m - s, m

        for b in self.buttons:
            b.w = b.h = s

    def draw(self):
        for b in self.buttons:
            b.draw()

    def touch_began(self, scene, touch):
        for b in self.buttons:
            if b.contains(touch.location):
                self.active_touches[touch.touch_id] = b
                if b is self.left_btn:
                    scene.holding_left = True
                elif b is self.right_btn:
                    scene.holding_right = True
                elif b is self.jump_btn:
                    if scene.on_ground:
                        scene.player_vy = scene.jump_power
                        scene.on_ground = False
                elif b is self.attack_btn:
                    if scene.attack_timer <= 0:
                        scene.attack_timer = scene.attack_duration
                        scene.attack_has_hit = False
                return

    def touch_ended(self, scene, touch):
        b = self.active_touches.pop(touch.touch_id, None)
        if b is self.left_btn:
            scene.holding_left = False
        elif b is self.right_btn:
            scene.holding_right = False
