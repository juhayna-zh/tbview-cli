import struct
from tbview.tf_protobuf.event_pb2 import Event
from tbview.tf_protobuf.summary_pb2 import Summary
from tbview.crc32c import masked_crc32c
from functools import lru_cache

@lru_cache(1024)
def test_crc32c(data, crc):
    crc = struct.unpack('I', crc)[0]
    cur_crc = masked_crc32c(data)
    if crc != cur_crc:
        print(f'Warning: CRC not match! Got {cur_crc}, expect {crc}')

def read_records(file_path):
    with open(file_path, 'rb') as f:
        while True:
            length_raw = f.read(8)
            if not length_raw:
                break
            test_crc32c(length_raw, f.read(4))
            length = struct.unpack('Q', length_raw)[0]
            event_raw = f.read(length)
            test_crc32c(event_raw, f.read(4))
            event = Event()
            event.ParseFromString(event_raw)
            yield event
            
