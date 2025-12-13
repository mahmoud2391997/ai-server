
import json
from fastapi import Request, Response
import re

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

class ArabicAttributeExtractorMiddleware:
    def __init__(self, app):
        self.app = app
        self.target_paths = [
            "/api/ai-nose/analyze",
            "/api/mood-advisor/analyze",
            "/api/skin-analyzer/analyze",
            "/api/occasion-detector/analyze",
            "/api/style-matcher/analyze",
            "/api/longevity-meter/analyze",
            "/api/perfume-memory/analyze",
            "/api/personality-map/analyze",
            "/api/gift-selector/select",
            "/api/description-generator/generate",
            "/api/ai-attributes/extract",
        ]
        # Basic keywords to detect Arabic
        self.arabic_pattern = re.compile(r'[\u0600-\u06FF]+')

    def is_arabic(self, text):
        return self.arabic_pattern.search(text) is not None

    def extract_attributes(self, text: str) -> dict:
        """
        Placeholder for AI-powered attribute extraction.
        This will be replaced with a call to a generative AI model.
        """
        if not text:
            return {}

        text_lower = text.lower()
        
        # Simple keyword matching as a placeholder
        mood_keywords = {
            'نشيط': ['منعش', 'نشيط', 'حيوي', 'طاقة', 'متحمس', 'fresh', 'energetic'],
            'هادئ': ['هادئ', 'مسترخي', 'مريح', 'هدوء', 'بارد'],
            'واثق': ['واثق', 'قوي', 'مؤثر', 'قائد', 'confident'],
            'رومانسي': ['رومانسي', 'حب', 'موعد', 'عاطفي', 'أمسية خاصة'],
            'سعيد': ['سعيد', 'فرح', 'مبسوط', 'مرح', 'adventurous']
        }
        
        occasion_keywords = {
            'يومي': ['صيف', 'يومي', 'عادي', 'بيت', 'منزل', 'منعش'],
            'عمل': ['عمل', 'مكتب', 'اجتماع', 'مقابلة'],
            'موعد': ['موعد', 'لقاء', 'خروج', 'أمسية خاصة', 'رومانسي'],
            'حفلة': ['حفلة', 'احتفال', 'مناسبة', 'عيد'],
            'زفاف': ['زفاف', 'عرس', 'زواج']
        }
        
        attributes = {}
        
        for mood, keywords in mood_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                attributes['mood'] = mood
                break 

        for occasion, keywords in occasion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                attributes['occasion'] = occasion
                break
        
        return attributes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["path"] not in self.target_paths:
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        body = await request.body()
        
        try:
            data = json.loads(body)
            prompt = data.get("text", "")

            if not prompt or not self.is_arabic(prompt):
                response = Response(
                    content=json.dumps({"error": "الرجاء إدخال طلب صحيح باللغة العربية"}),
                    media_type="application/json",
                    status_code=400
                )
                await response(scope, receive, send)
                return
            
            attributes = self.extract_attributes(prompt)
            
            if not attributes:
                response = Response(
                    content=json.dumps({"error": "لم أتمكن من فهم طلبك. الرجاء تقديم تفاصيل أكثر حول ما تبحث عنه."}),
                    media_type="application/json",
                    status_code=400
                )
                await response(scope, receive, send)
                return

            data["extracted_attributes"] = attributes
            modified_body = json.dumps(data).encode('utf-8')

            async def new_receive():
                return {'type': 'http.request', 'body': modified_body, 'more_body': False}

            await self.app(scope, new_receive, send)

        except json.JSONDecodeError:
            response = Response(
                content=json.dumps({"error": "Invalid JSON in request body"}),
                media_type="application/json",
                status_code=400
            )
            await response(scope, receive, send)
            return
        except Exception as e:
            response = Response(
                content=json.dumps({"error": "An internal error occurred"}),
                media_type="application/json",
                status_code=500
            )
            await response(scope, receive, send)
            return
