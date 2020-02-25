import pygame
import gameparts
import random

#initializing the mixer before pygame gets rid of audio lag https://stackoverflow.com/questions/18273722/pygame-sound-delay
pygame.mixer.init(frequency=44100, buffer=512)
pygame.init()

#display size variables
screenWidth = 420
screenHeight = 500
fieldMargin = 20

#settings variables
musicEnabled = True
sfxEnabled = True

#data variables
shapeNames = [b'I', b'J', b'L', b'O', b'S', b'T', b'Z']#shapeNames = [b'O']
bgImg = pygame.image.load('data/images/bg.png')
dropSound = pygame.mixer.Sound('data/audio/drop.ogg')

pygame.mixer.music.load('data/audio/music.ogg')
pygame.mixer.music.play(loops=-1) #loop the music forever

#timing variables
paused = False
clock = pygame.time.Clock()
FPS = 60  # Frames per second.
speedUnit = 500 #ms
dropSpeed = 10
currentSpeed = 1
speedTime = speedUnit//currentSpeed

#pygame screen setup
screen = pygame.display.set_mode((screenWidth, screenHeight),pygame.HWSURFACE)
pygame.display.set_caption('Water Wall')

#game part initialization
scoreBoard = gameparts.ScoreBoard(screen)
gameField = gameparts.GameField(10, 24, screenWidth, screenHeight, fieldMargin, screen, scoreBoard)
newPiece = gameparts.Piece(gameField, random.choice(shapeNames), 3, 0)

#next piece selector block, start off with a null piece (no blocks in it)
nextPiece = random.randint(0, len(shapeNames) - 1)
gameField.setNextPiece(newPiece.shapes[b'N'])


def init(scoreBoard, gameField):
	global nextPiece

	#reset the game speed
	currentSpeed = 1
	speedTime = speedUnit//currentSpeed
	pygame.time.set_timer(pygame.USEREVENT, speedTime) #reset the timer

	#reset the game pieces
	screen.blit(bgImg, (0,0))
	gameField.reset()
	newPiece.reset(shapeNames[nextPiece], gameField, 3, 0)
	scoreBoard.reset()

	#next piece display block
	nextPiece = random.randint(0, len(shapeNames) - 1)
	gameField.setNextPiece(newPiece.shapes[shapeNames[nextPiece]])
	
	#render
	scoreBoard.render()
	gameField.render()
	pygame.display.update()


def setSounds(musicEnabled, sfxEnabled, musicOrSFX):
	if not paused:
		pygame.time.set_timer(pygame.USEREVENT, 0) #prevent this from affecting the dropping of a piece

		if musicOrSFX: #make sure only one text will show at once
			if musicEnabled:
				pygame.mixer.music.set_volume(1.0)
				scoreBoard.setBigText(gameField, "Music on")
				pygame.display.update()
			else:
				pygame.mixer.music.set_volume(0.0)
				scoreBoard.setBigText(gameField, "Music off")
				pygame.display.update()
		else:
			if sfxEnabled:
				dropSound.set_volume(1.0)
				scoreBoard.setBigText(gameField, "SFX on")
				pygame.display.update()
			else:
				dropSound.set_volume(0.0)
				scoreBoard.setBigText(gameField, "SFX off")
				pygame.display.update()

		pygame.time.wait(1000) #display the sound status for 1 second
		pygame.event.clear()
		pygame.time.set_timer(pygame.USEREVENT, speedTime)
	

def processFrame(newPiece, gameField, scoreBoard, drop=True):
	global nextPiece
	global paused
	result = 0

	#drop handler
	if drop:
		returnValue = newPiece.dropOne(gameField) #drop the piece by one cell
		if returnValue == 1: #if the piece collided within the playable area..
			
			#save the field and check it for completed lines
			gameField.applyField()
			gameField.checkLines(speedTime, screen, scoreBoard)

			#move piece back above board and add to score
			newPiece.reset(shapeNames[nextPiece], gameField, 3, 0)
			scoreBoard.addScore(2) #user gains 2 points every time a piece is placed

			#next piece selector block
			nextPiece = random.randint(0, len(shapeNames) - 1)
			gameField.setNextPiece(newPiece.shapes[shapeNames[nextPiece]])

			#render
			gameField.reShow()
			screen.blit(bgImg, (0,0))
			scoreBoard.render()
			gameField.render()
			pygame.display.update()
			result = 1 #piece collided

		elif returnValue == 2: #if the piece collided above the playable area...

			#game over
			gameField.setNextPiece(newPiece.shapes[b'N'])
			if scoreBoard.score > scoreBoard.hiScore:
				scoreBoard.writeHiScore()
			
			#render
			#gameField.reShow()
			screen.blit(bgImg, (0,0))
			scoreBoard.render()
			gameField.render()

			scoreBoard.gameOver(gameField)

			pygame.display.update()
			result = 1 #piece collided

			#wait for F to be pressed or window to be closed
			waitingForF = True
			while waitingForF:
				event = pygame.event.wait()
				if event.type == pygame.QUIT:
					if scoreBoard.score > scoreBoard.hiScore:
						scoreBoard.writeHiScore()
					quit()
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_f:
						waitingForF = False
						pygame.time.set_timer(pygame.USEREVENT, 0)
						init(scoreBoard, gameField)

		elif returnValue == 3: #if the piece came in contact with another one or the floor...
			#play a sound
			dropSound.play()

			#allow 1.5 seconds for the player to adjust the piece
			pygame.time.set_timer(pygame.USEREVENT, 0)
			pygame.time.set_timer(pygame.USEREVENT, 1500)
			result = 0 #piece did not collide
			

	#render
	screen.blit(bgImg, (0,0))
	gameField.render()
	scoreBoard.render()
	pygame.display.update()
	return result

#this will show the title screen until the user presses space, also allowing them to view the help screen if they want to
scoreBoard.titleScreen() 

#this will initialize the game
init(scoreBoard, gameField)

#Game Event Loop==========================================
while True:
	clock.tick(FPS)
	#Input================================================
	#program will pause here until an event happens (input or timer)
	event = pygame.event.wait()

	if event.type == pygame.QUIT: #if the user clicks the close button on the window...
		if scoreBoard.score > scoreBoard.hiScore:
			scoreBoard.writeHiScore()
		quit()


	elif event.type == pygame.KEYDOWN and not paused: #only check these inputs if the game is not paused

		if event.key == pygame.K_LEFT or event.key == pygame.K_a: #move left
			newPiece.left(gameField)
			processFrame(newPiece, gameField, scoreBoard, drop=False)

		if event.key == pygame.K_RIGHT or event.key == pygame.K_d: #move right
			newPiece.right(gameField)
			processFrame(newPiece, gameField, scoreBoard, drop=False)

		if event.key == pygame.K_DOWN or event.key == pygame.K_s: #hold for soft drop
			speedTime = speedUnit//dropSpeed
			processFrame(newPiece, gameField, scoreBoard, drop=True)
			pygame.time.set_timer(pygame.USEREVENT, 0)
			pygame.time.set_timer(pygame.USEREVENT, speedTime)

		if event.key == pygame.K_x or event.key == pygame.K_m: #rotate right
			newPiece.rotateRight(gameField)
			processFrame(newPiece, gameField, scoreBoard, drop=False)

		if event.key == pygame.K_z or event.key == pygame.K_n: #rotate left
			newPiece.rotateLeft(gameField)
			processFrame(newPiece, gameField, scoreBoard, drop=False)

		if event.key == pygame.K_SPACE: #hard drop
			resultValue = 0
			while resultValue == 0: #drop one until a collision is detected
				resultValue = processFrame(newPiece, gameField, scoreBoard, drop=True)
				

	elif event.type == pygame.KEYUP and not paused: #only check these inputs if the game is not paused

		if event.key == pygame.K_DOWN or event.key == pygame.K_s: #stop softdropping
			speedTime = speedUnit // currentSpeed
			processFrame(newPiece, gameField, scoreBoard, drop=False)
			pygame.time.set_timer(pygame.USEREVENT, 0)
			pygame.time.set_timer(pygame.USEREVENT, speedTime)

	elif event.type == pygame.USEREVENT: #time to process and render a new frame
		processFrame(newPiece, gameField, scoreBoard, drop=True)


	if event.type == pygame.KEYDOWN: #check these inputs at any time
		if event.key == pygame.K_f:
			if paused:
				if scoreBoard.score > scoreBoard.hiScore:
					scoreBoard.writeHiScore()
				#render
				screen.blit(bgImg, (0,0))
				gameField.render()
				scoreBoard.render()
				scoreBoard.setBigText(gameField, "Byeee", shaded=True)
				pygame.display.update()
				pygame.time.wait(500)
				quit()

		if event.key == pygame.K_o: #toggle music
			musicEnabled = not musicEnabled
			setSounds(musicEnabled, sfxEnabled, True)
		if event.key == pygame.K_p: #toggle sfx
			sfxEnabled = not sfxEnabled
			setSounds(musicEnabled, sfxEnabled, False)

		if event.key == pygame.K_ESCAPE: #pause and unpause
			paused = not paused
			if paused:
				pygame.time.set_timer(pygame.USEREVENT, 0)
				#render
				screen.blit(bgImg, (0,0))
				gameField.render()
				scoreBoard.render()
				scoreBoard.setBigText(gameField, "PAUSED", subText="Press F to quit.", shaded=True)
				pygame.display.update()
			else:
				for i in range(3, 0, -1): #3 2 1 countdown
					#render
					screen.blit(bgImg, (0,0))
					gameField.render()
					scoreBoard.render()
					scoreBoard.setBigText(gameField, str(i) + "...", shaded=False)
					pygame.display.update()
					pygame.time.wait(1000)
				pygame.event.clear() #to prevent any keypresses during pause from being processed in the next frame
				processFrame(newPiece, gameField, scoreBoard, drop=False)
				pygame.time.set_timer(pygame.USEREVENT, speedTime)

