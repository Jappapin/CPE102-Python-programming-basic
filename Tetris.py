from random import randrange #สุ่มลำดับจำนวนตัวเลข
import pygame, sys

cell_size,cols,rows =	30,10,22 #กำหนดค่าขนาด cell จำนวนหลัก(columns) จำนวนแถว(rows)

colors = [(0,   0,   0),
		 (255, 85,  85),
		 (100, 200, 115),
		 (120, 108, 245),
		 (255, 140, 50 ),
		 (50,  120, 52 ),
		 (146, 202, 73 ),
		 (150, 161, 218 ),
		 (35,  35,  35)] #กำหนดค่าสีที่จะใช้

tetris_shapes = [[[1, 1, 1],	#รูปร่างบลอค
	 			[0, 1, 0]],
	 			 #รูปตัวT	
				[[0, 2, 2],
	 			[2, 2, 0]],
	 			 #รูปตัวS	
				[[3, 3, 0],
	 			[0, 3, 3]],
	 			 #รูปตัวZ	
				[[4, 0, 0],
	 			[4, 4, 4]],
	 			 #รูปตัวL	
				[[0, 0, 5],
	 			[5, 5, 5]],
	 			 #รูปตัวJ	
				[[6, 6, 6, 6]],
				 #เส้นตรง	
				[[7, 7],
	 			[7, 7]]] 
	 			#สีเหลี่ยมจัตุรัส
				
def rotate(shape): #หมุนบลอคทวนเข็มนาฬิกา
	return [ [ shape[y][x]for y in range(len(shape)) ]for x in range(len(shape[0]) - 1, -1, -1) ]

def check_collision(board, shape, offset): #เช็คว่ามีสิ่งกีดขวางรอบๆบลอคหรือไม่
	off_x, off_y = offset
	for cy, row in enumerate(shape):
		for cx, cell in enumerate(row):
			try:
				if cell and board[ cy + off_y ][ cx + off_x ]: #บลอคติดขอบ
					return True 
			except IndexError: 
			#เมื่อบลอคอยู่ทางขวาสุดของโซนเล่น ไม่ควรให้บลอคขยับออกนอกโซนเล่น ทางซ้ายเป็น 0 อยู่เล้วไม่สามารถเลื่อนแล้วตำแหน่งติดลบได้
				return True
	return False #ให้ค่า False เมื่อบลอคไม่มีสิ่งกีดขวางอยู่รอบ

def remove_row(board, row): #ลบแถวแล้วบวกด้วยแถวที่เป็น 0 (False) 
	del board[row]
	return [[False for i in range(cols)]] + board #cols = 10
	
def join_matrixes(mat1, mat2, mat2_off): 
#เมื่อบลอคตกถึงโซนเล่นด้านล่างให้รวมเป็นส่วน board ที่ไม่สามารถเลื่อนตำแหน่งได้
	off_x, off_y = mat2_off
	for cy, row in enumerate(mat2):
		for cx, val in enumerate(row):
			mat1[cy+off_y-1][cx+off_x] += val
	return mat1 #ให้ค่า board

def new_board(): #เคลียโซนเล่นให้เป็นพื้นที่ว่าง
	board = [ [ False for x in range(cols) ]for y in range(rows) ]#cols = 10 rows = 22
	board += [[ True for x in range(cols)]] #mark
	return board

class TetrisApp():
	def __init__(self):
		pygame.init() #เริ่มต้นใช้โมดูลในpygame
		pygame.key.set_repeat(300,25) 
		#เมื่อกดปุ่มค้างไว้จะทำงานซ้ำ 300 คือระยะห่างระหว่างการกดปุ่มครั้งแรกกับการทำงานซ้ำครั้งแรก 
		#25 คือระยะห่างระหว่างการทำซ้ำแต่ละครั้ง (หน่วยมิลลิวินาที)
		self.width = cell_size*(cols+6) #30*16 ความกว้างของหน้าต่างเกม
		self.height = cell_size*rows #30*22 ความสูงของหน้าต่างเกม
		self.rlim = cell_size*cols #30*10 ความกว้างของส่วนที่ใช้เล่น
		self.bground_grid = [[ 8 if x%2==y%2 else 0 for x in range(cols)] for y in range(rows)]
		#สีเทา(8)ในช่องที่ทั้งx%2และy%2มีค่าเท่ากัน
		self.default_font =  pygame.font.Font(pygame.font.get_default_font(), 18)
		#กำหนดฟอนต์ตัวอักษรและขนาดตัวอักษร
		self.screen = pygame.display.set_mode((self.width, self.height))
		#คำสั่งสร้างหน้าจอแสดงผลตามความกว้างและความสูงที่กำหนดไว้		
		self.init_game()
	
	def new_stone(self):
		self.stone = tetris_shapes[randrange(len(tetris_shapes))] 
		#กำหนดให้บลอคต่อไปที่จะหล่นลงมาสุ่มจาก list ของ tetris_shapes
		self.next_stone = tetris_shapes[randrange(len(tetris_shapes))]
		#ให้สุ่มบลอคใหม่ทุกครั้งที่เรียกใช้ฟังก์ชั่น
		self.stone_x = int(cols / 2 - len(self.stone)/2)
		self.stone_y = 0
		#กำหนดตำแหน่งให้บลอคใหม่เกิดด้านบนสุดตรงกลางของโซนที่ใช้		
		if check_collision(self.board,self.stone,(self.stone_x, self.stone_y)):
			self.gameover = True 
			#เมื่อบลอคที่สร้างใหม่ (next_stone) เจอสิ่งกีดขวางเกมจะจบ (Game over)
	
	def init_game(self): #ค่าเริ่มต้นเมื่อเริ่มเกม
		self.board = new_board()
		self.new_stone()
		self.score = 0
		pygame.time.set_timer(pygame.USEREVENT, 500) 
		#ฟังก์ชั่นที่เรียกใช้มีระยะเวลาห่างกัน 500 มิลลิวินาที (0.5วินาที)
	
	def disp_msg(self, msg, topleft): #ฟังก์ชั่นสร้างข้อความที่ปรากฏด้านขวามือของหน้าต่าง
		x,y = topleft
		for line in msg.splitlines(): 
		#แยกข้อความด้วยคำสั่ง splitlines เปลี่ยน string(msg) เป็นลิสต์ของสตริงเว้นแต่ละตัวด้วย \n วนจนครบทุกๆข้อความ(line)ในลิสต์
			self.screen.blit(self.default_font.render(line,True,(255,255,255)),(x,y)) 
			#สร้างข้อความ(line)ด้วยฟอนต์เริ่มต้น ลบเหลี่ยม สีขาว ที่จุด (x,y)
			y+=28 #ระยะห่างของแต่ละแถวข้อความ(line)ห่างกัน 28
	
	def center_msg(self, msg): #ฟังก์ชั่นสร้างข้อความที่กึ่งกลางของหน้าต่าง
		for i, line in enumerate(msg.splitlines()):
			msg_image =  self.default_font.render(line,True,(255,255,255))
			#กำหนดค่า msg_image เท่ากับการสร้างข้อความ(line)ด้วยฟอนต์เริ่มต้น ลบเหลี่ยม สีขาว		
			msgim_center_x, msgim_center_y = msg_image.get_size() #ความกว้างและความสูงของข้อความ
			msgim_center_x //= 2
			msgim_center_y //= 2
			self.screen.blit(msg_image,(30*8-msgim_center_x,30*11-msgim_center_y+i*28))
			#สร้างmsg_image ที่จุดกึ่งกลางของหน้าต่าง

	def draw_matrix(self, matrix, offset): #สร้างรูปสี่เหลี่ยม 
		off_x, off_y  = offset
		for y, row in enumerate(matrix): 
			for x, val in enumerate(row):
				if val: #เมื่อ val ไม่เท่ากับ 0
					pygame.draw.rect(self.screen,colors[val],pygame.Rect((off_x+x)*cell_size,(off_y+y)*cell_size, cell_size,cell_size),0)
                     #0 หมายถึงไม่มีเส้นขอบ แต่เติมวัตถุด้วยสีทั้งวัตถุ

	def add_score(self, n):
		combo = [0, 40, 100, 300]
		if n <= 2:self.score += combo[n]
		else:self.score += 300 
		#คะแนนบวกเพิ่มโดยถ้าทำคอมโบได้จะได้คะแนนพิเศษ สูงสุด 3 คอมโบ

	def move(self, delta_x): #ฟังก์ชั่นที่ใช้เลื่อนบลอคไปทางซ้ายขวา
		if not self.gameover and not self.paused:
			new_x = self.stone_x + delta_x
			if new_x < 0:
				new_x = 0 #กันไม่ให้บลอคออกนอกขอบโซนเล่นไปทางด้านซ้าย
			if new_x > cols - len(self.stone[0]):
				new_x = cols - len(self.stone[0]) #กันไม่ให้บลอคออกนอกโซนเล่นไปทางด้านขวา
			if not check_collision(self.board,self.stone,(new_x, self.stone_y)):
				#เมื่อเลื่อนแล้วไม่เจอสิ่งกีดขวาง 
				self.stone_x = new_x #เลื่อนเรียบร้อย

	def quit(self):
		sys.exit() #ออกจากหน้าต่างเกม
	
	def drop(self): 
		if not self.gameover and not self.paused:
			self.stone_y += 1 #ให้บลอคนั้นหล่นลงมาเรื่อยๆ
			if check_collision(self.board,self.stone,(self.stone_x, self.stone_y)): 
			#เมื่อบลอคชนพื้นด้านล่างหรือชนกับ board
				self.board = join_matrixes(self.board,self.stone,(self.stone_x, self.stone_y)) 
				#รวมบลอคนั้นเป็นส่วนหนึ่งของ board (ส่วนที่ไม่สามารถขยับได้)
				self.new_stone() #เรียกใช้ฟังก์ชั่นสร้าง(random)บลอคใหม่
				cleared_rows = 0 #กำหนดตัวแปร
				while True:
					for i, row in enumerate(self.board[:-1]): #เช็คแถวทุกแถว
						if 0 not in row: #ถ้าแถว(row)นั้นไม่มีช่องว่างเลย 
							self.board = remove_row(self.board, i) #ลบแถวนั้นออก
							cleared_rows += 1 # cleared_rows เก็บค่าจำนวนแถวที่เต็ม(ไม่มีช่องว่าง)
					else:
						break
				self.add_score(cleared_rows) #เรียกใช้ฟังก์ชั่นบวกคะแนนตามจำนวน cleared_rows
	
	def rotate_stone(self): 
		if not self.gameover and not self.paused: #ฟังก์ชั่นจะทำงานก็ต่อเมื่อเป็นไปตามเงื่อนไข
			new_stone = rotate(self.stone) #กำหนดค่า new_stone เท่ากับ บลอคที่หมุนทวนเข็มแล้ว
			if not check_collision(self.board,new_stone,(self.stone_x, self.stone_y)): 
			#เมื่อทำการหมุนบลอคแล้วไม่เจอสิ่งกีดขวาง
				self.stone = new_stone #หมุนบลอคเรียบร้อยแล้ว
	
	def toggle_pause(self):
		self.paused = not self.paused 
		#เมื่อเรียกใช้ฟังก์ชั่นจะเปลี่ยนค่า self.paused
	
	def start_game(self):
		if self.gameover:
			self.init_game()
			self.gameover = False 
			#เมื่อเรียกใช้ฟังก์ชั่นจะเป็นการเปลี่ยนค่า self.gameover และเรียกใช้ฟังก์ชั่น init_game()
	
	def run(self):
		key_actions = {	'ESCAPE':	self.quit,'LEFT':		lambda:self.move(-1),
			'RIGHT':	lambda:self.move(+1),'DOWN':		lambda:self.drop(),
			'UP':	self.rotate_stone,'p':	self.toggle_pause,'SPACE':	self.start_game}
		#กำหนดdictของปุ่ม(key)กับการทำงานเมื่อกดปุ่มนั้น(value)

		self.gameover,self.paused = False,False

		while True:
			self.screen.fill((0,0,0)) #สีพื้นหลังเป็นสีดำ
			if self.gameover: #เมื่อเกมจบ
				self.center_msg("Game Over!\nYour score: %d\nPress space bar to restart\nPress esc to exit" % self.score)
				#แสดงข้อความกึ่งกลางหน้าต่าง
			else:
				if self.paused: #เมื่อกด p (กดหยุดชั่วคราว)
					self.center_msg("Paused\nPress P to continue") #แสดงข้อความที่กึ่งกลางหน้าต่าง
				else:
					self.disp_msg("Control keys:\nDown : \n Drop stone \n faster\nLeft/Right : \n Move stone\nUp : \n Rotate Stone\nEsc : \n Quit game\nP : \n Pause game", 
						(self.rlim+cell_size, cell_size*5+75)) 
						#ปุ่มที่ใช้ในการเล่นและคำอธิบาย แสดงผลในตำแหน่งที่ระบุ(ด้านขวาล่างของหน้าต่าง)
					self.disp_msg("TETRIS GAME\n\nSCORE(s): \n%d" % (self.score),
						(self.rlim+cell_size,75)) 
						#ตัวนับคะแนน แสดงผลในตำแหน่งที่ระบุ(ด้านขวาบน)
					self.draw_matrix(self.bground_grid, (0,0)) #ตารางดำเทาด้านหลังโซนเล่น
					self.draw_matrix(self.board, (0,0)) #บลอคที่หล่นลงไปแล้ว ไม่ขยับ (board)
					self.draw_matrix(self.stone,(self.stone_x, self.stone_y)) #บลอคที่กำลังหล่นลงมา
			pygame.display.update() 

			for event in pygame.event.get():
				if event.type == pygame.USEREVENT:
					self.drop() #เรียกใช้ฟังก์ชั่นทุกๆ 0.5 วินาที
				elif event.type == pygame.QUIT:
					self.quit() #ปิดหน้าต่างเมื่อกดปุ่มกากบาทสีแดง
				elif event.type == pygame.KEYDOWN:
					for key in key_actions:
						if event.key == eval("pygame.K_"+key):
							key_actions[key]()

			pygame.time.Clock().tick(30) # 30 เฟรม ต่อวินาที
			pygame.display.set_caption("Tetris for Final Project") #ชื่อของหน้าต่าง
TetrisApp().run()
#References:    1) https://www.patanasongsivilai.com/blog/game-tetris/
#               2) https://gist.github.com/silvasur/565419
#               3) https://www.pygame.org/docs/index.html
#               4) https://theory.cpe.ku.ac.th/~pramook/418512/lecture06/pygame.ppt
