from __future__ import annotations
import os
import sys
import pygame


# import arcade # УБРАЛИ

class AssetManager:
    def __init__(self) -> None:
        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.join(sys._MEIPASS, "view")
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(script_dir))
            self.base_dir = os.path.join(project_root, "view")

        print(f"DEBUG: Assets base directory: {self.base_dir}")

        if not os.path.exists(self.base_dir):
            print(f"FATAL ERROR: View directory not found at {self.base_dir}")
            self.base_dir = os.getcwd()

        self._loaded = False

        # Вместо arcade.Texture будем хранить pygame.Surface
        self.bronze_coin_sprites: dict[str, list[pygame.Surface] | pygame.Surface] = {}
        self.silver_coin_sprites: dict[str, list[pygame.Surface] | pygame.Surface] = {}
        self.gold_coin_sprites: dict[str, list[pygame.Surface] | pygame.Surface] = {}
        self.lucky_coin_sprites: dict[str, list[pygame.Surface] | pygame.Surface] = {}
        self.cursed_coin_sprites: dict[str, list[pygame.Surface] | pygame.Surface] = {}
        self.wisp_sprites: list[pygame.Surface] = []
        self.beetle_sprites: dict[str, list[pygame.Surface]] = {}
        self.meteor_textures: list[pygame.Surface] = []
        self.explosion_textures: list[pygame.Surface] = []
        self.tornado_textures: list[pygame.Surface] = []
        self.crater_texture: pygame.Surface = None

    def load_all(self) -> None:
        print("Loading assets...")
        # Цвета заменили на кортежи RGB
        self._load_coin_type("bronze_coin", self.bronze_coin_sprites, (181, 166, 66))
        self._load_coin_type("silver_coin", self.silver_coin_sprites, (192, 192, 192))
        self._load_coin_type("gold_coin", self.gold_coin_sprites, (255, 215, 0))

        print("Generating Lucky Coin sprites...")
        self._generate_tinted_coins("lucky_coin", self.gold_coin_sprites, (100, 200, 100, 200))

        print("Generating Cursed Coin sprites...")
        self._generate_tinted_coins("cursed_coin", self.gold_coin_sprites, (40, 40, 40, 180))

        self._load_meteor_stuff()
        self._load_tornado_stuff()
        self._load_wisp_sprites()
        self._load_beetle_sprites()
        self._loaded = True

    def _load_wisp_sprites(self) -> None:
        wisp_dir = os.path.join(self.base_dir, "sprites", "wisp")
        if os.path.exists(wisp_dir):
            files = sorted(os.listdir(wisp_dir))
            loaded_count = 0
            for f in files:
                if f.endswith(".png"):
                    self.wisp_sprites.append(pygame.image.load(os.path.join(wisp_dir, f)).convert_alpha())
                    loaded_count += 1
            if loaded_count > 0:
                print(f"  -> Loaded {loaded_count} Wisp sprites")
            else:
                print(f"  WARNING: No PNG files found in {wisp_dir}")
        else:
            print(f"WARNING: Wisp folder not found: {wisp_dir}. Creating placeholder.")
            placeholder = self._create_placeholder_surface((128, 0, 128))
            self.wisp_sprites = [placeholder]

    def _load_beetle_sprites(self) -> None:
        beetle_dir = os.path.join(self.base_dir, "sprites", "beetle")
        sprites_dict = {"up": [], "down": [], "left": [], "right": []}

        if not os.path.exists(beetle_dir):
            print(f"  WARNING: Beetle folder not found: {beetle_dir}")
            self.beetle_sprites = sprites_dict
            return

        folder_map = {
            "up": ["up", "beetle_up"],
            "down": ["down", "beetle_down"],
            "left": ["left", "beetle_left"],
            "right": ["right", "beetle_right"]
        }

        for direction, variants in folder_map.items():
            loaded = False
            for folder_name in variants:
                dir_path = os.path.join(beetle_dir, folder_name)
                if os.path.exists(dir_path):
                    files = sorted(os.listdir(dir_path))
                    for f in files:
                        if f.endswith(".png"):
                            sprites_dict[direction].append(
                                pygame.image.load(os.path.join(dir_path, f)).convert_alpha()
                            )
                    if sprites_dict[direction]:
                        loaded = True
                        break
            if loaded:
                print(f"  -> Loaded {len(sprites_dict[direction])} frames for direction {direction}")

        self.beetle_sprites = sprites_dict

    def load_ui_assets(self) -> None:
        ui_base_dir = os.path.join(self.base_dir, "ui")
        self.ui_assets = {
            "btn_normal": None,
            "btn_pressed": None,
            "btn_disabled": None,
            "font_name": "Arial"
        }

        buttons_dir = os.path.join(ui_base_dir, "buttons")
        if os.path.exists(buttons_dir):
            self.ui_assets["btn_normal"] = pygame.image.load(os.path.join(buttons_dir, "normal.png")).convert_alpha()
            self.ui_assets["btn_pressed"] = pygame.image.load(os.path.join(buttons_dir, "pressed.png")).convert_alpha()
            self.ui_assets["btn_disabled"] = pygame.image.load(
                os.path.join(buttons_dir, "disabled.png")).convert_alpha()
            print(f"DEBUG: Loaded UI textures from {buttons_dir}")
        else:
            print(f"WARNING: UI buttons folder not found: {buttons_dir}")

        font_filename = "RuneScape-ENA.ttf"
        font_path = os.path.join(ui_base_dir, "fonts", font_filename)
        if os.path.exists(font_path):
            self.ui_assets["font_name"] = font_path
            print(f">>> SUCCESS: Font found at: {font_path}")
        else:
            print(f">>> WARNING: Font file NOT FOUND at: {font_path}")

    def _load_coin_type(self, folder_name: str, target_dict: dict, placeholder_color) -> None:
        sprites_dir = os.path.join(self.base_dir, "sprites", folder_name)
        if not os.path.exists(sprites_dir):
            print(f"WARNING: Folder '{sprites_dir}' not found. Using placeholders.")
            self._create_placeholders(target_dict, placeholder_color)
            return

        def load_dir(name: str) -> list[pygame.Surface]:
            path = os.path.join(sprites_dir, name)
            if not os.path.exists(path):
                return []
            files = sorted(os.listdir(path))

            # --- ДОБАВИТЬ ЭТОТ ОТЛАДОЧНЫЙ ВЫВОД ---
            if folder_name == "silver_coin" and name in ["up", "down"]:
                print(f"DEBUG: Загружаю анимацию {name} для серебряной монеты из: {path}")
                print(f"DEBUG: Найдены файлы: {files}")
            # ------------------------------------

            return [
                pygame.image.load(os.path.join(path, f)).convert_alpha()
                for f in files if f.endswith(".png")
            ]

        short_name = folder_name.replace("_coin", "")
        heads_file = f"{short_name}_heads.png"
        tails_file = f"{short_name}_tails.png"

        heads_path = os.path.join(sprites_dir, "heads", heads_file)
        tails_path = os.path.join(sprites_dir, "tails", tails_file)

        heads_tex = self._create_placeholder_surface(placeholder_color)
        tails_tex = self._create_placeholder_surface((0, 0, 255))

        if os.path.exists(heads_path):
            heads_tex = pygame.image.load(heads_path).convert_alpha()

        if os.path.exists(tails_path):
            tails_tex = pygame.image.load(tails_path).convert_alpha()

        # Загружаем направления
        up_list = load_dir("up")
        down_list = load_dir("down")
        left_list = load_dir("left")
        right_list = load_dir("right")
        # ... остальные направления

        # ЗАЩИТА: Если какая-то папка пуста, используем heads_tex, чтобы не было пустого списка
        if not up_list: up_list = [heads_tex]
        if not down_list: down_list = [heads_tex]
        if not left_list: left_list = [heads_tex]
        if not right_list: right_list = [heads_tex]

        # Аналогично для диагоналей
        up_left_list = load_dir("up_left")
        down_left_list = load_dir("down_left")
        up_right_list = load_dir("up_right")
        down_right_list = load_dir("down_right")

        if not up_left_list: up_left_list = [heads_tex]
        # ... и так далее для всех диагоналей

        target_dict.update({
            "up": up_list,
            "down": down_list,
            "left": left_list,
            "right": right_list,
            "up_left": up_left_list,
            "up_right": up_right_list,
            "down_left": down_left_list,
            "down_right": down_right_list,
            "heads": heads_tex,
            "tails": tails_tex,
        })
        print(f"  -> Loaded sprites for {folder_name}")

        def load_dir(name: str) -> list[pygame.Surface]:
            path = os.path.join(sprites_dir, name)
            if not os.path.exists(path):
                return []
            files = sorted(os.listdir(path))
            return [
                pygame.image.load(os.path.join(path, f)).convert_alpha()
                for f in files if f.endswith(".png")
            ]

        short_name = folder_name.replace("_coin", "")
        heads_file = f"{short_name}_heads.png"
        tails_file = f"{short_name}_tails.png"

        heads_path = os.path.join(sprites_dir, "heads", heads_file)
        tails_path = os.path.join(sprites_dir, "tails", tails_file)

        heads_tex = self._create_placeholder_surface(placeholder_color)
        tails_tex = self._create_placeholder_surface((0, 0, 255))

        if os.path.exists(heads_path):
            heads_tex = pygame.image.load(heads_path).convert_alpha()

        if os.path.exists(tails_path):
            tails_tex = pygame.image.load(tails_path).convert_alpha()

        target_dict.update({
            "up": load_dir("up"),
            "down": load_dir("down"),
            "left": load_dir("left"),
            "right": load_dir("right"),
            "up_left": load_dir("up_left"),
            "up_right": load_dir("up_right"),
            "down_left": load_dir("down_left"),
            "down_right": load_dir("down_right"),
            "heads": heads_tex,
            "tails": tails_tex,
        })
        print(f"  -> Loaded sprites for {folder_name}")

    def _create_placeholders(self, target_dict: dict, color) -> None:
        placeholder = self._create_placeholder_surface(color)
        tails_placeholder = self._create_placeholder_surface((0, 0, 255))
        target_dict.update({
            "up": [], "down": [], "left": [], "right": [],
            "heads": placeholder,
            "tails": tails_placeholder
        })

    def _create_placeholder_surface(self, color) -> pygame.Surface:
        surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        surface.fill(color)
        pygame.draw.rect(surface, (255, 255, 255, 255), (0, 0, 99, 99), 5)
        return surface

    def is_loaded(self) -> bool:
        return self._loaded

    def _load_meteor_stuff(self) -> None:
        meteor_dir = os.path.join(self.base_dir, "sprites", "meteor")
        if os.path.exists(meteor_dir):
            files = sorted(os.listdir(meteor_dir))
            for f in files:
                if f.endswith(".png"):
                    self.meteor_textures.append(pygame.image.load(os.path.join(meteor_dir, f)).convert_alpha())
            print(f"  -> Loaded {len(self.meteor_textures)} Meteor sprites")
        else:
            print(f"  -> WARNING: Meteor folder not found at {meteor_dir}")

        crater_path = os.path.join(self.base_dir, "sprites", "crater", "crater.png")
        if not os.path.exists(crater_path):
            crater_path = os.path.join(self.base_dir, "sprites", "crater", "Crater.png")

        if os.path.exists(crater_path):
            self.crater_texture = pygame.image.load(crater_path).convert_alpha()
            print("  -> Loaded Crater texture")
        else:
            print(f"  -> WARNING: Crater texture not found at {crater_path}")

        explosion_dir = os.path.join(self.base_dir, "sprites", "Explosion")
        if os.path.exists(explosion_dir):
            files = sorted(os.listdir(explosion_dir))
            for f in files:
                if f.endswith(".png"):
                    self.explosion_textures.append(pygame.image.load(os.path.join(explosion_dir, f)).convert_alpha())
            print(f"  -> Loaded {len(self.explosion_textures)} Explosion sprites")
        else:
            print(f"  -> WARNING: Explosion folder not found at {explosion_dir}")

    def _load_tornado_stuff(self):
        tornado_dir = os.path.join(self.base_dir, "sprites", "tornado")
        if os.path.exists(tornado_dir):
            files = sorted(os.listdir(tornado_dir))
            for f in files:
                if f.lower().endswith(".png"):
                    self.tornado_textures.append(pygame.image.load(os.path.join(tornado_dir, f)).convert_alpha())
            print(f"  -> Loaded {len(self.tornado_textures)} Tornado sprites")
        else:
            print(f"  -> WARNING: Tornado folder not found at {tornado_dir}")

    def _generate_tinted_coins(self, target_name: str, source_sprites: dict, tint_color: tuple) -> None:
        """Создает копии спрайтов с наложенным цветом через BLEND_MULT"""
        target_dict = {}
        for key in ["heads", "tails"]:
            if key in source_sprites:
                source_tex = source_sprites[key]
                target_dict[key] = self._create_tinted_texture(source_tex, tint_color)

        for key in ["up", "down", "left", "right", "up_left", "up_right", "down_left", "down_right"]:
            if key in source_sprites:
                source_list = source_sprites[key]
                target_list = []
                for tex in source_list:
                    target_list.append(self._create_tinted_texture(tex, tint_color))
                target_dict[key] = target_list

        if target_name == "lucky_coin":
            self.lucky_coin_sprites = target_dict
        elif target_name == "cursed_coin":
            self.cursed_coin_sprites = target_dict

    def _create_tinted_texture(self, source_surface: pygame.Surface, tint_color: tuple) -> pygame.Surface:
        """Перекрашивает текстуру, сохраняя тени (альфа-канал и яркость)"""
        # Создаем копию
        tinted = source_surface.copy()
        # Создаем поверхность цвета
        color_surface = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
        color_surface.fill(tint_color)
        # Накладываем цвет с флагом умножения (R = R_src * R_color / 255)
        # Это сохраняет тени оригинала, но меняет оттенок
        tinted.blit(color_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return tinted
