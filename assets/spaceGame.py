import pygame
import os
import time
import random

# Initialize fonts
pygame.font.init()
pygame.mixer.init()

### Window setup
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Game")

#### Load in image assets
# Enemy ships
RED_SPACE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png")), (90, 90)) # NEED REMADE

GREEN_SPACE_SHIP_SHIELD = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_ship_green_shield.png")), (90, 90)) # NEED REMADE
GREEN_SPACE_SHIP_SHIELD_BROKE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_ship_green_shield_broken.png")), (90, 90)) # NEED REMADE

BLUE_SPACE_SHIP_SHIELD = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_ship_blue_shield.png")), (90, 90)) # NEED REMADE
BLUE_SPACE_SHIP_SHIELD_BROKE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_ship_blue_shield_broken.png")), (90, 90)) # NEED REMADE

# Player ship sprites
PLAYER_SHIP_NEUTRAL = pygame.transform.scale(pygame.image.load(os.path.join("assets", "player_ship_neutral.png")), (70, 60))
PLAYER_SHIP_UP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "player_ship_up.png")), (70, 60))
PLAYER_SHIP_DOWN = pygame.transform.scale(pygame.image.load(os.path.join("assets", "player_ship_down.png")), (70, 60))
PLAYER_SHIP_LEFT = pygame.transform.scale(pygame.image.load(os.path.join("assets", "player_ship_left.png")), (70, 60))
PLAYER_SHIP_RIGHT = pygame.transform.scale(pygame.image.load(os.path.join("assets", "player_ship_right.png")), (70, 60))


# Enemy projectiles
RED_LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_laser_red.png")), (40, 40))
GREEN_LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_laser_green.png")), (40, 40))
BLUE_LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_laser_blue.png")), (40, 40))

# Player projectile
YELLOW_LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png")), (40, 40))

# Game background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

# Powerup sprites
SHIELD_IMG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_shield_powerup.png")), (30, 30))
RAPID_FIRE_IMG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_rapidfire_powerup.png")), (30, 30))
FAST_IMG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_fast_powerup.png")), (30, 30))
NUKE_IMG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_nuke_powerup.png")), (30, 30))

# Define Laser class
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(obj, self)

# Ship class
class Ship:

    COOLDOWN = 30

    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                if obj.shield:
                    obj.shield_health -= 10
                else:
                    obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
    
    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()

# Define Player class
class Player(Ship):

    def __init__(self, x, y, health = 100):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_SHIP_NEUTRAL
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.shield = False
        self.shield_health = 0
        self.nuke = False
        self.fast = False
        self.rapid = False
        
    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        if not obj.shielded:
                            objs.remove(obj)
                        elif obj.shielded:
                            obj.ship_img = obj.ship_broke_shield
                            obj.shielded = False
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))
        if self.shield:
            pygame.draw.rect(window, (0, 0, 255), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.shield_health/self.max_health), 10))


    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 17, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

# Define Enemy class
class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, None, RED_LASER),
        "green": (GREEN_SPACE_SHIP_SHIELD, GREEN_SPACE_SHIP_SHIELD_BROKE, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP_SHIELD, BLUE_SPACE_SHIP_SHIELD_BROKE, BLUE_LASER)
    }

    def __init__(self, x, y, color, health = 100):
        super().__init__(x, y, health)
        self.color = color
        if color == "blue" or color == "green":
            self.shielded = True
        else:
            self.shielded = False
        self.ship_img, self.ship_broke_shield, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel
        
    def shoot(self, num = 1):
        if self.cool_down_counter == 0:
            if num == 1:
                laser = Laser(self.x + 25, self.y + 35, self.laser_img)
                self.lasers.append(laser)
                self.cool_down_counter = 1
            elif num == 3:
                laser = Laser(self.x, self.y + 35, self.laser_img)
                self.lasers.append(laser)
                laser = Laser(self.x + 27, self.y + 35, self.laser_img)
                self.lasers.append(laser)
                laser = Laser(self.x + int(self.get_width()/2) + 7, self.y + 35, self.laser_img)
                self.lasers.append(laser)
                self.cool_down_counter = 1

# Define powerup class
class Powerup:
    TYPE_MAP = {
        "shield": (SHIELD_IMG),
        "rapidfire": (RAPID_FIRE_IMG),
        "fast": (FAST_IMG),
        "nuke": (NUKE_IMG)
    }

    def __init__(self, x, y, typeof):
        self.x = x
        self.y = y
        self.type = typeof
        self.powerup_img = self.TYPE_MAP[typeof]
        self.mask = pygame.mask.from_surface(self.powerup_img)

    def move(self, vel):
        self.y += vel

    def draw(self, window):
        window.blit(self.powerup_img, (self.x, self.y))
    
    def get_height(self):
        return self.powerup_img.get_height()


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

# The game
def main():

    # Begin the music!
    pygame.mixer.music.load(os.path.join("assets", "space_game_music.wav"))
    pygame.mixer.music.play(-1)

    run = True
    FPS = 60
    level = 0
    lives = 5

    # Create fonts
    main_font = pygame.font.SysFont("comicsans", 50)
    powerup_font = pygame.font.SysFont("comicsans", 40)
    lost_font = pygame.font.SysFont("comicsans", 60)

    # List of enemies
    enemies = []
    wave_length = 0

    # Relevant velocities
    enemy_vel = 1
    player_vel = 5
    laser_vel = 5

    # List of powerups
    powerups = []
    num_powerups = 0
    fast_timer = 0
    rapid_timer = 0

    clock = pygame.time.Clock()

    # Create player
    player = Player(300, 630)

    lost = False
    lost_count = 0
    
    paused = False
    pause_delay = 0

    nuke_deployed = False
    nuke_deployed_notification = 0
    nuke_enemies = False

    def redraw_window():
        # Draw BG
        WIN.blit(BG, (0,0))

        # Draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        # Draw powerups
        for powerup in powerups:
            powerup.draw(WIN)

        # Draw player
        player.draw(WIN)

        # If the player lost put a 
        if lost == True:
            lost_label = lost_font.render("You Lost!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))
            pygame.mixer.music.pause()

        # If paused post a pause screen
        if paused == True:
            pause_label = lost_font.render("Paused. Press enter to continue...", 1, (255, 255, 255))
            WIN.blit(pause_label, (WIDTH/2 - pause_label.get_width()/2, 350))

        # Notfiy player if they have nuke ready
        if player.nuke == True:
            nuke_label = main_font.render("NUKE READY", 1, (255,255,255))
            WIN.blit(nuke_label, (WIDTH/2 - nuke_label.get_width()/2, 10))

        # Notify of deployed nuke
        if nuke_deployed == True:
            nuke_deployed_label = main_font.render("NUKE DEPLOYED!", 1, (255,255,255))
            WIN.blit(nuke_deployed_label, (WIDTH/2 - nuke_deployed_label.get_width()/2, 10))

        # Powerup sidebar
        if player.shield:
            shield_label = powerup_font.render("Shield", 1, (255, 255, 255))
        else:
            shield_label = powerup_font.render("Shield", 1, (100, 100, 100))
            
        if player.rapid:
            rapid_label = powerup_font.render("Rapid Fire", 1, (255, 255, 255))
        else:
            rapid_label = powerup_font.render("Rapid Fire", 1, (100, 100, 100))
            
        if player.fast:
            fast_label = powerup_font.render("Fast Movement", 1, (255, 255, 255))
        else:
            fast_label = powerup_font.render("Fast Movement", 1, (100, 100, 100))

        WIN.blit(shield_label, (10, 50))
        WIN.blit(rapid_label, (10, 75))
        WIN.blit(fast_label, (10, 100))

        # Draw enemies
        for enemy in enemies:
            enemy.draw(WIN)

        pygame.display.update()


    while run:
        clock.tick(FPS)

        redraw_window()

        keys = pygame.key.get_pressed()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if paused:
            pause_delay += 1
            pygame.mixer.music.unpause()
            if keys[pygame.K_RETURN] and pause_delay > FPS/2:
                pause_delay = 0
                paused = False
                continue
            else:
                pygame.mixer.music.pause()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        quit()
                continue

        if nuke_deployed:
            nuke_deployed_notification += 1
            if nuke_deployed_notification > FPS*3:
                nuke_deployed = False

        if lost:
            if lost_count > FPS * 5:
                run = False
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        quit()
                continue
        if len(enemies) == 0:
            new_round = True
            level += 1
            wave_length += 3
            if level < 5:
                num_powerups = int(random.randrange(0, 2))
                for i in range(wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-wave_length * 100, -100), "red")
                    enemies.append(enemy)
            elif level >= 5 and level < 15:
                num_powerups = int(random.randrange(0, 3))
                for i in range(wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-wave_length * 100, -100), random.choice(["red", "green"]))
                    enemies.append(enemy)
            elif level >= 15:
                numpowerups = int(random.randrange(0, 5))
                for i in range(wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-wave_length * 100, -100), random.choice(["red", "blue", "green"]))
                    enemies.append(enemy)

        if len(powerups) == 0 and new_round:
            for i in range(num_powerups):
                powerup = Powerup(random.randrange(50, WIDTH-100), random.randrange(-500, -100), random.choice(["nuke", "fast", "rapidfire", "shield"]))
                powerups.append(powerup)
            new_round = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        if keys[pygame.K_a] and player.x - player_vel > 0: # Move left
            player.x -= player_vel
            player.ship_img = PLAYER_SHIP_LEFT
        if keys[pygame.K_w] and player.y - player_vel > 0: # Move up
            player.y -= player_vel
            player.ship_img = PLAYER_SHIP_UP
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 20 < HEIGHT: # Move down
            player.y += player_vel
            player.ship_img = PLAYER_SHIP_DOWN
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # Move right
            player.x += player_vel
            player.ship_img = PLAYER_SHIP_RIGHT
        if keys[pygame.K_SPACE]:
            player.shoot()
        if keys[pygame.K_ESCAPE]:
            paused = True
        if keys[pygame.K_z] and player.nuke:
            nuke_deployed = True
            nuke_enemies = True
            player.nuke = False
        if keys[pygame.K_UP]:
            level += 1
        if not (keys[pygame.K_d] or keys[pygame.K_s] or keys[pygame.K_w] or keys[pygame.K_a]):
            player.ship_img = PLAYER_SHIP_NEUTRAL

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*FPS) == 1:
                if enemy.color == "blue":
                    enemy.shoot(3)
                else:
                    enemy.shoot()

            if collide(enemy, player):
                if player.shield:
                    player.shield_health -= 10
                    enemies.remove(enemy)
                else:
                    player.health -= 10
                    enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -=1
                enemies.remove(enemy)

        if nuke_enemies:
            for enemy in enemies[:]:
                enemies.remove(enemy)
            nuke_enemies = False

        ##################
        # Manage powerups
        ##################
        for powerup in powerups[:]:
            powerup.move(enemy_vel)

            if collide(powerup, player):
                if powerup.type == "nuke":
                    player.nuke = True
                elif powerup.type == "fast":
                    player.fast = True
                    fast_timer = 0
                elif powerup.type == "rapidfire":
                    player.rapid = True
                    rapid_timer = 0
                elif powerup.type == "shield":
                    player.shield = True
                    player.shield_health = 100
                powerups.remove(powerup)

            elif powerup.y + powerup.get_height() > HEIGHT:
                powerups.remove(powerup)

        # Control the "fast" powerup
        if player.fast:
            player_vel = 10
            fast_timer += 1
            if fast_timer > FPS*15:
                player.fast = False
        else:
            player_vel = 5

        # Control the "rapid" powerup
        if player.rapid:
            player.COOLDOWN = 10
            rapid_timer += 1
            if rapid_timer > FPS*15:
                player.rapid = False
        else:
            player.COOLDOWN = 30

        # Control the "shield" powerup
        if player.shield_health == 0:
            player.shield = False

        player.move_lasers(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render("Left click to begin...", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

main_menu()