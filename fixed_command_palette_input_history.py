
import sublime
import sublime_plugin

widget_text = ""

command_palette_states  = ("open", "close")
is_command_palette_open = False

class FixedCommandPaletteLastInputHistoryCommand(sublime_plugin.WindowCommand):

    def run(self):
        global is_command_palette_open
        global is_command_palette_just_closed

        if is_command_palette_open:
            # print( "FixedCommandPaletteLastInputHistoryCommand, Command palette is already open, closing it..." )
            self.window.run_command( "fixed_hide_overlay_which_is_correctly_logged" )

        else:
            # print( "\nFixedCommandPaletteLastInputHistoryCommand, Opening fixed command palette..." )
            self.window.run_command( "show_overlay", {"overlay": "command_palette"} )
            self.window.run_command( "select_all" )

            self.window.run_command( "fixed_command_palette_last_input_history_helper" )
            self.window.run_command( "select_all" )

            is_command_palette_open = True


class FixedCommandPaletteLastInputHistoryHelperCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        selections = self.view.sel()

        global widget_text
        current_widget_text = self.view.substr( selections[0] )

        if len( current_widget_text ) \
                and current_widget_text != "\n":

            widget_text = current_widget_text
            self.view.erase( edit, selections[0] )

        # print( "FixedCommandPaletteLastInputHistoryCommand, widget_text:         %r" % ( str( widget_text ) ) )
        # print( "FixedCommandPaletteLastInputHistoryCommand, current_widget_text: %r" % ( str( current_widget_text ) ) )

        self.view.run_command( "append", {"characters": widget_text} )


class FixedCommandPaletteLastInputHistoryEventListener(sublime_plugin.EventListener):

    def on_activated( self, view ):
        """
            Allow to open the command palette correctly after running a command by pressing enter.

            How to detect when the user closed the `goto_definition` box?
            https://forum.sublimetext.com/t/how-to-detect-when-the-user-closed-the-goto-definition-box/25800
        """
        # print( "FixedCommandPaletteLastInputHistoryEventListener, on_activated, Setting is_command_palette_open to False..." )

        global is_command_palette_open
        is_command_palette_open = False

    def on_query_context(self, view, key, operator, operand, match_all):

        if key == "fixed_command_palette_last_input_history_context":
            # print( "FixedCommandPaletteLastInputHistoryEventListener, operand: %5s, is_command_palette_open: %s" % ( operand, str( is_command_palette_open ) ) )

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
        # print( "command_name: " + command_name )

        if command_name == "fixed_hide_overlay_which_is_correctly_logged":
            # print( "FixedCommandPaletteLastInputHistoryEventListener, set_command_palette_state, Setting is_command_palette_open to False..." )

            global is_command_palette_open
            is_command_palette_open = False


class FixedHideOverlayWhichIsCorrectlyLoggedCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.window.run_command( "hide_overlay" )


