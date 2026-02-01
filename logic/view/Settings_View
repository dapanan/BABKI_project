import arcade
import arcade.gui

class SettingsView(arcade.View):
    def __init__(self, settings, music):
        super().__init__()
        self.settings = settings
        self.music = music

        self.manager = arcade.gui.UIManager()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self.manager.enable()

        vbox = arcade.gui.UIBoxLayout(space_between=20)

        slider = arcade.gui.UISlider(
            value=self.settings.music_volume * 100,
            min_value=0,
            max_value=100,
            width=300
        )

        @slider.event()
        def on_change(event):
            self.settings.music_volume = slider.value / 100
            self.music.update()

        vbox.add(slider)

        back = arcade.gui.UIFlatButton(text="Назад", width=200)

        @back.event("on_click")
        def on_click(event):
            self.window.show_view(self.window.game_view)

        vbox.add(back)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=vbox
            )
        )

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.manager.draw()
