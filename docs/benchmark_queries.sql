-- Q1: Range scan - 5 minutes of EEG signal
SELECT * FROM signals
WHERE recording_id = 1
  AND channel_name = 'EEG Fpz-Cz'
  AND timestamp_ms BETWEEN 0 AND 300000;

-- Q2: Aggregation - mean and std per sleep stage
SELECT sleep_stage,
       AVG(amplitude)    AS mean_amplitude,
       STDDEV(amplitude) AS std_amplitude,
       COUNT(*)          AS sample_count
FROM signals
WHERE recording_id = 1
  AND channel_name = 'EEG Fpz-Cz'
GROUP BY sleep_stage;

-- Q3: Anomaly filter - all wake and unknown epochs
SELECT timestamp_ms, amplitude
FROM signals
WHERE recording_id = 1
  AND channel_name = 'EEG Fpz-Cz'
  AND sleep_stage IN ('W', '?')
ORDER BY timestamp_ms;

-- Q4: Full night scan - all channels for one subject
SELECT channel_name, COUNT(*) AS sample_count
FROM signals
WHERE recording_id = 1
GROUP BY channel_name;

-- Q5: Cross-subject comparison - mean EEG amplitude per subject
SELECT r.subject_id,
       AVG(s.amplitude) AS mean_amplitude,
       STDDEV(s.amplitude) AS std_amplitude
FROM signals s
JOIN recordings r ON s.recording_id = r.recording_id
WHERE s.channel_name = 'EEG Fpz-Cz'
GROUP BY r.subject_id;

-- Q6: Stage transition detection - find every change in sleep stage
SELECT timestamp_ms,
       sleep_stage,
       LAG(sleep_stage) OVER (ORDER BY timestamp_ms) AS prev_stage
FROM signals
WHERE recording_id = 1
  AND channel_name = 'EEG Fpz-Cz'
  AND sleep_stage IS NOT NULL
  AND sleep_stage != ''
ORDER BY timestamp_ms;

-- Q7: Peak amplitude detection - top 10 highest EEG spikes
SELECT timestamp_ms,
       amplitude,
       sleep_stage
FROM signals
WHERE recording_id = 1
  AND channel_name = 'EEG Fpz-Cz'
ORDER BY ABS(amplitude) DESC
LIMIT 10;

-- Q8: Time-windowed aggregation - mean amplitude per 10-minute window
SELECT (timestamp_ms / 600000) * 600000 AS window_start_ms,
       AVG(amplitude)  AS mean_amplitude,
       COUNT(*)        AS sample_count
FROM signals
WHERE recording_id = 1
  AND channel_name = 'EEG Fpz-Cz'
GROUP BY window_start_ms
ORDER BY window_start_ms;

-- Q9: Class imbalance check - stage distribution across all subjects
SELECT sleep_stage,
       COUNT(*)                            AS total_samples,
       ROUND(COUNT(*) * 100.0 /
         SUM(COUNT(*)) OVER (), 2)         AS percentage
FROM signals
WHERE channel_name = 'EEG Fpz-Cz'
GROUP BY sleep_stage
ORDER BY total_samples DESC;

-- Q10: Multi-channel correlation window - all channels at same timestamp range
SELECT timestamp_ms, channel_name, amplitude
FROM signals
WHERE recording_id = 1
  AND timestamp_ms BETWEEN 30000 AND 60000
ORDER BY timestamp_ms, channel_name;