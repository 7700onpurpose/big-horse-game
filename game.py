# 파일명: main.py (반드시 이 이름이어야 함!)
import pygame
import sys
import asyncio  # <--- 웹 버전에 필수!

# --- 초기 설정 ---
pygame.init()
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("인터랙티브 근육말 키우기 V2 Web")
clock = pygame.time.Clock()

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 80, 80)
BLUE = (80, 80, 255)
GREEN = (80, 200, 80)
YELLOW = (255, 200, 0)
ORANGE = (255, 150, 0)
PURPLE = (150, 50, 200)

# 폰트 설정 (웹에서는 기본 폰트로 대체될 수 있음)
font_big = pygame.font.Font(None, 40)
font_medium = pygame.font.Font(None, 28)
font_small = pygame.font.Font(None, 20)

# --- 게임 변수 ---
stats = {"상체": 0, "하체": 0, "유산소": 0, "코어": 0}
nutrients = {"단백질": 20, "탄수화물": 20, "지방": 20}
condition = 100 
level = 1
total_score = 0

# --- 음식 메뉴 ---
food_menu = {
    "단백질 쉐이크": {"단백질": 30, "탄수화물": 5, "지방": 0, "desc": "근육 빵빵!"},
    "말먹이": {"단백질": 10, "탄수화물": 30, "지방": 5, "desc": "기본 맛"},
    "집밥": {"단백질": 15, "탄수화물": 20, "지방": 10, "desc": "엄마 손맛"},
    "빵": {"단백질": 5, "탄수화물": 40, "지방": 15, "desc": "살찌는 맛"},
    "우육면": {"단백질": 25, "탄수화물": 25, "지방": 20, "desc": "동족의 맛(?)"}
}

# --- 이미지 불러오기 ---
def load_and_scale(filename):
    try:
        img = pygame.image.load(filename)
        return pygame.transform.scale(img, (350, 350))
    except FileNotFoundError:
        return None 

# 이미지 로드 (파일이 없으면 회색 박스로 대체)
base_img = load_and_scale("horse_idle.png")
if base_img is None:
    base_img = pygame.Surface((350, 350))
    base_img.fill(GRAY)

img_idle = base_img
img_act_upper = load_and_scale("act_upper.png") or base_img
img_act_lower = load_and_scale("act_lower.png") or base_img
img_act_cardio = load_and_scale("act_cardio.png") or base_img
img_act_core = load_and_scale("act_core.png") or base_img
img_act_sleep = load_and_scale("act_sleep.png") or base_img
img_act_rest = load_and_scale("act_rest.png") or base_img
img_act_eat = load_and_scale("act_eat.png") or base_img
img_final = load_and_scale("horse_final_muscle.png") or base_img

# --- 전역 변수 ---
current_image = img_idle
is_acting = False
action_end_time = 0
show_food_menu = False
msg_text = ""

# --- 그리기 함수들 ---
def draw_bar(screen, x, y, val, max_val, color, name):
    pygame.draw.rect(screen, (220, 220, 220), (x, y, 150, 20))
    ratio = min(val / max_val, 1.0)
    pygame.draw.rect(screen, color, (x, y, 150 * ratio, 20))
    pygame.draw.rect(screen, BLACK, (x, y, 150, 20), 2)
    txt = font_small.render(f"{name}: {int(val)}", True, BLACK)
    screen.blit(txt, (x + 5, y + 2))

def draw_button(txt, rect, color):
    pygame.draw.rect(screen
