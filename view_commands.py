
import sublime
import sublime_plugin


class SetViewNewNameCommand(sublime_plugin.TextCommand):

    def run(self, edit, new_name):

        if self.view.name() == 'Find Results':
            self.view.set_syntax_file( 'Packages/Text/Plain text.tmLanguage' )

        self.view.set_name( new_name )
        self.view.settings().set( 'last_input', new_name )

    def input(self, args):
        if "new_name" not in args:
            return SetViewNewNameInputHandler( self.view )


class SetViewNewNameInputHandler(sublime_plugin.TextInputHandler):

    def __init__(self, view):
        self.view = view

    def name(self):
        return "new_name"

    def placeholder(self):
        return "New View Name"

    def cancel(self):
        pass

    def initial_text(self):
        return self.view.settings().get( 'last_input', 'New Name' )

    def preview(self, text):
        pass

    def confirm(self, text):
        pass

    def validate(self, text):
        return len( text ) > 0

    def next_input(self, args):
        pass
