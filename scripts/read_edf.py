import mne
import warnings
warnings.filterwarnings('ignore')
from collections import Counter

subjects = [
    ('SC4001', 'SC4001E0-PSG.edf', 'SC4001EC-Hypnogram.edf'),
    ('SC4002', 'SC4002E0-PSG.edf', 'SC4002EC-Hypnogram.edf'),
]

SEP = "=" * 55

for s, psg_file, hypno_file in subjects:
    raw = mne.io.read_raw_edf(
        f'data/raw/sleep-edf/{psg_file}',
        preload=False, verbose=False)
    ann = mne.read_annotations(
        f'data/raw/sleep-edf/{hypno_file}')

    duration_h = raw.times[-1] / 3600
    n_samples  = int(raw.times[-1] * raw.info['sfreq'])
    stages     = Counter(a for a in ann.description)

    print(SEP)
    print(f"  SUBJECT : {s}")
    print(SEP)
    print(f"  Duration        : {duration_h:.2f} h  ({raw.times[-1]:.0f} s)")
    print(f"  Sampling rate   : {raw.info['sfreq']:.0f} Hz")
    print(f"  Total samples   : {n_samples:,}")
    print(f"  Annotations     : {len(ann)}")
    print(f"  Channels ({len(raw.ch_names)})    :")
    for ch in raw.ch_names:
        print(f"    - {ch}")
    print(f"  Sleep stages    :")
    for stage, count in sorted(stages.items()):
        bar = "#" * (count // 2)
        print(f"    {stage:<30} {count:>4}x  {bar}")
    print()

print(SEP)
print("  STATUS: both subjects loaded successfully")
print(SEP)