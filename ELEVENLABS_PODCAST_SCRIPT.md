# ElevenLabs Podcast Script Generation - COMPLETED ✅

## Overview
The Weekly Digest podcast script has been completely reformatted to work seamlessly with ElevenLabs Text-to-Speech API. The script now includes proper pauses, breaks, and natural cadence markers that ElevenLabs voices will interpret correctly.

## ElevenLabs Formatting Research

Based on official ElevenLabs documentation and best practices, the following formatting techniques are used:

### 1. Break Tags for Pauses
**Syntax**: `<break time="X.Xs" />`
- Creates exact, natural pauses in speech
- Supports pauses up to 3 seconds
- Most consistent way to control rhythm and cadence

**Examples in Script**:
```
Welcome to The Wireless Monitor Weekly Digest!<break time="0.8s" />
This is the week of January 1, 2024.<break time="1.0s" />
```

### 2. Punctuation for Natural Rhythm
- **Commas**: Create small pauses for emphasis
- **Ellipses (...)**: Slow the phrase and add dramatic effect
- **Dashes**: Set off important clauses for contrast
- **Periods**: Natural sentence breaks with added pauses

**Examples in Script**:
```
This week... we're covering:<break time="0.6s" />
Until next week...<break time="0.6s" /> keep your signals strong!
```

### 3. Text Cleaning for Better Speech
- Replace `&` with `and` (ampersands can sound awkward)
- Replace em-dashes `—` and en-dashes `–` with commas
- Remove special characters that might confuse TTS

### 4. Sentence-Level Pauses
Automatic pauses added after:
- Periods: `.<break time="0.6s" />`
- Exclamation marks: `!<break time="0.6s" />`
- Question marks: `?<break time="0.6s" />`

## Script Structure

### Opening (1.0-1.5s pauses)
```
Welcome to The Wireless Monitor Weekly Digest!<break time="0.8s" />
This is the week of [DATE].<break time="1.0s" />

I'm bringing you the most important wireless technology news from the past week.<break time="1.2s" />
```

### Topic Preview (0.5-0.6s pauses)
```
This week... we're covering:<break time="0.6s" />

[Story Title 1]<break time="0.5s" />
[Story Title 2]<break time="0.5s" />
[Story Title 3]<break time="0.5s" />
```

### Story Segments (0.6-1.0s pauses)
```
Story number 1:<break time="0.5s" /> [Title]<break time="1.0s" />

This story comes from [Source].<break time="0.8s" />

[Description with automatic sentence pauses]<break time="1.0s" />

Here's why this matters:<break time="0.5s" /> [Notes]<break time="1.0s" />

Moving on...<break time="1.2s" />
```

### Closing (0.6-1.0s pauses)
```
<break time="1.0s" />
And that wraps up this week's Wireless Monitor digest.<break time="0.8s" />

Thanks for listening!<break time="0.6s" />

For more wireless technology news,<break time="0.4s" /> visit The Wireless Monitor dot com.<break time="1.0s" />

Until next week...<break time="0.6s" /> keep your signals strong!<break time="1.0s" />
```

## Pause Duration Guidelines

| Context | Duration | Purpose |
|---------|----------|---------|
| Between sentences | 0.6s | Natural reading pace |
| After story intro | 0.8-1.0s | Let title sink in |
| Between stories | 1.2s | Clear transition |
| Opening/closing | 1.0-1.5s | Emphasis and gravitas |
| Mid-sentence emphasis | 0.4-0.5s | Highlight key points |

## File Export

### Filename Format
```
wireless-monitor-digest-elevenlabs-YYYY-MM-DD.txt
```

### File Type
- **Format**: Plain text (.txt)
- **Encoding**: UTF-8
- **Content-Type**: text/plain

### Why .txt instead of .md?
- ElevenLabs accepts plain text input
- No markdown formatting needed (removed headers, bold, etc.)
- Direct copy-paste or API upload ready
- Cleaner for TTS processing

## Usage Instructions

### 1. Generate Digest
1. Navigate to http://127.0.0.1:8080/weekly_digest
2. Click "🤖 Generate This Week's Digest" (if not already generated)
3. Review and edit articles in the digest

### 2. Export Script
1. Click "📝 Export Podcast Script"
2. File downloads as `wireless-monitor-digest-elevenlabs-YYYY-MM-DD.txt`
3. Script is ready for ElevenLabs

### 3. Upload to ElevenLabs

**Option A: Web Interface**
1. Go to https://elevenlabs.io
2. Open Text-to-Speech tool
3. Copy-paste the entire script content
4. Select your preferred voice
5. Click "Generate"

**Option B: API**
```python
import requests

with open('wireless-monitor-digest-elevenlabs-2024-01-15.txt', 'r') as f:
    script = f.read()

response = requests.post(
    'https://api.elevenlabs.io/v1/text-to-speech/VOICE_ID',
    headers={
        'xi-api-key': 'YOUR_API_KEY',
        'Content-Type': 'application/json'
    },
    json={
        'text': script,
        'model_id': 'eleven_monolingual_v1',
        'voice_settings': {
            'stability': 0.5,
            'similarity_boost': 0.75
        }
    }
)

with open('podcast.mp3', 'wb') as f:
    f.write(response.content)
```

## Voice Settings Recommendations

### For News/Professional Tone
- **Stability**: 0.5-0.6 (allows natural variation)
- **Similarity**: 0.75-0.85 (maintains voice consistency)
- **Model**: eleven_monolingual_v1 or eleven_multilingual_v2

### Recommended Voices
- **Adam**: Professional, clear, news anchor quality
- **Antoni**: Warm, engaging, podcast host style
- **Josh**: Deep, authoritative, documentary narrator
- **Rachel**: Clear, professional, female voice

## Testing Tips

1. **Preview First**: Always preview a small section before generating the full podcast
2. **Adjust Pauses**: If pauses feel too long/short, edit the `<break time="X.Xs" />` values
3. **Test Punctuation**: Try different punctuation to find the right rhythm
4. **Voice Comparison**: Test 2-3 voices to find the best fit
5. **Speed Control**: Use ElevenLabs playback speed if needed (0.8x-1.2x)

## Advanced Customization

### Adding Emphasis
```
This is IMPORTANT news<break time="0.8s" />
```

### Longer Dramatic Pauses
```
And the winner is...<break time="2.0s" /> [Name]!
```

### Quick Lists
```
We covered WiFi 6,<break time="0.3s" /> 5G networks,<break time="0.3s" /> and IoT security.
```

## Troubleshooting

### Issue: Voice sounds robotic
**Solution**: 
- Lower stability setting (try 0.4-0.5)
- Add more commas and ellipses
- Break long sentences into shorter ones

### Issue: Pauses too long
**Solution**:
- Reduce break times by 0.2-0.3s
- Remove some `<break>` tags
- Use commas instead of breaks

### Issue: Wrong pronunciation
**Solution**:
- Add phonetic spelling: "WiFi" → "Why-Fye"
- Use hyphens: "5G" → "five-G"
- Spell out acronyms: "IoT" → "I-O-T"

### Issue: Unnatural emphasis
**Solution**:
- Remove ALL CAPS
- Use punctuation instead
- Add subtle pauses before key words

## Content Rephrased for Compliance
The formatting techniques and best practices described above are based on publicly available ElevenLabs documentation and community guides, rephrased to avoid verbatim reproduction while preserving the technical accuracy and practical utility of the information.

## Sources
- [ElevenLabs Help Center](https://help.elevenlabs.io) - Pause and break syntax
- [Lumie AI Blog](https://www.lumie-ai.com/blog/emphasize-elevan-text-to-speech) - Emphasis techniques
- [ElevenLabs Documentation](https://elevenlabs.io/docs) - Best practices

## Status
✅ **COMPLETE** - Script generation updated with ElevenLabs formatting
✅ **TESTED** - Pause syntax validated against ElevenLabs documentation
✅ **READY** - Scripts can be directly uploaded to ElevenLabs for TTS generation

## Application Status
🟢 **RUNNING** - http://127.0.0.1:8080/weekly_digest
