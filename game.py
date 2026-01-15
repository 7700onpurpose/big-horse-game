import pygame
import sys
import asyncio

# --- 초기 설정 ---
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Muscle Horse Web V3")
clock = pygame.time.Clock()

# --- 색상 정의 ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 80, 80)
BLUE = (80, 80, 255)
GREEN = (80, 200, 80)
YELLOW = (255, 200, 0)
ORANGE = (255, 150, 0)
PURPLE = (150, 50, 200)

# --- 폰트 설정 (수정됨: 파일 직접 로딩) ---
# font.ttf 파일이 폴더에 있어야 한글이 나옵니다!
try:
    font_path = "font.ttf" 
    font_big = pygame.font.Font(font_path, 40)
    font_medium = pygame.font.Font(font_path, 28)
    font_small = pygame.font.Font(font_path, 16)
except:
    print("폰트 파일을 찾을 수 없어 기본 폰트를 사용합니다.")
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
    "말먹이": {"단백질": 10, "탄수화물": 30, "지방": 5, "desc": "가성비 최고"},
    "집밥": {"단백질": 15, "탄수화물": 20, "지방": 10, "desc": "엄마의 손맛"},
    "빵": {"단백질": 5, "탄수화물": 40, "지방": 15, "desc": "살찌는 맛"},
    "우육면": {"단백질": 25, "탄수화물": 25, "지방": 20, "desc": "동족의 맛(?)"}
}

# --- 이미지 불러오기 ---
def load_and_scale(filename):
    try:
        img = pygame.image.load(filename)
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

# --- 전역 변수 ---
current_image = img_idle
is_acting = False
action_end_time = 0
show_food_menu = False
msg_text = "운동을 시작해볼까?"

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

# UI 위치
btn_w, btn_h = 100, 50
start_x, start_y = 30, 450

btn_upper = pygame.Rect(start_x, start_y, btn_w, btn_h)
btn_lower = pygame.Rect(start_x + 110, start_y, btn_w, btn_h)
btn_cardio = pygame.Rect(start_x + 220, start_y, btn_w, btn_h)
btn_core = pygame.Rect(start_x + 330, start_y, btn_w, btn_h)

btn_sleep = pygame.Rect(start_x, start_y + 60, btn_w, btn_h)
btn_rest = pygame.Rect(start_x + 110, start_y + 60, btn_w, btn_h)
btn_eat_open = pygame.Rect(start_x + 220, start_y + 60, btn_w, btn_h)

food_buttons = []
for i, food_name in enumerate(food_menu.keys()):
    rect = pygame.Rect(200, 120 + (i * 60), 400, 50)
    food_buttons.append({"name": food_name, "rect": rect})
btn_close_menu = pygame.Rect(350, 450, 100, 40)

# --- 메인 로직 ---
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
                            msg_text = f"{f_name} 냠냠!"
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
                        msg_text = "상체 조지기!"
                    elif btn_lower.collidepoint(mouse_pos):
                        stats["하체"] += 10
                        current_image = img_act_lower
                        action_taken = True
                        msg_text = "하체는 스쿼트!"
                    elif btn_cardio.collidepoint(mouse_pos):
                        stats["유산소"] += 10
                        current_image = img_act_cardio
                        action_taken = True
                        msg_text = "지방 태우기!"
                    elif btn_core.collidepoint(mouse_pos):
                        stats["코어"] += 10
                        current_image = img_act_core
                        action_taken = True
                        msg_text = "플랭크 버티기!"
                    elif btn_sleep.collidepoint(mouse_pos):
                        condition = min(condition + 30, 100)
                        current_image = img_act_sleep
                        action_taken = True
                        msg_text = "쿨쿨..."
                    elif btn_rest.collidepoint(mouse_pos):
                        condition = min(condition + 10, 100)
                        current_image = img_act_rest
                        action_taken = True
                        msg_text = "잠깐 휴식..."
                    elif btn_eat_open.collidepoint(mouse_pos):
                        show_food_menu = True
                        msg_text = "뭐 먹을까?"

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
        
        # 게이지 그리기
        draw_bar(screen, 620, 30, nutrients["단백질"], 100, PURPLE, "단백질")
        draw_bar(screen, 620, 60, nutrients["탄수화물"], 100, ORANGE, "탄수화물")
        draw_bar(screen, 620, 90, nutrients["지방"], 100, YELLOW, "지방")
        
        draw_bar(screen, 30, 30, stats["상체"], 200, RED, "상체")
        draw_bar(screen, 30, 60, stats["하체"], 200, BLUE, "하체")
        draw_bar(screen, 30, 90, stats["유산소"], 200, GRAY, "유산소")
        draw_bar(screen, 30, 120, stats["코어"], 200, BLACK, "코어")

        level_txt = font_big.render(f"Lv.{level} 근육말", True, BLACK)
        screen.blit(level_txt, (SCREEN_WIDTH//2 - 80, 30))
        
        cond_color = BLUE if condition > 50 else RED
        draw_bar(screen, SCREEN_WIDTH//2 - 70, 70, condition, 100, cond_color, "컨디션")
        
        msg_surf = font_medium.render(msg_text, True, BLACK)
        screen.blit(msg_surf, (SCREEN_WIDTH//2 - msg_surf.get_width()//2, 550))

        if not show_food_menu:
            screen.blit(current_image, (SCREEN_WIDTH//2 - 150, 120))

        if show_food_menu:
            pygame.draw.rect(screen, (240, 240, 240), (150, 100, 500, 400))
            pygame.draw.rect(screen, BLACK, (150, 100, 500, 400), 3)
            for btn in food_buttons:
                draw_button(btn["name"], btn["rect"], WHITE)
                desc = food_menu[btn["name"]]["desc"]
                desc_surf = font_small.render(desc, True, GRAY)
                screen.blit(desc_surf, (btn["rect"].x + 10, btn["rect"].y + 35))
            draw_button("닫기", btn_close_menu, RED)
        else:
            draw_button("상체", btn_upper, RED)
            draw_button("하체", btn_lower, BLUE)
            draw_button("유산소", btn_cardio, GRAY)
            draw_button("코어", btn_core, BLACK)
            draw_button("잠자기", btn_sleep, GREEN)
            draw_button("휴식", btn_rest, GREEN)
            draw_button("식사", btn_eat_open, ORANGE)

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
