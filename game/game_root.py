from scene import *
from effects import Sparks
from controls import Controls
from combat import Combat
import ui


class GameRoot(Scene):
    # --- Backwards-compatible "attack_*" + "contact_cooldown" fields ---
    # This lets your existing Controls keep working even after Combat is added.
    @property
    def attack_timer(self):
        return self.combat.attack_timer

    @attack_timer.setter
    def attack_timer(self, v):
        self.combat.attack_timer = float(v)

    @property
    def attack_duration(self):
        return self.combat.attack_duration

    @attack_duration.setter
    def attack_duration(self, v):
        self.combat.attack_duration = float(v)

    @property
    def attack_w(self):
        return self.combat.attack_w

    @attack_w.setter
    def attack_w(self, v):
        self.combat.attack_w = float(v)

    @property
    def attack_h(self):
        return self.combat.attack_h

    @attack_h.setter
    def attack_h(self, v):
        self.combat.attack_h = float(v)

    @property
    def attack_has_hit(self):
        return self.combat.attack_has_hit

    @attack_has_hit.setter
    def attack_has_hit(self, v):
        self.combat.attack_has_hit = bool(v)

    @property
    def contact_cooldown(self):
        return self.combat.contact_cooldown

    @contact_cooldown.setter
    def contact_cooldown(self, v):
        self.combat.contact_cooldown = float(v)

    def setup(self):
        # --- PLAYER ---
        self.player_width = 40
        self.player_height = 60
        self.player_x = 100
        self.player_y = 0
        self.player_vx = 0
        self.player_vy = 0
        self.acceleration = 0.8
        self.friction = 0.85
        self.max_speed = 5
        self.gravity = -0.6
        self.on_ground = False
        self.jump_power = 12
        self.facing = 1

        self.player_has_moved = False
        self.player_damage = 0.5
        self.player_max_hp = 10
        self.player_hp = self.player_max_hp

        # --- ENEMY ---
        self.enemy_width = 50
        self.enemy_height = 60
        self.enemy_x = 500
        self.enemy_y = 0
        self.enemy_speed = 1.2
        self.enemy_max_hp = 3
        self.enemy_hp = self.enemy_max_hp
        self.enemy_damage = 1
        self.enemy_knockback_force = 4
        self.player_recoil_force = 2

        # --- COMBAT (NEW) ---
        self.combat = Combat()

        # If you want different default attack values, set them here:
        self.combat.attack_duration = 0.2
        self.combat.attack_w = 30
        self.combat.attack_h = 20
        self.combat.contact_cooldown_time = 0.6

        # --- CONTROLS ---
        self.holding_left = False
        self.holding_right = False
        self.controls = Controls(btn_size=70, btn_spacing=20)

        # --- SPARKS ---
        self.sparks = Sparks()

        # --- SPRITES ---
        self.player_sprite = ShapeNode(
            ui.Path.rect(0, 0, self.player_width, self.player_height),
            fill_color=(0.2, 0.6, 1),
            stroke_color='clear',
            parent=self
        )
        self.player_sprite.anchor_point = (0, 0)

        self.enemy_sprite = ShapeNode(
            ui.Path.rect(0, 0, self.enemy_width, self.enemy_height),
            fill_color=(1, 0.2, 0.2),
            stroke_color='clear',
            parent=self
        )
        self.enemy_sprite.anchor_point = (0, 0)

    def clamp_player(self):
        if self.player_x < 0:
            self.player_x = 0
            self.player_vx = 0
        elif self.player_x > self.size.w - self.player_width:
            self.player_x = self.size.w - self.player_width
            self.player_vx = 0

    def restart_game(self):
        self.setup()

    # Optional helper (if you ever want Controls to call this directly)
    def start_attack(self):
        self.combat.start_attack()

    def update(self):
        background(0.1, 0.1, 0.1)
        dt = 1 / 60

        # --- CONTROLS DRAW/LAYOUT ---
        self.controls.layout(self)
        self.controls.draw()
        ground_y = self.controls.jump_btn.y + self.controls.jump_btn.h + 10

        # --- COMBAT TIMERS (NEW) ---
        self.combat.update_timers(dt)

        # --- PLAYER MOVEMENT ---
        if self.holding_left:
            self.player_vx -= self.acceleration
            self.facing = -1
            self.player_has_moved = True
        elif self.holding_right:
            self.player_vx += self.acceleration
            self.facing = 1
            self.player_has_moved = True
        else:
            self.player_vx *= self.friction

        self.player_vx = max(-self.max_speed, min(self.player_vx, self.max_speed))
        self.player_x += self.player_vx

        # --- GRAVITY ---
        if not self.on_ground:
            self.player_vy += self.gravity
        self.player_y += self.player_vy

        if self.player_y <= ground_y:
            self.player_y = ground_y
            self.player_vy = 0
            self.on_ground = True
        else:
            self.on_ground = False

        self.clamp_player()

        # --- SPRITES ---
        self.player_sprite.position = (self.player_x, self.player_y)
        self.player_sprite.x_scale = self.facing

        self.enemy_y = ground_y
        self.enemy_sprite.position = (self.enemy_x, self.enemy_y)

        # --- ENEMY FOLLOW & COLLISION ---
        if self.player_has_moved:
            direction = 1 if self.player_x > self.enemy_x else -1
            proposed_x = self.enemy_x + direction * self.enemy_speed

            # prevent enemy passing through player
            if proposed_x + self.enemy_width < self.player_x or proposed_x > self.player_x + self.player_width:
                self.enemy_x = proposed_x

        # --- HITBOXES (VISIBLE) ---
        player_rect = self.combat.player_hitbox(
            self.player_x, self.player_y, self.player_width, self.player_height
        )
        enemy_rect = self.combat.enemy_hitbox(
            self.enemy_x, self.enemy_y, self.enemy_width, self.enemy_height
        )
        attack_rect = self.combat.attack_hitbox(
            self.player_x, self.player_y, self.player_width, self.player_height, self.facing
        )

        # Player hitbox (blue, debug)
        fill(0.2, 0.6, 1.0, 0.22)
        rect(*player_rect)

        # Enemy hitbox (red, debug)
        fill(1, 0.3, 0.3, 0.35)
        rect(*enemy_rect)

        # Attack box (yellow, debug)
        if attack_rect:
            fill(1, 0.8, 0.2, 0.55)
            rect(*attack_rect)

        # --- PLAYER ATTACK -> ENEMY ---
        if self.combat.try_attack_enemy(attack_rect, enemy_rect):
            self.enemy_hp -= self.player_damage

            direction = 1 if self.player_x < self.enemy_x else -1
            self.enemy_x += self.enemy_knockback_force * direction
            self.player_x -= self.player_recoil_force * direction
            self.clamp_player()

            self.sparks.spawn(
                self.enemy_x + self.enemy_width / 2,
                self.enemy_y + self.enemy_height / 2
            )

        # --- ENEMY CONTACT DAMAGE -> PLAYER ---
        if self.combat.try_enemy_contact_damage(player_rect, enemy_rect):
            self.player_hp -= self.enemy_damage
            self.sparks.spawn(
                self.player_x + self.player_width / 2,
                self.player_y + self.player_height / 2
            )

        # --- SPARKS ---
        self.sparks.update_and_draw(dt)

        # --- HEALTH BARS ---
        fill(0.2, 0.2, 0.2)
        rect(20, self.size.h - 30, 200, 10)
        fill(0.2, 1, 0.2)
        rect(20, self.size.h - 30, 200 * (self.player_hp / self.player_max_hp), 10)

        fill(0.2, 0.2, 0.2)
        rect(self.enemy_x, self.enemy_y + self.enemy_height + 8, 40, 6)
        fill(1, 0.3, 0.3)
        rect(self.enemy_x, self.enemy_y + self.enemy_height + 8,
             40 * (self.enemy_hp / self.enemy_max_hp), 6)

        # --- RESTART IF ENEMY DIES ---
        if self.enemy_hp <= 0:
            self.restart_game()

    # controls handle touches now
    def touch_began(self, touch):
        self.controls.touch_began(self, touch)

    def touch_ended(self, touch):
        self.controls.touch_ended(self, touch)


if __name__ == '__main__':
    run(GameRoot(), PORTRAIT, show_fps=True)
