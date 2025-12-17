# AI Attributes Range Query Guide

This guide explains how to query the `ai_attributes` table using PostgreSQL range types.

## Database Setup

First, ensure your `ai_attributes` table has the range columns and the RPC function:

1. **Add range columns to ai_attributes table** (if not already present):
```sql
ALTER TABLE ai_attributes 
ADD COLUMN IF NOT EXISTS geo_range BOX,
ADD COLUMN IF NOT EXISTS temp_range NUMRANGE,
ADD COLUMN IF NOT EXISTS datetime_range TSRANGE;
```

2. **Create the RPC function** by running:
```bash
psql -h your-db-host -U your-user -d your-database -f supabase/migrations/002_add_range_query_function.sql
```

Or execute the SQL in `supabase/migrations/002_add_range_query_function.sql` in your Supabase SQL editor.

## API Endpoint

**POST** `/api/ai-attributes/query-by-ranges`

## Request Format

### Option 1: Query with Range Overlaps

Find all records where ranges overlap with the provided ranges:

```json
{
  "geo_range": "(35,45),(30,40)",
  "temp_range": "[20,35)",
  "datetime_range": "[\"2024-01-01 14:00:00\",\"2024-01-01 22:00:00\")"
}
```

### Option 2: Query with Point Values

Find all records where the point values are contained within the ranges:

```json
{
  "point_latitude": 32.5,
  "point_longitude": 42.5,
  "temperature": 25,
  "datetime": "2024-01-01 18:00:00"
}
```

### Option 3: Mixed Query

Combine range overlaps and point checks:

```json
{
  "geo_range": "(35,45),(30,40)",
  "temperature": 25,
  "datetime_range": "[\"2024-01-01 14:00:00\",\"2024-01-01 22:00:00\")"
}
```

## Range Format Examples

### Geo Range (BOX)
- Format: `(x1,y1),(x2,y2)` where (x1,y1) and (x2,y2) are opposite corners
- Example: `(35,45),(30,40)` - Box from (30,40) to (35,45)

### Temperature Range (NUMRANGE)
- Format: `[min,max)` or `(min,max)` or `[min,max]` or `(min,max)`
  - `[` = inclusive start
  - `(` = exclusive start
  - `]` = inclusive end
  - `)` = exclusive end
- Example: `[20,35)` - From 20 (inclusive) to 35 (exclusive)

### DateTime Range (TSRANGE)
- Format: `["start","end")` or `('start','end')`
- Example: `["2024-01-01 14:00:00","2024-01-01 22:00:00")` - From 2 PM to 10 PM (exclusive)

## Example cURL Commands

### Test 1: Query with all ranges
```bash
curl -X POST http://localhost:8000/api/ai-attributes/query-by-ranges \
  -H "Content-Type: application/json" \
  -d '{
    "geo_range": "(35,45),(30,40)",
    "temp_range": "[20,35)",
    "datetime_range": "[\"2024-01-01 14:00:00\",\"2024-01-01 22:00:00\")"
  }'
```

### Test 2: Query with point coordinates
```bash
curl -X POST http://localhost:8000/api/ai-attributes/query-by-ranges \
  -H "Content-Type: application/json" \
  -d '{
    "point_latitude": 32.5,
    "point_longitude": 42.5,
    "temperature": 25,
    "datetime": "2024-01-01 18:00:00"
  }'
```

### Test 3: Query with temperature value only
```bash
curl -X POST http://localhost:8000/api/ai-attributes/query-by-ranges \
  -H "Content-Type: application/json" \
  -d '{
    "temperature": 25
  }'
```

## Response Format

```json
[
  {
    "attribute_id": "uuid",
    "perfume_id": "uuid",
    "mood_tag": "نشيط",
    "style_tag": "عصري",
    "occasion_tag": "يومي",
    "sillage_score": 8,
    "longevity_score": 7,
    "skin_compatibility": "دهنية",
    "geo_range": "(35,45),(30,40)",
    "temp_range": "[20,35)",
    "datetime_range": "[\"2024-01-01 14:00:00\",\"2024-01-01 22:00:00\")",
    "perfume_name": "اسم العطر",
    "perfume_brand": "العلامة",
    "perfume_price": 450.00
  }
]
```

## PostgreSQL Range Operators Used

- `@>` - Contains operator (checks if range contains a value)
- `&&` - Overlaps operator (checks if two ranges overlap)

## Notes

- All range parameters are optional
- If no parameters are provided, all records are returned
- The function uses AND logic - all provided conditions must match
- The RPC function must be created in the database before using this endpoint

