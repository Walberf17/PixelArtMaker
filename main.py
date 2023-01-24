"""
This is a helper for making new Pixel Arts.
There are good ones, but I want to try something else.
"""

__version__ = '0.2'

"""
We draw in the center, given a aspect ratio, then we can change the image, where the next one will be saved right 
on the right side. 
"""

# import things
import os, sys

os.environ['KIVY_ORIENTATION'] = 'LandscapeLeft LandscapeRight'

from textbox import TextBox
from scenes import Scene
import pygame as pg
from grid import DrawingGrid
from buttons import Button
from functools import partial
from marker import Marker

# init pygame
pg.init()


# variables


# Helpers
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
class Manager:
    def __init__(self, rect, grid_size):
        """
        Manage the images created, load and save then in the specified format
        """
        self.saving_folder = os.path.join('.', 'Images', 'Sprites')
        self.images = list()  # a list of list, each list is a sprite(pg.Surface), different list mean different
        # sprites actions
        self.button_sizes = [.05, 0.05]
        self.max_resolution = 64
        self.grid_size = grid_size
        self.btns = pg.sprite.Group()
        self.texts = pg.sprite.Group()
        self.markers = set()
        self.grid = DrawingGrid(area=(.75, .9), grid_size=self.grid_size, rect_to_be=screen_rect,
                                background=[0, 0, 0, 0], center=[.5,.55])
        self.images.append(list())
        self.images[0].append(self.grid.get_image())
        self.background = None
        self.idx = [0, 0]
        self.rect = rect

        rows, cols = self.grid_size
        self.text_resolution = TextBox(text=f'[{rows} x {cols}]', area=[.1, .05], rect_to_be=self.rect,
                                       relative_center=[.07, .65], font_color='black', bg_color=None,
                                       groups=[self.texts])

        self.marker_rows = Marker(area=[.025, .25], rect_to_be=self.rect, horizontal=False, groups=self.markers,
                                  center=[0.07-.07/3, .8])
        self.marker_cols = Marker(area=[.025, .25], rect_to_be=self.rect, horizontal=False, groups=self.markers,
                                  center=[0.07+.07/3, .8])

        self.marker_rows.set_percent((self.grid_size[0] * 2) / (self.max_resolution * 2))
        self.marker_cols.set_percent((self.grid_size[1] * 2) / (self.max_resolution * 2))

        self.change_resolution_text()

        self.text_idx = TextBox(text='[0 , 0]', area=[.1, .05], rect_to_be=self.rect, relative_center=[.5, .05],
                                font_color='black', bg_color=None, groups=[self.texts])
        self.build()
        self.check_folder()
        self.change_resolution()

    def build(self):

        # Buttons to change the index
        w, h = .3, .3
        default_x_dif = .05

        center = pg.Vector2(.5, .5)
        default_rect = pg.Rect(calc_proportional_size([0, 0, .1, .2], max_rect=self.rect))
        default_rect.center = calc_proportional_size([1 - default_x_dif, .3], max_rect=self.rect)

        Button(area=[w, h], center=center - [w, 0], rect_to_be=default_rect, text=f'<',
               on_click_up=partial(self.move_to_image, 0, -1), groups=[self.btns])
        Button(area=[w, h], center=center + [w, 0], rect_to_be=default_rect, text=f'>',
               on_click_up=partial(self.move_to_image, 0, 1), groups=[self.btns])
        Button(area=[w, h], center=center + [0, h], rect_to_be=default_rect, text=f'\/',
               on_click_up=partial(self.move_to_image, 1, 0), groups=[self.btns])
        Button(area=[w, h], center=center - [0, h], rect_to_be=default_rect, text=f'/\\',
               on_click_up=partial(self.move_to_image, -1, 0), groups=[self.btns])

        # Buttons to manage things
        Button(area=self.button_sizes, center=[.07, .05], rect_to_be=self.rect, text=f'Salvar',
               on_click_up=partial(self.save_image), groups=[self.btns])
        Button(area=self.button_sizes, center=[1 - default_x_dif, .9], rect_to_be=self.rect, text=f'Sair',
               on_click_up=partial(sys.exit), groups=[self.btns])

        # texts
        TextBox(text='Localização:', area=[.1, .065], rect_to_be=self.rect, relative_center=[0.35, .05],
                font_color='black', bg_color=None, groups=[self.texts])
        TextBox(text='Resolução:', area=[.1, .05], rect_to_be=self.rect, relative_center=[0.07, .55],
                font_color='black', bg_color=None, groups=[self.texts])

    def check_folder(self):
        os.makedirs(self.saving_folder, exist_ok=True)

    def save_image(self):
        self.move_to_image()
        max_sprites = self.get_max_sprites()
        full_size = pg.Vector2(self.grid_size).elementwise() * [max_sprites, len(self.images)]
        full_surf = pg.Surface(full_size).convert_alpha()
        full_surf.fill([0, 0, 0, 0])
        pos_0 = pg.Vector2(self.grid_size)
        for row, sprite in enumerate(self.images):
            for col, image in enumerate(sprite):
                new_pos = pos_0.elementwise() * [col, row]
                new_surf = pg.transform.scale(image, self.grid_size)
                full_surf.blit(new_surf, new_pos)

        name = input("Choose a name: ")
        path = os.path.join(self.saving_folder, f'{name} {self.grid_size[0]}x{self.grid_size[1]}.png')
        pg.image.save(full_surf, path)

    def get_max_sprites(self):
        max_sprites = float('-inf')
        for sprite in self.images:
            max_sprites = max([max_sprites, len(sprite)])
        return max_sprites

    def get_background_image(self):
        row, col = self.idx
        if col >= 1:
            self.background = self.images[row][col - 1].copy()
            self.background.set_alpha(70)
        else:
            self.background = None

    def move_to_image(self, rows=0, cols=0):
        row, col = self.idx
        new_row = int(max([0, row + rows]))
        new_col = int(max([0, col + cols]))
        if new_row >= len(self.images):
            new_row = len(self.images)
            new_col = 0
            new_image = pg.Surface(self.grid.rect.size).convert_alpha()
            new_image.fill([0, 0, 0, 0])
            self.images.append([new_image])
        if new_row != row:
            new_col = 0
        if new_col >= len(self.images[new_row]):
            new_col = len(self.images[new_row])
            new_image = pg.Surface(self.grid.rect.size).convert_alpha()
            new_image.fill([0, 0, 0, 0])
            self.images[new_row].append(new_image)
        self.idx = [new_row, new_col]
        self.images[row][col] = self.grid.get_image()
        self.grid.load_image(self.images[new_row][new_col])
        self.get_background_image()
        self.text_idx.change_text(f'[{new_row} , {new_col}]')

    def click_down(self, event):
        for btn in self.btns:
            if btn.click_down(event):
                return True

        for marker in self.markers:
            if marker.click_down(event):
                return True

        self.grid.click_down(event)

    def click_up(self, event):
        for btn in self.btns:
            btn.click_up(event)

        for marker in self.markers:
            if marker.click_up(event):
                self.change_resolution()
        self.grid.click_up(event)

    def draw(self, screen_to_draw):

        pg.draw.rect(screen_to_draw, 'white', self.grid.rect)
        for btn in self.btns:
            btn.draw(screen_to_draw)

        for text in self.texts:
            text.draw(screen_to_draw)

        for btn in self.markers:
            btn.draw(screen_to_draw)


        if self.background:
            screen_to_draw.blit(self.background, self.grid.rect.topleft)

        self.grid.draw(screen_to_draw)

    def update(self):
        for btn in self.btns:
            btn.update()
        for marker in self.markers:
            marker.update()
            if marker.clicked:
                self.change_resolution_text()
        self.grid.update()

    def change_resolution_text(self):
        rows = max(int((self.marker_rows.get_percent() * self.max_resolution)), 1)
        cols = max(int((self.marker_cols.get_percent() * self.max_resolution)), 1)
        self.text_resolution.change_text(new_text=f'[{rows} x {cols}]')

    def change_resolution(self):
        rows = max(int((self.marker_rows.get_percent() * self.max_resolution)), 1)
        cols = max(int((self.marker_cols.get_percent() * self.max_resolution)), 1)
        self.grid.change_size([rows, cols])
        self.change_resolution_text()


# runs
screen = pg.display.set_mode((1920, 1080), pg.FULLSCREEN)
screen_rect = screen.get_rect()
app = Manager(screen_rect, [32, 32])
scene = Scene(screen, {'draw': [[app]], 'click_down': [[app]], 'update': [[app]]}, fps=60)
scene.run()
