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


class ToolButton(Button):
    def do_action(self, on_click_down=True):
        """
        Do whatever the action set to do.
        :return: None
        """
        if on_click_down and self.on_click_down:
            self.on_click_down(self)
        elif (not on_click_down) and self.on_click_up:
            self.on_click_up(self)


class HelpWindow(Scene):
    def key_up_handler(self, event):
        if event.scancode == 58:
            print('parando')
            self.stop()

    def create_objects(self):
        known_btns = {
            'o': 'Seleciona a cor do local que o mouse está. (Dentro da tela)',
            'e': 'Ativa a borracha.',
            'Setas': 'Movem os quadros.',
            'Espaço': 'Exibe a primeira imagem como sombra.',
            'Ctrl+C': 'Copia a tela atual.',
            'Ctrl+V': 'Cola a tela copiada.',
            'del': 'Apaga a tela inteira',
        }

        texts = list()
        i = 0
        size = .9 / len(known_btns)
        for key, text in known_btns.items():
            center_y = size * i + .5 * size
            texts.append(TextBox(text=key, area=(.2, size), rect_to_be=self.screen_rect, relative_center=[.1, center_y],
                                 font_color="black", bg_color=None))
            texts.append(TextBox(text=' ==> ' + text, area=(.8, size), rect_to_be=self.screen_rect,
                                 relative_center=[.6, center_y], font_color="black", bg_color=None))
            i += 1

        dict_to_do = {
            'draw': [texts]
        }
        self.set_things_to_do(dict_to_do=dict_to_do)


class Manager:
    def __init__(self, rect, grid_size):
        """
        It creates the main app, given the rect it should occupy and the size of the image(width, height)
        :param rect: pg.Rect
        :param grid_size: list(int, int)
        """

        ####################### Variables #######################
        # Files
        self.dict_with_images = {
            'path': 'Images',
            '1': {'address': 'size1.png'},
            '2': {'address': 'size2.png'},
            '3': {'address': 'size3.png'},
            '4': {'address': 'SaveFile 32x32.png',
                  'size': [32, 32]},
            '5': {'address': 'transparent_bg'},
            '6': {'address': 'Bucket 32x32.png',
                  'size': [32, 32]},
            '7': {'address': 'Vertical Mirror 32x32.png',
                  'size': [32, 32]},
            '8': {'address': 'horizontal mirror 17x16.png',
                  'size': [17, 16]},
            '9': {'address': 'full mirror 17x17.png',
                  'size': [17, 16]},

        }
        self.saving_folder = os.path.join('.', 'Images', 'Sprites')

        # Constants
        self.button_sizes = [.05, 0.05]
        self.max_resolution = 64
        self.rect = rect
        self.bg_for_grid = pg.image.load(os.path.join('Images', 'transparent_bg.jpg'))


        # Variables
        self.idx = [0, 0]
        self.grid_size = grid_size
        self.colors = ['black'] * 3
        self.background_func = self.get_background_image
        self.copied = None
        self.background = None

        # Groups, sets and things
        self.images = list()
        self.images.append(list())

        self.markers = set()

        self.btns = Group()
        self.texts = Group()



        ####################### Objects #######################
        self.grid = DrawingGrid(area=(.75, .9), grid_size=self.grid_size, rect_to_be=screen_rect,
                                background=[0, 0, 0, 0], center=[.5, .55])

        self.animator = Animations(fps=45, area=[.1, .2], center=[.07, .2], rect_to_be=self.rect, color=[0, 0, 0, 0])
        self.marker_animator_velocity = Marker(area=[.1, .02], rect_to_be=self.rect, horizontal=True,
                                               groups=self.markers,
                                               center=[0.07, .32])

        self.color_picker = ColorSelector([.85, 0, .1, .1], [0, .0, 1, 1], self.rect)

        # Resolution - Grid Size
        width, height = self.grid_size
        self.text_resolution = TextBox(text=f'[{width} x {height}]', area=[.1, .05], rect_to_be=self.rect,
                                       relative_center=[.07, .65], font_color='black', bg_color=None,
                                       groups=[self.texts])
        ## Markers
        self.marker_rows = Marker(area=[.025, .25], rect_to_be=self.rect, horizontal=False, groups=self.markers,
                                  center=[0.07 - .07 / 3, .8])
        self.marker_rows.set_percent((self.grid_size[0] * 2) / (self.max_resolution * 2))

        self.marker_cols = Marker(area=[.025, .25], rect_to_be=self.rect, horizontal=False, groups=self.markers,
                                  center=[0.07 + .07 / 3, .8])
        self.marker_cols.set_percent((self.grid_size[1] * 2) / (self.max_resolution * 2))

        # Location
        self.text_idx = TextBox(text='[1 , 1]', area=[.1, .05], rect_to_be=self.rect, relative_center=[.5, .05],
                                font_color='black', bg_color=None, groups=[self.texts], resize_text=True,
                                keep_ratio=True)

        # Tools Selection
        self.selection_size_rect = pg.Rect([0, 0], calc_proportional_size([.03, .06], max_rect=self.rect))

        ####################### Calls #######################
        self.images[0].append(self.grid.get_image())
        self.change_resolution_text()
        self.build()
        self.check_folder()
        self.change_resolution()


    ####################### Build things #######################
    def build(self):
        """
        build the objects for controlling the things
        :return:
        """
        self.build_btns_idx()
        self.build_btns_managers()

        self.build_texts()
        self.build_btns_tools()

    def build_btns_idx(self):
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

    def build_btns_managers(self):
        # Buttons to manage things
        Button(area=self.button_sizes, center=[.07, .05], rect_to_be=self.rect, text=f'Salvar',
               on_click_up=partial(self.save_image), groups=[self.btns], image='4',
               dict_with_images=self.dict_with_images)
        Button(area=self.button_sizes, center=[.95, .9], rect_to_be=self.rect, text=f'Sair',
               on_click_up=partial(sys.exit), groups=[self.btns])
        Button(area=self.button_sizes, center=[.95, .8], rect_to_be=self.rect, text=f'Limpar',
               on_click_up=partial(self.clear_image), groups=[self.btns])

    def build_btns_tools(self):
        """
        This build the buttons used as tools for painting
        :return:
        """
        total_lines = 3
        total_cols = 3
        line_size = [1, 1/total_lines]

        # the full rect
        tools_rect = pg.Rect([0,0], calc_proportional_size([.1, .18], max_rect=self.rect))
        tools_rect.center = calc_proportional_size([.07, .4], max_rect=self.rect)

        # for each line (3 for now
        first_line = pg.Rect([0,0] , calc_proportional_size(line_size, max_rect=tools_rect))
        first_line.center = calc_proportional_size([.5, 1/total_lines], max_rect=tools_rect)+tools_rect.topleft

        second_line = pg.Rect([0, 0], calc_proportional_size(line_size, max_rect=tools_rect))
        second_line.center = calc_proportional_size([.5, 2 / total_lines], max_rect=tools_rect)+tools_rect.topleft

        third_line = pg.Rect([0, 0], calc_proportional_size(line_size, max_rect=tools_rect))
        third_line.center = calc_proportional_size([.5, 3 / total_lines], max_rect=tools_rect)+tools_rect.topleft

        area = pg.Vector2([1/total_cols, 1])-[.1,0.1]
        center = pg.Vector2([.5, .5])
        diff = [.25,0]

        # for the first line
        ToolButton(image='1', area=area, center=center-diff, rect_to_be=first_line, groups=[self.btns],
               on_click_up=partial(self.set_pen_size, 1), dict_with_images=self.dict_with_images).do_action(on_click_down=False)
        ToolButton(image='2', area=area, center=center, rect_to_be=first_line, groups=[self.btns],
               on_click_up=partial(self.set_pen_size, 4), dict_with_images=self.dict_with_images)
        ToolButton(image='3', area=area, center=center + diff, rect_to_be=first_line, groups=[self.btns],
               on_click_up=partial(self.set_pen_size, 8), dict_with_images=self.dict_with_images)

        # for the second line
        ToolButton(area=area, center=center, rect_to_be=second_line, text=f'Balde',
               on_click_up=partial(self.set_pen_size, 'color'), groups=[self.btns], image='6',
               dict_with_images=self.dict_with_images)

        # self.selection_size_rect.center = calc_proportional_size(center - (area.x, 0), max_rect=self.rect)

        # for the third line
        ToolButton(area=area, center=center - diff, rect_to_be=third_line, text=f'Es. V',
               on_click_up=partial(self.set_pen_size, 'mirror vertical'), groups=[self.btns], image='7',
               dict_with_images=self.dict_with_images)

        ToolButton(area=area, center=center, rect_to_be=third_line, text=f'Es. H',
                   on_click_up=partial(self.set_pen_size, 'mirror horizontal'), groups=[self.btns], image='8',
                   dict_with_images=self.dict_with_images)

        ToolButton(area=area, center=center+diff, rect_to_be=third_line, text=f'Es. F',
                   on_click_up=partial(self.set_pen_size, 'mirror full'), groups=[self.btns], image='9',
                   dict_with_images=self.dict_with_images)

        # The Eraser
        Button(text='Eraser', area=[.1, .1], center=[.75, .05], rect_to_be=self.rect, groups=[self.btns],
               on_click_up=partial(self.active_eraser))

    def build_texts(self):
        # texts
        TextBox(text='Localização:', area=[.1, .065], rect_to_be=self.rect, relative_center=[0.35, .05],
                font_color='black', bg_color=None, groups=[self.texts])
        TextBox(text='Resolução:', area=[.1, .05], rect_to_be=self.rect, relative_center=[0.07, .55],
                font_color='black', bg_color=None, groups=[self.texts])



    ####################### Manage Files #######################
    def save_image(self):
        self.move_to_image()
        max_sprites = self.get_max_sprites()
        grid_size = self.grid_size
        full_size = pg.Vector2(grid_size).elementwise() * [max_sprites, len(self.images)]
        full_surf = pg.Surface(full_size).convert_alpha()
        full_surf.fill([0, 0, 0, 0])
        pos_0 = pg.Vector2(grid_size)
        for row, sprite in enumerate(self.images):
            for col, image in enumerate(sprite):
                new_pos = pos_0.elementwise() * [col, row]
                new_surf = pg.transform.scale(image, grid_size)
                full_surf.blit(new_surf, new_pos)

        # name = input("Choose a name: ")
        name = 'tests'
        path = os.path.join(self.saving_folder, f'{name} {grid_size[0]}x{grid_size[1]}.png')
        pg.image.save(full_surf, path)


    def check_folder(self):
        os.makedirs(self.saving_folder, exist_ok=True)

    ####################### Tools and stuff #######################
    def set_pen_size(self, n, btn):
        funcs_dict = {
            1: self.grid.get_1_neighborhood,
            4: self.grid.get_4_neighborhood,
            8: self.grid.get_8_neighborhood,
            'color': self.grid.get_same_color_neighborhood,
            'mirror horizontal': self.grid.get_mirror_horizon,
            'mirror vertical': self.grid.get_mirror_vertical,
            'mirror full': self.grid.get_mirror_full,
        }
        func = funcs_dict.get(n, self.grid.get_1_neighborhood)
        self.grid.set_pen_size(func)
        self.selection_size_rect.size = calc_proportional_size([1.1, 1.1], max_rect=btn.rect)
        self.selection_size_rect.center = btn.rect.center

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
        self.color_picker.set_color(color)
        if color not in [[0, 0, 0, 0], (0, 0, 0, 0)]:
            self.colors.insert(0, color)
            self.colors.pop()

    def clear_image(self):
        image, frame = self.idx
        self.grid.image.fill([0, 0, 0, 0])
        self.move_to_image()

    def bucket(self):
        self.grid.bucket()
        self.move_to_image()

    def pick_color(self):
        pos = pg.Vector2(pg.mouse.get_pos())
        if self.grid.rect.collidepoint(pos):
            pos -= self.grid.rect.topleft
            color = self.grid.image.get_at([int(pos.x), int(pos.y)])
            self.set_color(color)

    def copy_surf(self, event):
        if event.unicode == '\x03':
            self.copied = self.grid.image.copy()

    def paste_surf(self):
        if self.copied:
            self.grid.image.blit(pg.transform.scale(self.copied, self.grid.rect.size), [0, 0])
        self.move_to_image()

    ####################### Screen Manager #######################
    def animate_animator(self):
        max_sprites = len(self.images[self.idx[0]])
        grid_size = self.grid_size
        full_size = pg.Vector2(grid_size).elementwise() * [max_sprites, 1]
        full_surf = pg.Surface(full_size).convert_alpha()
        full_surf.fill([0, 0, 0, 0])
        pos_0 = pg.Vector2(grid_size)
        for col, image in enumerate(self.images[self.idx[0]]):
            new_pos = pos_0.elementwise() * [col, 0]
            new_surf = pg.transform.scale(image, grid_size)
            full_surf.blit(new_surf, new_pos)
        path = os.path.join(self.saving_folder, f'animation.png')
        pg.image.save(full_surf, path)
        dict_with_images = {
            'path': os.path.join('Images', 'Sprites'),
            17121990: {
                "address": 'animation.png',
                'size': grid_size
            }
        }
        self.animator.define_images(17121990, dict_with_images)

    def change_resolution_text(self):
        width = max(int((self.marker_rows.get_percent() * self.max_resolution)), 1)
        height = max(int((self.marker_cols.get_percent() * self.max_resolution)), 1)
        self.text_resolution.change_text(new_text=f'[{width} x {height}]')


    def change_resolution(self):
        width = max(int((self.marker_rows.get_percent() * self.max_resolution)), 1)
        height = max(int((self.marker_cols.get_percent() * self.max_resolution)), 1)
        self.grid_size = [width, height]
        self.grid.change_size([height, width])
        self.change_resolution_text()
        self.move_to_image()
        self.get_background_image()
        self.background_func()

    ####################### Handlers #######################

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

    def key_down(self, event):
        funcs = {
            79: partial(self.move_to_image, 0, 1),
            80: partial(self.move_to_image, 0, -1),
            81: partial(self.move_to_image, 1, 0),
            82: partial(self.move_to_image, -1, 0),
            44: partial(self.change_background_func, self.get_first_as_background),
            5: self.active_eraser,
            76: partial(self.clear_image),
            18: self.pick_color,
            6: partial(self.copy_surf, event),
            25: self.paste_surf,
            58: self.help_window,
            # 8: partial(self.set_pen_size, 'mirror horizontal'),
            41: sys.exit,

        }

        if event.scancode in funcs:
            func = funcs.get(event.scancode)
            func()
        else:
            # print(event)
            pass

    def key_up(self, event):
        funcs = {
            44: partial(self.change_background_func, self.get_background_image),
            5: self.active_eraser,
        }

        if event.scancode in funcs:
            func = funcs.get(event.scancode)
            func()
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
        self.animator.update(velocity=self.marker_animator_velocity.get_percent() * 8)

    ####################### Helpers #######################

    def get_max_sprites(self):
        max_sprites = float('-inf')
        for sprite in self.images:
            max_sprites = max([max_sprites, len(sprite)])
        return max_sprites

    def change_background_func(self, background):
        self.background_func = background
        self.background_func()

    def get_background_image(self):
        row, col = self.idx
        if col >= 1:
            self.background = pg.transform.scale(self.images[row][col - 1], self.grid.rect.size)
            self.background.set_alpha(70)
        else:
            self.background = None

    def get_first_as_background(self):
        row, col = self.idx
        if col >= 1:
            self.background = pg.transform.scale(self.images[row][0], self.grid.rect.size)
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

    def help_window(self):
        helper_scene = HelpWindow(screen)
        helper_scene.run()












































# runs
screen = pg.display.set_mode(pg.display.get_desktop_sizes()[0], pg.FULLSCREEN)
pg.display.set_caption(f'PixelArtMaker')
screen_rect = screen.get_rect()
app = Manager(screen_rect, [16, 16])
scene = Scene(screen,
              {'draw': [[app]], 'click_down': [[app]], 'update': [[app]], 'key_down': [[app]], 'key_up': [[app]]},
              fps=60)
scene.run()
