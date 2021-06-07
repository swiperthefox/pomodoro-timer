from . import jsonconfig

class PomodoroTimerConfig(jsonconfig.JsonBasedConfig):
    def get_time(self, long_session, type):
        s_type = 'long' if long_session else 'short'
        return self.get_config(['session', s_type, type])
    def get_font_size(self):
        return self.get_config(['appearance', 'font', 'size'])
    def get_progress_position(self):
        return self.get_config(['appearance', 'progress_position'])
    def get_progress_on_top(self):
        return self.get_config(['appearance', 'progress_window_on_top'])
    def get_minimal_progress_window(self):
        return self.get_config(['appearance', 'minimal_progress_window'])
    def get_main_window_on_top(self):
        return self.get_config(['appearance', 'main_window_on_top'])
    def show_note_editor(self):
        return self.get_config(['notification', 'show_note_editor'])
    def use_audio_alert(self):
        return self.get_config(['notification', 'use_audio'])
    def get_audio_file(self):
        return self.get_config(['notification', 'audio_file'])