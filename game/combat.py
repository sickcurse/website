# Combat logic pulled out of GameRoot: attack timing, hitboxes,
# hit detection, and the enemy contact-damage cooldown.


def rects_overlap(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


class Combat:
    def __init__(self):
        # Attack state
        self.attack_timer = 0.0
        self.attack_duration = 0.2
        self.attack_w = 30.0
        self.attack_h = 20.0
        self.attack_has_hit = False

        # Enemy contact damage
        self.contact_cooldown = 0.0
        self.contact_cooldown_time = 0.6

    # --- STATE ---
    def start_attack(self):
        if self.attack_timer <= 0:
            self.attack_timer = self.attack_duration
            self.attack_has_hit = False

    def update_timers(self, dt):
        if self.attack_timer > 0:
            self.attack_timer = max(0.0, self.attack_timer - dt)
        if self.contact_cooldown > 0:
            self.contact_cooldown = max(0.0, self.contact_cooldown - dt)

    @property
    def attacking(self):
        return self.attack_timer > 0

    # --- HITBOXES (all return (x, y, w, h)) ---
    def player_hitbox(self, x, y, w, h):
        return (x, y, w, h)

    def enemy_hitbox(self, x, y, w, h):
        return (x, y, w, h)

    def attack_hitbox(self, px, py, pw, ph, facing):
        # None while not attacking, so callers can `if attack_rect:`
        if not self.attacking:
            return None
        if facing >= 0:
            ax = px + pw
        else:
            ax = px - self.attack_w
        ay = py + ph / 2 - self.attack_h / 2
        return (ax, ay, self.attack_w, self.attack_h)

    # --- HIT CHECKS ---
    def try_attack_enemy(self, attack_rect, enemy_rect):
        # One hit per swing: attack_has_hit latches until the next start_attack.
        if attack_rect is None or self.attack_has_hit:
            return False
        if rects_overlap(attack_rect, enemy_rect):
            self.attack_has_hit = True
            return True
        return False

    def try_enemy_contact_damage(self, player_rect, enemy_rect):
        if self.contact_cooldown > 0:
            return False
        if rects_overlap(player_rect, enemy_rect):
            self.contact_cooldown = self.contact_cooldown_time
            return True
        return False
