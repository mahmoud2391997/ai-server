-- Function to query ai_attributes by range types
-- This function allows querying using geo_range (box), temp_range (numrange), and datetime_range (tsrange)

CREATE OR REPLACE FUNCTION query_ai_attributes_by_ranges(
    geo_box TEXT DEFAULT NULL,
    point_lat NUMERIC DEFAULT NULL,
    point_lon NUMERIC DEFAULT NULL,
    temp_range_str TEXT DEFAULT NULL,
    temp_value NUMERIC DEFAULT NULL,
    dt_range_str TEXT DEFAULT NULL,
    dt_value TIMESTAMP DEFAULT NULL
)
RETURNS TABLE (
    attribute_id UUID,
    perfume_id UUID,
    mood_tag VARCHAR,
    style_tag VARCHAR,
    occasion_tag VARCHAR,
    sillage_score INT,
    longevity_score INT,
    skin_compatibility VARCHAR,
    geo_range BOX,
    temp_range NUMRANGE,
    datetime_range TSRANGE,
    perfume_name VARCHAR,
    perfume_brand VARCHAR,
    perfume_price NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        aa.attribute_id,
        aa.perfume_id,
        aa.mood_tag,
        aa.style_tag,
        aa.occasion_tag,
        aa.sillage_score,
        aa.longevity_score,
        aa.skin_compatibility,
        aa.geo_range,
        aa.temp_range,
        aa.datetime_range,
        p.name as perfume_name,
        p.brand as perfume_brand,
        p.price as perfume_price
    FROM ai_attributes aa
    JOIN perfumes p ON aa.perfume_id = p.perfume_id
    WHERE 
        -- Geo range: check if point is within box OR if boxes overlap
        (point_lat IS NULL AND point_lon IS NULL AND geo_box IS NULL) OR
        (point_lat IS NOT NULL AND point_lon IS NOT NULL AND aa.geo_range IS NOT NULL AND aa.geo_range @> box(point(point_lon, point_lat))) OR
        (geo_box IS NOT NULL AND aa.geo_range IS NOT NULL AND aa.geo_range && box(geo_box::box)) OR
        (geo_box IS NULL AND point_lat IS NULL AND point_lon IS NULL)
    AND
        -- Temperature range: check if value is within range OR if ranges overlap
        (temp_value IS NULL AND temp_range_str IS NULL) OR
        (temp_value IS NOT NULL AND aa.temp_range IS NOT NULL AND aa.temp_range @> temp_value) OR
        (temp_range_str IS NOT NULL AND aa.temp_range IS NOT NULL AND aa.temp_range && temp_range_str::numrange) OR
        (temp_value IS NULL AND temp_range_str IS NULL)
    AND
        -- DateTime range: check if value is within range OR if ranges overlap
        (dt_value IS NULL AND dt_range_str IS NULL) OR
        (dt_value IS NOT NULL AND aa.datetime_range IS NOT NULL AND aa.datetime_range @> dt_value) OR
        (dt_range_str IS NOT NULL AND aa.datetime_range IS NOT NULL AND aa.datetime_range && dt_range_str::tsrange) OR
        (dt_value IS NULL AND dt_range_str IS NULL);
END;
$$ LANGUAGE plpgsql;

