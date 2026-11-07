import math
import random
import pygame
import config

_CACHE = {}


class ScreenShake:
    """Clase para manejar el efecto de temblor de cámara."""
    def __init__(self):
        self.intensidad = 0
        self.duracion = 0.0

    def iniciar(self, intensidad, duracion):
        self.intensidad = intensidad
        self.duracion = duracion

    def actualizar(self, dt):
        if self.duracion > 0:
            self.duracion -= dt
        else:
            self.intensidad = 0
            self.duracion = 0.0

    def obtener_offset(self):
        # Genera coordenadas aleatorias basadas en la intensidad
        if self.intensidad > 0:
            ox = random.randint(-self.intensidad, self.intensidad)
            oy = random.randint(-self.intensidad, self.intensidad)
            return ox, oy
        return 0, 0


class GlowCache:
    """Caché estático de superficies de iluminación radial aditiva para 60 FPS en WebAssembly."""
    @staticmethod
    def get(radius, color, intensity=1.0):
        radius = max(2, int(radius))
        r_c = min(255, max(0, int(color[0] * intensity)))
        g_c = min(255, max(0, int(color[1] * intensity)))
        b_c = min(255, max(0, int(color[2] * intensity)))
        key = ("glow", radius, (r_c, g_c, b_c))
        if key not in _CACHE:
            size = radius * 2
            surf = pygame.Surface((size, size))
            surf.fill((0, 0, 0))
            steps = max(6, min(24, radius // 2))
            for i in range(steps, 0, -1):
                ratio = i / steps
                falloff = (1.0 - ratio) ** 2.0
                cr = min(255, int(r_c * falloff))
                cg = min(255, int(g_c * falloff))
                cb = min(255, int(b_c * falloff))
                rad = max(1, int(radius * ratio))
                pygame.draw.circle(surf, (cr, cg, cb), (radius, radius), rad)
            _CACHE[key] = surf
        return _CACHE[key]

    @staticmethod
    def blit(surface, x, y, radius, color, intensity=1.0):
        glow_surf = GlowCache.get(radius, color, intensity)
        r = glow_surf.get_width() // 2
        surface.blit(glow_surf, (int(x) - r, int(y) - r), special_flags=pygame.BLEND_RGB_ADD)


class GradientCache:
    """Caché estático de fondos con degradado vertical y viñetas pre-calculadas."""
    @staticmethod
    def get_vertical(width, height, top_color, bottom_color, vignette=True):
        key = ("grad_v", width, height, top_color, bottom_color, vignette)
        if key not in _CACHE:
            surf = pygame.Surface((width, height))
            for y in range(height):
                t = y / max(1, height - 1)
                r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
                g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
                b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
                pygame.draw.line(surf, (r, g, b), (0, y), (width, y))
            if vignette:
                vig = GradientCache.get_vignette(width, height)
                surf.blit(vig, (0, 0))
            _CACHE[key] = surf
        return _CACHE[key]

    @staticmethod
    def get_vignette(width, height, strength=130):
        key = ("vignette", width, height, strength)
        if key not in _CACHE:
            surf = pygame.Surface((width, height), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 0))
            steps = 22
            for i in range(steps):
                t = (i + 1) / steps
                alpha = int((t ** 2.2) * (strength / 6))
                pad_x = int((1.0 - t) * (width * 0.22))
                pad_y = int((1.0 - t) * (height * 0.22))
                rect = pygame.Rect(pad_x, pad_y, width - pad_x * 2, height - pad_y * 2)
                thickness = max(8, int(max(width, height) * 0.025))
                pygame.draw.rect(surf, (0, 0, 0, alpha), rect, thickness, border_radius=45)
            _CACHE[key] = surf
        return _CACHE[key]


class HeartRenderer:
    """Renderizador matemático paramétrico de corazones con pre-cálculo y caché."""
    @staticmethod
    def get_points(cx, cy, scale):
        pts = []
        steps = 36
        for i in range(steps):
            t = (i / steps) * math.tau
            x = 16 * (math.sin(t) ** 3)
            y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
            pts.append((cx + x * scale, cy + y * scale))
        return pts

    @staticmethod
    def get_cached_heart(scale, color, alpha=255, width=0):
        scale_key = round(scale, 2)
        key = ("heart", scale_key, color, alpha, width)
        if key not in _CACHE:
            size = max(12, int(scale_key * 38) + 8)
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pts = HeartRenderer.get_points(size // 2, size // 2, scale_key)
            c = (color[0], color[1], color[2], alpha)
            pygame.draw.polygon(surf, c, pts, width)
            _CACHE[key] = surf
        return _CACHE[key]

    @staticmethod
    def draw(surface, cx, cy, scale, color, alpha=255, width=0, glow=True):
        if glow:
            GlowCache.blit(surface, cx, cy, int(scale * 24), color, intensity=0.45 * (alpha / 255.0))
        surf = HeartRenderer.get_cached_heart(scale, color, alpha, width)
        surface.blit(surf, (int(cx) - surf.get_width() // 2, int(cy) - surf.get_height() // 2))


class TrailRenderer:
    """Buffer circular sin asignaciones dinámicas para estelas de movimiento."""
    def __init__(self, max_points=12):
        self.max_points = max_points
        self.points = []

    def add(self, x, y):
        if not self.points or math.hypot(x - self.points[-1][0], y - self.points[-1][1]) > 2.0:
            self.points.append((float(x), float(y)))
            if len(self.points) > self.max_points:
                self.points.pop(0)

    def clear(self):
        self.points.clear()

    def draw(self, surface, color, base_radius=6):
        n = len(self.points)
        if n < 2:
            return
        for i, (px, py) in enumerate(self.points):
            ratio = (i + 1) / n
            rad = max(2, int(base_radius * ratio * 1.6))
            GlowCache.blit(surface, px, py, rad, color, intensity=ratio * 0.45)


class FloatingParticles:
    """Sistema de partículas con Object Pooling para ambientes románticos, nieve o energía."""
    def __init__(self, count=45, width=config.WIDTH, height=config.HEIGHT, mode="romantic"):
        self.width = width
        self.height = height
        self.mode = mode
        self.pool = []
        for _ in range(count):
            p = {}
            self._reset_particle(p, initial=True)
            self.pool.append(p)

    def _reset_particle(self, p, initial=False):
        p["x"] = random.uniform(0, self.width)
        p["y"] = random.uniform(0, self.height) if initial else self.height + random.uniform(5, 35)
        p["vy"] = random.uniform(-16.0, -42.0)
        p["vx_amp"] = random.uniform(10.0, 26.0)
        p["freq"] = random.uniform(1.2, 3.2)
        p["phase"] = random.uniform(0, math.tau)
        p["size"] = random.choice([2, 3, 4, 5])
        p["is_heart"] = (self.mode == "romantic" and random.random() < 0.28)
        if self.mode == "romantic":
            p["color"] = random.choice([
                config.COLOR_ENERGY,
                (255, 90, 150),
                (255, 180, 210),
                (255, 220, 150)
            ])
        elif self.mode == "cyber":
            p["color"] = random.choice([
                config.COLOR_DANGER,
                config.COLOR_ENERGY,
                (0, 255, 140)
            ])
        else:
            p["color"] = (220, 240, 255)
        return p

    def update(self, dt):
        for p in self.pool:
            p["phase"] += p["freq"] * dt
            p["y"] += p["vy"] * dt
            p["x"] += math.sin(p["phase"]) * p["vx_amp"] * dt
            if p["y"] < -25:
                self._reset_particle(p, initial=False)

    def draw(self, surface, cam_x=0.0, parallax=1.0):
        for p in self.pool:
            sx = (p["x"] - cam_x * parallax) % self.width
            sy = p["y"]
            pulse = 0.65 + 0.35 * math.sin(p["phase"] * 1.5)
            if p["is_heart"]:
                HeartRenderer.draw(
                    surface, sx, sy,
                    scale=0.22 + (p["size"] * 0.04),
                    color=p["color"],
                    alpha=int(180 * pulse),
                    glow=True
                )
            else:
                GlowCache.blit(surface, sx, sy, p["size"] * 3, p["color"], intensity=0.65 * pulse)
                pygame.draw.circle(surface, (255, 255, 255), (int(sx), int(sy)), max(1, p["size"] // 2))


class BurstPool:
    """Pool pre-alocado para explosiones de partículas (chispas/corazones) sin usar GC."""
    def __init__(self, capacity=60):
        self.particles = [
            {"active": False, "x": 0.0, "y": 0.0, "vx": 0.0, "vy": 0.0,
             "life": 0.0, "max_life": 1.0, "color": (255, 255, 255), "size": 3, "heart": False}
            for _ in range(capacity)
        ]

    def emit(self, x, y, count=15, colors=None, heart_chance=0.3, speed_range=(40, 170)):
        if colors is None:
            colors = [config.COLOR_ENERGY, (255, 120, 170), (255, 255, 255)]
        spawned = 0
        for p in self.particles:
            if not p["active"]:
                ang = random.uniform(0, math.tau)
                spd = random.uniform(speed_range[0], speed_range[1])
                p["active"] = True
                p["x"] = float(x)
                p["y"] = float(y)
                p["vx"] = math.cos(ang) * spd
                p["vy"] = math.sin(ang) * spd
                p["max_life"] = random.uniform(0.55, 1.25)
                p["life"] = p["max_life"]
                p["color"] = random.choice(colors)
                p["size"] = random.randint(2, 5)
                p["heart"] = (random.random() < heart_chance)
                spawned += 1
                if spawned >= count:
                    break

    def update(self, dt):
        for p in self.particles:
            if p["active"]:
                p["life"] -= dt
                if p["life"] <= 0:
                    p["active"] = False
                else:
                    p["x"] += p["vx"] * dt
                    p["y"] += p["vy"] * dt
                    p["vy"] -= 12.0 * dt  # Leve flotación ascendente

    def draw(self, surface):
        for p in self.particles:
            if p["active"]:
                ratio = max(0.0, p["life"] / p["max_life"])
                if p["heart"]:
                    HeartRenderer.draw(
                        surface, p["x"], p["y"],
                        scale=0.28 * ratio + 0.1,
                        color=p["color"],
                        alpha=int(230 * ratio),
                        glow=True
                    )
                else:
                    GlowCache.blit(surface, p["x"], p["y"], int(p["size"] * 3 * ratio) + 2, p["color"], intensity=ratio)


class ProceduralUI:
    """Helpers de interfaz estilizada con caché de paneles traslúcidos."""
    @staticmethod
    def get_panel(width, height, bg_color=(15, 10, 22, 195), border_color=config.COLOR_ENERGY, cut=12):
        key = ("panel", width, height, bg_color, border_color, cut)
        if key not in _CACHE:
            surf = pygame.Surface((width, height), pygame.SRCALPHA)
            pts = [
                (cut, 0),
                (width - cut, 0),
                (width - 1, cut),
                (width - 1, height - cut),
                (width - cut, height - 1),
                (cut, height - 1),
                (0, height - cut),
                (0, cut)
            ]
            pygame.draw.polygon(surf, bg_color, pts)
            pygame.draw.polygon(surf, border_color, pts, 2)
            # Acentos de esquina
            corner_len = min(22, width // 6, height // 4)
            hi = (255, 255, 255, 180)
            pygame.draw.line(surf, hi, (cut, 3), (cut + corner_len, 3), 2)
            pygame.draw.line(surf, hi, (width - cut - corner_len, height - 4), (width - cut, height - 4), 2)
            _CACHE[key] = surf
        return _CACHE[key]

    @staticmethod
    def draw_panel(surface, rect, bg_color=(15, 10, 22, 195), border_color=config.COLOR_ENERGY, cut=12, glow=True):
        if glow:
            GlowCache.blit(surface, rect.centerx, rect.centery, max(rect.width, rect.height) // 2, border_color, intensity=0.18)
        panel = ProceduralUI.get_panel(rect.width, rect.height, bg_color, border_color, cut)
        surface.blit(panel, rect.topleft)
