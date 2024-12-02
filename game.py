import pygame
import random

pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("wa")
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED_HEAD = (255, 0, 0)
GREEN_BODY = (0, 255, 0)
BLUE_LEGS = (0, 0, 255)
# 盖亚
kill_sound = pygame.mixer.Sound("E:\\20241201_142328_1.wav")
class Target:
    def __init__(self):
        self.x = random.randint(100, 700)
        self.y = random.randint(100, 500)
        self.head_rect = pygame.Rect(self.x, self.y, 30, 30)
        self.body_rect = pygame.Rect(self.x, self.y + 40, 30, 40)
        self.legs_rect = pygame.Rect(self.x, self.y + 90, 30, 30)
        self.health = {
            "head": 1,
            "body": 4,
            "legs": 6
        }
    def draw(self):
        pygame.draw.rect(screen, RED_HEAD, self.head_rect)
        pygame.draw.rect(screen, GREEN_BODY, self.body_rect)
        pygame.draw.rect(screen, BLUE_LEGS, self.legs_rect)
    def check_hit(self, pos):
        if self.head_rect.collidepoint(pos):
            return "head"
        elif self.body_rect.collidepoint(pos):
            return "body"
        elif self.legs_rect.collidepoint(pos):
            return "legs"
        return None
    def take_damage(self, part):
        if part in self.health:
            self.health[part] -= 1
            if self.health[part] <= 0:
                return True
        return False
class GameState:
    def __init__(self):
        self.score = 0
        self.target = Target()

    def update_score(self):
        self.score += 1

    def reset_target(self):
        self.target = Target()
game_state = GameState()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            hit_part = game_state.target.check_hit(mouse_pos)
            if hit_part:
                if game_state.target.take_damage(hit_part):
                    print("keishai")
                    game_state.update_score()
                    game_state.reset_target()
                    kill_sound.play()
    screen.fill(WHITE)
    game_state.target.draw()
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"sum: {game_state.score}", True, BLACK)
    screen.blit(score_text, (10, 10))
    pygame.display.flip()
pygame.quit()