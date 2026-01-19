from __future__ import annotations
import os
import arcade
from PIL import Image, ImageDraw  # Импортируем Pillow для создания заглушек


class AssetManager:
    def __init__(self) -> None:
        # Поиск папки view
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

    def load_all(self) -> None:
        print("Loading assets...")
        self._load_coin_type("bronze_coin", self.bronze_coin_sprites, arcade.color.BRASS)
        self._load_coin_type("silver_coin", self.silver_coin_sprites, arcade.color.LIGHT_GRAY)
        self._load_coin_type("gold_coin", self.gold_coin_sprites, arcade.color.GOLD)
        self._loaded = True

    def load_ui_assets(self) -> None:
        """Загружает кнопки и шрифт для интерфейса"""
        ui_base_dir = os.path.join(self.base_dir, "ui")

        # --- 1. Загрузка кнопок (как было) ---
        self.ui_assets = {
            "btn_normal": None,
            "btn_pressed": None,
            "btn_disabled": None,
            "font_name": "Arial"  # По умолчанию, если файл не найдется
        }

        buttons_dir = os.path.join(ui_base_dir, "buttons")
        if os.path.exists(buttons_dir):
            self.ui_assets["btn_normal"] = arcade.load_texture(os.path.join(buttons_dir, "normal.png"))
            self.ui_assets["btn_pressed"] = arcade.load_texture(os.path.join(buttons_dir, "pressed.png"))
            self.ui_assets["btn_disabled"] = arcade.load_texture(os.path.join(buttons_dir, "disabled.png"))
            print(f"DEBUG: Loaded UI textures from {buttons_dir}")
        else:
            print(f"WARNING: UI buttons folder not found: {buttons_dir}")

        # --- 2. Загрузка шрифта (С ДЕТАЛЬНЫМИ ЛОГАМИ) ---
        # Формируем путь к папке шрифтов
        font_dir = os.path.join(self.base_dir, "ui", "fonts")

        print("-" * 50)
        print(f"DEBUG: Searching for fonts in: {font_dir}")
        print(f"DEBUG: Does this folder exist? {os.path.exists(font_dir)}")

        if os.path.exists(font_dir):
            # Собираем полный путь к файлу шрифта
            font_file = os.path.join(font_dir, "RuneScape-ENA.ttf")
            print(f"DEBUG: Trying to load: {font_file}")
            print(f"DEBUG: Does font file exist? {os.path.exists(font_file)}")

            if os.path.exists(font_file):
                # Файл есть! Используем его
                self.ui_assets["font_name"] = font_file
                print(">>> SUCCESS: Custom 'RuneScape-ENA' font loaded!")
            else:
                # Файла нет. Смотрим, что вообще лежит в папке
                print(">>> WARNING: RuneScape-ENA.ttf NOT FOUND!")
                print(f">>> List of files in folder: {os.listdir(font_dir)}")
                print(">>> Check for typos or hidden extensions like .txt")
        else:
            # Папки нет вообще
            print(f">>> ERROR: Folder 'fonts' does not exist in {ui_base_dir}")

        print("-" * 50)
    def _load_coin_type(self, folder_name: str, target_dict: dict, placeholder_color) -> None:
        """Универсальный метод загрузки для любого типа монетки"""
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

        # Формируем имена файлов
        short_name = folder_name.replace("_coin", "")
        heads_file = f"{short_name}_heads.png"
        tails_file = f"{short_name}_tails.png"

        heads_path = os.path.join(sprites_dir, "heads", heads_file)
        tails_path = os.path.join(sprites_dir, "tails", tails_file)

        # Создаем дефолтные текстуры через Pillow
        heads_tex = self._create_pil_texture(placeholder_color)
        tails_tex = self._create_pil_texture(arcade.color.BLUE)  # Решка синяя

        if os.path.exists(heads_path):
            heads_tex = arcade.load_texture(heads_path)

        if os.path.exists(tails_path):
            tails_tex = arcade.load_texture(tails_path)

        target_dict.update({
            "up": load_dir("up"),
            "down": load_dir("down"),
            "left": load_dir("left"),
            "right": load_dir("right"),
            "heads": heads_tex,
            "tails": tails_tex,
        })
        print(f"  -> Loaded sprites for {folder_name}")

    def _create_placeholders(self, target_dict: dict, color) -> None:
        """Создает заглушки, если папка не найдена"""
        placeholder = self._create_pil_texture(color)
        tails_placeholder = self._create_pil_texture(arcade.color.BLUE)

        target_dict.update({
            "up": [], "down": [], "left": [], "right": [],
            "heads": placeholder,
            "tails": tails_placeholder
        })

    def _create_pil_texture(self, color) -> arcade.Texture:
        # Создаем изображение 100x100
        pil_image = Image.new("RGBA", (100, 100), (int(color[0]), int(color[1]), int(color[2]), 255))

        draw = ImageDraw.Draw(pil_image)
        draw.rectangle([0, 0, 99, 99], outline=(255, 255, 255, 255), width=5)

        return arcade.Texture(image=pil_image)

    def is_loaded(self) -> bool:
        return self._loaded