import mne

file_path = "data/raw/sleep-edf/SC4001E0-PSG.edf"

raw = mne.io.read_raw_edf(file_path, preload=False)

print(raw.info)