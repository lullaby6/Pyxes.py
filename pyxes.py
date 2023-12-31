import pygame, json, uuid, datetime, os, copy

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def write_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f)

def delete_json(path):
    os.remove(path)

def get_distance(a, b):
    return ((a.x - b.x)**2 + (a.y - b.y)**2)**0.5

def positions_match(a, b):
    return a.x == b.x and a.y == b.y

def is_inside(a, b):
    return a.x >= b.x and a.y >= b.y and a.x+a.width <= b.x+b.width and a.y+a.height <= b.y+b.height

def is_collide(a, b):
    return (
        (a.x + a.width) > b.x and
        a.x < (b.x + b.width) and
        (a.y + a.height) > b.y and
        a.y < (b.y + b.height)
    )

class ObjectPlaceholder:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


Colors = {
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'purple': (255, 0, 255),
    'orange': (255, 165, 0),
    'cyan': (0, 255, 255),
    'brown': (165, 42, 42),
    'pink': (255, 192, 203),
    'lightgray': (211, 211, 211),
    'lightblue': (173, 216, 230),
    'lightgreen': (144, 238, 144),
}

class GameObject:
    def __init__(self, x = 0, y = 0, z = 0, width = 10, height = 10, color = Colors['white'], alpha = 255, scale_x = 1, scale_y = 1, rotation = 0, tags = [], gui = False, ignore_pause = False, active = True, visible = True):
        self.id = str(uuid.uuid4())
        self.name = None
        self.scene = None
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height
        self.color = color
        self.alpha = alpha
        self.tags = tags
        self.gui = gui
        self.ignore_pause = ignore_pause
        self.active = active
        self.visible = visible
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.rotation = rotation
        self.self_copy = copy.deepcopy(self)
    def reset(self):
        self.self_copy_reset = copy.deepcopy(self.self_copy)
        self.self_copy_reset.name = self.name
        self.self_copy_reset.scene = self.scene
        self.__dict__.update(self.self_copy_reset.__dict__)

        if hasattr(self, 'load'): self.load()
    def drawing(self):
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.surface.set_alpha(self.alpha)
        self.surface.fill(self.color)

        self.drawing_x = self.x
        self.drating_y = self.y
        if self.gui == False:
            self.drawing_x -= self.scene.game.camera.x
            self.drating_y -= self.scene.game.camera.y

        self.scaled_surface = pygame.transform.scale(self.surface, (self.width * self.scale_x, self.height * self.scale_y))
        self.rotated_surface = pygame.transform.rotate(self.scaled_surface, self.rotation)
        self.scene.game.screen.blit(self.rotated_surface, (self.drawing_x, self.drating_y))
    def add_tag(self, tag):
        self.tags.append(tag)
        return tag
    def remove_tag(self, tag):
        self.tags.remove(tag)
        return tag
    def has_tag(self, tag):
        return tag in self.tags
    def get_tags(self):
        return self.tags
    def set_z(self, z):
        self.z = z
        self.scene.sort_game_objects_by_z()
    def set_size(self, width, height):
        self.width = width
        self.height = height

class Image(GameObject):
    def __init__(self, x = 0, y = 0, z = 0, width = 10, height = 10, color = Colors['white'], alpha = 255, scale_x = 1, scale_y = 1, rotation = 0, tags = [], gui = False, ignore_pause = False, active = True, visible = True, image_path = '', image_width = None, image_height = None, image_alpha = 255, image_offset_x = 0, image_offset_y = 0, image_scale_x = 1, image_scale_y = 1, image_rotation = 0):
        super().__init__(x=x, y=y , z=z, width=width, height=height, color=color, alpha=alpha, scale_x=scale_x, scale_y=scale_y, rotation=rotation, tags=tags, gui=gui, ignore_pause=ignore_pause, active=active, visible=visible)
        self.image_offset_x = image_offset_x
        self.image_offset_y = image_offset_y
        self.image_alpha = image_alpha
        self.image_scale_x = image_scale_x
        self.image_scale_y = image_scale_y
        self.image_rotation = image_rotation
        self.load_image(image_path, image_width, image_height)
    def drawing_image(self):
        self.image_drawing_x = self.x
        self.image_drawing_y = self.y
        if self.gui == False:
            self.image_drawing_x -= self.scene.game.camera.x
            self.image_drawing_y -= self.scene.game.camera.y
        self.scaled_image_scale = pygame.transform.smoothscale(self.scaled_image.convert_alpha(), (self.image_width * self.image_scale_x, self.image_height * self.image_scale_y))
        self.rotated_image = pygame.transform.rotate(self.scaled_image_scale, self.image_rotation)
        self.scene.game.screen.blit(self.rotated_image, (self.image_drawing_x + self.image_offset_x, self.image_drawing_y + self.image_offset_y, self.image_width, self.image_height))
    def load_image(self, image_path, image_width = None, image_height = None):
        self.image_path = image_path
        self.image = pygame.image.load(self.image_path)
        self.image_rect = self.image.get_rect()
        self.image_original_width = self.image_rect[2]
        self.image_original_height = self.image_rect[3]
        self.set_image_size(image_width, image_height)
        self.scaled_image.set_alpha(self.image_alpha)
    def set_image_alpha(self, alpha):
        self.image_alpha = alpha
        self.scaled_image.set_alpha(self.image_alpha)
    def set_image_size(self, image_width = None, image_height = None):
        self.image_width = image_width
        self.image_height = image_height
        if self.image_width == None:
            self.image_width = self.image_original_width
        if self.image_height == None:
            self.image_height = self.image_original_height
        self.scaled_image = pygame.transform.scale(self.image, (self.image_width, self.image_height))
    def set_image_width(self, width):
        self.set_image_size(width=width, height=None)
    def set_image_height(self, height):
        self.set_image_size(width=None, height=height)
    def set_image_offset(self, image_offset_x = None, image_offset_y = None):
        if image_offset_x != None:
            self.image_offset_x = image_offset_x
        if image_offset_y != None:
            self.image_offset_y = image_offset_y
    def set_image_offset_x(self, image_offset_x):
        self.set_image_offset(image_offset_x=image_offset_x, image_offset_y=None)
    def set_image_offset_y(self, image_offset_y):
        self.set_image_offset(image_offset_x=None, image_offset_y=image_offset_y)


class Text(GameObject):
    def __init__(self, text = 'Text', font_size = 10, font_color = Colors['white'], font_alpha = 255, font_family = 'Arial', text_offset_x = 0, text_offset_y = 0):
        super().__init__()
        self.text = text
        self.font_size = font_size
        self.font_color = font_color
        self.font_alpha = font_alpha
        self.font_family = font_family
        self.text_offset_x = text_offset_x
        self.text_offset_y = text_offset_y

class Sound:
    def __init__(self, sound_path, volume = 100):
        self.sound_path = sound_path
        self.volume = volume
    def play(self):
        pass
    def stop(self):
        pass
    def pause(self):
        pass
    def unpause(self):
        pass
    def set_volume(self, volume):
        self.volume = volume
        pass

class Camera:
    def __init__(self, game, x = 0, y = 0, delay = 50, zoom = 1.0, minZoom = 0.1, maxZoom = 3.0):
        self.game = game
        self.x = x
        self.y = y
        self.delay = delay
        self.zoom = zoom
        self.minZoom = minZoom
        self.maxZoom = maxZoom
        # self.self_copy = copy.deepcopy(self)
    def reset(self):
        self.__dict__.update(self.self_copy.__dict__)
    def target(self, x, y):
        # self.x = x - (self.game.width / 2)
        # self.y = y - (self.game.height / 2)
        self.x += ((x - self.game.width/2) - self.x) / self.delay
        self.y += ((y - self.game.height/2) - self.y) / self.delay
    def set_zoom(self, zoom):
        self.zoom = max(self.minZoom, min(self.maxZoom, zoom))

class Scene:
    def __init__(self, ignore_pause = False):
        self.name = None
        self.game = None
        self.game_objects = {}
        self.ignore_pause = ignore_pause
        self.self_copy = copy.deepcopy(self)
    def reset(self):
        self.self_copy_reset = copy.deepcopy(self.self_copy)
        self.self_copy_reset.name = self.name
        self.self_copy_reset.game = self.game
        self.__dict__.update(self.self_copy_reset.__dict__)
        if hasattr(self, 'load'): self.load()

        for game_object in self.game_objects.values():
            game_object.reset()
            if hasattr(game_object, 'load'): game_object.load()

        self.sort_game_objects_by_z()
    def add_game_object(self, name, game_object):
        self.game_objects[name] = game_object
        self.game_objects[name].name = name
        self.game_objects[name].scene = self

        # Sort game objects by z
        self.sort_game_objects_by_z()

        if hasattr(self.game_objects[name], 'load'): self.game_objects[name].load()
        return self.game_objects[name]
    def sort_game_objects_by_z(self):
        game_objets_values = list(self.game_objects.values())
        game_objets_values_sorted_by_z = sorted(game_objets_values, key=lambda game_object: game_object.z)
        game_objets_sorted_by_z = {}
        for game_object in game_objets_values_sorted_by_z:
            game_objets_sorted_by_z[game_object.name] = game_object
        self.game_objects = game_objets_sorted_by_z
    def instant_game_object(self, game_object):
        random_uuid_name = str(uuid.uuid4())
        return self.add_game_object(random_uuid_name, game_object)
    def remove_game_object(self, name):
        del self.game_objects[name]
    def get_game_object(self, name):
        return self.game_objects[name]
    def get_game_objects_by_tag(self, tag):
        objects = []
        for game_object in self.game_objects.values():
            if game_object.has_tag(tag):
                objects.append(game_object)
        return objects

class Game:
    def __init__(self, width = 640, height = 480, bg_color = Colors['black'], bg_alpha = 255, title = 'Title', cursor = True, fps = 60, fill_on_pause = True, quit_on_escape = False, default_scene = Scene()):
        pygame.init()
        self.set_title(title)
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.bg_alpha = bg_alpha
        self.screen = pygame.display.set_mode((self.width, self.height))
        # self.screen.fill(self.bg_color)
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.prev_time = pygame.time.get_ticks()

        self.set_cursor_visibility(cursor)

        self.quit_on_escape = quit_on_escape
        self.fullscreen = False

        self.camera = Camera(self, 0, 0)

        self.running = False
        self.pause = False
        self.fill_on_pause = fill_on_pause

        self.pygame = pygame

        self.scenes = {}
        self.active_scene = None
        self.set_scene('default', default_scene)

        if hasattr(self, 'load'):
            self.load()
    def run(self):
        self.running = True
        while self.running:
            active_scene = self.get_active_scene()
            game_objects = active_scene.game_objects.values()

            self.pygame_events = {
                'key_down': pygame.KEYDOWN,
                'key_up': pygame.KEYUP,
                'mouse_down': pygame.MOUSEBUTTONDOWN,
                'mouse_up': pygame.MOUSEBUTTONUP,
                'mouse_motion': pygame.MOUSEMOTION,
                'mouse_wheel': pygame.MOUSEWHEEL,
                'joy_axis_motion': pygame.JOYAXISMOTION,
                'joy_button_down': pygame.JOYBUTTONDOWN,
                'joy_button_up': pygame.JOYBUTTONUP,
                'quit': pygame.QUIT,
                'fullscreen': pygame.FULLSCREEN,
                'resize': pygame.VIDEORESIZE,
                'expose': pygame.VIDEOEXPOSE,
                'focus': pygame.ACTIVEEVENT,
            }

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.quit_on_escape:
                        self.running = False
                elif event.type == pygame.MOUSEMOTION:
                    self.mouse_fixed_posotion_x = event.pos[0]
                    self.mouse_fixed_posotion_y = event.pos[1]
                    self.mouse_posotion_x = event.pos[0] + self.camera.x
                    self.mouse_posotion_y = event.pos[1] + self.camera.y
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for game_object in game_objects:
                        cursor = None
                        if game_object.gui == True:
                            cursor = ObjectPlaceholder(event.pos[0], event.pos[1], 0, 0)
                        else:
                            cursor = ObjectPlaceholder(event.pos[0] + self.camera.x, event.pos[1] + self.camera.y, 0, 0)
                        if is_inside(cursor, game_object) and hasattr(game_object, 'on_click') and game_object.active == True and ((game_object.ignore_pause == True and self.pause == True) or (self.pause == False)):
                            getattr(game_object, 'on_click')(event)
                for eventName in self.pygame_events:
                    if event.type == self.pygame_events[eventName]:
                        key_name = None
                        if hasattr(event, 'key'): key_name = pygame.key.name(event.key)
                        if hasattr(self, eventName):
                            getattr(self, eventName)(event, key_name)
                        if hasattr(active_scene, eventName):
                            getattr(active_scene, eventName)(event, key_name)
                        for game_object in game_objects:
                            if hasattr(game_object, eventName) and game_object.active == True and ((game_object.ignore_pause == True and self.pause == True) or (self.pause == False)):
                                getattr(game_object, eventName)(event, key_name)

            current_time = pygame.time.get_ticks()
            self.delta_time = (current_time - self.prev_time) / 1000.0
            self.prev_time = current_time

            if self.camera.zoom != 1.0:
                self.screen.fill(self.bg_color)

            if self.pause == False or (self.pause == True and self.fill_on_pause == True):
                self.bg_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                self.bg_surface.set_alpha(self.bg_alpha)
                self.bg_surface.fill(self.bg_color)
                self.screen.blit(self.bg_surface, (0, 0))

            if hasattr(self, 'update'):
                self.update()

            if hasattr(self, 'draw'):
                self.draw()

            if ((active_scene.ignore_pause == True and self.pause == True) or (self.pause == False)):
                if hasattr(active_scene, 'update'):
                    active_scene.update()
                if hasattr(active_scene, 'draw'):
                    active_scene.draw()

            for game_object in game_objects:
                if game_object.active == True:
                    if ((game_object.ignore_pause == True and self.pause == True) or (self.pause == False)):
                        # Check collision
                        for game_object_2 in game_objects:
                            if game_object_2.active == True:
                                if game_object.id != game_object_2.id and game_object.gui == False and game_object_2.gui == False and is_collide(game_object, game_object_2):
                                    if hasattr(game_object, 'on_collide'):
                                        game_object.on_collide(game_object_2)
                                    if hasattr(game_object_2, 'on_collide') and ((game_object_2.ignore_pause == True and self.pause == True) or (self.pause == False)):
                                        game_object_2.on_collide(game_object)

                        if hasattr(game_object, 'update'):
                            game_object.update()

                    if game_object.visible == True:
                        game_object.drawing()
                        if hasattr(game_object, 'drawing_image'):
                            game_object.drawing_image()
                        if hasattr(game_object, 'drawing_text'):
                            game_object.drawing_text()
                        if hasattr(game_object, 'draw'):
                            game_object.draw()

            # Draw the zoomed screen
            if self.camera.zoom != 1.0:
                scaled_screen = pygame.transform.scale(self.screen, (int(self.width * self.camera.zoom), int(self.height * self.camera.zoom)))
                self.screen.fill(self.bg_color)
                scaled_screen_position = (self.width/2 - scaled_screen.get_size()[0]/2, self.height/2 - scaled_screen.get_size()[1]/2)
                self.screen.blit(scaled_screen, scaled_screen_position)

            pygame.display.flip()
            pygame.display.update()
            self.clock.tick(self.fps)
    def set_title(self, title):
        self.title = title
        pygame.display.set_caption(title)
    def add_scene(self, name, scene):
        self.scenes[name] = scene
        self.scenes[name].name = name
        self.scenes[name].game = self
        if hasattr(self.scenes[name], 'load'): self.scenes[name].load()
        return self.scenes[name]
    def change_scene(self, name):
        self.active_scene = name
    def set_scene(self, name, scene):
        self.add_scene(name, scene)
        self.change_scene(name)
    def get_active_scene(self):
        return self.scenes[self.active_scene]
    def remove_scene(self, name):
        del self.scenes[name]
    def reset_scene(self):
        self.get_active_scene().reset()
    def set_fullscreen(self, fullscreen = True):
        self.fullscreen = fullscreen
        if fullscreen == True:
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.width, self.height))
    def toggle_fullscreen(self):
        self.set_fullscreen(not self.fullscreen)
    def set_size(self, width, height):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
    def set_pause(self, pause):
        self.pause = pause
        active_scene = self.get_active_scene()
        game_objects = active_scene.game_objects.values()

        if hasattr(self, 'on_pause'):
            self.on_pause(self.pause)

        if hasattr(active_scene, 'on_pause') and ((active_scene.ignore_pause == True and self.pause == True) or (self.pause == False)):
            active_scene.on_pause(self.pause)
        for game_object in game_objects:
            if hasattr(game_object, 'on_pause') and ((game_object.ignore_pause == True and self.pause == True) or (self.pause == False)):
                game_object.on_pause(self.pause)
    def toggle_pause(self):
        self.set_pause(not self.pause)
    def set_fps(self, fps):
        self.fps = fps
        self.clock = pygame.time.Clock()
    def set_cursor(self, cursor):
        pygame.mouse.set_cursor(cursor)
    def set_cursor_visibility(self, visibility):
        self.cusor = visibility
        pygame.mouse.set_visible(visibility)
    def toggle_cursor_visibility(self):
        self.set_cursor_visibility(not self.cursor)
    def hide_cursor(self):
        self.cursor = False
        pygame.mouse.set_visible(False)
    def show_cursor(self):
        self.cursor = True
        pygame.mouse.set_visible(True)
    def custom_event(self, eventName, prop = None):
        active_scene = self.get_active_scene()
        game_objects = active_scene.game_objects.values()

        if hasattr(self, eventName):
            getattr(self, eventName)(prop)

        if hasattr(active_scene, eventName) and ((active_scene.ignore_pause == True and self.pause == True) or (self.pause == False)):
            getattr(active_scene, eventName)(prop)

        for game_object in game_objects:
            if hasattr(game_object, eventName) and ((game_object.ignore_pause == True and self.pause == True) or (self.pause == False)):
                getattr(game_object, eventName)(prop)
    def screenshot(self, folder_path = 'screenshots'):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_file_name = f'{self.title} screenshot - {timestamp}.png'
        screenshot_file_path = os.path.join(folder_path, screenshot_file_name)
        pygame.image.save(self.screen, screenshot_file_path)
    def set_icon(self, path):
        self.icon_path = path
        self.icon_image = pygame.image.load(path)
        pygame.display.set_icon(self.icon_image)