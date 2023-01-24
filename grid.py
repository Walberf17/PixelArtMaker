"""
This is the class for drawing a grid in the screen

It draw, click down, click up, save a image, and create a surface
"""
import os
import pygame as pg
from color_selector import ColorSelector
from scenes import Scene
from pygame.sprite import Sprite, Group
from buttons import Button
from functools import partial



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


# classes
class DrawingGrid(Sprite):
    def __init__(self, grid_size, area, rect_to_be, background='white', center=(.5, .5), *args, **kwargs):
        max_rect = pg.Rect([0, 0], calc_proportional_size(area, max_area=[1, 1], max_rect=rect_to_be))
        self.grid_size = grid_size
        self.cells_dict = {}
        self.cells = dict()
        self.selected_cells = set()
        self.clicked = False

        # color picker
        self.color_picker = ColorSelector([.85, 0, .1, .1], [0, .0, 1, 1], rect_to_be)

        # Groups
        self.buttons = Group()

        # for the draw
        self.area = area
        self.rect_to_be = rect_to_be
        self.center = center
        cell_width = max_rect.w / self.grid_size[1]
        cell_height = max_rect.h / self.grid_size[0]
        self.background = background
        self.cells_size = pg.Vector2([int(min([cell_width, cell_height]))] * 2)
        new_rect = pg.Rect([0, 0], self.cells_size.elementwise() * self.grid_size[::-1])
        new_rect.center = calc_proportional_size(center, max_rect=rect_to_be)
        self.rect = new_rect
        self.image = pg.Surface(self.rect.size).convert_alpha()
        self.fill(self.background)

        self.selection_size_rect = pg.Rect([0,0], calc_proportional_size([.025,.05], max_rect=self.rect_to_be))
        self.selection_size_rect.center = calc_proportional_size([.07-0.025, .35], max_rect=self.rect_to_be)

        self.neighborhood_func = self.get_1_neighborhood

        self.build()

    def change_size(self, new_size):
        self.grid_size = new_size
        max_rect = pg.Rect([0, 0], calc_proportional_size(self.area, max_area=[1, 1], max_rect=self.rect_to_be))
        cell_width = max_rect.w / self.grid_size[1]
        cell_height = max_rect.h / self.grid_size[0]
        self.cells_size = pg.Vector2([int(min([cell_width, cell_height]))] * 2)
        new_rect = pg.Rect([0, 0], self.cells_size.elementwise() * self.grid_size[::-1])
        new_rect.center = calc_proportional_size(self.center, max_rect=self.rect_to_be)
        self.rect = new_rect
        self.load_image(self.image)

    def fill(self, color):
        self.image.fill(color)

    def build(self):
        """
        Create the cell for it to run
        :return:
        """

        rows, cols = self.grid_size
        for row in range(rows):
            for col in range(cols):
                self.cells[(row, col)] = self.background

        # Buttons
        Button(text='Eraser', area=[.1, .1], center=[.75, .05], rect_to_be=self.rect_to_be , groups=[self.buttons],
               on_click_up=partial(self.set_color, [0,0,0,0]))

        ## for size
        dict_with_images = {
            'path': 'Images', '1': {'address': 'size1.png'},
            'path': 'Images', '2': {'address': 'size2.png'},
            'path': 'Images', '3': {'address': 'size3.png'},

        }
        area = pg.Vector2([.025,.05])
        center = pg.Vector2([.07, .35])
        Button(image='1', area=area, center=center-(area.x,0), rect_to_be=self.rect_to_be , groups=[self.buttons],
               on_click_up=partial(self.set_size, 1), dict_with_images=dict_with_images)
        Button(image='2', area=area, center=center, rect_to_be=self.rect_to_be , groups=[self.buttons],
               on_click_up=partial(self.set_size, 4), dict_with_images=dict_with_images)
        Button(image='3', area=area, center=center+(area.x,0), rect_to_be=self.rect_to_be , groups=[self.buttons],
               on_click_up=partial(self.set_size, 8), dict_with_images=dict_with_images)

    def create_rect(self, idx):
        pos = pg.Vector2(self.cells_size).elementwise() * idx[::-1]
        size = self.cells_size
        return pg.Rect(pos, size)

    def draw(self, screen_to_draw):
        """
        Drow a thin black rect and the rect with its color
        :param screen_to_draw: pg.Screen Object
        :return:
        """
        screen_to_draw.blit(self.image, self.rect.topleft)


        pg.draw.rect(screen_to_draw, 'white', self.selection_size_rect)
        for btn in self.buttons:
            btn.draw(screen_to_draw)

        # draw the lines and columns
        rows, cols = self.grid_size
        ## columns
        for col in range(cols+1):
            pos_0 = [self.cells_size[0]*col+self.rect.left, self.rect.top]
            pos_1 = [self.cells_size[0]*col+self.rect.left, self.rect.bottom]
            pg.draw.line(surface=screen_to_draw, color='gray', start_pos=pos_0, end_pos=pos_1, width=3)

        ## rows
        for row in range(rows+1):
            pos_0 = [self.rect.left, self.rect.top+self.cells_size[1]*row]
            pos_1 = [self.rect.right, self.rect.top+self.cells_size[1]*row]
            pg.draw.line(surface=screen_to_draw, color='gray', start_pos=pos_0, end_pos=pos_1, width=3)

        self.color_picker.draw(screen_to_draw)

        mouse_pos = pg.mouse.get_pos()
        if not self.clicked and self.rect.collidepoint(mouse_pos):
            center_idx = self.get_index(mouse_pos)
            indexes = self.get_neighborhoods(center_idx)
            new_surf = pg.Surface(self.rect.size).convert_alpha()
            new_surf.fill([0,0,0,0])
            for idx in indexes:
                color = self.color_picker.color
                if color == [0,0,0,0]:
                    color = 'white'
                pg.draw.rect(new_surf, color, self.create_rect(idx))
            new_surf.set_alpha(150)
            screen_to_draw.blit(new_surf, self.rect)

    def click_down(self, event):
        """
        Check if it is clicked
        :param event: pg.MOUSEBUTTONDOWN
        :return: if clicked
        """
        if self.color_picker.click_down(event):
            return True
        for btn in self.buttons:
            if btn.click_down(event):
                return True
        if self.rect.collidepoint(event.pos):
            self.clicked = True
            return True

        return False

    def get_index(self, pos):
        x, y = pos
        col = int((y - self.rect.top) // self.cells_size.y)
        row = int((x - self.rect.left) // self.cells_size.x)
        return (col, row)

    def update(self, velocity=6):
        """
        For naw, it only paints the rects if clicked
        :param velocity:
        :param color:
        :return:
        """
        # paint the grid
        color = self.color_picker.get_color()

        for btn in self.buttons:
            btn.update()

        mouse_pos = pg.mouse.get_pos()

        center_idx = self.get_index(mouse_pos)
        indexes = self.get_neighborhoods(center_idx)

        if self.clicked:
            for idx in indexes:
                if idx not in self.selected_cells:
                    self.selected_cells.add(idx)
                    self.image.fill(color, self.create_rect(idx))

        self.color_picker.update()

    def click_up(self, event=None):
        """
        Deselect the selected cells and set itself as not clicked
        :param event: pg.MOUSEBUTTONUP
        :return: None
        """
        self.clicked = False
        self.color_picker.click_up(event)
        for btn in self.buttons:
            if btn.click_up(event):
                return True
        self.selected_cells.clear()
        # self.save_image('Images/color_wheel.jpg')

    def save_image(self, name):
        pg.image.save(self.image, name)

    def create_image(self):
        new_surf = pg.Surface(self.rect_to_be.size).convert_alpha()
        new_surf.fill([0, 0, 0, 0])
        self.draw(new_surf)
        surf = pg.Surface(self.rect.size).convert_alpha()
        surf.fill([0, 0, 0, 0])
        surf.blit(new_surf, [0, 0], self.rect)
        return pg.transform.scale(surf, self.grid_size).convert_alpha()

    def get_image(self):
        # return self.create_image()
        return self.image

    def load_image(self, image):
        if isinstance(image, str):
            image = pg.image.load(image).convert_alpha()
        self.image = pg.transform.scale(image, self.rect.size)

    def set_color(self, color):
        self.color_picker.set_color(color)

    def set_size(self, func):
        funcs_dict = {
            1: [self.get_1_neighborhood, [.07-0.025, .35]],
            4: [self.get_4_neighborhood, [.07, .35]],
            8: [self.get_8_neighborhood, [.07+0.025, .35]],
        }
        self.neighborhood_func, center = funcs_dict.get(func, self.get_1_neighborhood)
        self.selection_size_rect.center = calc_proportional_size(center, max_rect=self.rect_to_be)

    def get_possibilities(self, idx):
        row, col = idx
        max_rows, max_cols = self.grid_size
        possible_rows = list(range(max([0, row-1]), min([row+1, max_rows-1])+1))
        possible_cols = list(range(max([0, col-1]), min([col+1, max_cols-1])+1))
        return [possible_rows, possible_cols]

    def get_neighborhoods(self, center_idx):
        return self.neighborhood_func(center_idx=center_idx)

    def get_1_neighborhood(self, center_idx):
        return [center_idx]

    def get_8_neighborhood(self, center_idx):
        rows , cols = self.get_possibilities(center_idx)
        neighborhood = set()
        for row in rows:
            for col in cols:
                # if row != col:
                    neighborhood.add((row, col))
        neighborhood.add(center_idx)
        return neighborhood

    def get_4_neighborhood(self, center_idx):
        i, j = center_idx
        rows, cols = self.get_possibilities(center_idx)
        neighborhood = set()
        for row in rows:
            neighborhood.add((row, j))
        for col in cols:
            neighborhood.add((i, col))
        # neighborhood.add(center_idx)
        return neighborhood


# tests

if __name__ == '__main__':
    screen = pg.display.set_mode((800, 500))
    screen_rect = screen.get_rect()
    a = DrawingGrid(area=(.8, 1), grid_size=(64, 64), rect_to_be=screen_rect, background='white')
    scene = Scene(screen, {'draw': [[a]], 'click_down': [[a]], 'update': [[a]]})
    scene.run()
