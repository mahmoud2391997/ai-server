// ============================================
// AI Nose Endpoint - Quick Start Code
// Copy and paste into your frontend project
// ============================================

// 1. BASIC USAGE - Simple Text Query
async function analyzePerfume(text) {
  const response = await fetch('http://localhost:8000/api/ai-nose/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: text,
    }),
  });
  
  const data = await response.json();
  return data;
}

// Usage:
// const result = await analyzePerfume('أريد عطر منعش للصيف');
// console.log(result.recommendations);


// 2. WITH GPS LOCATION (Auto-fetches weather)
async function analyzeWithLocation(text, latitude, longitude) {
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
  
  const data = await response.json();
  return data;
}

// Usage with browser geolocation:
// navigator.geolocation.getCurrentPosition(async (position) => {
//   const result = await analyzeWithLocation(
//     'عطر مناسب للطقس',
//     position.coords.latitude,
//     position.coords.longitude
//   );
//   console.log('Weather:', result.metadata.weather);
//   console.log('Location:', result.metadata.location);
// });


// 3. WITH OPTIONS (Mood, Occasion, Gender)
async function analyzeWithOptions(text, mood, occasion, gender) {
  const response = await fetch('http://localhost:8000/api/ai-nose/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: text,
      options: {
        mood: mood,        // e.g., "نشيط", "هادئ", "رومانسي"
        occasion: occasion, // e.g., "يومي", "عمل", "حفلة"
        gender: gender,     // "Male", "Female", "Unisex"
      },
    }),
  });
  
  const data = await response.json();
  return data;
}

// Usage:
// const result = await analyzeWithOptions('عطر فاخر', 'واثق', 'حفلة', 'Male');


// 4. COMPLETE EXAMPLE - React Component
function AINoseComponent() {
  const [text, setText] = React.useState('');
  const [result, setResult] = React.useState(null);
  const [loading, setLoading] = React.useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      // Get user location
      const position = await new Promise((resolve, reject) => {
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
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="أدخل وصف العطر..."
      />
      <button onClick={handleAnalyze} disabled={loading}>
        {loading ? 'جاري التحليل...' : 'تحليل'}
      </button>
      
      {result && (
        <div>
          <p>{result.analysis}</p>
          {result.recommendations.map((perfume) => (
            <div key={perfume.perfume_id}>
              <h3>{perfume.name} - {perfume.brand}</h3>
              <p>التوافق: {perfume.compatibility_score}%</p>
              <p>السعر: {perfume.price} ريال</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}


// 5. REACT HOOK
function useAINose() {
  const [result, setResult] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const analyze = async (request) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/api/ai-nose/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error('Request failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { analyze, result, loading, error };
}

// Usage:
// const { analyze, result, loading } = useAINose();
// await analyze({ text: 'عطر منعش' });


// 6. ERROR HANDLING
async function analyzeWithErrorHandling(text) {
  try {
    const response = await fetch('http://localhost:8000/api/ai-nose/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Request failed');
    }

    return await response.json();
  } catch (error) {
    if (error instanceof TypeError) {
      console.error('Network error - check if server is running');
    } else {
      console.error('Error:', error);
    }
    throw error;
  }
}


// ============================================
// RESPONSE STRUCTURE
// ============================================
/*
{
  "analysis": "بناءً على تحليل الأنف الإلكتروني...",
  "recommendations": [
    {
      "perfume_id": "uuid",
      "name": "اسم العطر",
      "brand": "العلامة",
      "compatibility_score": 95,
      "reason": "يناسب مزاجك نشيط",
      "price": 450.0,
      "mood_tag": "نشيط",
      "occasion_tag": "يومي",
      "longevity_score": 85,
      "sillage_score": 75
    }
  ],
  "confidence": 0.92,
  "metadata": {
    "detected_mood": "نشيط",
    "detected_occasion": "يومي",
    "weather": {
      "description": "صافي",
      "temperature": 35
    },
    "location": {
      "city": "الرياض",
      "country": "SA"
    },
    "time": "02:30 PM"
  }
}
*/

