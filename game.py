import pygame
import sys
import asyncio  # 웹 버전 필수 라이브러리

# --- 초기 설정 ---
pygame.init()
# 웹 환경에 최적화된 해상도 (800x600)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Muscle Horse Web V2")
clock = pygame.time.Clock()

# --- 색상 정의 ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 80, 80)      # 상체/체력
BLUE = (80, 80, 255)     # 하체/지능
GREEN = (80, 200, 80)    # 휴식/회복
YELLOW = (255, 200, 0)   # 지방
ORANGE = (255, 150, 0)   # 탄수화물
PURPLE = (150, 50, 200)  # 단백질

# --- 폰트 설정 ---
# 웹에서는 시스템 한글 폰트가 없을 수 있어 기본 영문 폰트 사용
font_big = pygame.font.Font(None, 40)
font_medium = pygame.font.Font(None, 28)
font_small = pygame.font.Font(None, 20)

# --- 게임 변수 (저장 데이터) ---
stats = {"Upper": 0, "Lower": 0, "Cardio": 0, "Core": 0}   # 운동 스탯
nutrients = {"Protein": 20, "Carb": 20, "Fat": 20}         # 영양소
condition = 100 
level = 1
total_score = 0

# --- 음식 메뉴 데이터 ---
food_menu = {
    "Protein Shake": {"Protein": 30, "Carb": 5, "Fat": 0, "desc": "Muscle++"},
    "Horse Feed": {"Protein": 10, "Carb": 30, "Fat": 5, "desc": "Yummy"},
    "Mom's Meal": {"Protein": 15, "Carb": 20, "Fat": 10, "desc": "Good"},
    "Bread": {"Protein": 5, "Carb": 40, "Fat": 15, "desc": "So Fatty"},
    "Beef Noodle": {"Protein": 25, "Carb": 25, "Fat": 20, "desc": "Tasty!"}
}

# --- 이미지 불러오기 함수 (소문자 필수!) ---
def load_and_scale(filename):
    try:
        img = pygame.image.load(filename)
        # 화면 크기에 맞춰 말 크기도 300x300으로 조정
        return pygame.transform.scale(img, (300, 300))
    except FileNotFoundError:
        return None 

# 이미지 로드 (파일 없으면 회색 박스로 대체)
base_img = load_and_scale("horse_idle.png")
if base_img is None:
    base_img = pygame.Surface((300, 300))
    base_img.fill(GRAY)

# 상태별 이미지 연결
img_idle = base_img
img_act_upper = load_and_scale("act_upper.png") or base_img
img_act_lower = load_and_scale("act_lower.png") or base_img
img_act_cardio = load_and_scale("act_cardio.png") or base_img
img_act_core = load_and_scale("act_core.png") or base_img
img_act_sleep = load_and_scale("act_sleep.png") or base_img
img_act_rest = load_and_scale("act_rest.png") or base_img
img_act_eat = load_and_scale("act_eat.png") or base_img
img_final = load_and_scale("horse_final_muscle.png") or base_img

# --- 전역 변수 설정 ---
current_image = img_idle
is_acting = False
action_end_time = 0
show_food_menu = False
msg_text = "Let's Workout!"

# --- 그리기 함수들 ---

# 1. 게이지바 그리기
def draw_bar(screen, x, y, val, max_val, color, name):
    # 배경바
    pygame.draw.rect(screen, (220, 220, 220), (x, y, 140, 20))
    # 게이지
    ratio = min(val / max_val, 1.0)
    pygame.draw.rect(screen, color, (x, y, 140 * ratio, 20))
    # 테두리
    pygame.draw.rect(screen, BLACK, (x, y, 140, 20), 2)
    # 텍스트
    txt = font_small.render(f"{name}: {int(val)}", True, BLACK)
    screen.blit(txt, (x + 5, y + 3))

# 2. 버튼 그리기
def draw_button(txt, rect, color):
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    text_surf = font_small.render(txt, True, WHITE)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

# --- UI 위치 설정 (800x600 기준) ---
btn_w, btn_h = 100, 50
start_x, start_y = 30, 450 # 버튼 시작 위치

# 운동 버튼 (윗줄)
btn_upper = pygame.Rect(start_x, start_y, btn_w, btn_h)
btn_lower = pygame.Rect(start_x + 110, start_y, btn_w, btn_h)
btn_cardio = pygame.Rect(start_x + 220, start_y, btn_w, btn_h)
btn_core = pygame.Rect(start_x + 330, start_y, btn_w, btn_h)

# 생활 버튼 (아랫줄)
btn_sleep = pygame.Rect(start_x, start_y + 60, btn_w, btn_h)
btn_rest = pygame.Rect(start_x + 110, start_y + 60, btn_w, btn_h)
btn_eat_open = pygame.Rect(start_x + 220, start_y + 60, btn_w, btn_h)

# 음식 메뉴 버튼 (동적 생성)
food_buttons = []
for i, food_name in enumerate(food_menu.keys()):
    # 메뉴판 중앙 배치
    rect = pygame.Rect(200, 120 + (i * 60), 400, 50)
    food_buttons.append({"name": food_name, "rect": rect})
btn_close_menu = pygame.Rect(350, 450, 100, 40)


# ==========================================
# 메인 게임 로직 (Async 필수!)
# ==========================================
async def main():
    global current_image, is_acting, action_end_time, show_food_menu, msg_text, condition, total_score, level, stats, nutrients
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()

        # 1. 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                # A. 메뉴판이 열렸을 때
                if show_food_menu:
                    for btn in food_buttons:
                        if btn["rect"].collidepoint(mouse_pos):
                            f_name = btn["name"]
                            f_data = food_menu[f_name]
                            
                            # 영양소 섭취
                            nutrients["Protein"] = min(nutrients["Protein"] + f_data["Protein"], 100)
                            nutrients["Carb"] = min(nutrients["Carb"] + f_data["Carb"], 100)
                            nutrients["Fat"] = min(nutrients["Fat"] + f_data["Fat"], 100)
                            
                            msg_text = f"Yum! {f_name}"
                            current_image = img_act_eat
                            is_acting = True
                            action_end_time = current_time + 1000
                            show_food_menu = False # 닫기
                    
                    if btn_close_menu.collidepoint(mouse_pos):
                        show_food_menu = False # 그냥 닫기

                # B. 평소 상태 (행동 중이 아닐 때)
                elif not is_acting:
                    action_taken = False
                    
                    if btn_upper.collidepoint(mouse_pos):
                        stats["Upper"] += 10
                        current_image = img_act_upper
                        action_taken = True
                        msg_text = "Upper Body Workout!"
                    elif btn_lower.collidepoint(mouse_pos):
                        stats["Lower"] += 10
                        current_image = img_act_lower
                        action_taken = True
                        msg_text = "Leg Day!"
                    elif btn_cardio.collidepoint(mouse_pos):
                        stats["Cardio"] += 10
                        current_image = img_act_cardio
                        action_taken = True
                        msg_text = "Burning Fat..."
                    elif btn_core.collidepoint(mouse_pos):
                        stats["Core"] += 10
                        current_image = img_act_core
                        action_taken = True
                        msg_text = "Plank 1 min!"
                    elif btn_sleep.collidepoint(mouse_pos):
                        condition = min(condition + 30, 100)
                        current_image = img_act_sleep
                        action_taken = True
                        msg_text = "Zzz... Good night."
                    elif btn_rest.collidepoint(mouse_pos):
                        condition = min(condition + 10, 100)
                        current_image = img_act_rest
                        action_taken = True
                        msg_text = "Taking a break."
                    elif btn_eat_open.collidepoint(mouse_pos):
                        show_food_menu = True
                        msg_text = "What to eat?"

                    # 행동 시작 처리
                    if action_taken:
                        is_acting = True
                        action_end_time = current_time + 1000
                        # 운동 시 컨디션 소모
                        if not btn_sleep.collidepoint(mouse_pos) and not btn_rest.collidepoint(mouse_pos):
                             condition = max(condition - 5, 0)

        # 2. 상태 업데이트
        if is_acting and current_time >= action_end_time:
            is_acting = False
            current_image = img_idle

        # 레벨 계산
        total_score = sum(stats.values())
        level = 1 + (total_score // 100)
        
        # 최종 진화 (레벨 5 이상)
        if level >= 5 and not is_acting:
             current_image = img_final
        elif not is_acting:
             current_image = img_idle

        # 3. 화면 그리기
        screen.fill(WHITE)
        
        # 오른쪽 위: 영양소 게이지
        draw_bar(screen, 620, 30, nutrients["Protein"], 100, PURPLE, "Pro")
        draw_bar(screen, 620, 60, nutrients["Carb"], 100, ORANGE, "Carb")
        draw_bar(screen, 620, 90, nutrients["Fat"], 100, YELLOW, "Fat")
        
        # 왼쪽 위: 운동 스탯 게이지
        draw_bar(screen, 30, 30, stats["Upper"], 200, RED, "Upper")
        draw_bar(screen, 30, 60, stats["Lower"], 200, BLUE, "Lower")
        draw_bar(screen, 30, 90, stats["Cardio"], 200, GRAY, "Cardio")
        draw_bar(screen, 30, 120, stats["Core"], 200, BLACK, "Core")

        # 중앙: 레벨 및 컨디션
        level_txt = font_big.render(f"Lv.{level} Muscle Horse", True, BLACK)
        screen.blit(level_txt, (SCREEN_WIDTH//2 - 100, 30))
        
        cond_color = BLUE if condition > 50 else RED
        draw_bar(screen, SCREEN_WIDTH//2 - 70, 70, condition, 100, cond_color, "Cond")
        
        # 메시지 창
        msg_surf = font_medium.render(msg_text, True, BLACK)
        screen.blit(msg_surf, (SCREEN_WIDTH//2 - msg_surf.get_width()//2, 550))

        # 캐릭터 그리기 (메뉴 없을 때만)
        if not show_food_menu:
            screen.blit(current_image, (SCREEN_WIDTH//2 - 150, 120))

        # 버튼 및 메뉴 그리기
        if show_food_menu:
            # 메뉴판 배경
            pygame.draw.rect(screen, (240, 240, 240), (150, 100, 500, 400))
            pygame.draw.rect(screen, BLACK, (150, 100, 500, 400), 3)
            # 메뉴 버튼들
            for btn in food_buttons:
                draw_button(btn["name"], btn["rect"], WHITE)
                # 설명 텍스트
                desc = food_menu[btn["name"]]["desc"]
                desc_surf = font_small.render(desc, True, GRAY)
                screen.blit(desc_surf, (btn["rect"].x + 10, btn["rect"].y + 35))
            
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
        
        # [중요] 웹브라우저 동기화 대기
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
