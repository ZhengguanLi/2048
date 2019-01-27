import numpy, sys, random, pygame
from pygame.locals import*

Size = 4                                          #4*4行列
Block_WH = 110                                    #每个块的长度宽度
BLock_Space = 10                                  #两个块之间的间隙
Block_Size = Block_WH * Size + (Size + 1) * BLock_Space
Matrix = numpy.zeros([Size,Size])                 #初始化矩阵4*4的0矩阵
Screen_Size = (Block_Size, Block_Size+110)
Title_Rect = pygame.Rect(0, 0, Block_Size,110)      #设置标题矩形的大小
Score = 0

#数块颜色
Block_Color = {
        0:(150,150,150),
        2:(255,255,255),
        4:(255,255,128),
        8:(255,255,0),
        16:(255,220,128),
        32:(255,220,0),
        64:(255,190,0),
        128:(255,160,0),
        256:(255,130,0),
        512:(255,100,0),
        1024:(255,70,0),
        2048:(255,40,0),
        4096:(255,10,0),
}

#基础类
class UpdateNew(object):
	def __init__(self,matrix):
		super(UpdateNew, self).__init__()
		self.matrix = matrix
		self.score = 0
		self.zerolist = []

	def combine_row(self,row):
		# add same number together, e.g. 2 2 4 0 0 0 => 8 0 0 0 0 0

		start = 0
		end = Size - row.count(0) - 1
		while start < end:
			if row[start] == row[start+1]:
				row[start] *= 2
				row[start+1:] = row[start+2:]
				row.append(0)

				self.score += int(row[start]) # update score
			start += 1
		return row

	def remove_zero(self, row):
		# e.g. 2 0 2 0 0 4 ==> 2 2 4 0 0 0

		while True:
			temp_row = row[:]
			try:
				row.remove(0)
				row.append(0)
			except:
				pass
			
			# if all non-zero numbers are moved to left
			if row == temp_row:
				break

		return self.combine_row(row)

	def to_sequence(self, matrix):
		temp_matrix = matrix.copy()
		m, n = matrix.shape
		for i in range(m):
			new_row = self.remove_zero(list(matrix[i]))
			matrix[i] = new_row
			for k in range(Size - 1, Size - new_row.count(0) - 1, -1):     #添加所有没有值的坐标
				self.zerolist.append((i, k))
		if matrix.min() == 0 and (matrix != temp_matrix).any(): #矩阵中有最小值0且移动后的矩阵不同，才可以添加0位置处添加随机数
			GameInit.init_data(Size,matrix, self.zerolist)
			
		return matrix
	                      

class LeftAction(UpdateNew):
	def __init__(self,matrix):
		super(LeftAction, self).__init__(matrix)

	def handle_data(self):
		matrix = self.matrix.copy()
		temp_matrix = self.to_sequence(matrix)
		return temp_matrix, self.score

class RightAction(UpdateNew):
	def __init__(self,matrix):
		super(RightAction, self).__init__(matrix)

	def handle_data(self):
		matrix = self.matrix.copy()[:,::-1]
		temp_matrix = self.to_sequence(matrix)
		return temp_matrix[:,::-1],self.score

class UpAction(UpdateNew):
	def __init__(self,matrix):
		super(UpAction, self).__init__(matrix)

	def handle_data(self):
		matrix = self.matrix.copy().T
		temp_matrix = self.to_sequence(matrix)
		return temp_matrix.T, self.score


class DownAction(UpdateNew):
	def __init__(self,matrix):
		super(DownAction, self).__init__(matrix)

	def handle_data(self):
		matrix = self.matrix.copy()[::-1].T
		temp_matrix = self.to_sequence(matrix)
		return temp_matrix.T[::-1], self.score


class GameInit(object):
	def __init__(self):
		super(GameInit, self).__init__()

	@staticmethod
	def get_rand_pos(zerolist = None):
		if zerolist == None:
			i = random.randint(0, Size-1)
			j = random.randint(0, Size-1)
		else:
			i, j = random.sample(zerolist, 1)[0]
		return i, j

	@staticmethod
	def get_random_num():
		n = random.random()
		if n > 0.8:
			n = 4
		else:
			n = 2
		return n


	@classmethod
	def init_data(cls, Size, matrix = None, zeros_pos = None):
		if matrix is None:
			matrix = Matrix.copy()
		i, j = cls.get_rand_pos(zeros_pos) #zerolist空任意返回(x,y)位置，否则返回任意一个0元素位置
		rand = cls.get_random_num()
		matrix[i][j] = rand

		return matrix

	@classmethod
	def draw_surface(cls, screen, matrix, score):
		pygame.draw.rect(screen, (255, 255, 255), Title_Rect)              #第一个参数是屏幕，第二个参数颜色，第三个参数rect大小，第四个默认参数
		font1 = pygame.font.SysFont('simsun', 48)
		font2 = pygame.font.SysFont(None, 32)
		screen.blit(font1.render('Score:', True, (255,127,0)), (20,25))     #font.render第一个参数是文本内容，第二个参数是否抗锯齿，第三个参数字体颜色
		screen.blit(font1.render('%s' % score, True, (255,127,0)), (170,25))
		screen.blit(font2.render('up', True, (255,127,0)), (360,20))
		screen.blit(font2.render('left  down  right', True, (255,127,0)), (300,50))
		m, n = matrix.shape
		for i in range(m):
			for j in range(n):
				cls.draw_block(screen,i,j,Block_Color[matrix[i][j]],matrix[i][j])


	@staticmethod
	def draw_block(screen, row, column, color, blocknum):
		font = pygame.font.SysFont('stxingkai', 80)
		w = column * Block_WH + (column + 1) * BLock_Space
		h = row * Block_WH + (row + 1) * BLock_Space + 110
		pygame.draw.rect(screen, color, (w, h, 110, 110))
		if blocknum != 0:
			fw,fh = font.size(str(int(blocknum)))
			screen.blit(font.render(str(int(blocknum)), True, (0, 0, 0)), (w + (110 - fw)/2, h + (110 - fh)/2))

	@staticmethod
	def keyDownPressed(keyvalue,matrix):
		if keyvalue == K_LEFT:
			return LeftAction(matrix)
		elif keyvalue == K_RIGHT:
			return RightAction(matrix)
		elif keyvalue == K_UP:
			return UpAction(matrix)
		elif keyvalue == K_DOWN:
			return DownAction(matrix)

	@staticmethod
	def game_over(matrix):
	# return if game is over if all blocks are filled
		temp_matrix = matrix.copy()
		m, n = temp_matrix.shape
		for i in range(m):
			for j in range(n - 1):
				if temp_matrix[i][j] == temp_matrix[i][j+1]: #如果每行存在相邻两个数相同，则游戏没有结束
					print('游戏没有结束')
					return False
		for i in range(n):
			for j in range(m - 1):
				if temp_matrix[j][i] == temp_matrix[j+1][i]:
					print('游戏没有结束')
					return False
		print('Game Over')
		return True

def main():
	# initialize
	pygame.init()
	current_score = 0 # initialize score to 0

	screen = pygame.display.set_mode(Screen_Size, 0, 32) # 屏幕设置
	matrix = GameInit.init_data(Size)
	GameInit.draw_surface(screen, matrix, current_score)
	pygame.display.update()

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit(0)
			elif event.type == pygame.KEYDOWN:
				actionObject = GameInit.keyDownPressed(event.key,matrix)  #创建各种动作类的对象
				matrix, score = actionObject.handle_data()
				current_score += score   
				GameInit.draw_surface(screen, matrix, current_score)
				if matrix.min() != 0:
					GameInit.game_over(matrix)

		pygame.display.update()

if __name__ == '__main__':
	main()