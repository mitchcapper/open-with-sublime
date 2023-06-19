import sublime
import sublime_plugin
import os
import sys
import subprocess
from functools import partial

SETTINGS_FILE = 'OpenWith.sublime-settings'
SETTINGS_KEY = 'apps'

s = sublime.load_settings(SETTINGS_FILE)

class OpenWithCommand(sublime_plugin.WindowCommand):

	def cursor_position(self, view):
		return view.rowcol(view.sel()[0].begin())

  
	def description(self):
		return 'Open file with application/editor.'

	def get_apps(self):
		return self.window.active_view().settings().get(SETTINGS_KEY, self.get_default_settings())

	@staticmethod
	def get_default_settings():
		return sublime.load_settings(SETTINGS_FILE).get(SETTINGS_KEY, [])

	def run(self, *args, **kwargs):
		apps = self.get_apps()
		select_app = partial(self.select_app, apps)
		if 'name' and ' command' in kwargs:
			self.prepare_command(kwargs)
		elif 'name' in kwargs:
			select_app(kwargs['name'])
		else:
			app_names = [app['name'] for app in apps]
			self.window.show_quick_panel(app_names, select_app)

	def select_app(self, apps, app_name):
		for i, app in enumerate(apps):
			if app_name == i or app_name == app['name']:
				self.prepare_command(app)

	def prepare_command(self, app):
		view = self.window.active_view()
		line, column = self.cursor_position(view)
		# self.activate(app)
		filename = view.file_name()
		variables = {
			'line': line + 1,
			'column': column + 1,
			'filename': filename,
			'directory': os.path.dirname(filename)
		}

		self._run(app.get('command'), variables)

	def update_tab_menu_file():
		cache_path = os.path.join(sublime.cache_path(), __package__)
		menu = OpenWithCommand.create_menu()
		if not os.path.exists(cache_path):
			os.mkdir(cache_path)

		cache_path = os.path.join(cache_path, "Tab Context.sublime-menu")
		with open(cache_path, "w", encoding="utf-8") as menu_file:
			menu_file.write(sublime.encode_value(menu, False))

	def create_menu():
		apps=OpenWithCommand.get_default_settings()

		menu = [{
			"caption": "Open With",
			"children": [{
				"caption": app['name'],
				"command": "open_with",
				"args": {"name": app['name']}
			} for app in apps]
		}]
		

		menu.insert(0,{"caption": "-", "id": "separator"})

		return menu

	@staticmethod
	def _template(cmd, variables):
		return map(lambda s: s.format(**variables), cmd)

	def _run(self, cmd, variables):
#		proc_env = os.environ.copy()
#		encoding = sys.getfilesystemencoding()
#		for k, v in proc_env.items():
#			proc_env[k] = os.path.expandvars(v).encode(encoding)
#		print(f'Running command {cmd} with vars: {variables}')
		#subprocess.Popen(self._template(cmd, variables), env=proc_env)
		subprocess.Popen(self._template(cmd, variables))

def plugin_loaded():
	global s
	s = sublime.load_settings(SETTINGS_FILE)
	#print(f"Loaded settings {s.get(SETTINGS_KEY)} ivew is: {sublime}")
	OpenWithCommand.update_tab_menu_file()