# Aura AI Server - API Endpoints Reference

## Base URL
```
http://localhost:8000
```

## Interactive API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🎯 AI Feature Endpoints

### 1. AI Nose (الأنف الإلكتروني)
```http
POST /api/ai-nose/analyze
```
**Request Body:**
```json
{
  "text": "أريد عطر منعش للصيف",
  "image_data": "base64_encoded_image (optional)",
  "options": {
    "mood": "نشيط",
    "occasion": "يومي",
    "gender": "Male",
    "skin_type": "دهنية"
  },
  "context": {
    "location": {
      "latitude": 24.7136,
      "longitude": 46.6753
    }
  },
  "user_id": "uuid (optional)"
}
```

**Note:** If you provide `latitude` and `longitude` in the `context.location` object, the API will **automatically fetch** weather, location (city/country), and current time. You can also provide weather/location/time manually if you already have this data.

**Response:**
```json
{
  "analysis": "تحليل الأنف الإلكتروني...",
  "recommendations": [
    {
      "perfume_id": "uuid",
      "name": "اسم العطر",
      "brand": "العلامة",
      "compatibility_score": 0.95,
      "reason": "سبب التوصية",
      "price": 450.0,
      "mood_tag": "نشيط",
      "occasion_tag": "يومي",
      "style_tag": "عصري",
      "longevity_score": 85,
      "sillage_score": 75,
      "skin_compatibility": "دهنية"
    }
  ],
  "confidence": 0.92,
  "metadata": {
    "detected_mood": "نشيط",
    "detected_occasion": "يومي",
    "weather": {
      "description": "صافي",
      "temperature": 35,
      "humidity": 60
    },
    "location": {
      "city": "الرياض",
      "country": "SA",
      "latitude": 24.7136,
      "longitude": 46.6753
    },
    "time": "02:30 PM",
    "recommendations_count": 3,
    "recommendations_with_ids": ["uuid1", "uuid2", "uuid3"]
  }
}
```

**Key Features:**
- ✅ **Automatic weather fetching** from coordinates (if `latitude`/`longitude` provided)
- ✅ **All recommendations include `perfume_id`** for easy reference
- ✅ Returns weather, location, and time data in metadata
- ✅ Context-aware recommendations based on weather, mood, occasion, and skin type

---

### 2. Mood Advisor (مستشار المزاج)
```http
POST /api/mood-advisor/analyze
```
**Request Body:**
```json
{
  "text": "أشعر بالسعادة اليوم",
  "audio_data": "base64_encoded_audio (optional)",
  "options": {
    "mood": "سعيد"
  }
}
```

---

### 3. Skin Analyzer (محلل البشرة)
```http
POST /api/skin-analyzer/analyze
```
**Request Body:**
```json
{
  "text": "بشرتي دهنية",
  "image_data": "base64_encoded_hand_image (optional)",
  "options": {
    "skin_type": "دهنية"
  }
}
```

---

### 4. Occasion Detector (كاشف المناسبة)
```http
POST /api/occasion-detector/analyze
```
**Request Body:**
```json
{
  "text": "أحتاج عطر لحفلة",
  "options": {
    "occasion": "حفلة"
  }
}
```

---

### 5. Style Matcher (مطابقة الأسلوب)
```http
POST /api/style-matcher/analyze
```
**Request Body:**
```json
{
  "text": "أسلوبي كلاسيكي",
  "image_data": "base64_encoded_style_image (optional)",
  "options": {
    "style": "كلاسيكي"
  }
}
```

---

### 6. Longevity Meter (مقياس الثبات)
```http
POST /api/longevity-meter/analyze
```
**Request Body:**
```json
{
  "text": "عود الملكي",
  "context": {
    "weather": {"temperature": 35}
  },
  "options": {
    "skin_type": "دهنية"
  }
}
```

---

### 7. Perfume Memory (ذاكرة العطر)
```http
POST /api/perfume-memory/analyze
```
**Request Body:**
```json
{
  "text": "أحب العود والورد",
  "user_id": "uuid (optional)"
}
```

---

### 8. Personality Map (خريطة الشخصية)
```http
POST /api/personality-map/analyze
```
**Request Body:**
```json
{
  "text": "أنا شخص واثق وقائد",
  "options": {
    "personality": "القائد الواثق"
  }
}
```

---

### 9. Gift Selector (محدد الهدايا)
```http
POST /api/gift-selector/analyze
```
**Request Body:**
```json
{
  "text": "أريد هدية لوالدتي في عيد الأم",
  "options": {
    "recipient": "والدتك",
    "occasion": "عيد الأم",
    "relationship": "أم"
  }
}
```

---

### 10. Description Generator (مولد الوصف)
```http
POST /api/description-generator/generate
```
**Request Body:**
```json
{
  "text": "عود كمبودي مع ياسمين وعنبر",
  "options": {
    "name": "عود الملكي",
    "ingredients": {
      "top": "عود كمبودي",
      "heart": "ياسمين",
      "base": "عنبر"
    }
  }
}
```

---

### 11. Bottle Renderer (مولد شكل الزجاجة)
```http
POST /api/bottle-renderer/render
```
**Request Body:**
```json
{
  "text": "زجاجة ذهبية مربعة",
  "options": {
    "shape": "مربع",
    "color": "ذهبي",
    "size": "100 مل"
  }
}
```

---

### 12. Price Optimizer (موازن الأسعار)
```http
POST /api/price-optimizer/optimize
```
**Request Body:**
```json
{
  "text": "عود الملكي الفاخر",
  "options": {
    "product": "عود الملكي",
    "current_price": 450
  }
}
```

---

### 13. Text-to-Speech (المساعد الصوتي)
```http
POST /api/tts/synthesize
```
**Request Body:**
```json
{
  "text": "مرحباً بك في أورا",
  "voice": "ar-SA-HamedNeural",
  "rate": "+0%",
  "pitch": "+0Hz",
  "volume": "+0%"
}
```

**Response:** Audio stream (audio/mpeg)

---

### 14. Weather Service
```http
POST /api/weather/get-weather
```
**Request Body:**
```json
{
  "latitude": 24.7136,
  "longitude": 46.6753
}
```

**Response:**
```json
{
  "weather": {
    "description": "صافي",
    "temperature": 25,
    "humidity": 60,
    "condition": "clear"
  },
  "location": {
    "city": "الرياض",
    "country": "SA",
    "latitude": 24.7136,
    "longitude": 46.6753
  },
  "time": "02:30 PM",
  "isRealData": true
}
```

---

## 📊 Data Management Endpoints

### Perfumes
- `GET /api/perfumes` - List all perfumes
- `GET /api/perfumes/{id}` - Get perfume by ID
- `POST /api/perfumes` - Create perfume
- `PUT /api/perfumes/{id}` - Update perfume
- `DELETE /api/perfumes/{id}` - Delete perfume

### Customers
- `GET /api/customers` - List all customers
- `GET /api/customers/{id}` - Get customer by ID
- `POST /api/customers` - Create customer
- `PUT /api/customers/{id}` - Update customer
- `DELETE /api/customers/{id}` - Delete customer

### Orders
- `GET /api/orders` - List all orders
- `GET /api/orders/{id}` - Get order by ID
- `POST /api/orders` - Create order
- `PUT /api/orders/{id}` - Update order
- `DELETE /api/orders/{id}` - Delete order

### Ingredients
- `GET /api/ingredients` - List all ingredients
- `GET /api/ingredients/{id}` - Get ingredient by ID
- `POST /api/ingredients` - Create ingredient
- `PUT /api/ingredients/{id}` - Update ingredient
- `DELETE /api/ingredients/{id}` - Delete ingredient

### Database
- `GET /api/database/all-tables` - Get all data from all tables

### Prompts
- `GET /api/prompts` - List all prompts
- `GET /api/prompts/{feature}` - Get prompt by feature
- `POST /api/prompts` - Create prompt
- `PUT /api/prompts/{id}` - Update prompt

### Admin
- `GET /api/admin/*` - Admin operations

---

## 🔧 Utility Endpoints

### Health Check
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy"
}
```

### Root
```http
GET /
```
**Response:**
```json
{
  "message": "Aura AI Server is running"
}
```

---

## 📝 Common Request Schema

Most AI endpoints use the `MultiModalRequest` schema:

```typescript
interface MultiModalRequest {
  text?: string;              // Text input
  image_data?: string;        // Base64 encoded image
  audio_data?: string;        // Base64 encoded audio
  options?: {                 // Additional options
    mood?: string;
    occasion?: string;
    style?: string;
    gender?: "Male" | "Female" | "Unisex";
    skin_type?: string;
    personality?: string;
    [key: string]: any;
  };
  user_id?: string;           // Optional user ID for personalization
  context?: {                 // Contextual data
    weather?: {
      description?: string;
      temperature?: number;
      humidity?: number;
    };
    location?: {
      city?: string;
      country?: string;
      latitude?: number;
      longitude?: number;
    };
    time?: string;
  };
}
```

---

## 🚀 Quick Start Examples

### Example 1: AI Nose Analysis (with automatic weather fetching)
```bash
curl -X POST http://localhost:8000/api/ai-nose/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "أريد عطر منعش للصيف",
    "context": {
      "location": {
        "latitude": 24.7136,
        "longitude": 46.6753
      }
    }
  }'
```

**Response includes:**
- Weather data (automatically fetched from coordinates)
- Location info (city, country from coordinates)
- Current time
- 3 perfume recommendations with IDs

### Example 2: Text-to-Speech
```bash
curl -X POST http://localhost:8000/api/tts/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "مرحباً بك في أورا",
    "voice": "ar-SA-HamedNeural"
  }' \
  --output speech.mp3
```

### Example 3: Weather Data
```bash
curl -X POST http://localhost:8000/api/weather/get-weather \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 24.7136,
    "longitude": 46.6753
  }'
```

---

## ⚠️ Missing Endpoints (To Be Implemented)

1. **Perfume Driver** - `POST /api/perfume-driver/analyze`
2. **Smell Journey Simulator** - `POST /api/smell-journey/simulate`
3. **Ad Builder** - `POST /api/ad-builder/generate`
4. **Trial Simulator** - `POST /api/trial-simulator/simulate`
5. **Recommendation Engine** - `POST /api/recommendation-engine/recommend`

---

## 📚 Additional Resources

- See `FEATURES_STATUS.md` for detailed feature implementation status
- See `README.md` for setup and deployment instructions
- Interactive API docs available at `/docs` when server is running

