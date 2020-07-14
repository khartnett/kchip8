import sys, pygame
pygame.init()

size = width, height = 640, 320
speed = [2, 2]
black = 0, 0, 0
white = 255, 255, 255
drawFlag = False
opcode = 0
memory = [0] * 4096
V = [0] * 16 # Registers
I = 0 # Index Register
pc = 0 # Program Counter
sp = 0 # stack pointer
delay_timer = 0;
sound_timer = 0;

beepEffect = pygame.mixer.Sound('beep.wav')

chip8_fontset = [
    0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
    0x20, 0x60, 0x20, 0x20, 0x70, # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
    0x90, 0x90, 0xF0, 0x10, 0x10, # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
    0xF0, 0x10, 0x20, 0x40, 0x40, # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90, # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
    0xF0, 0x80, 0x80, 0x80, 0xF0, # C
    0xE0, 0x90, 0x90, 0x90, 0xE0, # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
    0xF0, 0x80, 0xF0, 0x80, 0x80  # F
]


screen = pygame.display.set_mode(size)

def fillPixel(x, y, color):
	screen.fill(color, pygame.Rect(x * 10, y * 10, 10, 10))

def setupGraphics():
    a = 0

def setupInput():
    a = 0

def initialize():
    global pc, opcode, I, sp, memory, delay_timer, sound_timer
    # Initialize registers and memory once
    pc     = 0x200  # Program counter starts at 0x200
    opcode = 0      # Reset current opcode
    I      = 0      # Reset index register
    sp     = 0      # Reset stack pointer

    # Clear display
    # Clear stack
    # Clear registers V0-VF
    # Clear memory

    # Load fontset
    for i in range(0, 79):
        memory[i] = chip8_fontset[i];

    # Reset timers
    delay_timer = 0
    sound_timer = 0

def loadGame(gameFile):
    global memory
    f = open(gameFile + ".ch8","rb")
    gameBytes = list(f.read())
    for i, gameByte in enumerate(gameBytes) :
        memory[i + 512] = gameByte
        print(str(i + 512) + ': ' + hex(gameByte))

    f.close()
    a = 0

def emulateCycle():
    global pc, opcode, I, sp, memory, delay_timer, sound_timer
    # Fetch Opcode
    opcode = memory[pc] << 8 | memory[pc + 1]
    # Decode Opcode
    decoded = opcode & 0xF000
    # Execute Opcode
    if decoded == 0xA000: # ANNN: Sets I to the address NNN
        I = opcode & 0x0FFF
        pc += 2
    elif decoded == 0x0000:
        sub_decoded = opcode & 0x000F
        if sub_decoded == 0x0000: # 0x00E0: Clears the screen
            print('0x00E0: Clears the screen')
        elif sub_decoded == 0x000E: # 0x00EE: Returns from subroutine
            print('0x00E0: Clears the screen')
        else:
            print ('Unknown opcode:[0x0000] ' + hex(opcode))
    elif decoded == 0x2000: # 0x2NNN:	Calls subroutine at NNN.
        stack[sp] = pc
        sp += 1
        pc = opcode & 0x0FFF
    else:
        print ('Unknown opcode: ' + hex(opcode))
    # Update timers
    if delay_timer > 0:
        delay_timer -= 1
    if sound_timer > 0:
        if sound_timer == 1:
            beepEffect.play()
        sound_timer -= 1

def drawGraphics():
    a = 0

def setKeys():
    a = 0

screen.fill(black)
fillPixel(0, 0, white)
fillPixel(1, 1, white)
fillPixel(63, 31, white)
pygame.display.flip()

ball = pygame.image.load("intro_ball.gif")
ballrect = ball.get_rect()

setupGraphics()
setupInput()
initialize()
loadGame('pong')
while 1:
    #emulateCycle()
    if (drawFlag) :
        drawGraphics()
    setKeys()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.KEYDOWN: # or event.type == pygame.KEYUP:
            print(event)
            beepEffect.play()
            if event.key == pygame.K_RIGHT:
                speed[0] += 1
            elif event.key == pygame.K_LEFT:
                speed[0] -= 1
            elif event.key == pygame.K_DOWN:
                speed[1] += 1
            elif event.key == pygame.K_UP:
                speed[1] -= 1

    ballrect = ballrect.move(speed)
    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > height:
        speed[1] = -speed[1]

    # screen.fill(black)
    screen.blit(ball, ballrect)
    pygame.display.flip()
