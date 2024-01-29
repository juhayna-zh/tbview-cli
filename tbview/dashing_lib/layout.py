from .dashing import Tile, TBox

from typing import Optional
from functools import lru_cache


class RatioSplit(Tile):
    def __init__(self, *items, ratios=[], rest_pad_to:Optional[int]= None, **kw):
        super(RatioSplit, self).__init__(**kw)
        self.items = items
        self.ratios = ratios
        assert len(ratios) == len(items), "Please offer proper ratios"
        self.rest_pad_to = rest_pad_to
    
    @lru_cache()
    def calc_item_size(self, idx, total):
        if idx != self.rest_pad_to:
            return int((total // sum(self.ratios)) * self.ratios[idx])
        else:
            ret = int(total+0)
            for i in range(len(self.ratios)):
                if i != idx:
                    ret -= self.calc_item_size(i, total)
            return ret

    def _display(self, tbox, parent):
        """Render current tile and its items. Recurse into nested splits
        """
        tbox = self._draw_borders_and_title(tbox)

        if not self.items:
            # empty split
            self._fill_area(tbox, " ")
            return

        x = tbox.x
        y = tbox.y
        for idx, it in enumerate(self.items):
            if isinstance(self, RatioVSplit):
                item_height = self.calc_item_size(idx, tbox.h)
                item_width = tbox.w
            else:
                item_height = tbox.h
                item_width = self.calc_item_size(idx, tbox.w)
            it._display(TBox(tbox.t, x, y, item_width, item_height), self)
            if isinstance(self, RatioVSplit):
                x += item_height
            else:
                y += item_width

        # Fill leftover area
        if isinstance(self, RatioVSplit):
            leftover_x = tbox.h - x + 1
            if leftover_x > 0:
                self._fill_area(TBox(tbox.t, x, y, tbox.w, leftover_x), " ")
        else:
            leftover_y = tbox.w - y + 1
            if leftover_y > 0:
                self._fill_area(TBox(tbox.t, x, y, leftover_y, tbox.h), " ")

class RatioVSplit(RatioSplit):
    pass 

class RatioHSplit(RatioSplit):
    pass