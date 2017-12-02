
import sublime
import sublime_plugin

clipboard_text = ""

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
            self.window.run_command( "copy" )

            global clipboard_text
            current_clipboard_text = sublime.get_clipboard()

            # print( "FixedCommandPaletteLastInputHistoryCommand, clipboard_text:         %r" % ( str( clipboard_text ) ) )
            # print( "FixedCommandPaletteLastInputHistoryCommand, current_clipboard_text: %r" % ( str( current_clipboard_text ) ) )

            if len( current_clipboard_text ) \
                    and current_clipboard_text != "\n":

                clipboard_text = current_clipboard_text

            else:
                sublime.set_clipboard( clipboard_text )

            self.window.run_command( "paste" )
            self.window.run_command( "select_all" )

            is_command_palette_open = True


class FixedCommandPaletteLastInputHistoryEventListener(sublime_plugin.EventListener):

    def on_activated( self, view ):
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


