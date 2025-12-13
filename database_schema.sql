--
-- PostgreSQL database schema for the Aura AI Perfume Store
--

-- Customers Table
CREATE TABLE customers (
    customer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Perfumes Table
CREATE TABLE perfumes (
    perfume_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(255),
    gender VARCHAR(50) CHECK (gender IN ('Male', 'Female', 'Unisex')),
    concentration VARCHAR(50) CHECK (concentration IN ('Parfum', 'EDP', 'EDT', 'EDC', 'Extrait')),
    price NUMERIC(10, 2),
    ml_size INT,
    description_llm TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI Attributes Table
CREATE TABLE ai_attributes (
    attribute_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    perfume_id UUID REFERENCES perfumes(perfume_id) ON DELETE CASCADE,
    mood_tag VARCHAR(100),
    style_tag VARCHAR(100),
    occasion_tag VARCHAR(100),
    sillage_score INT,
    longevity_score INT,
    skin_compatibility VARCHAR(100)
);

-- Ingredients Table
CREATE TABLE ingredients (
    ingredient_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT
);

-- Perfume-Ingredients Linking Table
CREATE TABLE perfume_ingredients (
    perfume_id UUID REFERENCES perfumes(perfume_id) ON DELETE CASCADE,
    ingredient_id UUID REFERENCES ingredients(ingredient_id) ON DELETE CASCADE,
    note_type VARCHAR(50) CHECK (note_type IN ('Top', 'Heart', 'Base')),
    PRIMARY KEY (perfume_id, ingredient_id)
);

-- Orders Table
CREATE TABLE orders (
    order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(customer_id) ON DELETE SET NULL,
    total_amount NUMERIC(10, 2),
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Order Items Table
CREATE TABLE order_items (
    order_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(order_id) ON DELETE CASCADE,
    perfume_id UUID REFERENCES perfumes(perfume_id) ON DELETE RESTRICT,
    quantity INT,
    price_at_purchase NUMERIC(10, 2)
);

-- Customer Interactions Table (for AI learning)
CREATE TABLE customer_interactions (
    interaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(customer_id) ON DELETE CASCADE,
    feature_used VARCHAR(100),
    input_data JSONB,
    output_data JSONB,
    interaction_time TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Customer AI Profiles Table
CREATE TABLE customer_profiles (
    profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(customer_id) ON DELETE CASCADE,
    perfume_drivers JSONB, -- e.g., {"likes": ["oud", "vanilla"], "dislikes": ["citrus"]}
    personality_map JSONB, -- e.g., {"type": "Romantic", "traits": ["elegant", "sophisticated"]}
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Prompts Table
CREATE TABLE prompts (
    prompt_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    feature VARCHAR(100) UNIQUE NOT NULL,
    prompt_text TEXT NOT NULL,
    version INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE
);
