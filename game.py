import pygame
import sys

# --- 초기 설정 ---
pygame.init()
SCREEN_WIDTH = 1000 # 버튼이 많아져서 화면을 좀 넓혔습니다.
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("인터랙티브 근육말 키우기")
clock = pygame.time.Clock()

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 50, 50)    # 운동 계열
BLUE = (50, 50, 255)   # 하체
GREEN = (50, 200, 50)  # 휴식 계열

# 폰트 설정
try:
    font_big = pygame.font.SysFont("malgungothic", 30, bold=True)
    font_small = pygame.font.SysFont("malgungothic", 18)
except:
    font_big = pygame.font.Font(None, 40)
    font_small = pygame.font.Font(None, 24)

# --- 게임 변수 (스탯) ---
stats = {"상체": 0, "하체": 0, "유산소": 0, "코어": 0}
condition = 100 # 컨디션 스탯 추가 (휴식하면 회복)
total_score = 0

# --- 이미지 불러오기 함수 ---
def load_and_scale(filename):
    try:
        img = pygame.image.load(filename)
        return pygame.transform.scale(img, (350, 350)) # 그림 크기 통일
    except FileNotFoundError:
        print(f"오류: {filename} 파일을 찾을 수 없습니다.")
        sys.exit()

# 이미지 로딩 (파일명이 정확해야 합니다!)
img_idle = load_and_scale("horse_idle.png") # 기본 상태

# 행동 이미지들
img_act_upper = load_and_scale("act_upper.png")
img_act_lower = load_and_scale("act_lower.png")
img_act_cardio = load_and_scale("act_cardio.png")
img_act_core = load_and_scale("act_core.png")
img_act_sleep = load_and_scale("act_sleep.png")
img_act_rest = load_and_scale("act_rest.png")
img_act_eat = load_and_scale("act_eat.png")

# 최종 이미지 (선택사항, 일단 기본 이미지로 대체해둠)
try:
    img_final = load_and_scale("horse_final_muscle.png")
except:
    img_final = img_idle 


# --- 상태 관리 변수 ---
current_image = img_idle   # 현재 화면에 보여줄 이미지
is_acting = False          # 현재 말이 행동 중인가?
action_end_time = 0        # 행동이 끝나는 시간
ACTION_DURATION = 1000     # 행동 지속 시간 (ms 단위, 1000ms = 1초)


# --- 버튼 정의 함수 (코드를 깔끔하게 하기 위해) ---
def draw_button(txt, rect, color):
    pygame.draw.rect(screen, color, rect)
    text_surf = font_small.render(txt, True, WHITE)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

# 버튼 위치 정의 (2줄로 배치)
btn_w, btn_h = 120, 60
margin = 20
start_x = 50
row1_y = 500
row2_y = 580

# 윗줄: 운동 버튼
btn_upper = pygame.Rect(start_x, row1_y, btn_w, btn_h)
btn_lower = pygame.Rect(start_x + (btn_w+margin)*1, row1_y, btn_w, btn_h)
btn_cardio = pygame.Rect(start_x + (btn_w+margin)*2, row1_y, btn_w, btn_h)
btn_core = pygame.Rect(start_x + (btn_w+margin)*3, row1_y, btn_w, btn_h)

# 아랫줄: 휴식 버튼
btn_sleep = pygame.Rect(start_x, row2_y, btn_w, btn_h)
btn_rest = pygame.Rect(start_x + (btn_w+margin)*1, row2_y, btn_w, btn_h)
btn_eat = pygame.Rect(start_x + (btn_w+margin)*2, row2_y, btn_w, btn_h)


# --- 메인 게임 루프 ---
running = True
while running:
    current_time = pygame.time.get_ticks() # 현재 시간 측정

    # 1. 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN and not is_acting: # 행동 중이 아닐 때만 클릭 가능
            mouse_pos = event.pos
            action_taken = False # 행동을 했는지 체크

            # --- 운동 버튼 클릭 ---
            if btn_upper.collidepoint(mouse_pos):
                stats["상체"] += 10
                current_image = img_act_upper
                action_taken = True
                condition -= 5 # 운동하면 컨디션 하락
            elif btn_lower.collidepoint(mouse_pos):
                stats["하체"] += 10
                current_image = img_act_lower
                action_taken = True
                condition -= 5
            elif btn_cardio.collidepoint(mouse_pos):
                stats["유산소"] += 10
                current_image = img_act_cardio
                action_taken = True
                condition -= 5
            elif btn_core.collidepoint(mouse_pos):
                stats["코어"] += 10
                current_image = img_act_core
                action_taken = True
                condition -= 5
            
            # --- 휴식 버튼 클릭 ---
            elif btn_sleep.collidepoint(mouse_pos):
                condition += 30
                current_image = img_act_sleep
                action_taken = True
            elif btn_rest.collidepoint(mouse_pos):
                condition += 15
                current_image = img_act_rest
                action_taken = True
            elif btn_eat.collidepoint(mouse_pos):
                condition += 20
                current_image = img_act_eat
                action_taken = True

            # 행동을 시작했다면 타이머 설정
            if action_taken:
                is_acting = True
                action_end_time = current_time + ACTION_DURATION
                total_score = sum(stats.values())
                condition = min(condition, 100)      # 컨디션 최대 100 제한
                condition = max(condition, 0)        # 컨디션 최소 0 제한

    # 2. 게임 상태 업데이트 (타이머 체크)
    if is_acting and current_time >= action_end_time:
        # 행동 시간이 끝났으면 기본 상태로 복귀
        is_acting = False
        # 최종 진화 조건 체크 (예: 총점 200점 이상)
        if total_score >= 200:
             current_image = img_final
        else:
             current_image = img_idle


    # 3. 화면 그리기
    screen.fill(WHITE) # 배경

    # 스탯 표시
    info_txt = f"상체:{stats['상체']} 하체:{stats['하체']} 유산소:{stats['유산소']} 코어:{stats['코어']}"
    score_surf = font_small.render(info_txt, True, BLACK)
    screen.blit(score_surf, (30, 30))
    
    cond_txt = f"현재 컨디션: {condition} / 총 근육량: {total_score}"
    cond_surf = font_big.render(cond_txt, True, BLUE if condition > 50 else RED)
    screen.blit(cond_surf, (30, 60))

    # 캐릭터 그리기 (화면 중앙)
    screen.blit(current_image, (SCREEN_WIDTH//2 - 175, 120))

    # 버튼 그리기 (함수 활용)
    draw_button("상체(아령)", btn_upper, RED)
    draw_button("하체(스쿼트)", btn_lower, BLUE)
    draw_button("유산소(런닝)", btn_cardio, GRAY)
    draw_button("코어(플랭크)", btn_core, BLACK)
    
    draw_button("잠자기(Zzz)", btn_sleep, GREEN)
    draw_button("휴식하기", btn_rest, GREEN)
    draw_button("식사하기", btn_eat, GREEN)


    pygame.display.flip()
    clock.tick(60)

pygame.quit()