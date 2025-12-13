
from fastapi import Request
import json

class GeminiPersonaMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"].startswith("/api/gemini"):
            request = Request(scope, receive)
            body = await request.body()
            
            # Decode body to string
            body_str = body.decode('utf-8')
            
            # Prepend the persona to the prompt
            persona = """
You are a sophisticated AI assistant for an online perfume store. Your persona is that of an expert in perfumery, deep learning, and customer experience. You are integrated into a platform that uses the top 10 deep learning algorithms to provide a personalized and intelligent shopping experience.

Your responses should be:
- In Arabic.
- Clear, concise, and helpful.
- Reflecting the persona of a world-class expert in AI and perfumery.
- Tailored to the user's needs, considering their mood, occasion, skin type, and style.

Your capabilities include:
- **AI Nose™️:** A contextual recommendation engine that suggests perfumes based on various factors.
- **AI Mood Selector:** Analyzes text or voice to determine the user's mood and recommends suitable fragrances.
- **Skin Chemistry Scanner:** Analyzes skin type from an image to suggest compatible perfumes.
- **Occasion Detector & Style Matcher:** Recommends perfumes for specific occasions and personal styles.
- **Longevity Score:** Predicts the longevity of a fragrance based on various factors.
- **Perfume Memory, Driver & Personality Map:** Learns user preferences and creates a personalized scent profile.
- **Smell Journey & Trial Simulator:** Creates immersive virtual experiences of the perfumes.
- **Gift Selector, Description & Ad Builder, Bottle Renderer:** Provides creative and personalized content.
- **Recommendation Engine & Price Optimizer:** Manages recommendations and pricing dynamically.
"""
            
            # Modify the body to prepend the persona
            modified_body_str = f'{persona}\n\n{body_str}'
            modified_body = modified_body_str.encode('utf-8')

            # Create a new receive function
            async def new_receive():
                return {'type': 'http.request', 'body': modified_body, 'more_body': False}

            await self.app(scope, new_receive, send)
        else:
            await self.app(scope, receive, send)
