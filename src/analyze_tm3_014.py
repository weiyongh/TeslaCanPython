"""TM3-014 raw-bit evidence export; stdlib only, no action-time inference.

Fields follow input/tesla_model3_ONYX.dbc. Semantics require vehicle validation.
Only standard Rx data frames in hex/absolute ASC format are supported.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

FIELDS = {
    0x3C2: ('VCLEFT_hornSwitchPressed', 2, 3),
    0x2E1: ('VCFRONT_hornOn', 51, 7),
    0x273: ('UI_honkHorn', 61, 0),
    0x3B3: ('UI_soundHornOnLock', 4, 0),
    0x2A9: ('EPBL_hornRequest', 48, 0),
    0x2E8: ('EPBR_hornRequest', 48, 0),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('asc', type=Path)
    parser.add_argument('--output', type=Path, default=Path('output/TM3-014'))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    samples = defaultdict(list)
    counts, pages = Counter(), defaultdict(Counter)
    frame_count, first, last = 0, None, None
    with args.asc.open() as source:
        header = [next(source).strip() for _ in range(3)]
        if 'base hex timestamps absolute' not in header:
            raise ValueError('Expected hex/absolute ASC')
        for number, line in enumerate(source, 4):
            a = line.split()
            if len(a) < 6 or a[3:5] != ['Rx', 'd']:
                continue
            t, channel, can_id = float(a[0]), a[1], int(a[2], 16)
            data = bytes.fromhex(' '.join(a[6:]))
            if len(data) != int(a[5]):
                raise ValueError(f'DLC mismatch at line {number}')
            if last is not None and t < last:
                raise ValueError(f'Timestamp regression at line {number}')
            first = t if first is None else first
            last = t
            frame_count += 1
            counts[channel, can_id] += 1
            if can_id not in FIELDS:
                continue
            name, bit, mask = FIELDS[can_id]
            if not data:
                continue
            pages[channel, can_id][data[0] & mask] += 1
            if data[0] & mask or len(data) * 8 <= bit:
                continue
            value = (int.from_bytes(data, 'little') >> bit) & 1
            samples[channel, can_id].append((t, value, number, data.hex(' ')))
    summary = {'source': str(args.asc), 'sha256': hashlib.sha256(args.asc.read_bytes()).hexdigest(),
               'header': header, 'frames': frame_count, 'first_s': first, 'last_s': last, 'signals': []}
    with (args.output / 'signal_samples.csv').open('w', newline='') as sf, (args.output / 'signal_edges.csv').open('w', newline='') as ef:
        sw, ew = csv.writer(sf), csv.writer(ef)
        columns = ['channel', 'id', 'signal', 'time_s', 'value', 'asc_line', 'raw_hex']
        sw.writerow(columns)
        ew.writerow(columns + ['kind'])
        for channel in sorted({c for c, i in counts}):
            for can_id, (name, bit, mask) in FIELDS.items():
                rows = samples[channel, can_id]
                gaps = [b[0] - a[0] for a, b in zip(rows, rows[1:])]
                summary['signals'].append({'channel': channel, 'id': hex(can_id), 'signal': name,
                    'total_frames': counts[channel, can_id], 'pages': dict(pages[channel, can_id]),
                    'valid_samples': len(rows), 'ones': sum(r[1] for r in rows),
                    'median_gap_s': median(gaps) if gaps else None, 'max_gap_s': max(gaps) if gaps else None})
                for j, row in enumerate(rows):
                    record = [channel, hex(can_id), name, *row]
                    sw.writerow(record)
                    if j == 0 or row[1] != rows[j-1][1]:
                        ew.writerow(record + ['initial' if j == 0 else 'observed_change'])
    (args.output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
