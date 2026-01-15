import pygame
import sys
import asyncio

# --- 초기 설정 ---
pygame.init()
# [변경] 웹 환경에 맞게 해상도 축소 (1000 -> 800)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
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
    "Protein Shake": {"단백질": 30, "탄수화물": 5, "지방": 0, "desc": "Muscle!"},
    "Horse Feed": {"단백질": 10, "탄수화물": 30, "지방": 5, "desc": "Yummy"},
    "Mom's Meal": {"단백질": 15, "탄수화물": 20, "지방": 10, "desc": "Good"},
    "Bread": {"단백질": 5, "탄수화물": 40, "지방": 15, "desc": "Fatty"},
    "Beef Noodle": {"단백질": 25, "탄수화물": 25, "지방": 20, "desc": "Tasty"}
}

# --- 이미지 불러오기 ---
def load_and_scale(filename):
    try:
        img = pygame.image.load(filename)
        # [변경] 말 크기도 화면에 맞춰 살짝 줄임 (350 -> 300)
        return pygame.transform.scale(img, (300, 300))
    except FileNotFoundError:
        return None 

base_img = load_and_scale("horse_idle.png")
if base_img is None:
    base_img = pygame.Surface((300, 300))
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

current_image = img_idle
is_acting = False
action_end_time = 0
show_food_menu = False
msg_text = ""

# --- 그리기 함수들 ---
def draw_bar(screen, x, y, val, max_val, color, name):
    pygame.draw.rect(screen, (220, 220, 220), (x, y, 140, 20))
    ratio = min(val / max_val, 1.0)
    pygame.draw.rect(screen, color, (x, y, 140 * ratio, 20))
    pygame.draw.rect(screen, BLACK, (x, y, 140, 20), 2)
    txt = font_small.render(f"{name}: {int(val)}", True, BLACK)
    screen.blit(txt, (x + 5, y + 2))

def draw_button(txt, rect, color):
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    text_surf = font_small.render(txt, True, WHITE)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

# [변경] 버튼 위치 재조정 (800x600 기준)
btn_w, btn_h = 100, 50 # 버튼 크기도 조금 줄임
start_x, start_y = 30, 450 # 버튼 시작 위치 위로 올림

# 상단 줄
btn_upper = pygame.Rect(start_x, start_y, btn_w, btn_h)
btn_lower = pygame.Rect(start_x + 110, start_y, btn_w, btn_h)
btn_cardio = pygame.Rect(start_x + 220, start_y, btn_w, btn_h)
btn_core = pygame.Rect(start_x + 330, start_y, btn_w, btn_h)

# 하단 줄
btn_sleep = pygame.Rect(start_x, start_y + 60, btn_w, btn_h)
btn_rest = pygame.Rect(start_x + 110, start_y + 60, btn_w, btn_h)
btn_eat_open = pygame.Rect(start_x + 220, start_y + 60, btn_w, btn_h)

# 메뉴판 위치 조정
food_buttons = []
for i, food_name in enumerate(food_menu.keys()):
    rect = pygame.Rect(200, 100 + (i * 60), 400, 50)
    food_buttons.append({"name": food_name, "rect": rect})
btn_close_menu = pygame.Rect(350, 420, 100, 40)

async def main():
    global current_image, is_acting, action_end_time, show_food_menu, msg_text, condition, total_score, level, stats, nutrients
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                if show_food_menu:
                    for btn in food_buttons:
                        if btn["rect"].collidepoint(mouse_pos):
                            f_name = btn["name"]
                            f_data = food_menu[f_name]
                            nutrients["단백질"] = min(nutrients["단백질"] + f_data["단백질"], 100)
                            nutrients["탄수화물"] = min(nutrients["탄수화물"] + f_data["탄수화물"], 100)
                            nutrients["지방"] = min(nutrients["지방"] + f_data["지방"], 100)
                            msg_text = f"Yum! {f_name}"
                            current_image = img_act_eat
                            is_acting = True
                            action_end_time = current_time + 1000
                            show_food_menu = False
                    if btn_close_menu.collidepoint(mouse_pos):
                        show_food_menu = False

                elif not is_acting:
                    action_taken = False
                    if btn_upper.collidepoint(mouse_pos):
                        stats["상체"] += 10
                        current_image = img_act_upper
                        action_taken = True
                        msg_text = "Upper Body Workout!"
                    elif btn_lower.collidepoint(mouse_pos):
                        stats["하체"] += 10
                        current_image = img_act_lower
                        action_taken = True
                        msg_text = "Leg Day!"
                    elif btn_cardio.collidepoint(mouse_pos):
                        stats["유산소"] += 10
                        current_image = img_act_cardio
                        action_taken = True
                        msg_text = "Burning Fat..."
                    elif btn_core.collidepoint(mouse_pos):
                        stats["코어"] += 10
                        current_image = img_act_core
                        action_taken = True
                        msg_text = "Plank!"
                    elif btn_sleep.collidepoint(mouse_pos):
                        condition = min(condition + 30, 100)
                        current_image = img_act_sleep
                        action_taken = True
                        msg_text = "Zzz..."
                    elif btn_rest.collidepoint(mouse_pos):
                        condition = min(condition + 10, 100)
                        current_image = img_act_rest
                        action_taken = True
                        msg_text = "Resting..."
                    elif btn_eat_open.collidepoint(mouse_pos):
                        show_food_menu = True
                        msg_text = "Menu"

                    if action_taken:
                        is_acting = True
                        action_end_time = current_time + 1000
                        if not btn_sleep.collidepoint(mouse_pos) and not btn_rest.collidepoint(mouse_pos):
                             condition = max(condition - 5, 0)

        if is_acting and current_time >= action_end_time:
            is_acting = False
            current_image = img_idle

        total_score = sum(stats.values())
        level = 1 + (total_score // 100)
        if level >= 5 and not is_acting:
             current_image = img_final
        elif not is_acting:
             current_image = img_idle

        screen.fill(WHITE)
        
        # [변경] 게이지바 위치 조정 (화면 오른쪽 끝에 맞춤)
        # x좌표 620 정도로 당겨옴
        draw_bar(screen, 620, 30, nutrients["단백질"], 100, PURPLE, "Pro")
        draw_bar(screen, 620, 60, nutrients["탄수화물"], 100, ORANGE, "Carb")
        draw_bar(screen, 620, 90, nutrients["지방"], 100, YELLOW, "Fat")
        
        draw_bar(screen, 30, 30, stats["상체"], 200, RED, "Upper")
        draw_bar(screen, 30, 60, stats["하체"], 200, BLUE, "Lower")
        draw_bar(screen, 30, 90, stats["유산소"], 200, GRAY, "Cardio")
        draw_bar(screen, 30, 120, stats["코어"], 200, BLACK, "Core")

        level_txt = font_big.render(f"Lv.{level} Muscle Horse", True, BLACK)
        screen.blit(level_txt, (SCREEN_WIDTH//2 - 100, 30))
        
        cond_color = BLUE if condition > 50 else RED
        draw_bar(screen, SCREEN_WIDTH//2 - 70, 70, condition, 100, cond_color, "Cond")
        
        msg_surf = font_medium.render(msg_text, True, BLACK)
        screen.blit(msg_surf, (SCREEN_WIDTH//2 - msg_surf.get_width()//2, 550))

        if not show_food_menu:
            screen.blit(current_image, (SCREEN_WIDTH//2 - 150, 120))

        if show_food_menu:
            pygame.draw.rect(screen, (240, 240, 240), (150, 80, 500, 400))
            pygame.draw.rect(screen, BLACK, (150, 80, 500, 400), 3)
            for btn in food_buttons:
                draw_button(btn["name"], btn["rect"], WHITE)
            draw_button("Close", btn_close_menu, RED)
        else:
            draw_button("Upper", btn_upper, RED)
            draw_button("Lower", btn_lower, BLUE)
            draw_button("Cardio", btn_cardio, GRAY)
            draw_button("Core", btn_core, BLACK)
            draw_button("Sleep", btn_sleep, GREEN)
            draw_button("Rest", btn_rest, GREEN)
            draw_button("Eat", btn_eat_open, ORANGE)

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
