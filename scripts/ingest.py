import mne
import psycopg2
import warnings
warnings.filterwarnings('ignore')
from io import StringIO

RELATIONAL = "host=localhost port=5434 dbname=sleep_relational user=postgres password=postgres"
TIMESCALE  = "host=localhost port=5434 dbname=sleep_timeseries user=postgres password=postgres"

def parse_stages(hypno_path):
    ann = mne.read_annotations(hypno_path)
    stages = {}
    for onset, dur, label in zip(ann.onset, ann.duration, ann.description):
        stage = label.replace('Sleep stage ', '').strip()
        for sec in range(int(onset), int(onset + max(dur, 30)), 30):
            stages[sec] = stage
    return stages

def ingest(subject_id, psg_path, hypno_path, conn_str):
    stages = parse_stages(hypno_path)
    raw    = mne.io.read_raw_edf(psg_path, preload=False, verbose=False)
    fs     = int(raw.info['sfreq'])

    conn = psycopg2.connect(conn_str)
    cur  = conn.cursor()

    cur.execute(
        "INSERT INTO subjects (subject_id) VALUES (%s) ON CONFLICT DO NOTHING",
        (subject_id,))
    cur.execute(
        """INSERT INTO recordings
           (subject_id, psg_filename, hypno_filename, duration_sec, sampling_rate)
           VALUES (%s,%s,%s,%s,%s) RETURNING recording_id""",
        (subject_id, psg_path, hypno_path, int(raw.times[-1]), fs))
    rec_id = cur.fetchone()[0]

    TARGET = ['EEG Fpz-Cz', 'EEG Pz-Oz', 'EOG horizontal']
    for ch in TARGET:
        if ch not in raw.ch_names:
            continue
        signal = raw.get_data(picks=[ch])[0]
        buf = StringIO()
        for j, amp in enumerate(signal):
            ts_ms = int(j / fs * 1000)
            epoch = (ts_ms // 30000) * 30
            stage = stages.get(epoch, '')
            buf.write(f"{rec_id}\t{ts_ms}\t{ch}\t{amp}\t{stage}\n")
        buf.seek(0)
        cur.copy_from(buf, 'signals',
            columns=['recording_id','timestamp_ms',
                     'channel_name','amplitude','sleep_stage'])
        print(f"  channel {ch} done")

    conn.commit()
    cur.close()
    print(f"Done: {subject_id} -> {conn_str.split('dbname=')[1].split(' ')[0]}")

subjects = [
    ('SC4001','data/raw/sleep-edf/SC4001E0-PSG.edf','data/raw/sleep-edf/SC4001EC-Hypnogram.edf'),
    ('SC4002','data/raw/sleep-edf/SC4002E0-PSG.edf','data/raw/sleep-edf/SC4002EC-Hypnogram.edf'),
]

for sid, psg, hyp in subjects:
    print(f"\nIngesting {sid}...")
    ingest(sid, psg, hyp, RELATIONAL)
    ingest(sid, psg, hyp, TIMESCALE)

print("\nAll done.")