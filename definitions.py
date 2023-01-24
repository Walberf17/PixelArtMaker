import random
import math
import pygame as pg

def calc_proportional_size(expected = None , max_area = (1,1) , max_rect = None):
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
		expected = [1 , 1]

	if type(expected) in [float , int]:
		return (proportion[1]*expected)
	elif len(expected) == 2:
		return proportion.elementwise()*expected
	elif len(expected) == 4:
		pos = proportion.elementwise()*expected[:2] + max_rect.topleft
		size = proportion.elementwise()*expected[2:]
		return [pos , size]
	else:
		raise TypeError(f'value not good enought, {expected}')

def get_ang(pos1 , pos2):
	"""
	:return: angle in radians
	"""
	x1 , y1 = pos1
	x2 , y2 = pos2
	return math.atan2((y2 - y1) , (x2 - x1))

def set_pop_class(pop_class):
	global POPULATION_CLASSES
	POPULATION_CLASSES[0] = pop_class