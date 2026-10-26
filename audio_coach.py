"""
Audio Coach & Real-Time Vocal Cue Synthesizer.

Delivers client-side spoken coaching feedback and motivation via Web Speech API.
"""

from typing import Optional
import streamlit.components.v1 as components


def speak_coach_cue(text: str, rate: float = 1.1) -> None:
    """
    Speaks coaching instructions through client device browser speakers.
    """
    if not text or not text.strip():
        return

    clean_text = text.replace('"', '\\"').replace("'", "\\'").replace("\n", " ")

    js_code = f"""
    <script>
    (function() {{
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            var utterance = new SpeechSynthesisUtterance("{clean_text}");
            utterance.rate = {rate};
            utterance.pitch = 1.05;
            window.speechSynthesis.speak(utterance);
        }}
    }})();
    </script>
    """
    components.html(js_code, height=0, width=0)
