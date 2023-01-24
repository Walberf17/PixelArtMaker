"""
color selector box for selecting colors
"""
import pygame as pg
from os.path import join


# helpers
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


class ColorSelector:
	def __init__(self, small_relative_rect, big_relative_rect, rect_to_be):
		self.rect_to_be = rect_to_be
		self.small_rect = pg.Rect(calc_proportional_size(small_relative_rect, max_rect=rect_to_be))
		self.big_rect = pg.Rect(calc_proportional_size(big_relative_rect, max_rect=rect_to_be))
		self.original_image = pg.image.load(join('.', 'Images', "color_wheel.png")).convert_alpha()
		self.image = pg.transform.scale(self.original_image, self.big_rect.size)
		self.small_image = pg.transform.scale(self.original_image, self.small_rect.size)
		self.clicked = False
		self.small_clicked = False
		self.selecting = False
		self.color = "black"

	def draw(self, screen_to_draw):
		pg.draw.rect(screen_to_draw, self.color, self.small_rect)
		if self.selecting:
			color = "red"
		else:
			color = "green"
		if self.selecting:
			screen_to_draw.blit(self.image, self.big_rect)
		else:
			screen_to_draw.blit(self.small_image, self.small_rect)

	def click_down(self, event):
		if self.small_rect.collidepoint(event.pos):
			self.small_clicked = True
			self.selecting = True
		return any([self.selecting, self.small_clicked])

	def click_up(self, event):
		if self.small_clicked:
			self.selecting = self.small_rect.collidepoint(event.pos)
			self.small_clicked = False
			return True
		else:
			self.small_clicked = self.selecting = False

	def update(self):
		if self.selecting:

			if self.big_rect.collidepoint(pg.mouse.get_pos()):
				pos = pg.Vector2(pg.mouse.get_pos()).elementwise() - (self.big_rect.topleft)
				self.color = self.image.get_at([int(pos.x), int(pos.y)])

	def get_color(self):
		return self.color
