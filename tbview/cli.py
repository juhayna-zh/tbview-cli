import argparse
import os
import sys
import inquirer
from tbview.viewer import TensorboardViewer
from tbview.parser import read_records

def check_file_or_directory(path):
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"{path} is not a valid file or directory")
    return path

def is_event_file(path:str):
    return path.startswith('events.out.tfevents')

def local_event_name(path):
    base = os.path.basename(path)
    base = base.replace('events.out.tfevents.', '')
    return 'events.out.tfevents.' + base[:base.index('.')]

def local_event_dir(path):
    dir = os.path.basename(path)
    if dir == '':
        dir = '.'
    return dir

def run_main(args):
    path = args.path

    if os.path.isfile(path):
        if is_event_file(path):
            target_event_path = os.path.abspath(path)
            target_event_name = local_event_name(path)
            target_event_dir = None
        else:
            print(f"Warning: invalid event filename: {path}")
            target_event_path = os.path.abspath(path)
            target_event_name = os.path.basename(path)
            target_event_dir = None
    elif os.path.isdir(path):
        target_options = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if is_event_file(file):
                    size = os.path.getsize(os.path.join(path, root, file))
                    target_options.append((root, file, size))
        if len(target_options) == 0:
            raise RuntimeError(f"No event file found in directory {path}")
        target_options = sorted(target_options, key=lambda x:x[2], reverse=True)
        options = [f'[{i}] {local_event_dir(op[0])}/{local_event_name(op[1])}'for i, op in enumerate(target_options)]
        options[0] += ' (default)'
        questions = [
            inquirer.List('choice',
                            message="Found more than one event file, please select with arrow keys",
                            choices=options,
                            carousel=True,
                            )
        ]
        answers = inquirer.prompt(questions)
        if answers is None:
            return
        select_index = options.index(answers['choice'])

        target_event_path = os.path.abspath(os.path.join(target_options[select_index][0], target_options[select_index][1]))
        target_event_name = local_event_name(target_options[select_index][1])
        target_event_dir = local_event_dir(target_options[select_index][0])
    
    target_event_tag = target_event_name if target_event_dir is None else target_event_dir

    if args.h5:
        import h5py
        import numpy as np
        records = {}
        for event in read_records(target_event_path):
            summary = event.summary
            for value in summary.value:
                if value.HasField('simple_value'):
                    # print(value.tag, value.simple_value, event.step)
                    if value.tag not in records:
                        records[value.tag] = {}
                    records[value.tag][event.step] = value.simple_value
        
        with h5py.File(os.path.dirname(target_event_path)+os.sep+'[hdf5]' + os.path.basename(target_event_path)+'.h5', 'w') as hf:
            for tag in records:
                group = hf.create_group(tag)
                
                steps = sorted(records[tag].keys())
                values = [records[tag][step] for step in steps]
                
                steps_array = np.array(steps, dtype='int64')
                values_array = np.array(values, dtype='float32')
                
                group.create_dataset('steps', data=steps_array)
                group.create_dataset('values', data=values_array)
    else:
        tbviewer = TensorboardViewer(target_event_path, target_event_tag)
        tbviewer.run()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='path to tensorboard log directory or event file', type=check_file_or_directory)
    parser.add_argument('-h5', action='store_true', help='convert to h5 file')
    parser.usage = f'{sys.argv[0]} path'

    args = parser.parse_args()

    run_main(args)

if __name__ == '__main__':
    main()
