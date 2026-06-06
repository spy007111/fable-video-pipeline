**Goal:** Remove frame mismatch between audio and video after concat.
Cause: concat re-encode / frame-alignment drift; the last subtitle staying too long.

Fix:
1. Extend the last subtitle line to the exact video end; this covers any concat lag.
2. Sync the ASS timeline to cumulative ffprobe duration; never guess.
3. Include the last scene/frame in each segment; don't strip it during transform.
4. Do not post-hoc rescale timestamps.
