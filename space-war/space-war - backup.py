# Imports
import pygame
import random
import math
import os
# Initialize game engine
pygame.init()
pygame.mixer.init()


# Window
WIDTH = 1000
HEIGHT = 700
SIZE = (WIDTH, HEIGHT)
TITLE = "Space War"
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption(TITLE)

# stages
START = 0
PLAYING = 1
WIN = 2
LOSE = 3

stage = START

#misc
shots = 0


#font
FONT_SM = pygame.font.Font("assets/fonts/heav.ttf", 24)
FONT_MD = pygame.font.Font("assets/fonts/heav.ttf", 32)
FONT_LG = pygame.font.Font("assets/fonts/heav.ttf", 64)
FONT_XL = pygame.font.Font("assets/fonts/heav.ttf", 96)


# Timer
clock = pygame.time.Clock()
refresh_rate = 60

# Colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (100, 255, 100)

#Sounds
song1 = "assets/sounds/Bonus Stage Glowball - Sonic the Hedgehog 3 [OST].wav"
song2 = "assets/sounds/Sonic CD (USA) Music Special Stage-[AudioTrimmer.com].wav"
song3 = "assets/sounds/mini_boss_music.wav"
song4 = "assets/sounds/game_over.wav"
song5 = "assets/sounds/win.wav"
songs = [song1, song2, song3, song4, song5]
current_song = 0 

def start_music(song):
    pygame.mixer.music.load(song)
    pygame.mixer.music.play(-1)
   



enemy_explosion = pygame.mixer.Sound('assets/sounds/enemy_explode.wav')
shot = pygame.mixer.Sound('assets/sounds/bullet.wav')
enemy_shot = pygame.mixer.Sound('assets/sounds/bomb.wav')
damage = pygame.mixer.Sound('assets/sounds/damage.wav')
explosion = pygame.mixer.Sound('assets/sounds/death.wav')

# Images
ship_img = pygame.image.load('assets/images/ship.png')
hit = pygame.image.load('assets/images/damage.png')
laser_img = pygame.image.load('assets/images/laser.png')
bomb_img = pygame.image.load('assets/images/enemy_laser.gif')
mob_img1 = pygame.image.load('assets/images/Buzz_bomber.png')
mob_img2 = pygame.image.load('assets/images/puffer_fish.png')
mini_boss = pygame.image.load('assets/images/boss1.png')
start_screen = pygame.image.load('assets/images/start_screen.gif') 
background = pygame.image.load('assets/images/Death_Egg.gif')



# Game classes    
class Ship(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()

        self.image = image
        self.mask = pygame.mask.from_surface(self.image) 
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.speed = 5
        self.shield = 10 

    def move_left(self):
        self.rect.x -= self.speed
        if self.rect.x <= 0:
            self.rect.x = 0
        
    def move_right(self):
        self.rect.x += self.speed
        if self.rect.x >= 920:
            self.rect.x = 920

    def shoot(self):  
        laser = Laser(laser_img)
        laser.rect.centerx = self.rect.centerx
        laser.rect.centery = self.rect.top
        lasers.add(laser)
    

    def update(self, bombs, mobs):
        hit_list = pygame.sprite.spritecollide(self, bombs, True, pygame.sprite.collide_mask)
            
        for hit in hit_list:
            pygame.mixer.Sound.play(damage)
            player.shield -= 1

        hit_list = pygame.sprite.spritecollide(self, mobs, False, pygame.sprite.collide_mask)
        if len(hit_list) > 0:
            player.shield = 0

        if player.shield == 0:
            pygame.mixer.Sound.play(explosion)
            current_song = 3
            start_music(songs[current_song]) 
            pygame.mixer.music.play(0)
            self.kill()
             
             
    
class Laser(pygame.sprite.Sprite):
    
    def __init__(self, image):
        super().__init__()

        self.image = image 
        self.rect = self.image.get_rect()
        
        self.speed = 5

    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < -10:
            self.kill() 
    
class Mob(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()

        self.image = image
        self.mask = pygame.mask.from_surface(self.image) 
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if self.image == mob_img2:
            self.shield = 2 

    def drop_bomb(self):
        bomb = Bomb(bomb_img)
        bomb.rect.centerx = self.rect.centerx
        bomb.rect.centery = self.rect.bottom
        bombs.add(bomb)

    def update(self, lasers):
        hit_list = pygame.sprite.spritecollide(self, lasers, True, pygame.sprite.collide_mask)
        if len(hit_list) > 0:
            if self.image == mob_img2:
                self.shield -= 1
                if self.shield == 0:
                    pygame.mixer.Sound.play(enemy_explosion)
                    player.score += 100
                    self.kill()
            else:     
                pygame.mixer.Sound.play(enemy_explosion)
                player.score += 100
                self.kill()

        if self.rect.top > 700: 
            self.kill()




class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()

        self.image = image
        self.mask = pygame.mask.from_surface(self.image) 
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.shield = 50

    def drop_bomb(self):
        bomb = Bomb(bomb_img)
        bomb.rect.centerx = self.rect.centerx
        bomb.rect.centery = self.rect.bottom
        bombs.add(bomb)

    def update(self, lasers):
        hit_list = pygame.sprite.spritecollide(self, lasers, True, pygame.sprite.collide_mask)
        if len(hit_list) > 0 :
            self.shield -= 1

        if self.shield == 0:
            pygame.mixer.Sound.play(enemy_explosion)
            player.score += 1000
            current_song = 4
            start_music(songs[current_song])
            self.kill()
            pygame.mixer.music.play(0)
            

        if self.rect.top > 700: 
            self.kill()





class Boss_AI:
    def __init__(self, bosses):
        self.bosses = bosses
        self.moving_right = True
        self.speed = 5
        self.bomb_rate = 10
        
    def move(self):
        reverse = False
        
        for b in bosses:
            if self.moving_right:
                b.rect.x += self.speed
                if b.rect.right >= WIDTH:
                    reverse = True
            else:
                b.rect.x -= self.speed
                if b.rect.left <=0:
                    reverse = True

        if reverse == True:
            self.moving_right = not self.moving_right
            for b in bosses:
                b.rect.y += 0 


    def choose_bomber(self):
        rand = random.randrange(0, self.bomb_rate)
        all_bosses = bosses.sprites()
        
        if len(all_bosses) > 0 and rand == 0:
            return random.choice(all_bosses)
        else:
            return None

                

    def update(self):
        self.move()

        bomber = self.choose_bomber()
        if bomber != None:
            pygame.mixer.Sound.play(enemy_shot)
            bomber.drop_bomb()

       
class Bomb(pygame.sprite.Sprite):
    
    def __init__(self, image):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect()
        
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > HEIGHT:
            self.kill()
           
        
        
    
# implement some kind of wave system     
class Fleet:

    def __init__(self, mobs):
        self.mobs = mobs
        self.moving_right = True
        self.speed = 5
        self.bomb_rate = 60

    def move(self):
        reverse = False
        
        for m in mobs:
            if self.moving_right:
                m.rect.x += self.speed
                if m.rect.right >= WIDTH:
                    reverse = True
            else:
                m.rect.x -= self.speed
                if m.rect.left <=0:
                    reverse = True

        if reverse == True:
            self.moving_right = not self.moving_right
            for m in mobs:
                m.rect.y += 32


    def choose_bomber(self):
        rand = random.randrange(0, self.bomb_rate)
        all_mobs = mobs.sprites()
        
        if len(all_mobs) > 0 and rand == 0:
            return random.choice(all_mobs)
        else:
            return None

                

    def update(self):
        self.move()

        bomber = self.choose_bomber()
        if bomber != None:
            pygame.mixer.Sound.play(enemy_shot)
            bomber.drop_bomb()


def game_setup():
    global x, y, image, lasers, bombs, mobs, player, ship, fleet, stage, bosses, boss_AI 
    
    stage = START
      
    # Make game objects
    ship = Ship(384, 536, ship_img)

    # Make sprite groups
    player = pygame.sprite.GroupSingle()
    player.add(ship)
    player.score = 0
    player.shield = 10
    player.level = 0 
    if stage == PLAYING:
        player.level = 1 

    
    lasers = pygame.sprite.Group()   
    bombs = pygame.sprite.Group()

    mobs = pygame.sprite.Group()
    fleet = Fleet(mobs)

# Game helper functions
def show_title_screen():
    screen.blit(start_screen, (0, 0))  
    title_text = FONT_XL.render("Space War!", 1, WHITE)
    subtitle = FONT_MD.render("(Press ENTER to start.)", True, WHITE)
    t_rect = title_text.get_rect()
    t_rect.centerx = WIDTH/2
    t_rect.bottom = HEIGHT/2
    s_rect = subtitle.get_rect()
    s_rect.centerx = WIDTH/2
    s_rect.bottom = (HEIGHT/2) + 25 
    screen.blit(title_text, t_rect)
    screen.blit(subtitle, s_rect)

def show_stats(player):
    score_text = FONT_MD.render('Score: ' + str(player.score), 1, WHITE)
    screen.blit(score_text, [32, 32])

    health_text = FONT_MD.render('Shield: ' + str(player.shield), 1, WHITE)
    screen.blit(health_text, [32, 64])

    level_text = FONT_MD.render('Level: ' + str(player.level), 1, WHITE)
    screen.blit(level_text, [32, 96])

def level_setup():
    global x, y, image, lasers, bombs, mobs, player, ship, fleet, stage, bosses, boss_AI

    if player.level == 5:
        current_song = 2
        start_music(songs[current_song]) 


    # wave1 
    mob1 = Mob(128, 85, mob_img1)
    mob2 = Mob(256, 85, mob_img1)
    mob3 = Mob(384, 85, mob_img1)
    wave1 = [mob1, mob2, mob3] 
    
    #wave 2
    mob4 = Mob(128, 0, mob_img1)
    mob5 = Mob(256, 0, mob_img1)
    mob6 = Mob(384, 0, mob_img1)
    mob7 = Mob(0, 0, mob_img2)
    mob8 = Mob(512, 0, mob_img2)
    wave2 = [mob4, mob5, mob6, mob7, mob8]

    #wave3
    mob9 = Mob(128, 0, mob_img2)
    mob10 = Mob(256, 0, mob_img2)
    mob11 = Mob(384, 0, mob_img2)
    mob12 = Mob(0, 0, mob_img2)
    mob13 = Mob(512, 0, mob_img2)
    mob14 = Mob(64, 100, mob_img2)
    mob15 = Mob(450, 100, mob_img2) 
    wave3 = [mob9, mob10, mob11, mob12, mob13, mob14, mob15]


    #wave4
    mob17 = Mob(128, 0, mob_img1)
    mob18 = Mob(256, 0, mob_img2)
    mob19 = Mob(384, 0, mob_img1)
    mob20 = Mob(0, 0, mob_img2)
    mob21 = Mob(512, 0, mob_img2)
    mob22 = Mob(128, 100, mob_img2)
    mob23 = Mob(256, 100, mob_img1)
    mob24 = Mob(384, 100, mob_img2)
    mob25 = Mob(0, 100, mob_img1)
    mob26 = Mob(512, 100, mob_img1)
    
    wave4 = [mob17, mob18, mob19, mob20, mob21, mob22, mob23, mob24, mob25, mob26]

    #wave 5/boss
    if player.level == 5:
        boss1 = Boss(500, 0 , mini_boss)
        bosses = pygame.sprite.GroupSingle()
        bosses.add(boss1)
        boss_AI = Boss_AI(bosses) 
        
    
    mobs = pygame.sprite.Group()
    if player.level ==1: 
        mobs.add(wave1)
    if player.level == 2:
        mobs.add(wave2)
    if player.level == 3:
        mobs.add(wave3)
    if player.level == 4:
        mobs.add(wave4)
 

# Game loop
game_setup()

if stage == START:
    start_music(songs[current_song])
    pygame.mixer.music.play(-1)

if stage == PLAYING:
    current_song = 1
    start_music(songs[current_song]) 
    pygame.mixer.music.play(-1)


    
done = False

while not done:
    # Event processing (React to key presses, mouse clicks, etc.)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True        
        elif event.type == pygame.KEYDOWN:
            if stage == START:
                current_song = 0
                start_music(songs[current_song]) 
                if event.key == pygame.K_KP_ENTER:
                    stage = PLAYING
                    current_song = 1
                    start_music(songs[current_song]) 
            if event.key == pygame.K_SPACE and stage == PLAYING:
                pygame.mixer.Sound.play(shot)
                shots += 1 
                ship.shoot()

    if stage == PLAYING:
        pressed = pygame.key.get_pressed()

        if pressed[pygame.K_LEFT]:
            ship.move_left()
        elif pressed[pygame.K_RIGHT]:
            ship.move_right()
        
    
    # Game logic (Check for collisions, update points, etc.)
    if stage == PLAYING:
        player.update(bombs, mobs)
        if player.level == 5:
            player.update(bombs, bosses)
            
        lasers.update()
        mobs.update(lasers)
        bombs.update()
        fleet.update()
        
        if player.level == 5: 
            bosses.update(lasers)
            boss_AI.update()
        if len(player) == 0:
            stage = LOSE
            
        elif len(mobs) == 0 and player.level !=5:
            player.score += 100 * shots
            player.level+=1
            level_setup()

        if player.level == 5 and len(bosses) == 0:
            player.score += 100 * shots
            player.level+=1
            stage = WIN
                    
    # Drawing code (Describe the picture. It isn't actually drawn yet.)
    if stage == START:
        show_title_screen() 

    elif stage == PLAYING:
        screen.blit(background, (0, 0))
        lasers.draw(screen)
        player.draw(screen)
        bombs.draw(screen)
        mobs.draw(screen) 
        show_stats(player)
        if player.level == 5:
            bosses.draw(screen)

    if stage == WIN:
        screen.blit(start_screen, (0,0)) 
        win_text = FONT_XL.render("YOU WIN!", True, WHITE)
        win_subtext = FONT_MD.render("(Press R to restart.)", True, WHITE)
        w_rect = win_text.get_rect()
        w_rect.centerx = WIDTH/2
        w_rect.bottom =  HEIGHT/2 
        r_rect = win_subtext.get_rect()
        r_rect.centerx = WIDTH/2
        r_rect.bottom = (HEIGHT/2) + 20
        screen.blit(win_text, w_rect)
        screen.blit(win_subtext, r_rect)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                stage = START
                current_song = 0
                start_music(songs[current_song]) 
                game_setup() 

    elif stage == LOSE:
        screen.blit(start_screen, (0, 0))
        lose_text = FONT_XL.render("Game Over", True, WHITE)
        lose_subtext = FONT_MD.render("(Press R to restart.)", True, WHITE)
        l_rect = lose_text.get_rect()
        l_rect.centerx = WIDTH/2
        l_rect.bottom = (HEIGHT/2) 
        g_rect = lose_subtext.get_rect()
        g_rect.centerx = WIDTH/2
        g_rect.bottom = (HEIGHT/2) + 20
        screen.blit(lose_text, l_rect)
        screen.blit(lose_subtext, g_rect)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                stage = START
                current_song = 0
                start_music(songs[current_song]) 
                game_setup() 
        
    
    # Update screen (Actually draw the picture in the window.)
    pygame.display.flip()


    # Limit refresh rate of game loop 
    clock.tick(refresh_rate)


# Close window and quit
pygame.quit()
