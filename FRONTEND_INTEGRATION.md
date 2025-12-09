# Frontend Integration Guide

This guide shows how to update your frontend to work with the updated backend API endpoints.

## 1. TTS (Text-to-Speech) Endpoint

### Endpoint
```
POST /api/tts/text-to-voice
```

### Request Format
```typescript
interface TTSRequest {
  text: string;
  voice?: string;        // Optional, e.g., "ar-SA-HamedNeural"
  rate?: string;         // Optional, default: "+0%"
  pitch?: string;         // Optional, default: "+0Hz"
  volume?: string;       // Optional, default: "+0%"
}
```

### Response
- **Success (200)**: Returns audio file (MP3) as binary blob
- **Error (400/500)**: JSON with `detail` field

### Frontend Implementation Example

```typescript
// api.ts or similar
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function textToSpeech(
  text: string,
  voice?: string
): Promise<Blob> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tts/text-to-voice`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        voice: voice || 'ar-SA-HamedNeural', // Default Arabic voice
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'TTS generation failed');
    }

    // Return audio blob
    return await response.blob();
  } catch (error) {
    console.error('TTS error:', error);
    throw error;
  }
}

// Usage in component
async function handleSpeak(text: string) {
  try {
    const audioBlob = await textToSpeech(text);
    
    // Create audio URL and play
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    audio.play();
    
    // Clean up URL after playing
    audio.onended = () => URL.revokeObjectURL(audioUrl);
  } catch (error) {
    console.error('TTS error:', error);
    // Show user-friendly error message
    alert('فشل في توليد الصوت. يرجى المحاولة مرة أخرى.');
  }
}
```

### React Hook Example

```typescript
import { useState } from 'react';

export function useTextToSpeech() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const speak = async (text: string, voice?: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/tts/text-to-voice`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, voice }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'TTS generation failed');
      }

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      
      return new Promise<void>((resolve, reject) => {
        audio.onended = () => {
          URL.revokeObjectURL(audioUrl);
          resolve();
        };
        audio.onerror = reject;
        audio.play();
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return { speak, isLoading, error };
}
```

### Error Handling

The TTS endpoint may return these errors:
- **400**: Invalid request (empty text, text too long)
- **500**: Service unavailable (network/proxy issues)

```typescript
try {
  await textToSpeech(text);
} catch (error) {
  if (error.message.includes('proxy') || error.message.includes('network')) {
    // Show message about network configuration
    alert('مشكلة في الاتصال. يرجى التحقق من إعدادات الشبكة.');
  } else {
    // Generic error
    alert('فشل في توليد الصوت. يرجى المحاولة مرة أخرى.');
  }
}
```

---

## 2. Admin Customers Endpoint

### Endpoint
```
GET /api/admin/customers?page=1&limit=10
```

### Query Parameters
- `page` (number, default: 1): Page number (starts from 1)
- `limit` (number, default: 10, max: 100): Items per page

### Response Format
```typescript
interface Customer {
  customer_id: string;
  name: string | null;
  email: string | null;
  phone: string | null;
  created_at: string | null;
  preferences: Record<string, any> | null;
}

interface CustomersListResponse {
  customers: Customer[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}
```

### Frontend Implementation Example

```typescript
// api.ts
export async function getCustomers(
  page: number = 1,
  limit: number = 10
): Promise<CustomersListResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/admin/customers?page=${page}&limit=${limit}`,
    {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch customers');
  }

  return await response.json();
}
```

### React Component Example

```typescript
import { useState, useEffect } from 'react';

interface Customer {
  customer_id: string;
  name: string | null;
  email: string | null;
  phone: string | null;
  created_at: string | null;
  preferences: Record<string, any> | null;
}

interface CustomersListResponse {
  customers: Customer[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export function CustomersList() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  const [pagination, setPagination] = useState({
    total: 0,
    total_pages: 0,
  });

  useEffect(() => {
    fetchCustomers();
  }, [page]);

  const fetchCustomers = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/admin/customers?page=${page}&limit=${limit}`
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch customers');
      }

      const data: CustomersListResponse = await response.json();
      setCustomers(data.customers);
      setPagination({
        total: data.total,
        total_pages: data.total_pages,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Customers ({pagination.total})</h1>
      
      {loading && <p>Loading...</p>}
      {error && <p className="error">Error: {error}</p>}
      
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Created At</th>
          </tr>
        </thead>
        <tbody>
          {customers.map((customer) => (
            <tr key={customer.customer_id}>
              <td>{customer.customer_id}</td>
              <td>{customer.name || 'N/A'}</td>
              <td>{customer.email || 'N/A'}</td>
              <td>{customer.phone || 'N/A'}</td>
              <td>{customer.created_at || 'N/A'}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="pagination">
        <button
          disabled={page === 1}
          onClick={() => setPage(page - 1)}
        >
          Previous
        </button>
        <span>
          Page {page} of {pagination.total_pages}
        </span>
        <button
          disabled={page >= pagination.total_pages}
          onClick={() => setPage(page + 1)}
        >
          Next
        </button>
      </div>
    </div>
  );
}
```

### Using React Query (TanStack Query)

```typescript
import { useQuery } from '@tanstack/react-query';

function useCustomers(page: number = 1, limit: number = 10) {
  return useQuery({
    queryKey: ['customers', page, limit],
    queryFn: async () => {
      const response = await fetch(
        `${API_BASE_URL}/api/admin/customers?page=${page}&limit=${limit}`
      );
      if (!response.ok) {
        throw new Error('Failed to fetch customers');
      }
      return response.json() as Promise<CustomersListResponse>;
    },
  });
}

// Usage in component
function CustomersList() {
  const [page, setPage] = useState(1);
  const { data, isLoading, error } = useCustomers(page, 10);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {/* Render customers */}
      {data?.customers.map((customer) => (
        <div key={customer.customer_id}>{customer.email}</div>
      ))}
    </div>
  );
}
```

---

## 3. Updated API Base URL

Make sure your frontend uses the correct API base URL:

```typescript
// .env.local or environment config
NEXT_PUBLIC_API_URL=http://localhost:8000

// Or for production
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

---

## 4. CORS Configuration

The backend is configured to allow all origins. If you need to restrict it, update `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Summary of Changes

1. **TTS Endpoint**: 
   - URL: `/api/tts/text-to-voice`
   - Method: POST
   - Returns: Audio blob (MP3)
   - Handle errors gracefully (proxy/network issues)

2. **Admin Customers Endpoint**:
   - URL: `/api/admin/customers`
   - Method: GET
   - Query params: `page`, `limit`
   - Returns: Paginated customer list with metadata

3. **Error Handling**: Both endpoints return JSON errors with `detail` field

4. **Response Types**: Update TypeScript interfaces to match backend response models

