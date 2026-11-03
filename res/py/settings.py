# Project settings. API keys go in keys.py (gitignored), not here.

# ---------- Fish Audio TTS ----------

TTS_ENGINE = "drama-3"
TTS_AUDIO_FORMAT = "mp3"   # mp3, wav, opus, pcm

# Voice models: name -> Fish Audio model id.
# Find ids with FishTTS().search_voice_models("narrator") or on fish.audio.
VOICE_MODELS = {
    "bixby": "",
    # "narrator": "c70cfb98867a4bfb9ae20d2401257b92",
}
DEFAULT_VOICE = "bixby"

# Allowed [mood] tags. Drama 3 accepts any free-form [direction],
# but using a mood not listed here prints a warning.
MOODS = [
    # basic emotions
    "happy", "sad", "angry", "excited", "calm", "nervous", "confident", "surprised",
    "satisfied", "delighted", "scared", "worried", "upset", "frustrated", "depressed",
    "empathetic", "embarrassed", "disgusted", "moved", "proud", "relaxed", "grateful",
    "curious", "sarcastic",
    # advanced emotions
    "disdainful", "unhappy", "anxious", "hysterical", "indifferent", "uncertain",
    "doubtful", "confused", "disappointed", "regretful", "guilty", "ashamed", "jealous",
    "envious", "hopeful", "optimistic", "pessimistic", "nostalgic", "lonely", "bored",
    "contemptuous", "sympathetic", "compassionate", "determined", "resigned",
    # tones
    "in a hurry tone", "shouting", "screaming", "whispering", "soft tone", "emphasis",
    # sounds
    "laughing", "chuckling", "sobbing", "crying loudly", "sighing", "groaning",
    "panting", "gasping", "yawning", "snoring", "clear throat",
    "audience laughing", "background laughter", "crowd laughing",
    # pauses
    "break", "long-break",
]
