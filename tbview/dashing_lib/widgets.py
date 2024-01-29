from .dashing import Tile, TBox, Text
import io
from contextlib import redirect_stdout
from typing import Callable

class PlotextTile(Tile):
    def __init__(self, plot_fn: Callable[[TBox], None], *args, **kw):
        super(PlotextTile, self).__init__(**kw)
        self.plot_fn = plot_fn

    def _display(self, tbox, parent):
        tbox = self._draw_borders_and_title(tbox)
        st = self.plot_to_string(TBox(tbox.t, 0, 0, w=tbox.w-4, h=tbox.h-2 ))
        for dx, line in enumerate(st.splitlines()):
            print(
                tbox.t.move(tbox.x + dx + 1, tbox.y + 2)
                + line
                + " " * (tbox.w - len(line) - 1)
            )
        dx += 2
        while dx < tbox.h:
            print(tbox.t.move(tbox.x + dx, tbox.y) + " " * tbox.w)
            dx += 1

    def plot_to_string(self, tbox):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.plot_fn(tbox)
        return buf.getvalue()



class SelectionTile(Text):
    def __init__(self, options, current=0, color=0, *args, **kw):
        super().__init__('', color, *args, **kw)
        self._current = current
        self._options = options

    @property
    def current(self):
        return self._current
    
    @current.setter
    def current(self, c):
        self._current = c
    
    @property
    def options(self):
        return self._options
    
    @options.setter
    def options(self, options):
        self._options = options
    
    def _apply_options_to_text(self, tbox:TBox):
        t = tbox.t
        styled_options = [
            (t.on_white if i == self._current else t.white)(opt)
            for i,opt in enumerate(self._options)
        ]
        self.text = '\n'.join(styled_options)
    
    def _display(self, tbox, parent):
        self._apply_options_to_text(tbox)
        super()._display(tbox, parent)