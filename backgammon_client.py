import pygame
import ecys

import config
import color
import graphic as g
import component as c
import system as s


class BackgammonClient:
    def __init__(self, game):
        self.frame_rate = config.FRAME_RATE
        self.surface = pygame.display.set_mode(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )
        self.background_image = config.BACKGROUND_IMAGE
        pygame.display.set_caption(config.CAPTION)
        self.clock = pygame.time.Clock()
        self.local_pvp_button = None
        self.win_button = None
        self.game = game
        self.world = self._create_world()

    def run(self):
        while True:
            self.world.update()
            self.clock.tick(self.frame_rate)

    def save_history(self, filename):
        with open(filename, 'w') as history_file:
            for number, turn in enumerate(self.game.history):
                color = 'White' if number % 2 == 0 else 'Red'
                history_file.write(f'{number}. {color} {turn}\n')

    def _create_world(self):
        world = ecys.World()
        world.add_system(s.TurnSystem(self), priority=5)
        world.add_system(s.ArrangeDiesSystem(self), priority=4)
        world.add_system(s.ArrangePiecesSystem(self), priority=3)
        world.add_system(s.InputSystem(self), priority=2)
        world.add_system(s.HintSystem(self), priority=1)
        world.add_system(s.RenderSystem(self),  priority=0)
        self._create_points(world)
        self._create_pieces(world)
        self._create_dies(world)
        self._create_banners(world)
        self._create_menu_buttons(world)
        return world

    @staticmethod
    def _create_dies(world):
        world.create_entity(
            c.Render(coords=g.DIE_COORDS[color.RED, 1]),
            c.Die(color.RED, 1)
        )
        world.create_entity(
            c.Render(coords=g.DIE_COORDS[color.RED, 2]),
            c.Die(color.RED, 2)
        )
        world.create_entity(
            c.Render(coords=g.DIE_COORDS[color.WHITE, 1]),
            c.Die(color.WHITE, 1)
        )
        world.create_entity(
            c.Render(coords=g.DIE_COORDS[color.WHITE, 2]),
            c.Die(color.WHITE, 2)
        )

    def _create_banners(self, world):
        for point in self.game.board.points:
            world.create_entity(
                c.Render(coords=g.BANNER_COORDS[point.number]),
                c.AdditionalBanner(),
                point
            )

    def _create_pieces(self, world):
        for point in self.game.board.points:
            for piece in point.pieces:
                if point.color == color.RED:
                    image = config.RED_PIECE_IMAGE
                else:
                    image = config.WHITE_PIECE_IMAGE
                world.create_entity(
                    c.Render(image),
                    piece
                )

    def _create_points(self, world):
        self._create_from_points(world)
        self._create_to_points(world)

    def _create_from_points(self, world):
        world.create_entity(
            c.Render(config.WHITE_FROM_IMAGE, g.FROM_COORDS[0]),
            c.FromPointInput(),
            self.game.board.points[0]
        )
        world.create_entity(
            c.Render(config.RED_FROM_IMAGE, g.FROM_COORDS[25]),
            c.FromPointInput(),
            self.game.board.points[25]
        )
        image = config.RED_FROM_IMAGE
        for point in self.game.board.points[1:25]:
            if point.number >= 13:
                image = config.WHITE_FROM_IMAGE
            world.create_entity(
                c.Render(image, g.FROM_COORDS[point.number]),
                c.FromPointInput(),
                point
            )

    def _create_to_points(self, world):
        image = config.TO_IMAGE
        for point in self.game.board.points:
            world.create_entity(
                c.Render(image, g.TO_COORDS[point.number]),
                c.ToPoint(),
                point
            )

    def _create_menu_buttons(self, world):
        self.local_pvp_button = world.create_entity(
            c.Render(
                config.MENU_BUTTON_IMAGES[g.LOCAL],
                g.MENU_BUTTON_COORDS[g.LOCAL]
            )
        )
        self.win_button = world.create_entity(
            c.Render(coords=g.MENU_BUTTON_COORDS[g.WIN])
        )