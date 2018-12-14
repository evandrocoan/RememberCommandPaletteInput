
import sublime
import sublime_plugin

import os

from collections import deque
from channel_manager.channel_utilities import load_data_file
from channel_manager.channel_utilities import write_data_file

from debug_tools import getLogger
log = getLogger( 1, __name__ )

# Until python 3.5 the popitem() has has a bug where it does not accepts the last=False argument
# https://bugs.python.org/issue24394 TypeError: popitem() takes no keyword arguments, then,
# automatically detect which one we have here:
# https://docs.python.org/3/library/collections.html#collections.OrderedDict.popitem
def pop_last_item(dictionary):
    dictionary.popitem(last=True)

try:
    {1: 'a'}.popitem(last=True)

except TypeError:

    def pop_last_item(dictionary):
        dictionary.popitem()

CURRENT_PACKAGE_FILE   = os.path.dirname( os.path.realpath( __file__ ) )
PACKAGE_ROOT_DIRECTORY = CURRENT_PACKAGE_FILE.replace( ".sublime-package", "" )
CURRENT_PACKAGE_NAME   = os.path.basename( PACKAGE_ROOT_DIRECTORY )

g_settings = \
{
    "last_input": "",
    "workspaces": {}
}

MAXIMUM_WORSPACES_ENTRIES = 100

command_palette_states  = ("open", "close")
is_command_palette_open = False


def plugin_loaded():
    load_settings()


def load_settings():
    global g_settings
    global g_package_settings_path

    g_package_settings_path = os.path.join( sublime.packages_path(), "User", CURRENT_PACKAGE_NAME + ".inputs" )

    try:
        # Returns an OrderedDict
        g_settings = load_data_file( g_package_settings_path, exceptions=True )

    except:
        log.exception( "Could not load the settings file" )
        write_data_file( g_package_settings_path, g_settings, debug=0 )


def save_settings(widget_text):
    g_settings['last_input'] = widget_text
    project_file_name = sublime.active_window().project_file_name()

    if project_file_name:
        workspaces = g_settings.get( 'workspaces', {} )

        # https://docs.python.org/3/library/collections.html#collections.OrderedDict.move_to_end
        # https://stackoverflow.com/questions/16664874/how-can-i-add-an-element-at-the-top-of-an-ordereddict-in-python
        workspaces[project_file_name] = widget_text
        workspaces.move_to_end( project_file_name, last=False )

        while len( workspaces ) > MAXIMUM_WORSPACES_ENTRIES:
            pop_last_item( workspaces )

    write_data_file( g_package_settings_path, g_settings, debug=0 )


def get_input():
    project_file_name = sublime.active_window().project_file_name()
    workspaces = g_settings.get( 'workspaces', {} )
    widget_text = workspaces.get( project_file_name, g_settings.get( 'last_input', "" ) )
    return widget_text


class FixedCommandPaletteLastInputHistoryCommand(sublime_plugin.WindowCommand):

    def run(self):
        global is_command_palette_open
        global is_command_palette_just_closed

        if is_command_palette_open:
            # log( 2, "Command palette is already open, closing it..." )
            self.window.run_command( "fixed_hide_overlay_which_is_correctly_logged" )

        else:
            # log( 2, "Opening fixed command palette..." )
            self.window.run_command( "show_overlay", {"overlay": "command_palette"} )
            self.window.run_command( "select_all" )

            self.window.run_command( "fixed_command_palette_last_input_history_helper" )
            self.window.run_command( "select_all" )

            is_command_palette_open = True


class FixedCommandPaletteLastInputHistoryHelperCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        selections = self.view.sel()
        current_widget_text = self.view.substr( selections[0] )

        if len( current_widget_text ):
            save_settings( current_widget_text )
            self.view.erase( edit, selections[0] )

        # log( 2, "widget_text:         %r", get_input() )
        # log( 2, "current_widget_text: %r", current_widget_text )

        self.view.run_command( "append", {"characters": get_input()} )


class FixedCommandPaletteLastInputHistoryEventListener(sublime_plugin.EventListener):

    def on_activated( self, view ):
        """
            Allow to open the command palette correctly after running a command by pressing enter.

            How to detect when the user closed the `goto_definition` box?
            https://forum.sublimetext.com/t/how-to-detect-when-the-user-closed-the-goto-definition-box/25800
        """
        # log( 2, "on_activated, Setting is_command_palette_open to False..." )

        global is_command_palette_open
        is_command_palette_open = False

    def on_query_context(self, view, key, operator, operand, match_all):

        if key == "fixed_command_palette_last_input_history_context":
            # log( 2, "operand: %5s, is_command_palette_open: %s", operand, is_command_palette_open )

            if operand in command_palette_states:

                return operand == "open" \
                        or operand == "close" and is_command_palette_open

            else:
                return not is_command_palette_open

        return None

    def on_window_command(self, window, command_name, args):
        self.set_command_palette_state(window, command_name, args)

    def on_text_command(self, window, command_name, args):
        self.set_command_palette_state(window, command_name, args)

    def set_command_palette_state(self, window, command_name, args):
        # log( 2, "command_name: %s", command_name )

        if command_name == "fixed_hide_overlay_which_is_correctly_logged":
            # log( 2, "Setting is_command_palette_open to False..." )

            global is_command_palette_open
            is_command_palette_open = False


class FixedHideOverlayWhichIsCorrectlyLoggedCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.window.run_command( "hide_overlay" )


