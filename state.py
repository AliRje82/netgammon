import socket

import config
import color
import logic
import component as c
import graphic as g


class State:
    def __init__(self, client):
        self.client = client

    def pause(self):
        pass

    def save_history(self, filename):
        pass

    def start_local_game(self):
        pass

    def start_network_game(self):
        pass

    def handle_received(self):
        pass

    def move(self, from_point, to_point):
        pass

    def end_move(self):
        pass

    @property
    def possible_points(self):
        return []

    def set_state_image(self):
        state_button = self.client.state_button
        render = state_button.get_component(c.Render)
        render.visible = False

    def set_local_button_image(self):
        local_button = self.client.local_button
        render = local_button.get_component(c.Render)
        render.visible = False

    def set_network_button_image(self):
        network_button = self.client.network_button
        render = network_button.get_component(c.Render)
        render.visible = False


class LockState(State):
    def start_local_game(self):
        self.client.game.restart()
        self.client.game.roll_dice()
        self.client.state = LocalPlayingState(self.client)

    def start_network_game(self):
        if not self.client.bgp.closed:
            self.client.bgp.close()
        self.client.bgp.connect()
        self.client.state = SearchingOpponentState(self.client)

    @State.possible_points.getter
    def possible_points(self):
        return []

    def set_local_button_image(self):
        local_button = self.client.local_button
        render = local_button.get_component(c.Render)
        render.visible = True

    def set_network_button_image(self):
        network_button = self.client.network_button
        render = network_button.get_component(c.Render)
        render.visible = True
        render.image = config.MENU_BUTTON_IMAGES[g.NET]['press']


class WinState(LockState):
    def set_state_image(self):
        state_button = self.client.state_button
        render = state_button.get_component(c.Render)
        render.visible = True
        render.image = config.MENU_BUTTON_IMAGES[g.STATE][self.client.game.color]

    def save_history(self, filename):
        self.client.save_history(filename)


class PauseState(LockState):
    def __init__(self, client, from_state):
        super().__init__(client)
        self.from_state = from_state

    def pause(self):
        self.client.state = self.from_state


class SearchingOpponentState(LockState):
    def start_local_game(self):
        self.client.bgp.close()
        self.client.state = NetworkPlayingState(self.client)

    def start_network_game(self):
        pass

    def set_network_button_image(self):
        network_button = self.client.network_button
        render = network_button.get_component(c.Render)
        render.visible = True
        render.image = config.MENU_BUTTON_IMAGES[g.NET]['pressed']

    def handle_received(self):
        try:
            message = self.client.bgp.receive()
            if message['command'] == 'COLOR':
                self.client.network_game_color = message['arg']
                self.client.restart_game()
                if self.client.network_game_color == color.WHITE:
                    self.client.game_roll_dice()
                    self.client.bgp.send_dies(self.client.game.roll)
        except socket.timeout as e:
            raise e
        except (socket.error, ConnectionError):
            self.client.state = DisconnectedState(self.client)


class DisconnectedState(LockState):
    def set_state_image(self):
        state_button = self.client.state_button
        render = state_button.get_component(c.Render)
        render.visible = True
        render.image = config.MENU_BUTTON_IMAGES[g.STATE][g.DISCONNECT]


class PlayingState(State):
    def pause(self):
        self.client.state = PauseState(self.client, self)

    def move(self, from_point, to_point):
        self.client.game.move(from_point, to_point)

    def _check_win_state(self):
        if self.client.game.game_over:
            self.client.state = WinState(self.client)


class LocalPlayingState(PlayingState):
    def end_move(self):
        self.client.game.roll_dice()
        self._check_win_state()

    @State.possible_points.getter
    def possible_points(self):
        return self.client.game.possible_points


class NetworkPlayingState(PlayingState):
    def move(self, from_point, to_point):
        super().move(from_point, to_point)
        self.client.bgp.send_move(from_point, to_point)

    def end_move(self):
        self.client.bgp.send_end_move()
        self._check_win_state()

    def handle_received(self):
        try:
            message = self.client.bgp.receive()
            if message['command'] == 'QUIT':
                self.client.bgp.close()
            if self.client.network_game_color == self.client.game.color:
                if message['command'] == 'DIES':
                    die1, die2 = message['args']
                    self.client.game.roll_dice(logic.Roll(die1, die2))
            elif self.client.network_game_color != self.client.game.color:
                if message['command'] == 'MOVE':
                    from_point, to_point = message['args']
                    self.client.game.move(from_point, to_point)
                elif message['command'] == 'ENDMOVE':
                    roll = logic.Roll()
                    self.client.game.roll_dice(roll)
                    self.client.bgp.send_dies(roll.die1, roll.die2)
        except socket.timeout as e:
            raise e
        except (socket.error, ConnectionError):
            self.client.state = DisconnectedState(self.client)

    @State.possible_points.getter
    def possible_points(self):
        if self.client.network_game_color != self.client.game.color:
            return []
        return self.client.game.possible_points
