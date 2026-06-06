# TTS Pronunciation Errors in Edge-TTS

## Overview

Edge-TTS (free TTS engine) has **inherent pronunciation limitations** for proper nouns (names, places). This is a fundamental constraint that cannot be resolved through workflow optimization.

## Known Issues

| Proper Noun | Correct Pronunciation | Edge-TTS Output | Impact |
|-------------|----------------------|-----------------|--------|
| Ziqi (子期) | /ˈziːtʃiː/ | "Ziki" | Character name misheard |
| Tai (泰) | /taɪ/ | "Ty" | Mountain name misheard |
| Boya (伯牙) | /ˈboʊjɑː/ | "Boy it" | Character name misheard |
| Zhong (钟) | /tʃoʊŋ/ | "Jong" | Character name misheard |

## Root Cause Analysis

| Layer | Problem | Root Cause | Fixable? |
|-------|---------|------------|----------|
| L1 | Subtitle text incomplete | English script was simplified | ✅ Fixable |
| L2 | TTS pronunciation errors | Edge-TTS mispronounces proper nouns | ❌ **Inherent limitation** |
| L3 | Whisper inherits TTS errors | Whisper faithfully transcribes audio | ✅ Avoidable |

## Key Lessons

### 1. Subtitle Text Must Match Correct Script

**❌ Wrong approach:** Use Whisper transcription to generate ASS subtitles
```python
result = subprocess.run(['whisper', audio_path, '--model', 'base'], capture_output=True, text=True)
ass_text = parse_whisper_output(result.stdout)  # Inherits TTS errors!
```

**✅ Correct approach:** Use original script text for ASS subtitles
```python
with open('voiceover_script.json') as f:
    script = json.load(f)
ass_text = next(s['en'] for s in script if s['id'] == scene_id)  # Correct text
```

### 2. TTS Pronunciation Errors Are Unfixable with Free TTS

Edge-TTS pronunciation of proper nouns is:
- **Non-deterministic** — varies by context
- **Non-configurable** — no phonetic spelling override
- **Inherent to the model** — not a bug, but a limitation

### 3. Subtitles Should Display Correct Text

Even when audio pronunciation is wrong, subtitles (as visual information) should display the correct English text. This ensures:
- Readability for viewers
- Accuracy for reference purposes
- Professional quality

### 4. Solutions for Perfect Pronunciation

| Option | Pros | Cons |
|--------|------|------|
| **ElevenLabs (paid)** | Custom pronunciation, high quality | Cost (~$5-22/month) |
| **Azure Neural TTS (paid)** | SSML phonetic control, high quality | Cost, complex setup |
| **Manual recording** | Perfect control | Time-consuming |
| **Simplify character names** | Free, works with Edge-TTS | Less authentic |

### 5. Simplified Names Strategy

If using free TTS, consider simplifying character names:

| Original | Simplified | Trade-off |
|----------|------------|-----------|
| Ziqi | "the woodcutter" | Loses character identity |
| Boya | "the musician" | Loses character identity |
| Mount Tai | "the great mountain" | Less culturally specific |

## Verification Workflow

When users report subtitle-audio mismatch:

1. **Check English script completeness** — Are key descriptions missing?
2. **Check ASS text source** — Is it based on correct script or Whisper transcription?
3. **Transcribe original audio with Whisper** — Compare ASS text, identify TTS errors
4. **Accept TTS limitations** — Subtitles show correct text; pronunciation errors are TTS engine constraints

## Reference

- `fable-video-pipeline` skill: Main fable video production pipeline
- `gaoshan-liushui-project-termination-2026-06-05.md`: Case study of project termination due to TTS issues