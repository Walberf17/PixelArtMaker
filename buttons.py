"""
Buttons class
This class makes buttons_group,
do the click down and up stuffs,
change color when roovered
stuff in general
"""
import pygame as pg
from animations import Animations
from textbox import TextBox


class Button(Animations):
    def __init__(self, area=(1, 1), center=None, rect_to_be=None, image: str = None, text=None, dict_with_images=None,
                 on_click_down=None, on_click_up=None, colors=None, groups=None, font_color="black", **kwargs):
        """
        It creates a rect in the screen, and does a action when interacted. If calls update, when hoovered it slightly
        change the color.

        :param area: list with 2 sizes, from 0 to 1.
        :param center: the center of the rect, in proportion
        :param rect_to_be: pg.Rect object, the rect to where it will be
        :param image: str address of the image to Animations
        :param text: String or None, to show on the button
        :param on_click_down: func to call when clicked down
        :param on_click_up: func to call when clicked up
        :param colors: list with 3 colors, for when hovered, clicked or default
        :param groups:
        """
        if colors is None:
            colors = ['orange', 'orange4', 'orange2']
        Animations.__init__(self, area=area, color=colors[0], rect_to_be=rect_to_be, image_name=image, center=center,
                            groups=groups, dict_with_images=dict_with_images, **kwargs)
        self.on_click_down = on_click_down
        self.image = image
        self.clicked = False
        self.on_click_up = on_click_up
        self.colors = colors
        if text is None:
            self.text = None
        else:
            self.text = TextBox(text=text, area=(.9, .9), rect_to_be=self.rect, relative_center=(.5, .5), font=None,
                                font_color=font_color, bg_color=None, groups=None, **kwargs)
        self.fingers_id = set()

    def finger_down(self, event):
        """
        Check if it is clicked, and it set to do action on click, do the action
        :param event: position of the click
        :return: bool
        """

        old_click = self.clicked
        screen_rect = self.rect_to_be
        p_x = event.x * screen_rect.w
        p_y = event.y * screen_rect.h
        if self.rect.collidepoint((p_x, p_y)):  # cheeck click
            self.clicked = True
            self.color = self.colors[1]
            self.do_action(on_click_down=True)
            self.fingers_id.add(event.finger_id)
            if old_click != self.clicked:
                if self.clicked:
                    self.do_action(on_click_down=True)
        return self.clicked

    def finger_up(self, event):
        """
        Set itself as not clicked, and it set to do a action, do the action if the mouse it in the rect
        :param event: pg.MOUSEBUTTONUP event
        :return:
        """
        old_click = self.clicked
        if self.fingers_id:
            screen_rect = self.rect_to_be
            p_x = event.x * screen_rect.w
            p_y = event.y * screen_rect.h
            if self.rect.collidepoint((p_x, p_y)):
                self.do_action(on_click_down=False)
                self.fingers_id.discard(event.finger_id)
        self.clicked = bool(self.fingers_id)
        if old_click != self.clicked:
            if not self.clicked:
                self.do_action(on_click_down=False)

    def finger_motion(self, event):
        """
		check if the button is pressed with the given motion
		:param event: pg.FINGERMOTION
		"""
        old_click = self.clicked
        screen_rect = self.rect_to_be
        p_x = event.x * screen_rect.w
        p_y = event.y * screen_rect.h
        if self.rect.collidepoint((p_x, p_y)):
            self.fingers_id.add(event.finger_id)
        else:
            self.fingers_id.discard(event.finger_id)
        self.clicked = bool(self.fingers_id)
        if old_click != self.clicked:
            if self.clicked:
                self.do_action(on_click_down=True)
            else:
                self.do_action(on_click_down=False)

    def draw(self, screen_to_draw):
        """
		draw itself on the surface given
		:param screen_to_draw: pg.Surface
		:return: None
		"""
        Animations.draw(self, screen_to_draw=screen_to_draw)
        if self.text and self.images is None:
            self.text.draw(screen_to_draw=screen_to_draw)

    def click_down_edit(self, event, button_pressed=None):
        """
        create and put buttons_group in place, then print them
        :param button_pressed: mouse button clicked, int
        :param event: pg.Event
        :return: boo
        """
        if self.rect.collidepoint(event.pos):
            if button_pressed:
                ev_btn = button_pressed
            else:
                ev_btn = event.button
            if ev_btn == 1:
                self.clicked = True
                return True

            elif ev_btn == 4:
                self.rect.inflate_ip(10, 0)

            elif ev_btn == 5:
                self.rect.inflate_ip(-10, 0)

            elif ev_btn == 7:
                self.rect.inflate_ip(0, 10)

            elif ev_btn == 6:
                self.rect.inflate_ip(0, -10)

            elif ev_btn == 3:
                screen_rect = self.rect_to_be
                x, y, w, h = self.rect
                x = x / screen_rect.w
                y = y / screen_rect.h
                w = w / screen_rect.w
                h = h / screen_rect.h
                print(f'{x} , {y} , {w} , {h}', f'"{self.txt}"')
            return True

    def click_down(self, event):
        """
        Check if it is clicked, and it set to do action on click, do the action
        :param event: pg.MOUSEBUTTONDOWN
        :return: bool
        """
        if self.rect.collidepoint(event.pos):  # cheeck click
            self.clicked = True
            self.color = self.colors[1]
            self.do_action(on_click_down=True)
            return self.clicked

    def move(self):
        """
        move itself in clicked
        :return:
        """
        if self.clicked:
            self.rect.move_ip(pg.mouse.get_rel())
        if self.text is not None:
            self.text.center_image()

    def click_up(self, event):
        """
        Set itself as not clicked, and it set to do a action, do the action if the mouse it in the rect
        :param event: pg.MOUSEBUTTONUP event
        :return:
        """
        if self.clicked:
            self.clicked = False
            self.color = self.colors[0]
            if self.on_click_up:
                if self.rect.collidepoint(event.pos):
                    self.do_action(on_click_down=False)

    def click_up_edit(self, event):
        """
        Set itself as not clicked, and it set to do a action, do the action if the mouse it in the rect
        :param event: pg.MOUSEBUTTONUP event
        :return:
        """
        if self.clicked:
            screen_rect = self.rect_to_be
            self.clicked = False
            self.color = self.colors[0]
            x, y, w, h = self.rect
            x = x / screen_rect.w
            y = y / screen_rect.h
            w = w / screen_rect.w
            h = h / screen_rect.h
            print(f'{x} , {y} , {w} , {h}', f'"{self.txt}"')
            return True

    def do_action(self, on_click_down=True):
        """
        Do whatever the action set to do.
        :return: None
        """
        if on_click_down and self.on_click_down:
            self.on_click_down()
        elif (not on_click_down) and self.on_click_up:
            self.on_click_up()

    def update(self):
        """
        Just change its color when hoovered or clicked
        :return:
        """
        if self.clicked and self.rect.collidepoint(pg.mouse.get_pos()):
            self.color = self.colors[1]
        else:
            self.color = self.colors[0]
        if self.images:
            Animations.update(self)
