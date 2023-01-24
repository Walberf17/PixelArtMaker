import pygame as pg, sys

# variables
font1 = pg.font.SysFont('Arial', 86, False, False)
font2 = pg.font.SysFont('Arial', 50, False, False)


def calc_proportional_size(expected=None, max_area=(1, 1), max_rect=None):
	"""
	It calculates a proportional thing to the given rect and max size, given in units.
	The max size is the proportion, max size of the rect, in units.
	:param expected: a list or tuple with the size in meters
	:param max_area: a list with the max are of the thing that you want to compare
	:param max_rect: pygame.Rect, the rect that you want to compare
	:return:
	"""
	if max_rect is None:
		raise EOFError(f'Max rect not found')
	max_sizes = pg.Vector2(max_rect.size)
	proportion = max_sizes.elementwise() / max_area

	if expected is None:
		expected = [1, 1]

	if type(expected) in [float, int]:
		return (proportion[1] * expected)
	elif len(expected) == 2:
		return proportion.elementwise() * expected
	elif len(expected) == 4:
		pos = proportion.elementwise() * expected[:2] + max_rect.topleft
		size = proportion.elementwise() * expected[2:]
		return [pos, size]
	else:
		raise TypeError(f'value not good enought, {expected}')


# classes
class Marker:
	def __init__(self, area, rect_to_be, center=(.5, .5), horizontal=True, groups=None):
		self.rect = pg.Rect([0., 0], calc_proportional_size(area, max_rect=rect_to_be))
		self.horizontal = horizontal
		self.rect_to_be = rect_to_be
		self.rect.center = calc_proportional_size(center, max_rect=rect_to_be)
		new_w = self.rect.w
		new_h = self.rect.h
		if self.horizontal:
			new_w *= .1
		else:
			new_h *= .1
		self.pointer = pg.Rect(calc_proportional_size((0, 0, new_w, new_h), max_rect=rect_to_be))
		self.pointer = self.pointer.fit(self.rect)
		self.pointer.center = self.rect.center
		self.clicked = False
		if self.horizontal:
			self.max_dist = self.rect.w - self.pointer.w
		else:
			self.max_dist = self.rect.h - self.pointer.h
		if groups is None:
			groups = []
		if type(groups) != list:
			groups = [groups]
		for group in groups:
			group.add(self)
		self.fingers_id = set()

	def draw(self, screen_to_draw, draw_value=False, max_val=100):
		pg.draw.rect(screen_to_draw, 'red', self.rect)
		pg.draw.rect(screen_to_draw, 'green', self.pointer)
		pg.draw.rect(screen_to_draw, "black", self.rect, 5)
		if draw_value:
			txt = font1.render(str(int(self.get_percent() * max_val)), True, 'white', 'black')
			txtrect = txt.get_rect()
			txtrect.center = self.pointer.center[0], self.pointer.top + (txtrect.h / 2)
			screen_to_draw.blit(txt, txtrect.topleft)

	def update(self):
		if self.clicked:
			if self.horizontal:
				self.pointer.move_ip(pg.mouse.get_rel()[0], 0)
			else:
				self.pointer.move_ip(0, pg.mouse.get_rel()[1])
			self.pointer.clamp_ip(self.rect)

	def click_down(self, event):
		self.clicked = self.rect.collidepoint(event.pos)
		return self.clicked

	def click_up(self, event):
		if self.clicked:
			self.clicked = False
			return True

	def get_percent(self):
		if self.horizontal:
			dist = abs(self.pointer.x - self.rect.x)
			percent = dist / self.max_dist
		else:
			dist = abs(self.pointer.bottom - self.rect.bottom)
			percent = dist / self.max_dist
		return percent

	def set_percent(self, percent):
		dist = percent * self.max_dist
		if self.horizontal:
			self.pointer.x = self.rect.x + dist
		else:
			self.pointer.bottom = self.rect.bottom - dist

	def finger_down(self, event):
		"""
		Check if it is clicked, and it set to do action on click, do the action
		:param pos: position of the click
		:return: bool
		"""
		screen_rect = self.rect_to_be
		p_x = event.x * screen_rect.w
		p_y = event.y * screen_rect.h
		if self.rect.collidepoint((p_x, p_y)):  # cheeck click
			self.clicked = True
			self.fingers_id.add(event.finger_id)
		self.clicked = bool(self.fingers_id)
		return self.clicked

	def finger_up(self, event):
		"""
		Set itself as not clicked, and it set to do a action, do the action if the mouse it in the rect
		:param event: pg.MOUSEBUTTONUP event
		:return:
		"""
		if self.fingers_id:
			self.fingers_id.discard(event.finger_id)
		self.clicked = bool(self.fingers_id)

	def finger_motion(self, event):
		"""
		check if the button is pressed with the given motion
		:param event: pg.FINGERMOTION
		"""
		if self.fingers_id:
			if event.finger_id in self.fingers_id:
				screen_rect = self.rect_to_be
				p_x = event.dx * screen_rect.w
				p_y = event.dy * screen_rect.h
				self.pointer.move_ip(p_x, p_y)
				self.pointer.clamp_ip(self.rect)
