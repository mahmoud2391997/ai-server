# Frontend Integration Guide: AI Nose Endpoint

Complete guide for integrating the AI Nose endpoint in your frontend application.

## Endpoint

```
POST /api/ai-nose/analyze
```

## Base URL

```
http://localhost:8000  (development)
https://your-domain.com  (production)
```

---

## Request Format

### TypeScript Interface

```typescript
interface AINoseRequest {
  text?: string;                    // User's text input (optional)
  image_data?: string;              // Base64 encoded image (optional)
  options?: {
    mood?: string;                  // e.g., "نشيط", "هادئ", "رومانسي"
    occasion?: string;              // e.g., "يومي", "عمل", "حفلة"
    gender?: "Male" | "Female" | "Unisex";
    skin_type?: string;             // e.g., "دهنية", "جافة"
  };
  user_id?: string;                 // Optional user ID for personalization
  context?: {
    location?: {
      latitude: number;             // Auto-fetches weather if provided
      longitude: number;
      city?: string;                // Optional: override city
      country?: string;             // Optional: override country
    };
    weather?: {                     // Optional: provide manually
      description: string;
      temperature: number;
      humidity?: number;
    };
    time?: string;                  // Optional: e.g., "02:30 PM"
  };
}
```

### Response Format

```typescript
interface AINoseResponse {
  analysis: string;                 // Arabic analysis text
  recommendations: Array<{
    perfume_id: string;              // UUID
    name: string;                    // Perfume name
    brand: string;                   // Brand name
    compatibility_score: number;    // 0-100
    reason: string;                  // Why this perfume was recommended
    price: number;                   // Price in SAR
    mood_tag?: string;
    occasion_tag?: string;
    style_tag?: string;
    longevity_score?: number;
    sillage_score?: number;
    skin_compatibility?: string;
  }>;
  confidence: number;                // 0-1
  metadata: {
    detected_mood?: string;
    detected_occasion?: string;
    weather?: {
      description: string;
      temperature: number;
      humidity: number;
    };
    location?: {
      city: string;
      country: string;
      latitude: number;
      longitude: number;
    };
    time?: string;
    recommendations_count: number;
    recommendations_with_ids: string[];
  };
}
```

---

## JavaScript/TypeScript Examples

### Example 1: Basic Text Query

```typescript
async function analyzeWithText(text: string) {
  try {
    const response = await fetch('http://localhost:8000/api/ai-nose/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: text,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data: AINoseResponse = await response.json();
    return data;
  } catch (error) {
    console.error('AI Nose error:', error);
    throw error;
  }
}

// Usage
const result = await analyzeWithText('أريد عطر منعش للصيف');
console.log(result.recommendations);
```

### Example 2: With GPS Coordinates (Auto Weather Fetching)

```typescript
async function analyzeWithLocation(
  text: string,
  latitude: number,
  longitude: number
) {
  const response = await fetch('http://localhost:8000/api/ai-nose/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: text,
      context: {
        location: {
          latitude: latitude,
          longitude: longitude,
        },
      },
    }),
  });

  const data: AINoseResponse = await response.json();
  return data;
}

// Usage - Get user's location first
navigator.geolocation.getCurrentPosition(
  async (position) => {
    const result = await analyzeWithLocation(
      'أريد عطر مناسب للطقس الحالي',
      position.coords.latitude,
      position.coords.longitude
    );
    console.log('Weather:', result.metadata.weather);
    console.log('Location:', result.metadata.location);
  },
  (error) => console.error('Geolocation error:', error)
);
```

### Example 3: With Options (Mood, Occasion, Gender)

```typescript
async function analyzeWithOptions(
  text: string,
  mood: string,
  occasion: string,
  gender: string
) {
  const response = await fetch('http://localhost:8000/api/ai-nose/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: text,
      options: {
        mood: mood,
        occasion: occasion,
        gender: gender,
      },
    }),
  });

  const data: AINoseResponse = await response.json();
  return data;
}

// Usage
const result = await analyzeWithOptions(
  'أريد عطر فاخر',
  'واثق',
  'حفلة',
  'Male'
);
```

### Example 4: Complete Example with Image Upload

```typescript
async function analyzeWithImage(
  text: string,
  imageFile: File,
  latitude?: number,
  longitude?: number
) {
  // Convert image to base64
  const imageBase64 = await fileToBase64(imageFile);

  const requestBody: AINoseRequest = {
    text: text,
    image_data: imageBase64,
  };

  // Add location if provided
  if (latitude && longitude) {
    requestBody.context = {
      location: {
        latitude: latitude,
        longitude: longitude,
      },
    };
  }

  const response = await fetch('http://localhost:8000/api/ai-nose/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  });

  const data: AINoseResponse = await response.json();
  return data;
}

// Helper function to convert file to base64
function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      const base64 = (reader.result as string).split(',')[1]; // Remove data:image/...;base64, prefix
      resolve(base64);
    };
    reader.onerror = (error) => reject(error);
  });
}

// Usage in React
function PerfumeAnalyzer() {
  const [result, setResult] = useState<AINoseResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async (text: string, imageFile?: File) => {
    setLoading(true);
    try {
      let data;
      if (imageFile) {
        data = await analyzeWithImage(text, imageFile);
      } else {
        data = await analyzeWithText(text);
      }
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {loading && <p>تحليل...</p>}
      {result && (
        <div>
          <p>{result.analysis}</p>
          {result.recommendations.map((perfume) => (
            <div key={perfume.perfume_id}>
              <h3>{perfume.name}</h3>
              <p>{perfume.brand}</p>
              <p>التوافق: {perfume.compatibility_score}%</p>
              <p>السعر: {perfume.price} ريال</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### Example 5: React Hook

```typescript
import { useState } from 'react';

interface UseAINoseReturn {
  analyze: (request: AINoseRequest) => Promise<void>;
  result: AINoseResponse | null;
  loading: boolean;
  error: string | null;
}

export function useAINose(apiBaseUrl: string = 'http://localhost:8000'): UseAINoseReturn {
  const [result, setResult] = useState<AINoseResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = async (request: AINoseRequest) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiBaseUrl}/api/ai-nose/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Request failed');
      }

      const data: AINoseResponse = await response.json();
      setResult(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return { analyze, result, loading, error };
}

// Usage in component
function MyComponent() {
  const { analyze, result, loading, error } = useAINose();

  const handleClick = async () => {
    await analyze({
      text: 'أريد عطر منعش',
      context: {
        location: {
          latitude: 24.7136,
          longitude: 46.6753,
        },
      },
    });
  };

  return (
    <div>
      <button onClick={handleClick} disabled={loading}>
        {loading ? 'جاري التحليل...' : 'تحليل'}
      </button>
      {error && <p>خطأ: {error}</p>}
      {result && <p>{result.analysis}</p>}
    </div>
  );
}
```

---

## React Native Example

```typescript
import { useState } from 'react';
import { Alert } from 'react-native';
import * as Location from 'expo-location';

async function analyzeWithLocation(text: string) {
  try {
    // Get user location
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission denied', 'Location permission is required');
      return;
    }

    const location = await Location.getCurrentPositionAsync({});
    const { latitude, longitude } = location.coords;

    // Call AI Nose API
    const response = await fetch('http://your-api-url/api/ai-nose/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: text,
        context: {
          location: {
            latitude: latitude,
            longitude: longitude,
          },
        },
      }),
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
    Alert.alert('Error', 'Failed to analyze');
  }
}
```

---

## Error Handling

```typescript
async function analyzeWithErrorHandling(request: AINoseRequest) {
  try {
    const response = await fetch('http://localhost:8000/api/ai-nose/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json();
      
      switch (response.status) {
        case 400:
          throw new Error(`Invalid request: ${errorData.detail}`);
        case 500:
          throw new Error(`Server error: ${errorData.detail}`);
        default:
          throw new Error(`Request failed: ${errorData.detail}`);
      }
    }

    const data: AINoseResponse = await response.json();
    return data;
  } catch (error) {
    if (error instanceof TypeError) {
      // Network error
      console.error('Network error - check if server is running');
    } else {
      console.error('Error:', error);
    }
    throw error;
  }
}
```

---

## Best Practices

### 1. Environment Variables

```typescript
// .env
NEXT_PUBLIC_API_URL=http://localhost:8000

// config.ts
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

### 2. API Client Class

```typescript
class AINoseClient {
  constructor(private baseUrl: string) {}

  async analyze(request: AINoseRequest): Promise<AINoseResponse> {
    const response = await fetch(`${this.baseUrl}/api/ai-nose/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Request failed');
    }

    return response.json();
  }

  async analyzeWithGPS(text: string, lat: number, lon: number) {
    return this.analyze({
      text,
      context: {
        location: { latitude: lat, longitude: lon },
      },
    });
  }
}

// Usage
const client = new AINoseClient('http://localhost:8000');
const result = await client.analyzeWithGPS('عطر منعش', 24.7136, 46.6753);
```

### 3. Request Debouncing

```typescript
import { useMemo } from 'react';
import { debounce } from 'lodash';

function useDebouncedAnalyze() {
  const debouncedAnalyze = useMemo(
    () =>
      debounce(async (text: string) => {
        const response = await fetch('/api/ai-nose/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text }),
        });
        return response.json();
      }, 500),
    []
  );

  return debouncedAnalyze;
}
```

---

## Complete Example: Full-Featured Component

```typescript
import React, { useState } from 'react';

interface PerfumeRecommendation {
  perfume_id: string;
  name: string;
  brand: string;
  compatibility_score: number;
  reason: string;
  price: number;
}

function AINoseAnalyzer() {
  const [text, setText] = useState('');
  const [recommendations, setRecommendations] = useState<PerfumeRecommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState('');
  const [weather, setWeather] = useState<any>(null);

  const handleAnalyze = async () => {
    if (!text.trim()) return;

    setLoading(true);
    try {
      // Get user location
      const position = await new Promise<GeolocationPosition>((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject);
      });

      const response = await fetch('http://localhost:8000/api/ai-nose/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          context: {
            location: {
              latitude: position.coords.latitude,
              longitude: position.coords.longitude,
            },
          },
        }),
      });

      const data = await response.json();
      setRecommendations(data.recommendations);
      setAnalysis(data.analysis);
      setWeather(data.metadata.weather);
    } catch (error) {
      console.error('Error:', error);
      alert('فشل التحليل. يرجى المحاولة مرة أخرى.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ai-nose-analyzer">
      <h2>الأنف الإلكتروني AI Nose™</h2>
      
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="أدخل وصف العطر الذي تبحث عنه..."
        rows={4}
      />
      
      <button onClick={handleAnalyze} disabled={loading}>
        {loading ? 'جاري التحليل...' : 'تحليل'}
      </button>

      {weather && (
        <div className="weather-info">
          <p>الطقس: {weather.description}, {weather.temperature}°م</p>
        </div>
      )}

      {analysis && (
        <div className="analysis">
          <p>{analysis}</p>
        </div>
      )}

      {recommendations.length > 0 && (
        <div className="recommendations">
          <h3>التوصيات:</h3>
          {recommendations.map((perfume) => (
            <div key={perfume.perfume_id} className="perfume-card">
              <h4>{perfume.name} - {perfume.brand}</h4>
              <p>التوافق: {perfume.compatibility_score}%</p>
              <p>{perfume.reason}</p>
              <p>السعر: {perfume.price} ريال</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AINoseAnalyzer;
```

---

## Quick Reference

### Minimal Request
```json
{
  "text": "أريد عطر منعش"
}
```

### With Location (Auto Weather)
```json
{
  "text": "عطر للصيف",
  "context": {
    "location": {
      "latitude": 24.7136,
      "longitude": 46.6753
    }
  }
}
```

### With All Options
```json
{
  "text": "أريد عطر فاخر",
  "options": {
    "mood": "واثق",
    "occasion": "حفلة",
    "gender": "Male",
    "skin_type": "دهنية"
  },
  "context": {
    "location": {
      "latitude": 24.7136,
      "longitude": 46.6753
    }
  },
  "user_id": "user-uuid-here"
}
```

---

## Testing with cURL

```bash
# Basic test
curl -X POST http://localhost:8000/api/ai-nose/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "أريد عطر منعش"}'

# With location
curl -X POST http://localhost:8000/api/ai-nose/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "عطر للصيف",
    "context": {
      "location": {
        "latitude": 24.7136,
        "longitude": 46.6753
      }
    }
  }'
```

---

## Notes

1. **Automatic Weather Fetching**: If you provide `latitude` and `longitude` in `context.location`, the API automatically fetches weather, location name, and current time.

2. **Perfume IDs**: All recommendations include `perfume_id` which you can use to fetch more details or add to cart.

3. **Error Handling**: Always wrap API calls in try-catch blocks and handle network errors gracefully.

4. **Loading States**: Show loading indicators while the API is processing.

5. **CORS**: Make sure your backend has CORS enabled for your frontend domain.

