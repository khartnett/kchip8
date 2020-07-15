import sys, pygame, random
pygame.init()

size = width, height = 640, 320
speed = [2, 2]
black = 0, 0, 0
white = 255, 255, 255
drawFlag = False
runCycle = True
opcode = 0
memory = [0] * 4096
stack = [0] * 16
keysPressed = [0] * 16
waitForKey = False
waitForKeyV = 0
gfx = [0] * (64 * 32)
V = [0] * 16 # Registers
I = 0 # Index Register
pc = 0 # Program Counter
sp = 0 # stack pointer
delay_timer = 0
sound_timer = 0

beepEffect = pygame.mixer.Sound('beep.wav')

keyMap = {
    pygame.K_1: 0x01, pygame.K_2: 0x02, pygame.K_3: 0x03, pygame.K_4: 0x0C,
    pygame.K_q: 0x04, pygame.K_w: 0x05, pygame.K_e: 0x06, pygame.K_r: 0x0D,
    pygame.K_a: 0x07, pygame.K_s: 0x08, pygame.K_d: 0x09, pygame.K_f: 0x0E,
    pygame.K_z: 0x0A, pygame.K_x: 0x00, pygame.K_c: 0x0B, pygame.K_v: 0x0F,
}

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
    for i in range(0, 80):
        memory[i] = chip8_fontset[i]

    # Reset timers
    delay_timer = 0
    sound_timer = 0

def loadGame(gameFile):
    global memory
    f = open(gameFile + ".ch8","rb")
    gameBytes = list(f.read())
    #gameBytes = [0x60, 0x05, 0xF0, 0x29, 0x60, 0x00, 0x61, 0x00, 0xd0, 0x15, 0x12, 0x28]
    for i, gameByte in enumerate(gameBytes) :
        memory[i + 512] = gameByte
        #print(str(i + 512) + ': ' + hex(gameByte))
    f.close()

def emulateCycle():
    global pc, opcode, I, V, sp, memory, stack, gfx, drawFlag, delay_timer, sound_timer, runCycle, waitForKey, waitForKeyV
    # Fetch Opcode
    opcode = memory[pc] << 8 | memory[pc + 1]
    # print('pc: ' + hex(pc))
    pc += 2
    # Decode Opcode
    decoded = opcode & 0xF000
    NNN = opcode & 0x0FFF
    NN = opcode & 0x00FF
    N = opcode & 0x000F
    X = (opcode & 0x0F00) >> 8
    Y = (opcode & 0x00F0) >> 4
    unknownOp = False
    opDesc = ''
    # Execute Opcode
    if decoded == 0x0000:
        if NN == 0x00E0: # 0x00E0: Clears the screen
            opDesc = 'Clears the screen'
            gfx = [0] * (64 * 32)
            drawFlag = True
        elif NN == 0x00EE: # 0x00EE: Returns from subroutine
            opDesc = 'Returns from subroutine'
            sp -= 1
            pc = stack[sp]
        else:
            unknownOp = True
    elif decoded == 0x1000: # 0x1NNN:	Jumps to address NNN.
        opDesc = 'Jumps to address NNN'
        pc = NNN
    elif decoded == 0x2000: # 0x2NNN:	Calls subroutine at NNN.
        opDesc = 'Calls subroutine at NNN'
        stack[sp] = pc
        sp += 1
        pc = NNN
    elif decoded == 0x3000: # 0x3XNN:	Skips the next instruction if VX equals NN.
        opDesc = 'Skips the next instruction if VX equals NN'
        if (V[X] == NN):
            pc += 2
    elif decoded == 0x4000: # 0x4XNN:	Skips the next instruction if VX doesn't equal NN.
        opDesc = "Skips the next instruction if VX doesn't equal NN"
        if (V[X] != NN):
            pc += 2
    elif decoded == 0x5000: # 0x5XY0:	Skips the next instruction if VX equals VY.
        opDesc = 'Skips the next instruction if VX equals VY'
        if (V[X] == V[Y]):
            pc += 2
    elif decoded == 0x6000: # 0x6XNN:	Sets VX to NN.
        opDesc = 'Sets VX to NN'
        V[X] = NN
    elif decoded == 0x7000: # 0x7XNN:	Adds NN to VX. (Carry flag is not changed).
        opDesc = 'Adds NN to VX. (Carry flag is not changed)'
        V[X] += NN
        while (V[X] > 255):
            V[X] -= 256
    elif decoded == 0x8000:
        if N == 0x0000: # 0x8XY0 Sets VX to the value of VY.
            opDesc = 'Sets VX to the value of VY'
            V[X] = V[Y]
        elif N == 0x0001: # 0x8XY1 Sets VX to VX or VY. (Bitwise OR operation)
            opDesc = 'Sets VX to VX or VY. (Bitwise OR operation)'
            V[X] = V[X] | V[Y]
        elif N == 0x0002: # 0x8XY2 Sets VX to VX and VY. (Bitwise AND operation)
            opDesc = 'Sets VX to VX and VY. (Bitwise AND operation)'
            V[X] = V[X] & V[Y]
        elif N == 0x0003: # 0x8XY3 Sets VX to VX xor VY.
            opDesc = 'Sets VX to VX xor VY'
            V[X] = V[X] ^ V[Y]
        elif N == 0x0004: # 0x8XY4 Adds VY to VX. VF is set to 1 when there's a carry, and to 0 when there isn't.
            opDesc = "Adds VY to VX. VF is set to 1 when there's a carry, and to 0 when there isn't"
            V[X] += V[Y]
            if (V[X] > 255):
                V[X] -= 256
                V[0xF] = 1 # carry
            else:
                V[0xF] = 0
        elif N == 0x0005: # 0x8XY5 VY is subtracted from VX. VF is set to 0 when there's a borrow, and 1 when there isn't.
            opDesc = "VY is subtracted from VX. VF is set to 0 when there's a borrow, and 1 when there isn't"
            V[X] -= V[Y]
            if (V[X] < 0):
                V[X] += 256
                V[0xF] = 0
            else:
                V[0xF] = 1 # borrow
        elif N == 0x0006: # 0x8XY6 Stores the least significant bit of VX in VF and then shifts VX to the right by 1.
            opDesc = 'Stores the least significant bit of VX in VF and then shifts VX to the right by 1'
            V[0xF] = V[X] & 1
            V[X] >>= 1
        elif N == 0x0007: # 0x8XY7 Sets VX to VY minus VX. VF is set to 0 when there's a borrow, and 1 when there isn't.
            opDesc = "Sets VX to VY minus VX. VF is set to 0 when there's a borrow, and 1 when there isn't"
            V[X] = V[Y] - V[X]
            if (V[X] < 0):
                V[X] += 256
                V[0xF] = 0
            else:
                V[0xF] = 1 # borrow
        elif N == 0x000E: # 0x8XYE Stores the most significant bit of VX in VF and then shifts VX to the left by 1.
            opDesc = 'Stores the most significant bit of VX in VF and then shifts VX to the left by 1'
            V[0xF] = V[X] & 0x80
            V[X] <<= 1
        else:
            unknownOp = True
    elif decoded == 0xA000: # ANNN: Sets I to the address NNN
        opDesc = 'Sets I to the address NNN'
        I = NNN
    elif decoded == 0xB000: # BNNN: Jumps to the address NNN plus V0
        opDesc = 'Jumps to the address NNN plus V0'
        I = NNN + V[0]
    elif decoded == 0xC000: # CXNN: Sets VX to the result of a bitwise and operation on a random number (Typically: 0 to 255) and NN
        opDesc = 'Sets VX to the result of a bitwise and operation on a random number'
        V[X] = random.randint(0, 255) & NN
    elif decoded == 0xD000: # Draws a sprite at coordinate (VX, VY) that has a width of 8 pixels and a height of N pixels
        opDesc = 'Draws a sprite at coordinate (VX, VY) that has a width of 8 pixels and a height of N pixels'
        screen_x = V[X]
        screen_y = V[Y]
        V[0xF] = 0
        for yline in range(0, N):
            pixel = memory[I + yline]
            for xline in range(0, 8):
                if ((pixel & (0x80 >> xline)) != 0):
                    gfx_index = (screen_x + xline + ((screen_y + yline) * 64)) % (64 * 32)
                    if(gfx[gfx_index] == 1):
                        V[0xF] = 1
                    gfx[gfx_index] ^= 1
        drawFlag = True
    elif decoded == 0xE000:
        if NN == 0x009E: # 0xEX9E Skips the next instruction if the key stored in VX is pressed.
            opDesc = 'Skips the next instruction if the key stored in VX is pressed'
            if keysPressed[V[X]] == 1:
                pc = pc + 2
        elif NN == 0x00A1: # 0xEXA1 Skips the next instruction if the key stored in VX isn't pressed.
            opDesc = "Skips the next instruction if the key stored in VX isn't pressed"
            if keysPressed[V[X]] == 0:
                pc = pc + 2
        else:
            unknownOp = True
    elif decoded == 0xF000:
        if NN == 0x0007: # 0xFX07 Sets VX to the value of the delay timer.
            opDesc = 'Sets VX to the value of the delay timer'
            V[X] = delay_timer
        elif NN == 0x000A: # 0xFX0A A key press is awaited, and then stored in VX. (Blocking)
            opDesc = 'A key press is awaited, and then stored in VX'
            waitForKeyV = X
            runCycle = False
            waitForKey = True
        elif NN == 0x0015: # 0xFX15 Sets the delay timer to VX.
            opDesc = 'Sets the delay timer to VX'
            delay_timer = V[X]
        elif NN == 0x0018: # 0xFX18 Sets the sound timer to VX.
            opDesc = 'Sets the sound timer to VX'
            sound_timer = V[X]
        elif NN == 0x001E: # 0xFX1E Adds VX to I. VF is not affected.
            opDesc = 'Adds VX to I. VF is not affected'
            I += V[X]
        elif NN == 0x0029: # 0xFX29 Sets I to the location of the sprite for the character in VX. Characters 0-F (in hexadecimal) are represented by a 4x5 font.
            opDesc = 'Sets I to the location of the sprite for the character in VX. Characters 0-F'
            I = V[X] * 5
        elif NN == 0x0033: # Stores the Binary-coded decimal representation of VX at the addresses I, I plus 1, and I plus 2
            opDesc = 'Stores the Binary-coded decimal representation of VX at the addresses I, I plus 1, and I plus 2'
            memory[I]     = V[X] // 100
            memory[I + 1] = (V[X] // 10) % 10
            memory[I + 2] = (V[X] % 100) % 10
        elif NN == 0x0055: # 0xFX55 Stores V0 to VX (including VX) in memory starting at address I
            opDesc = 'Stores V0 to VX (including VX) in memory starting at address I'
            for v_index in range(0, X + 1):
                V[v_index] = memory[I + v_index]
        elif NN == 0x0065: # 0xFX65 Fills V0 to VX (including VX) with values from memory starting at address I. The offset from I is increased by 1 for each value written, but I itself is left unmodifie
            opDesc = 'Fills V0 to VX (including VX) with values from memory starting at address I'
            for v_index in range(0, X + 1):
                memory[I + v_index] = V[v_index]
        else:
            unknownOp = True
    else:
        unknownOp = True


    if unknownOp:
        print ('Unknown opcode: ' + hex(opcode))
        runCycle = False
    else:
        print ('opcode: ' + hex(opcode) + ' : ' + opDesc)
        # print ('V')
        # printIndexList(V)
        # print ('I ' + hex(I))

    if opcode == 0x1228:
        runCycle = False
    # Update timers
    if delay_timer > 0:
        delay_timer -= 1
    if sound_timer > 0:
        if sound_timer == 1:
            beepEffect.play()
        sound_timer -= 1

def drawGraphics():
    global gfx, drawFlag, runCycle
    screen.fill(black)
    for pixelIndex, pixel in enumerate(gfx):
        if pixel:
            fillPixel(pixelIndex % 64, pixelIndex // 64, white)
    pygame.display.flip()
    # print (gfx)
    # exit()
    drawFlag = False
    #runCycle = False

def setKeys():
    global keysPressed, runCycle, waitForKey, waitForKeyV, V
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.KEYDOWN: # or event.type == pygame.KEYUP:
            if event.key in keyMap:
                keysPressed[keyMap[event.key]] = 1
                if waitForKey == True:
                    V[waitForKeyV] = keyMap[event.key]
                    runCycle = True
                    waitForKey = False
            print(event)
        if event.type == pygame.KEYUP:
            if event.key in keyMap:
                keysPressed[keyMap[event.key]] = 0
            print(event)

def printIndexList(theList, perLine = 10):
    listToPrint = []
    for lindex, litem in enumerate(theList):
        listToPrint.append(hex(lindex) + ' => ' + hex(litem))
        if (len(listToPrint) >= perLine):
            print(', '.join(listToPrint))
            listToPrint = []
    if (len(listToPrint) >= 0):
        print(', '.join(listToPrint))
# screen.fill(black)
# fillPixel(0, 0, white)
# fillPixel(1, 1, white)
# fillPixel(63, 31, white)
# pygame.display.flip()

ball = pygame.image.load("intro_ball.gif")
ballrect = ball.get_rect()

setupGraphics()
setupInput()
random.seed()
initialize()
loadGame('kt') #si') #'pong') ll
printIndexList(memory)
#exit()
while 1:
    if (runCycle) :
        emulateCycle()
        if (drawFlag) :
            drawGraphics()
    setKeys()

    # for event in pygame.event.get():
    #     if event.type == pygame.QUIT: sys.exit()
    #     if event.type == pygame.KEYDOWN: # or event.type == pygame.KEYUP:
    #         print(event)
    #         beepEffect.play()
    #         if event.key == pygame.K_RIGHT:
    #             speed[0] += 1
    #         elif event.key == pygame.K_LEFT:
    #             speed[0] -= 1
    #         elif event.key == pygame.K_DOWN:
    #             speed[1] += 1
    #         elif event.key == pygame.K_UP:
    #             speed[1] -= 1

    # ballrect = ballrect.move(speed)
    # if ballrect.left < 0 or ballrect.right > width:
    #     speed[0] = -speed[0]
    # if ballrect.top < 0 or ballrect.bottom > height:
    #     speed[1] = -speed[1]

    # screen.fill(black)
    # screen.blit(ball, ballrect)
    # pygame.display.flip()
