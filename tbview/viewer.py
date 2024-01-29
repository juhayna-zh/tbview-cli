from tbview.dashing_lib.layout import RatioHSplit, RatioVSplit
from tbview.dashing_lib.widgets import PlotextTile, SelectionTile
from tbview.dashing_lib import *
import plotext as plt
from time import sleep
import blessed
from tbview.parser import read_records
from collections import OrderedDict

ERROR = '[ERROR]'
WARN = '[WARN]'
INFO = '[INFO]'
DEBUG = '[DEBUG]'

class TensorboardViewer:
    def __init__(self, event_path, event_tag) -> None:
        self.event_path = event_path
        self.event_tag = event_tag
        self.term = blessed.Terminal()
        self.logger = Log(title=' Log/Err', border_color=15)
        self.tag_selector = SelectionTile(
                    options= [],
                    current=0,
                    title=' Tags List', 
                    border_color=15,
                )
        self.ui = RatioHSplit(
            PlotextTile(self.plot, title='Plot', border_color=15),
            RatioVSplit(
                Text(" 1.Press arrow keys to locate coordinates.\n\n 2.Use number 1-9 or W/S to select tag.\n\n 3.Ctrl+C to quit.", color=15, title=' Tips', border_color=15),
                self.tag_selector,
                self.logger,
                ratios=(2, 4, 2),
                rest_pad_to=1,
            ),
            ratios=(4, 1) if self.term.width > 100 else (3, 1),
            rest_pad_to=1
        )

        self.records = OrderedDict()
        self.scan_event()

    
    def scan_event(self):
        for event in read_records(self.event_path):
            summary = event.summary
            for value in summary.value:
                if value.HasField('simple_value'):
                    # print(value.tag, value.simple_value, event.step)
                    if value.tag not in self.records:
                        self.records[value.tag] = {}
                    self.records[value.tag][event.step] = value.simple_value
        
        self.tag_selector.options = [
            f'[{i+1}] {root_tag} '
            for i, root_tag in enumerate(self.records)
        ]

    def handle_input(self, key):
        if key is None:
            return
        if key.is_sequence:
            pass 
        else: 
            if key.isdigit():
                digit = int(key)  
                if digit > 0 and digit <= len(self.tag_selector.options):
                    self.tag_selector.current = digit - 1

    def log(self, msg, level=''):
        self.logger.append(self.term.white(f'{level} {msg}'))

    def plot(self, tbox):
        plt.theme('clear')
        plt.cld()
        plt.plot_size(tbox.w, tbox.h)
        key = list(self.records.keys())[self.tag_selector.current]
        plt.title(key)
        plt.plot(self.records[key].keys(), self.records[key].values())
        plt.xfrequency(10)
        plt.xlabel('step')
        plt.show()

    def run(self):
        term = self.term
        ui = self.ui
        self.log('tbview-cli started.', INFO)
        self.log(f'current run: {self.event_tag}', INFO)
        try:
            with term.fullscreen(), term.cbreak(), term.hidden_cursor():
                while True:
                    ui.ratios = (4, 1) if term.width > 100 else (3, 1)
                    ui.display()
                    key = term.inkey(timeout=0.1)
                    if key:
                        self.handle_input(key)
                        self.scan_event()
                    else:
                        sleep(0.3)
        except KeyboardInterrupt:
            print('exit.')

