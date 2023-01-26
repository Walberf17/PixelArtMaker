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
from color_selector import ColorSelector
from pygame.sprite import Group
from animations import Animations

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

class ColorButton(Button):
    def do_action(self, on_click_down=True):
        """
        Do whatever the action set to do.
        :return: None
        """
        if on_click_down and self.on_click_down:
            self.on_click_down(self)
        elif (not on_click_down) and self.on_click_up:
            self.on_click_up(self)


class Manager:
    def __init__(self, rect, grid_size):
        """
        Manage the images created, load and save then in the specified format
        """

        # dict with images

        self.dict_with_images = {
            'path': 'Images',
            '1': {'address': 'size1.png'},
            '2': {'address': 'size2.png'},
            '3': {'address': 'size3.png'},
            '4': {'address': 'SaveFile 32x32.png',
                  'size': [32, 32]},
            '5': {'address': 'transparent_bg'}

        }

        self.saving_folder = os.path.join('.', 'Images', 'Sprites')
        self.images = list()  # a list of list, each list is a sprite(pg.Surface), different list mean different
        # sprites actions
        self.button_sizes = [.05, 0.05]
        self.max_resolution = 64
        self.grid_size = grid_size

        # groups
        self.btns = pg.sprite.Group()
        self.texts = pg.sprite.Group()

        self.markers = set()
        self.grid = DrawingGrid(area=(.75, .9), grid_size=self.grid_size, rect_to_be=screen_rect,
                                background=[0, 0, 0, 0], center=[.5, .55])
        self.images.append(list())
        self.images[0].append(self.grid.get_image())
        self.background = None
        self.idx = [0, 0]
        self.rect = rect

        self.colors = ['black'] * 5
        self.pallet = list()

        self.animator = Animations(fps=45, area=[.1, .2], center=[.07, .2], rect_to_be=self.rect, color=[0, 0, 0, 0])

        # groups
        self.btns = Group()
        self.texts = Group()

        # color picker
        self.color_picker = ColorSelector([.85, 0, .1, .1], [0, .0, 1, 1], self.rect)
        self.bg_for_grid = pg.image.load(os.path.join('Images', 'transparent_bg.jpg'))

        rows, cols = self.grid_size
        self.text_resolution = TextBox(text=f'[{rows} x {cols}]', area=[.1, .05], rect_to_be=self.rect,
                                       relative_center=[.07, .65], font_color='black', bg_color=None,
                                       groups=[self.texts])

        self.marker_rows = Marker(area=[.025, .25], rect_to_be=self.rect, horizontal=False, groups=self.markers,
                                  center=[0.07 - .07 / 3, .8])
        self.marker_cols = Marker(area=[.025, .25], rect_to_be=self.rect, horizontal=False, groups=self.markers,
                                  center=[0.07 + .07 / 3, .8])

        self.marker_rows.set_percent((self.grid_size[0] * 2) / (self.max_resolution * 2))
        self.marker_cols.set_percent((self.grid_size[1] * 2) / (self.max_resolution * 2))

        self.change_resolution_text()

        self.selection_size_rect = pg.Rect([0, 0], calc_proportional_size([.025, .05], max_rect=self.rect))

        self.text_idx = TextBox(text='[1 , 1]', area=[.1, .05], rect_to_be=self.rect, relative_center=[.5, .05],
                                font_color='black', bg_color=None, groups=[self.texts])

        self.background_func = self.get_background_image

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
               on_click_up=partial(self.save_image), groups=[self.btns], image='4',
               dict_with_images=self.dict_with_images)
        Button(area=self.button_sizes, center=[1 - default_x_dif, .9], rect_to_be=self.rect, text=f'Sair',
               on_click_up=partial(sys.exit), groups=[self.btns])
        Button(area=self.button_sizes, center=[1 - default_x_dif, .8], rect_to_be=self.rect, text=f'Limpar',
               on_click_up=partial(self.clear_image, [0, 0, 0, 0]), groups=[self.btns])

        # buttons to manage colors
        for i in range(5):
            self.pallet.append(ColorButton(area=[w, h], center=center + [0, h * (i + 3)], rect_to_be=default_rect,
                                           on_click_up=self.change_btn_color,
                                           groups=[self.btns], colors=['black'] * 3))

        # texts
        TextBox(text='Localização:', area=[.1, .065], rect_to_be=self.rect, relative_center=[0.35, .05],
                font_color='black', bg_color=None, groups=[self.texts])
        TextBox(text='Resolução:', area=[.1, .05], rect_to_be=self.rect, relative_center=[0.07, .55],
                font_color='black', bg_color=None, groups=[self.texts])

        # Eraser
        Button(text='Eraser', area=[.1, .1], center=[.75, .05], rect_to_be=self.rect, groups=[self.btns],
               on_click_up=partial(self.active_eraser))

        ## for pen size

        area = pg.Vector2([.025, .05])
        center = pg.Vector2([.07, .4])
        Button(image='1', area=area, center=center - (area.x, 0), rect_to_be=self.rect, groups=[self.btns],
               on_click_up=partial(self.set_pen_size, 1), dict_with_images=self.dict_with_images)
        Button(image='2', area=area, center=center, rect_to_be=self.rect, groups=[self.btns],
               on_click_up=partial(self.set_pen_size, 4), dict_with_images=self.dict_with_images)
        Button(image='3', area=area, center=center + (area.x, 0), rect_to_be=self.rect, groups=[self.btns],
               on_click_up=partial(self.set_pen_size, 8), dict_with_images=self.dict_with_images)
        self.selection_size_rect.center = calc_proportional_size(center - (area.x, 0), max_rect=self.rect)

    def set_pen_size(self, n):
        funcs_dict = {
            1: [self.grid.get_1_neighborhood, [.07 - 0.025, .35]],
            4: [self.grid.get_4_neighborhood, [.07, .35]],
            8: [self.grid.get_8_neighborhood, [.07 + 0.025, .35]],
        }
        func, center = funcs_dict.get(n, self.grid.get_1_neighborhood)
        self.grid.set_pen_size(func)
        self.selection_size_rect.centerx = calc_proportional_size(center, max_rect=self.rect)[0]

    def change_btn_color(self, btn):
        color = btn.color
        self.color_picker.set_color(btn.color)
        self.set_color(color)

    def active_eraser(self):
        if self.color_picker.color == [0, 0, 0, 0]:
            self.color_picker.color = self.colors[0]
        else:
            self.color_picker.color = [0, 0, 0, 0]

    def set_color(self, color):
        if color in [[0, 0, 0, 0], (0, 0, 0, 0)]:
            return
        self.color_picker.set_color(color)
        if color not in self.colors:
            self.colors.insert(0, color)
            self.colors.pop()
            for btn, color in zip(self.pallet, self.colors):
                btn.colors = [color] * 3
                btn.color = color

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

    def animate_animator(self):
        row, col = self.idx
        full_size = pg.Vector2(self.grid_size).elementwise() * [len(self.images[row]), 1]
        full_surf = pg.Surface(full_size).convert_alpha()
        full_surf.fill([0, 0, 0, 0])
        pos_0 = pg.Vector2(self.grid_size)
        for idx, frame in enumerate(self.images[row]):
            new_pos = pos_0.elementwise() * [idx, 0]
            new_surf = pg.transform.scale(frame, self.grid_size)
            full_surf.blit(new_surf, new_pos)
        path = os.path.join(self.saving_folder, f'animation.png')
        pg.image.save(full_surf, path)
        dict_with_images = {
            'path': os.path.join('Images', 'Sprites'),
            17121990: {
                "address": 'animation.png',
                'size': self.grid_size
            }
        }
        self.animator.define_images(17121990, dict_with_images)

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

    def get_first_as_background(self):
        row, col = self.idx
        if col >= 1:
            self.background = self.images[0][0].copy()
            self.background.set_alpha(70)
        else:
            self.background = None

    def move_to_image(self, rows=0, cols=0):
        row, col = self.idx
        new_row = int(max([0, row + rows]))
        new_col = int(max([0, col + cols]))

        # save the working image
        self.images[row][col] = self.grid.get_image()

        # add new sprite
        if new_row >= len(self.images):
            new_row = len(self.images)
            new_col = 0
            new_image = self.images[0][0].copy()
            # new_image.fill([0, 0, 0, 0])
            self.images.append([new_image])
        if new_row != row:
            new_col = 0

        # add new frame
        if new_col >= len(self.images[new_row]):
            new_col = len(self.images[new_row])
            new_image = self.images[new_row][new_col - 1].copy()
            # new_image.fill([0, 0, 0, 0])
            self.images[new_row].append(new_image)

        # handle things
        self.idx = [new_row, new_col]
        self.grid.load_image(self.images[new_row][new_col])
        self.background_func()
        self.text_idx.change_text(f'[{new_row + 1} , {new_col + 1}]')
        self.animate_animator()

    def click_down(self, event):
        for btn in self.btns:
            if btn.click_down(event):
                return True

        for marker in self.markers:
            if marker.click_down(event):
                return True

        self.grid.click_down(event)

        if self.color_picker.click_down(event):
            return True

    def click_up(self, event):
        for btn in self.btns:
            btn.click_up(event)

        for marker in self.markers:
            if marker.click_up(event):
                self.change_resolution()
        if self.grid.click_up(event):
            self.move_to_image()
        if self.color_picker.click_up(event):
            color = self.color_picker.get_color()
            self.set_color(color)

    def draw(self, screen_to_draw):

        screen_to_draw.blit(self.bg_for_grid, self.grid.rect, self.grid.rect)
        screen_to_draw.blit(self.bg_for_grid, self.animator.rect, self.animator.rect)
        pg.draw.rect(screen_to_draw, 'white', self.selection_size_rect)
        # pg.draw.rect(screen_to_draw, 'white', self.grid.rect)

        self.grid.draw(screen_to_draw)

        for btn in self.btns:
            btn.draw(screen_to_draw)

        for text in self.texts:
            text.draw(screen_to_draw)

        for btn in self.markers:
            btn.draw(screen_to_draw)

        if self.background:
            screen_to_draw.blit(self.background, self.grid.rect.topleft)

        self.color_picker.draw(screen_to_draw)
        self.animator.draw(screen_to_draw=screen_to_draw)

    def update(self):
        for btn in self.btns:
            btn.update()
        for marker in self.markers:
            marker.update()
            if marker.clicked:
                self.change_resolution_text()
        self.color_picker.update()
        self.grid.set_color(self.color_picker.get_color())
        self.grid.update()
        self.animator.update()

    def change_resolution_text(self):
        rows = max(int((self.marker_rows.get_percent() * self.max_resolution)), 1)
        cols = max(int((self.marker_cols.get_percent() * self.max_resolution)), 1)
        self.text_resolution.change_text(new_text=f'[{rows} x {cols}]')

    def change_resolution(self):
        rows = max(int((self.marker_rows.get_percent() * self.max_resolution)), 1)
        cols = max(int((self.marker_cols.get_percent() * self.max_resolution)), 1)
        self.grid.change_size([rows, cols])
        self.change_resolution_text()
        self.move_to_image()

    def clear_image(self):
        image, frame = self.idx
        self.grid.image.fill([0, 0, 0, 0])
        self.move_to_image()

    def key_down(self, event):
        funcs = {
            79: partial(self.move_to_image, 0, 1),
            80: partial(self.move_to_image, 0, -1),
            81: partial(self.move_to_image, 1, 0),
            82: partial(self.move_to_image, -1, 0),
            44: partial(self.change_background_func, self.get_first_as_background),
            5: self.active_eraser,
            76: partial(self.clear_image),
            18: self.pick_color
        }

        if event.scancode in funcs:
            func = funcs.get(event.scancode)
            func()
        else:
            print(event.scancode)

    def change_background_func(self, background):
        self.background_func = background
        self.background_func()

    def key_up(self, event):
        funcs = {
            44: partial(self.change_background_func, self.get_background_image),
            5: self.active_eraser,
        }

        if event.scancode in funcs:
            func = funcs.get(event.scancode)
            func()

    def pick_color(self):
        pos = pg.Vector2(pg.mouse.get_pos())
        if self.grid.rect.collidepoint(pos):
            pos -= self.grid.rect.topleft
            color = self.grid.image.get_at([int(pos.x), int(pos.y)])
            print(color)
            self.set_color(color)


# runs
screen = pg.display.set_mode(pg.display.get_desktop_sizes()[0], pg.FULLSCREEN)
pg.display.set_caption(f'PixelArtMaker')
screen_rect = screen.get_rect()
app = Manager(screen_rect, [32, 32])
scene = Scene(screen,
              {'draw': [[app]], 'click_down': [[app]], 'update': [[app]], 'key_down': [[app]], 'key_up': [[app]]},
              fps=60)
scene.run()
