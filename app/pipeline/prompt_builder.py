import re
import random
from collections import Counter

class PromptBuilder:
    """
    AI Cinematic Still Generator
    Focus: Emotion, storytelling, single powerful moment
    """

    EMOTIONAL_CORES = [
        "heartbreak", "longing", "forbidden love", "betrayal",
        "silent regret", "unspoken confession", "painful goodbye",
        "moment before everything changes", "last look",
        "hope against all odds", "love vs duty"
    ]

    VISUAL_MOODS = [
        "melancholic blue hour", "golden hour romance",
        "rainy window reflection", "soft morning light",
        "dramatic backlit silhouette", "intimate candlelight",
        "cold moonlight distance", "warm embrace glow"
    ]

    CINEMATIC_FRAMINGS = [
        "close-up on eyes (tears forming)",
        "over-the-shoulder longing gaze",
        "two figures separated by distance",
        "hand reaching but not touching",
        "reflection in mirror/water",
        "silhouette in doorway",
        "face half in shadow"
    ]

    STORY_ARCHETYPES = {
        "separation": "Two people forced apart, one final glance",
        "reunion": "After years, their eyes meet again",
        "choice": "Torn between love and duty, frozen in indecision",
        "sacrifice": "Letting go of everything for someone else",
        "reveal": "The moment truth is spoken without words"
    }

    BANNED_WORDS = {
        'youtube', 'subscribe', 'like', 'comment', 'channel',
        'video', 'drama', 'episode', 'scene', 'clip', 'fmv',
        '2022', '2023', '2024', '2025', 'cdrama', 'kdrama'
    }

    def build(self, post: dict) -> str:
        """Generate AI cinematic still prompt from viral video metadata"""
        
        caption = post.get("caption", "")
        title = post.get("title", caption)
        
        # Extract core emotion/concept
        keywords = self._extract_emotional_keywords(caption + " " + title)
        archetype = self._detect_story_archetype(caption)
        
        # Random cinematic elements
        emotion = random.choice(self.EMOTIONAL_CORES)
        mood = random.choice(self.VISUAL_MOODS)
        framing = random.choice(self.CINEMATIC_FRAMINGS)
        
        prompt = f"""
**AI CINEMATIC STILL** — Ultra-realistic photograph, film quality

**Narrative concept:**
{self.STORY_ARCHETYPES.get(archetype, "A single emotionally charged moment frozen in time")}

Inspired by: "{self._clean_title(title)[:80]}"

**Emotional core:**
{emotion} — the weight of unspoken words, the pull of impossible choices

**Visual storytelling:**
{framing}
{mood}
Everything is communicated through:
- body language (subtle tension, hesitation)
- eyes (vulnerability, longing, pain)
- space between characters (distance that speaks volumes)

**Cinematic execution:**
- Single-frame moment (not a sequence)
- Feels like one unforgettable paused second
- Film still aesthetic (35mm cinema lens)
- Shallow depth of field (f/1.4 bokeh)
- Natural/practical lighting only
- Color grading: desaturated with warm/cool contrast
- Composition: rule of thirds, leading lines
- Grain: subtle 35mm film texture

**Character authenticity:**
- East Asian features (respectful, realistic)
- Period-appropriate Chinese drama wardrobe
- Natural expressions (no posed smiles)
- Realistic human anatomy (correct hands, proportions)
- Age-appropriate casting

**Mood keywords:**
{', '.join(keywords[:5])}

**Technical specs:**
- 8K resolution
- Professional photography quality
- Photorealistic rendering
- Sharp focus on subject
- Atmospheric depth

**CRITICAL EXCLUSIONS:**
- No text, subtitles, captions
- No logos, watermarks, UI elements
- No extra fingers or limbs
- No artificial/staged poses
- No modern clothing anachronisms
""".strip()

        return prompt

    def _extract_emotional_keywords(self, text: str) -> list:
        """Extract emotion/story words, filter noise"""
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        
        # Remove banned + stopwords
        stopwords = {'this', 'that', 'with', 'from', 'have', 'will', 'your', 
                    'when', 'look', 'such', 'were', 'some', 'sort'}  #  ADD MORE
        words = [w for w in words if w not in self.BANNED_WORDS and w not in stopwords]
        
        # Prioritize emotional vocabulary ( EXPAND)
        emotional = {
            'love', 'heart', 'tears', 'pain', 'kiss', 'embrace', 
            'separation', 'reunion', 'regret', 'sacrifice', 'choice',
            'betrayal', 'longing', 'hope', 'fear', 'desire', 'grief',
            'passion', 'loss', 'forgiveness', 'redemption'
        }
        
        counts = Counter(words)
        keywords = []
        
        for word, _ in counts.most_common(20):  #  UP FROM 15
            if word in emotional:
                keywords.insert(0, word)
            else:
                keywords.append(word)
        
        #  FALLBACK: If no emotional words, use archetype-specific defaults
        if not any(w in emotional for w in keywords):
            return ['longing', 'romance', 'emotion', 'separation']
        
        return keywords[:8] if keywords else ['romance', 'drama', 'emotion']

    def _detect_story_archetype(self, text: str) -> str:
        """Detect story pattern from caption"""
        text = text.lower()
        
        if any(w in text for w in ['divorce', 'left', 'goodbye', 'apart']):
            return 'separation'
        if any(w in text for w in ['reunion', 'meet again', 'return']):
            return 'reunion'
        if any(w in text for w in ['choice', 'duty', 'must', 'cannot']):
            return 'choice'
        if any(w in text for w in ['sacrifice', 'give up', 'let go']):
            return 'sacrifice'
        if any(w in text for w in ['secret', 'truth', 'reveal', 'confession']):
            return 'reveal'
        
        return 'separation'  # default

    def _clean_title(self, title: str) -> str:
        """Remove noise from title for prompt"""
        # Remove URLs
        title = re.sub(r'http[s]?://\S+', '', title)
        
        # Remove brackets, hashtags, emojis
        title = re.sub(r'\[.*?\]|\(.*?\)|#\w+', '', title)
        
        # Remove special chars (keep letters, numbers, basic punctuation)
        title = re.sub(r'[^\w\s,.!?\'-]', '', title)
        
        # Collapse whitespace
        title = re.sub(r'\s+', ' ', title).strip()
        
        #  SMART TRUNCATE: Cut at sentence/word boundary
        if len(title) > 80:
            # Try to cut at punctuation
            truncated = title[:80]
            last_punct = max(
                truncated.rfind('.'),
                truncated.rfind('!'),
                truncated.rfind('?'),
                truncated.rfind(',')
            )
            if last_punct > 40:  # only if reasonable
                title = truncated[:last_punct + 1]
            else:
                # Cut at last space
                last_space = truncated.rfind(' ')
                if last_space > 40:
                    title = truncated[:last_space] + '...'
                else:
                    title = truncated + '...'
        
        return title


