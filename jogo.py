import pygame
import sys
import random
from pygame.locals import *

# Set up pygame.
pygame.init()
mainClock = pygame.time.Clock()

# Configura janela.
WINDOWWIDTH = 400
WINDOWHEIGHT = 400
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
pygame.display.set_caption('Input')

# Configura cores.
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Configura tamanho dos elementos pedra/comida/teleporte.
FOODSIZE = 20
TELEPORTSIZE = 20
ROCKSIZE = 5

NEWFOOD = 40
NEWTELEPORT = 500

# Set up MAZE
maze_width = 10
cell_size = WINDOWWIDTH // maze_width  # Divide o width da tela em 10, pois o espaço ocupado por cada pedra será de 40 (400//10) ou seja, 10 pedras de largura)


def generate_maze(maze):
    print("=-"*25)
    for l in range(len(maze)):
        aleatorio = random.randint(1,5)
        while aleatorio > 0:
            for c in range(len(maze[l])):
                maze[l][c] = random.randint(0, 1) 
            print(maze[l])
            aleatorio-=1
    return maze

def create_food(drawGroup):
    '''Create new food sprite'''
    food = pygame.sprite.Sprite(drawGroup)
    food.image = pygame.image.load("data/img/banana.png")
    food.rect = pygame.Rect(random.randint(0, WINDOWWIDTH - FOODSIZE), random.randint(0, WINDOWHEIGHT - FOODSIZE), FOODSIZE, FOODSIZE)
    return food

def create_rock(x, y, drawGroup):
    '''Create new rock sprite at specified position'''
    rock = pygame.sprite.Sprite(drawGroup)
    rock.image = pygame.image.load("data/img/rock.png")
    rock.rect = pygame.Rect(x, y, ROCKSIZE, ROCKSIZE)
    return rock

def create_teleport(drawGroup):
    '''Create new teleport element sprite'''
    teleport_element = pygame.sprite.Sprite(drawGroup)
    teleport_element.image = pygame.image.load("data/img/teleport.png")
    teleport_element.rect = pygame.Rect(random.randint(0, WINDOWWIDTH - TELEPORTSIZE), random.randint(0, WINDOWHEIGHT - TELEPORTSIZE), TELEPORTSIZE, TELEPORTSIZE)
    return teleport_element

# Text function
def draw_text(windowSurface, text, size, text_col, position):
    font = pygame.font.Font(None, size)
    text = font.render(text, True, text_col)
    text_rect = text.get_rect(center=position)
    windowSurface.blit(text, text_rect)

# Sounds
bite = pygame.mixer.Sound("data/sounds/bite.wav")
teleport = pygame.mixer.Sound("data/sounds/teleport.wav")
fail = pygame.mixer.Sound("data/sounds/wrong.wav")
monkey_scream = pygame.mixer.Sound("data/sounds/monkey_scream.wav")
mouseOver_fx = pygame.mixer.Sound("data/sounds/mouseOver_soundfx.wav")
die_sound = pygame.mixer.Sound("data/sounds/die_sound.wav")
shrink_sound = pygame.mixer.Sound("data/sounds/shrink.wav")
teleportSpawn_sound = pygame.mixer.Sound("data/sounds/teleport_spawn.wav")
getTeleport_sound = pygame.mixer.Sound("data/sounds/get_teleport.wav")


maze = [
    [1, 1, 1, 1, 1, 0, 0, 1, 1, 1],
    [1, 1, 0, 1, 0, 0, 0, 0, 1, 1],
    [0, 0, 1, 1, 0, 0, 1, 0, 0, 0],
    [1, 0, 0, 0, 1, 1, 1, 1, 0, 1],
    [0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
    [1, 1, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 0, 0, 1, 1, 1]
]

# Função Menu Principal
def menu():
    # Carrega imagem de fundo do menu principal
    background = pygame.image.load("data/img/menu_background.png")
    background = pygame.transform.scale(background, (WINDOWWIDTH, WINDOWHEIGHT))

    click = False
    button_1_hover = False
    button_2_hover = False

    # Som ambiente do menu
    pygame.mixer.music.load("data/sounds/menu_ambience.wav")
    pygame.mixer.music.play(-1) # Toca infinitamente

    while True:
        windowSurface.blit(background, (0, 0))
        draw_text(windowSurface, 'Menu', 74, BLACK, (WINDOWWIDTH // 2, 50))

        # Armazena posicao do mouse
        mx, my = pygame.mouse.get_pos()

        button_1 = pygame.Rect(WINDOWWIDTH // 2 - 50, 150, 100, 50)
        button_2 = pygame.Rect(WINDOWWIDTH // 2 - 50, 250, 100, 50)


        if button_1.collidepoint((mx, my)):
            if not button_1_hover:
                mouseOver_fx.play()
                button_1_hover = True
            if click:
                monkey_scream.play()
                game()
        else:
            button_1_hover = False

        if button_2.collidepoint((mx, my)):
            if not button_2_hover:
                mouseOver_fx.play()
                button_2_hover = True
            if click:
                pygame.quit()
                sys.exit()
        else:
            button_2_hover = False

        pygame.draw.rect(windowSurface, BLACK, button_1)
        pygame.draw.rect(windowSurface, BLACK, button_2)
        draw_text(windowSurface, 'Jogar', 30, WHITE, button_1.center)
        draw_text(windowSurface, 'Sair', 30, WHITE, button_2.center)

        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        pygame.display.update()
        mainClock.tick(60)

# Função do jogo
def game():

    # Configura variáveis de movimento e velocidade
    moveLeft = False
    moveRight = False
    moveUp = False
    moveDown = False
    MOVESPEED = 6

    # Configura player
    player_width = 40
    player_height = 40
    player_hitbox = pygame.Rect(200, 200, player_width, player_height)
    original_hitbox_size = (player_width, player_height)  # Armazena tamanho original do player

    # Configura sprites
    drawGroup = pygame.sprite.Group()

    player = pygame.sprite.Sprite(drawGroup)
    player.image = pygame.image.load("data/img/monkey.png")
    player.rect = player_hitbox
    

    teleport_use = 3 # Variável para controlar quantidade de teleportes disponíveis
    points = 0 # Variável para controlar quantidade de bananas ingeridas (pontuação)
    points_color = (0, 0, 0) # Variável para controlar cor do texto da pontuação
    shrink_color = (0, 0, 0) # Variável para controlar cor do texto da habilidade de digerir

    teleport_timer = 0  # Timer para controlar criação de elementos de teleporte
    food_timer = 0  # Timer para controlar criação de bananas
    grow_timer = 0  # Timer para controlar cooldown de DIGERIR
    eat_timer = 0   # Timer para controlar quando o player ingeriu banana pela última vez
    timer_position = (450, 450) # Variável para controlar a posição do timer de "Game Over"
    timer_text = '5'

    # Create initial foods
    # foods = [create_food() for _ in range(20)]
    
    foods = []
    rocks = []
    teleports = []

    # Carrega Soundtrack do jogo
    pygame.mixer.music.load("data/sounds/game_soundtrack.wav")
    pygame.mixer.music.play(-1)

    # Gera matriz do labirinto
    final_maze = generate_maze(maze)

    # Cria paredes do labirinto
    for row_index, row in enumerate(final_maze):
        for col_index, cell in enumerate(row):
            if cell == 1:
                rock_x = col_index * cell_size
                rock_y = row_index * cell_size
                rocks.append(create_rock(rock_x, rock_y, drawGroup))

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_LEFT or event.key == K_a:
                    moveRight = False
                    moveLeft = True
                if event.key == K_RIGHT or event.key == K_d:
                    moveLeft = False
                    moveRight = True
                if event.key == K_UP or event.key == K_w:
                    moveDown = False
                    moveUp = True
                if event.key == K_DOWN or event.key == K_s:
                    moveUp = False
                    moveDown = True
            if event.type == KEYUP:
                # Close mouth
                # player.image = pygame.image.load("data/img/monkey.png")
                if event.key == K_ESCAPE:
                    return
                if event.key == K_LEFT or event.key == K_a:
                    moveLeft = False
                if event.key == K_RIGHT or event.key == K_d:
                    moveRight = False
                if event.key == K_UP or event.key == K_w:
                    moveUp = False
                if event.key == K_DOWN or event.key == K_s:
                    moveDown = False
                if event.key == K_x:
                    if teleport_use == 0:
                        fail.play()
                    else:
                        teleport_use -= 1
                        teleport.play()
                        # Teleporta para posição do mouse
                        player_hitbox.left = pygame.mouse.get_pos()[0] - player_hitbox.width//2
                        player_hitbox.top = pygame.mouse.get_pos()[1] - player_hitbox.height//2
                if event.key == K_c:
                    if grow_timer < 300:
                        fail.play()
                    elif grow_timer >= 300:
                        # Verifica se player não está no tamanho original
                        if player_width > original_hitbox_size[0] and player_height > original_hitbox_size[1]:
                            shrink_sound.play()
                            # Escala original
                            player.image = pygame.image.load("data/img/monkey.png")
                            # Hitbox original
                            player_width = original_hitbox_size[0]
                            player_height = original_hitbox_size[1]
                            player_hitbox = pygame.Rect(player_hitbox.left, player_hitbox.top, player_width, player_height)
                            player.rect = player_hitbox
                            grow_timer = 0  # Reseta grow_timer
                            shrink_color = (0,0,0)


        # Incrementa Contadores
        food_timer += 1
        grow_timer += 1
        eat_timer += 1
        teleport_timer += 1

        # Verifica timer desde a última banana ingerida       
        if eat_timer == 40:
            timer_text = '5'
            timer_position = (200, 250) # Muda posição do timer para que fique visível
        if eat_timer == 80:
            timer_text = '4'
        if eat_timer == 120:
            timer_text = '3'
        if eat_timer == 160:
            timer_text = '2'
        if eat_timer == 200:
            timer_text = '1'
        if eat_timer == 240:
            timer_text = '0'
            moveLeft = False
            moveRight = False
            moveUp = False
            moveDown = False
            pygame.mixer.music.stop()
            die_sound.play()
            gameOver(points) # Chama menu "Game Over"

        # Cria banana
        if food_timer >= NEWFOOD:
            food_timer = 0
            foods.append(create_food(drawGroup))

        # Cria elemento teleporte
        if teleport_timer >= NEWTELEPORT:
            teleport_timer = 0
            teleportSpawn_sound.play()
            teleports.append(create_teleport(drawGroup))


        windowSurface.fill(WHITE)

        # Armazena posição atual para caso de colisão com pedras
        initial_position = player_hitbox.topleft

        if moveDown:
            if player_hitbox.bottom > WINDOWHEIGHT:
                player_hitbox.bottom = 0 # Wrap around
            player_hitbox.top += MOVESPEED
        if moveUp:
            if player_hitbox.top < 0:
                player_hitbox.top = WINDOWHEIGHT
            player_hitbox.top -= MOVESPEED
        if moveLeft:
            if player_hitbox.left < 0:
                player_hitbox.left = WINDOWWIDTH
            player_hitbox.left -= MOVESPEED
        if moveRight:
            if player_hitbox.right > WINDOWWIDTH:
                player_hitbox.right = 0
            player_hitbox.right += MOVESPEED
        
        # Colisão com pedras
        for rock in rocks:
            if player_hitbox.colliderect(rock.rect):
                player_hitbox.topleft = initial_position
                break
        

        # Colisão com elementos de teleporte
        for teleport_element in teleports[:]:
            if player_hitbox.colliderect(teleport_element.rect):
                getTeleport_sound.play()
                teleport_use += 1
                teleports.remove(teleport_element)
                drawGroup.remove(teleport_element)
                
        # Colisão com bananas
        for food in foods[:]:
            if player_hitbox.colliderect(food.rect):
                eat_timer = 0
                timer_position = (450, 450) # Altera posição da contagem para que suma da tela
                bite.play()
                # Open mouth
                # player.image = pygame.image.load("data/img/open_mouth_monkey.png")
                points += 1
                print(f"Bananas: {points}")
                foods.remove(food)
                drawGroup.remove(food)
                if (points+1)%5 == 0:
                    points_color = RED # Muda cor do texto dos pontos para VERMELHO caso player esteja prestes a crescer
                if points%5 == 0: # Cresce a cada 5 bananas ingeridas
                    # Aumenta escala da imagem em 30%
                    player.image = pygame.transform.scale(player.image, (player.image.get_width() * 1.3, player.image.get_height() * 1.3))
                    # Aumenta hitbox em 30%
                    player_width = player_width*1.3 
                    player_height = player_height*1.3
                    player_hitbox = pygame.Rect(player_hitbox.left, player_hitbox.top, player_width, player_height)
                    player.rect = player_hitbox
                    points_color = BLACK # Volta texto dos pontos à cor padrão


        # Desenha Sprites
        drawGroup.draw(windowSurface)


        # Verifica se DIGERIR já está disponível
        if grow_timer >= 300:
            shrink_color = RED


        # Escreve textos na tela
        draw_text(windowSurface, 'Bananas: ' + str(points), 20, points_color, (50, 20))
        draw_text(windowSurface, 'Teleportes: ' + str(teleport_use), 20, (0, 0, 0), (50, 40))
        draw_text(windowSurface, 'DIGERIR', 60, shrink_color, (310, 370))
        draw_text(windowSurface, timer_text, 80, RED, timer_position)

        pygame.display.update()
        mainClock.tick(40)


def gameOver(score):
    # Carrega imagem de fundo do menu gameOver
    background = pygame.image.load("data/img/gameOver_background.png")
    background = pygame.transform.scale(background, (WINDOWWIDTH, WINDOWHEIGHT))
    
    click = False
    button_1_hover = False
    button_2_hover = False



    while True:
        windowSurface.blit(background, (0, 0))
        draw_text(windowSurface, 'Game Over', 74, WHITE, (WINDOWWIDTH // 2, 50))
        draw_text(windowSurface, f'Bananas: {score}', 30, WHITE, (WINDOWWIDTH // 2, 100))

        mx, my = pygame.mouse.get_pos()

        button_1 = pygame.Rect(WINDOWWIDTH // 2 - 200 // 2, 150, 200, 50)
        button_2 = pygame.Rect(WINDOWWIDTH // 2 - 200 // 2, 250, 200, 50)

        if button_1.collidepoint((mx, my)):
            if not button_1_hover:
                mouseOver_fx.play()
                button_1_hover = True
            if click:
                monkey_scream.play()
                game()
        else:
            button_1_hover = False

        if button_2.collidepoint((mx, my)):
            if not button_2_hover:
                mouseOver_fx.play()
                button_2_hover = True
            if click:
                menu()
        else:
            button_2_hover = False

        pygame.draw.rect(windowSurface, WHITE, button_1)
        pygame.draw.rect(windowSurface, WHITE, button_2)
        draw_text(windowSurface, 'Jogar Novamente', 30, BLACK, button_1.center)
        draw_text(windowSurface, 'Voltar ao Menu', 30, BLACK, button_2.center)

        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        pygame.display.update()
        mainClock.tick(60)


# Roda loop princpial
menu()