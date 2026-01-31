from __future__ import annotations
import os
import arcade
from PIL import Image, ImageDraw, ImageEnhance, ImageOps


class AssetManager:
    def __init__(self) -> None:
        self.base_dir = os.path.join(os.getcwd(), "view")
        if not os.path.exists(self.base_dir):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(script_dir))
            self.base_dir = os.path.join(project_root, "view")
        if not os.path.exists(self.base_dir):
            self.base_dir = os.getcwd()

        print(f"DEBUG: Assets base directory: {self.base_dir}")

        self._loaded = False

        self.bronze_coin_sprites: dict[str, list[arcade.Texture] | arcade.Texture] = {}
        self.silver_coin_sprites: dict[str, list[arcade.Texture] | arcade.Texture] = {}
        self.gold_coin_sprites: dict[str, list[arcade.Texture] | arcade.Texture] = {}
        self.lucky_coin_sprites: dict[str, list[arcade.Texture] | arcade.Texture] = {}
        self.cursed_coin_sprites: dict[str, list[arcade.Texture] | arcade.Texture] = {}
        self.wisp_sprites: list[arcade.Texture] = []
        self.beetle_sprites: list[arcade.Texture] = []
        self.meteor_textures: list[arcade.Texture] = []
        self.explosion_textures: list[arcade.Texture] = []
        self.tornado_textures: list[arcade.Texture] = []
        self.crater_texture: arcade.Texture = None

    def load_all(self) -> None:
        print("Loading assets...")
        self._load_coin_type("bronze_coin", self.bronze_coin_sprites, arcade.color.BRASS)
        self._load_coin_type("silver_coin", self.silver_coin_sprites, arcade.color.LIGHT_GRAY)
        self._load_coin_type("gold_coin", self.gold_coin_sprites, arcade.color.GOLD)
        # === ЗАГРУЗКА СПЕЦИАЛЬНЫХ МОНЕТ (TINTING) ===
        # Lucky Coin (Мягкий зеленый оттенок)
        print("Generating Lucky Coin sprites...")
        self._generate_tinted_coins("lucky_coin", self.gold_coin_sprites, (100, 200, 100, 200))

        # Cursed Coin (Темно-серый оттенок)
        print("Generating Cursed Coin sprites...")  # <--- Исправил текст
        self._generate_tinted_coins("cursed_coin", self.gold_coin_sprites,
                                    (40, 40, 40, 180))  # <--- Исправил название на "cursed_coin"
        self._load_meteor_stuff()
        self._load_tornado_stuff()
        self._load_wisp_sprites()  # <--- Загрузка виспа
        self._load_beetle_sprites()
        self._loaded = True

    def _load_wisp_sprites(self) -> None:
        """Загружает спрайты виспа (wisp000 - wisp021)"""
        wisp_dir = os.path.join(self.base_dir, "sprites", "wisp")

        if os.path.exists(wisp_dir):
            files = sorted(os.listdir(wisp_dir))
            loaded_count = 0
            for f in files:
                if f.endswith(".png"):
                    self.wisp_sprites.append(arcade.load_texture(os.path.join(wisp_dir, f)))
                    loaded_count += 1

            if loaded_count > 0:
                print(f"  -> Loaded {loaded_count} Wisp sprites")
            else:
                print(f"  WARNING: No PNG files found in {wisp_dir}")
        else:
            print(f"WARNING: Wisp folder not found: {wisp_dir}. Creating placeholder.")
            placeholder = self._create_pil_texture(arcade.color.PURPLE)
            self.wisp_sprites = [placeholder]

    def _load_beetle_sprites(self) -> None:
        """Загружает спрайты жука из папки view/sprites/beetle"""
        beetle_dir = os.path.join(self.base_dir, "sprites", "beetle")

        # Структура: {"up": [tex1, ...], "down": [...], ...}
        sprites_dict = {"up": [], "down": [], "left": [], "right": []}

        if not os.path.exists(beetle_dir):
            print(f"  WARNING: Beetle folder not found: {beetle_dir}")
            self.beetle_sprites = sprites_dict
            return

        # Пробуем разные варианты имен папок (с префиксом beetle_ и без)
        # В твоем случае: beetle_up, beetle_down...
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
                                arcade.load_texture(os.path.join(dir_path, f))
                            )
                    if sprites_dict[direction]:
                        loaded = True
                        break  # Если нашли в одной папке, вторую не ищем

            if loaded:
                print(f"  -> Loaded {len(sprites_dict[direction])} frames for direction {direction}")

        self.beetle_sprites = sprites_dict

    def load_ui_assets(self) -> None:
        """Загружает кнопки и шрифт для интерфейса"""
        ui_base_dir = os.path.join(self.base_dir, "ui")

        self.ui_assets = {
            "btn_normal": None,
            "btn_pressed": None,
            "btn_disabled": None,
            "font_name": "Arial"
        }

        buttons_dir = os.path.join(ui_base_dir, "buttons")
        if os.path.exists(buttons_dir):
            self.ui_assets["btn_normal"] = arcade.load_texture(os.path.join(buttons_dir, "normal.png"))
            self.ui_assets["btn_pressed"] = arcade.load_texture(os.path.join(buttons_dir, "pressed.png"))
            self.ui_assets["btn_disabled"] = arcade.load_texture(os.path.join(buttons_dir, "disabled.png"))
            print(f"DEBUG: Loaded UI textures from {buttons_dir}")
        else:
            print(f"WARNING: UI buttons folder not found: {buttons_dir}")

        font_dir = os.path.join(self.base_dir, "ui", "fonts")

        print("-" * 50)
        print(f"DEBUG: Searching for fonts in: {font_dir}")
        if os.path.exists(font_dir):
            font_file = os.path.join(font_dir, "RuneScape-ENA.ttf")
            if os.path.exists(font_file):
                self.ui_assets["font_name"] = font_file
                print(">>> SUCCESS: Custom 'RuneScape-ENA' font loaded!")
            else:
                print(">>> WARNING: RuneScape-ENA.ttf NOT FOUND!")
        else:
            print(f">>> ERROR: Folder 'fonts' does not exist in {ui_base_dir}")
        print("-" * 50)

    def _load_coin_type(self, folder_name: str, target_dict: dict, placeholder_color) -> None:
        sprites_dir = os.path.join(self.base_dir, "sprites", folder_name)

        if not os.path.exists(sprites_dir):
            print(f"WARNING: Folder '{sprites_dir}' not found. Using placeholders.")
            self._create_placeholders(target_dict, placeholder_color)
            return

        def load_dir(name: str) -> list[arcade.Texture]:
            path = os.path.join(sprites_dir, name)
            if not os.path.exists(path):
                return []
            files = sorted(os.listdir(path))
            return [
                arcade.load_texture(os.path.join(path, f))
                for f in files if f.endswith(".png")
            ]

        short_name = folder_name.replace("_coin", "")
        heads_file = f"{short_name}_heads.png"
        tails_file = f"{short_name}_tails.png"

        heads_path = os.path.join(sprites_dir, "heads", heads_file)
        tails_path = os.path.join(sprites_dir, "tails", tails_file)

        heads_tex = self._create_pil_texture(placeholder_color)
        tails_tex = self._create_pil_texture(arcade.color.BLUE)

        if os.path.exists(heads_path):
            heads_tex = arcade.load_texture(heads_path)

        if os.path.exists(tails_path):
            tails_tex = arcade.load_texture(tails_path)

        target_dict.update({
            "up": load_dir("up"),
            "down": load_dir("down"),
            "left": load_dir("left"),
            "right": load_dir("right"),
            # Добавляем диагональные анимации
            "up_left": load_dir("up_left"),
            "up_right": load_dir("up_right"),
            "down_left": load_dir("down_left"),
            "down_right": load_dir("down_right"),
            # --------------------------------
            "heads": heads_tex,
            "tails": tails_tex,
        })
        print(f"  -> Loaded sprites for {folder_name}")

    def _create_placeholders(self, target_dict: dict, color) -> None:
        placeholder = self._create_pil_texture(color)
        tails_placeholder = self._create_pil_texture(arcade.color.BLUE)

        target_dict.update({
            "up": [], "down": [], "left": [], "right": [],
            "heads": placeholder,
            "tails": tails_placeholder
        })

    def _create_pil_texture(self, color) -> arcade.Texture:
        pil_image = Image.new("RGBA", (100, 100), (int(color[0]), int(color[1]), int(color[2]), 255))
        draw = ImageDraw.Draw(pil_image)
        draw.rectangle([0, 0, 99, 99], outline=(255, 255, 255, 255), width=5)
        return arcade.Texture(image=pil_image)

    def is_loaded(self) -> bool:
        return self._loaded

    def _load_meteor_stuff(self) -> None:
        # 1. Загрузка Метеорита (falling)
        meteor_dir = os.path.join(self.base_dir, "sprites", "meteor")
        if os.path.exists(meteor_dir):
            files = sorted(os.listdir(meteor_dir))
            for f in files:
                if f.endswith(".png"):
                    self.meteor_textures.append(arcade.load_texture(os.path.join(meteor_dir, f)))
            print(f"  -> Loaded {len(self.meteor_textures)} Meteor sprites")
        else:
            print(f"  -> WARNING: Meteor folder not found at {meteor_dir}")

        # 2. Загрузка Кратера (crater)
        crater_path = os.path.join(self.base_dir, "sprites", "crater", "crater.png")
        if not os.path.exists(crater_path):
            crater_path = os.path.join(self.base_dir, "sprites", "crater", "Crater.png")  # Другой вариант регистра

        if os.path.exists(crater_path):
            self.crater_texture = arcade.load_texture(crater_path)
            print("  -> Loaded Crater texture")
        else:
            print(f"  -> WARNING: Crater texture not found at {crater_path}")

        # 3. Загрузка Взрыва (Explosion) - ИСПРАВЛЕННЫЙ ПУТЬ
        # Ищем в папке view/sprites/Explosion
        explosion_dir = os.path.join(self.base_dir, "sprites", "Explosion")

        if os.path.exists(explosion_dir):
            files = sorted(os.listdir(explosion_dir))
            for f in files:
                if f.endswith(".png"):
                    self.explosion_textures.append(arcade.load_texture(os.path.join(explosion_dir, f)))
            print(f"  -> Loaded {len(self.explosion_textures)} Explosion sprites from {explosion_dir}")
        else:
            print(f"  -> WARNING: Explosion folder not found at {explosion_dir}")

    def _load_tornado_stuff(self):
        # Загрузка спрайтов Торнадо
        tornado_dir = os.path.join(self.base_dir, "sprites", "tornado")
        if os.path.exists(tornado_dir):
            files = sorted(os.listdir(tornado_dir))
            for f in files:
                if f.lower().endswith(".png"):
                    self.tornado_textures.append(arcade.load_texture(os.path.join(tornado_dir, f)))
            print(f"  -> Loaded {len(self.tornado_textures)} Tornado sprites")
        else:
            print(f"  -> WARNING: Tornado folder not found at {tornado_dir}")

    def _generate_tinted_coins(self, target_name: str, source_sprites: dict, tint_color: tuple) -> None:
        """Создает копии спрайтов с наложенным цветом"""
        target_dict = {}

        # Обрабатываем Heads и Tails (одиночные текстуры)
        for key in ["heads", "tails"]:
            if key in source_sprites:
                source_tex = source_sprites[key]
                target_dict[key] = self._create_tinted_texture(source_tex, tint_color)

        # Обрабатываем анимации (списки)
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

    def _create_tinted_texture(self, source_texture: arcade.Texture, tint_color: tuple) -> arcade.Texture:
        """Перекрашивает текстуру, СООХРАНЯЯ ПРОЗРАЧНОСТЬ"""
        img = source_texture.image

        if img is None:
            return source_texture

        # 1. Разделяем картинку на каналы (R, G, B, Alpha)
        # Это позволяет сохранить форму монетки (прозрачные пиксели)
        if img.mode == 'RGBA':
            r, g, b, a = img.split()
            # Объединяем только цвет, без прозрачности, и переводим в Ч/Б
            rgb_img = Image.merge('RGB', (r, g, b))
            gray = rgb_img.convert('L')
        else:
            # Если вдруг картинка без прозрачности, просто красим всё
            gray = img.convert('L')
            a = None

        # 2. Берем цвет для окраски
        r_tint, g_tint, b_tint, _ = tint_color

        # 3. Красим черно-белую картинку в нужный цвет
        # Black - это тени, White - это светлые части
        colored = ImageOps.colorize(gray, black=(20, 20, 20), white=(r_tint, g_tint, b_tint))

        # 4. Переводим результат в RGBA
        colored_rgba = colored.convert('RGBA')

        # 5. ВОЗВРАЩАЕМ ПРОЗРАЧНОСТЬ!
        # Мы берем альфу (форму) из оригинала и накладываем на новую картинку
        if a:
            colored_rgba.putalpha(a)

        return arcade.Texture(image=colored_rgba)