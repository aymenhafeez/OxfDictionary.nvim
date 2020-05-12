import pynvim
from .dictionary import OxfordDict

@pynvim.plugin
class Dictionary:

    def __init__(self, nvim):
        self.nvim = nvim
        self.app_id = nvim.eval("g:OxfDictionary#app_id")
        self.app_key = nvim.eval("g:OxfDictionary#app_key")

    def get_word(self,args):
        if args:
            word = args[0]
        else:
            word = self.nvim.eval('expand("<cword>")')
        return word

    def echo(self, *msgs):
        self.nvim.command("echo '{}'".format(msgs))

    def re_definition(self,word):
        if word:
            return OxfordDict(self.app_id, self.app_key).get_definition(word)
        else:
            return "Words are not selected.", -1

    @pynvim.command('Definition', nargs='*')
    def display_def(self, args=''):
        selectedW = self.get_word(args)
        defs = self.re_definition(selectedW)

        #If an error occurs, return error message.
        if defs[1] == -1:
            self.nvim.command("echo '{}'".format(defs[0]))
            return

        screen_height = int(self.nvim.command_output("echo &lines"))
        screen_width = int(self.nvim.command_output("echo &columns"))
        fwin_height = defs[1]
        fwin_width = defs[2]
        cWin_col = self.nvim.current.window.col
        cWin_row = self.nvim.current.window.row
        win_cursol = self.nvim.current.window.cursor

        #where to set the new window
        cursor_row = cWin_row+win_cursol[0] \
            - int(self.nvim.command_output("echo line('w0')")) + 1
        if cursor_row > screen_height/2:
            anchor = 'SW'
            fwin_row = max(int(fwin_height), cursor_row-1)
        else:
            anchor = 'NW'
            fwin_row = min(screen_height-fwin_height, cursor_row+1)

        #make floating window
        self.nvim.command("let buf = nvim_create_buf(v:false, v:true)")
        self.nvim.command("call nvim_buf_set_lines(buf, 0, -1, v:true, ['Definition'])")
        for meaning in defs[0]:
            self.nvim.command("call nvim_buf_set_lines(buf, -1, -1, v:true, ['{}'])"\
                              .format(meaning))
        self.nvim.command("let opts = {{'relative': 'editor',\
                                        'width': {0},\
                                        'height': {1},\
                                        'col': 15,\
                                        'row': {2},\
                                        'anchor': '{3}',\
                                        'style': 'minimal'}}"\
                          .format(fwin_width, fwin_height+1, fwin_row, anchor))
        self.nvim.command("let win = nvim_open_win(buf, 1, opts)")

