import pygame
import sys

# --- 초기 설정 ---
pygame.init()
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("인터랙티브 근육말 키우기 V2")
clock = pygame.time.Clock()

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 80, 80)      # 운동/체력
BLUE = (80, 80, 255)     # 마나/지능 느낌
GREEN = (80, 200, 80)    # 휴식/회복
YELLOW = (255, 200, 0)   # 지방
ORANGE = (255, 150, 0)   # 탄수화물
PURPLE = (150, 50, 200)  # 단백질

# 폰트 설정
try:
    font_big = pygame.font.SysFont("malgungothic", 30, bold=True)
    font_medium = pygame.font.SysFont("malgungothic", 20, bold=True)
    font_small = pygame.font.SysFont("malgungothic", 16)
except:
    font_big = pygame.font.Font(None, 40)
    font_medium = pygame.font.Font(None, 28)
    font_small = pygame.font.Font(None, 20)

# --- 게임 변수 ---
# 1. 운동 스탯
stats = {"상체": 0, "하체": 0, "유산소": 0, "코어": 0}
# 2. 영양소 스탯 (최대 100)
nutrients = {"단백질": 20, "탄수화물": 20, "지방": 20}
condition = 100 
level = 1
total_score = 0

# --- 음식 메뉴 데이터 ---
food_menu = {
    "단백질 쉐이크": {"단백질": 30, "탄수화물": 5, "지방": 0, "desc": "근육이 빵빵!"},
    "말먹이": {"단백질": 10, "탄수화물": 30, "지방": 5, "desc": "기본적인 맛"},
    "집밥": {"단백질": 15, "탄수화물": 20, "지방": 10, "desc": "엄마의 손맛"},
    "빵": {"단백질": 5, "탄수화물": 40, "지방": 15, "desc": "살찌는 맛"},
    "우육면": {"단백질": 25, "탄수화물": 25, "지방": 20, "desc": "동족의 맛(?)"}
}

# --- 이미지 불러오기 (없으면 대체) ---
def load_and_scale(filename):
    try:
        img = pygame.image.load(filename)
        return pygame.transform.scale(img, (350, 350))
    except FileNotFoundError:
        # 파일이 없으면 그냥 빈 화면 안 띄우고 넘어가기 위해 에러 처리
        return None 

# 일단 idle 하나로 다 돌려막기 (파일이 있으면 로드됨)
base_img = load_and_scale("horse_idle.png")
if base_img is None:
    # 이미지가 아예 없으면 빨간 사각형으로 대체 (오류 방지)
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

# --- 상태 관리 ---
current_image = img_idle
is_acting = False
action_end_time = 0
show_food_menu = False # 메뉴판이 열렸는지 확인하는 변수
msg_text = "" # 화면 상단에 띄울 메시지

# --- UI 그리기 함수들 ---

# 1. 게이지바 그리기 (위치x, 위치y, 현재값, 최대값, 색상, 이름)
def draw_bar(screen, x, y, val, max_val, color, name):
    # 배경 회색 바
    pygame.draw.rect(screen, (220, 220, 220), (x, y, 150, 20))
    # 실제 값 게이지
    ratio = min(val / max_val, 1.0) # 100% 넘지 않게
    pygame.draw.rect(screen, color, (x, y, 150 * ratio, 20))
    # 테두리
    pygame.draw.rect(screen, BLACK, (x, y, 150, 20), 2)
    
    # 텍스트
    txt = font_small.render(f"{name}: {val}", True, BLACK)
    screen.blit(txt, (x + 5, y + 2))

# 2. 버튼 그리기
def draw_button(txt, rect, color):
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, BLACK, rect, 2) # 테두리
    text_surf = font_small.render(txt, True, WHITE)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

# 버튼 위치 설정
btn_w, btn_h = 120, 60
start_x, start_y = 50, 500
# 운동 버튼들
btn_upper = pygame.Rect(start_x, start_y, btn_w, btn_h)
btn_lower = pygame.Rect(start_x + 140, start_y, btn_w, btn_h)
btn_cardio = pygame.Rect(start_x + 280, start_y, btn_w, btn_h)
btn_core = pygame.Rect(start_x + 420, start_y, btn_w, btn_h)
# 하단 버튼들
btn_sleep = pygame.Rect(start_x, start_y + 80, btn_w, btn_h)
btn_rest = pygame.Rect(start_x + 140, start_y + 80, btn_w, btn_h)
btn_eat_open = pygame.Rect(start_x + 280, start_y + 80, btn_w, btn_h) # 식사 메뉴 열기

# 음식 메뉴 버튼들 (동적으로 생성)
food_buttons = []
for i, food_name in enumerate(food_menu.keys()):
    # 화면 중앙에 팝업처럼 배치
    rect = pygame.Rect(300, 150 + (i * 70), 400, 60)
    food_buttons.append({"name": food_name, "rect": rect})
btn_close_menu = pygame.Rect(450, 550, 100, 50)


# --- 메인 루프 ---
running = True
while running:
    current_time = pygame.time.get_ticks()

    # --- 이벤트 처리 ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # A. 식사 메뉴가 열려있을 때 (운동 버튼 클릭 불가)
            if show_food_menu:
                # 1. 음식 선택
                for btn in food_buttons:
                    if btn["rect"].collidepoint(mouse_pos):
                        f_name = btn["name"]
                        f_data = food_menu[f_name]
                        
                        # 영양소 섭취
                        nutrients["단백질"] = min(nutrients["단백질"] + f_data["단백질"], 100)
                        nutrients["탄수화물"] = min(nutrients["탄수화물"] + f_data["탄수화물"], 100)
                        nutrients["지방"] = min(nutrients["지방"] + f_data["지방"], 100)
                        
                        msg_text = f"{f_name} 섭취! ({f_data['desc']})"
                        current_image = img_act_eat
                        is_acting = True
                        action_end_time = current_time + 1000
                        show_food_menu = False # 먹었으면 메뉴 닫기
                
                # 2. 닫기 버튼
                if btn_close_menu.collidepoint(mouse_pos):
                    show_food_menu = False

            # B. 일반 상황 (운동/휴식 가능)
            elif not is_acting:
                action_taken = False
                
                if btn_upper.collidepoint(mouse_pos):
                    stats["상체"] += 10
                    current_image = img_act_upper
                    action_taken = True
                    msg_text = "상체 조지기! 으랏차!"
                elif btn_lower.collidepoint(mouse_pos):
                    stats["하체"] += 10
                    current_image = img_act_lower
                    action_taken = True
                    msg_text = "하체는 스쿼트가 제맛이지."
                elif btn_cardio.collidepoint(mouse_pos):
                    stats["유산소"] += 10
                    current_image = img_act_cardio
                    action_taken = True
                    msg_text = "지방을 태우자! 헉헉..."
                elif btn_core.collidepoint(mouse_pos):
                    stats["코어"] += 10
                    current_image = img_act_core
                    action_taken = True
                    msg_text = "플랭크 1분 버티기!"
                elif btn_sleep.collidepoint(mouse_pos):
                    condition = min(condition + 30, 100)
                    current_image = img_act_sleep
                    action_taken = True
                    msg_text = "쿨쿨... 근성장은 자는 동안 일어난다."
                elif btn_rest.collidepoint(mouse_pos):
                    condition = min(condition + 10, 100)
                    current_image = img_act_rest
                    action_taken = True
                    msg_text = "잠깐 휴식 중..."
                elif btn_eat_open.collidepoint(mouse_pos):
                    show_food_menu = True # 메뉴판 열기!
                    msg_text = "무엇을 먹을까?"

                if action_taken:
                    is_acting = True
                    action_end_time = current_time + 1000
                    # 운동하면 컨디션/영양소 감소 로직 (원하면 추가 가능)
                    if not btn_sleep.collidepoint(mouse_pos) and not btn_rest.collidepoint(mouse_pos):
                         condition = max(condition - 5, 0)

    # --- 상태 업데이트 ---
    if is_acting and current_time >= action_end_time:
        is_acting = False
        current_image = img_idle

    # 레벨 계산 (총점 100점마다 1레벨업)
    total_score = sum(stats.values())
    level = 1 + (total_score // 100)
    
    # 레벨별 이미지 진화
    if level >= 5 and not is_acting: # 레벨 5 넘으면 근육말
         current_image = img_final
    elif not is_acting:
         current_image = img_idle


    # --- 화면 그리기 ---
    screen.fill(WHITE)
    
    # 1. 정보창 (게이지바 표시)
    # 영양소 (오른쪽 상단)
    draw_bar(screen, 800, 30, nutrients["단백질"], 100, PURPLE, "단백질")
    draw_bar(screen, 800, 60, nutrients["탄수화물"], 100, ORANGE, "탄수화물")
    draw_bar(screen, 800, 90, nutrients["지방"], 100, YELLOW, "지방")
    
    # 운동 스탯 (왼쪽 상단)
    draw_bar(screen, 30, 30, stats["상체"], 200, RED, "상체 Lv")
    draw_bar(screen, 30, 60, stats["하체"], 200, BLUE, "하체 Lv")
    draw_bar(screen, 30, 90, stats["유산소"], 200, GRAY, "유산소 Lv")
    draw_bar(screen, 30, 120, stats["코어"], 200, BLACK, "코어 Lv")

    # 중앙 정보 (레벨 & 컨디션)
    level_txt = font_big.render(f"Lv.{level} 근육말", True, BLACK)
    screen.blit(level_txt, (SCREEN_WIDTH//2 - 80, 50))
    
    cond_color = BLUE if condition > 50 else RED
    draw_bar(screen, SCREEN_WIDTH//2 - 75, 90, condition, 100, cond_color, "컨디션")
    
    msg_surf = font_medium.render(msg_text, True, BLACK)
    screen.blit(msg_surf, (SCREEN_WIDTH//2 - msg_surf.get_width()//2, 650))


    # 2. 캐릭터
    if not show_food_menu:
        screen.blit(current_image, (SCREEN_WIDTH//2 - 175, 150))

    # 3. 버튼 그리기
    if show_food_menu:
        # 음식 메뉴판 배경 (반투명하게 하고 싶지만, 간단하게 회색 박스로)
        pygame.draw.rect(screen, (240, 240, 240), (250, 100, 500, 520))
        pygame.draw.rect(screen, BLACK, (250, 100, 500, 520), 3) # 테두리
        
        title = font_big.render("=== 오늘의 식단 ===", True, BLACK)
        screen.blit(title, (400, 120))

        for btn in food_buttons:
            # 음식 버튼 색상은 영양소 비율에 따라 다르게 할 수도 있지만 일단 통일
            draw_button(btn["name"], btn["rect"], WHITE)
            # 버튼 옆에 설명 추가 (옵션)
            btn_txt = font_small.render(food_menu[btn["name"]]['desc'], True, GRAY)
            screen.blit(btn_txt, (btn["rect"].x + 10, btn["rect"].y + 40))

        draw_button("닫기", btn_close_menu, RED)
        
    else:
        # 평소 운동 버튼들
        draw_button("상체", btn_upper, RED)
        draw_button("하체", btn_lower, BLUE)
        draw_button("유산소", btn_cardio, GRAY)
        draw_button("코어", btn_core, BLACK)
        
        draw_button("잠자기", btn_sleep, GREEN)
        draw_button("휴식", btn_rest, GREEN)
        draw_button("식사하기", btn_eat_open, ORANGE) # 식사 버튼 색 변경

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
