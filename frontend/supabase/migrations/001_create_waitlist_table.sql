-- Create waitlist table
CREATE TABLE IF NOT EXISTS waitlist (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    source VARCHAR(100),
    referrer TEXT,
    utm_source VARCHAR(100),
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(100),
    utm_term VARCHAR(100),
    utm_content VARCHAR(100),
    ref VARCHAR(100),
    referral VARCHAR(100),
    user_agent TEXT,
    ip_address INET,
    country VARCHAR(10),
    timezone VARCHAR(100),
    position INTEGER,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'unsubscribed')),
    referral_code VARCHAR(50) UNIQUE,
    referred_by UUID REFERENCES waitlist(id) ON DELETE SET NULL,
    confirmation_token VARCHAR(100) UNIQUE,
    confirmation_sent_at TIMESTAMP WITH TIME ZONE,
    confirmed_at TIMESTAMP WITH TIME ZONE,
    unsubscribed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_waitlist_email ON waitlist(email);
CREATE INDEX IF NOT EXISTS idx_waitlist_status ON waitlist(status);
CREATE INDEX IF NOT EXISTS idx_waitlist_position ON waitlist(position);
CREATE INDEX IF NOT EXISTS idx_waitlist_referral_code ON waitlist(referral_code);
CREATE INDEX IF NOT EXISTS idx_waitlist_created_at ON waitlist(created_at);

-- Create trigger to automatically update position and updated_at
CREATE OR REPLACE FUNCTION update_waitlist_position()
RETURNS TRIGGER AS $$
BEGIN
    -- Update position for new entries
    IF TG_OP = 'INSERT' THEN
        NEW.position = (SELECT COALESCE(MAX(position), 0) + 1 FROM waitlist WHERE status = 'pending');
        NEW.updated_at = NOW();
        RETURN NEW;
    END IF;
    
    -- Update updated_at for updates
    IF TG_OP = 'UPDATE' THEN
        NEW.updated_at = NOW();
        RETURN NEW;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trigger_update_waitlist_position
    BEFORE INSERT OR UPDATE ON waitlist
    FOR EACH ROW
    EXECUTE FUNCTION update_waitlist_position();

-- Create function to generate unique referral codes
CREATE OR REPLACE FUNCTION generate_referral_code()
RETURNS TEXT AS $$
DECLARE
    chars TEXT := 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    result TEXT := '';
    i INTEGER;
    code_length INTEGER := 8;
BEGIN
    FOR i IN 1..code_length LOOP
        result := result || substr(chars, floor(random() * length(chars) + 1)::int, 1);
    END LOOP;
    
    -- Check if code already exists, if so, try again
    IF EXISTS(SELECT 1 FROM waitlist WHERE referral_code = result) THEN
        RETURN generate_referral_code();
    END IF;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Create function to generate referral code on insert
CREATE OR REPLACE FUNCTION set_referral_code()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.referral_code IS NULL THEN
        NEW.referral_code = generate_referral_code();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trigger_set_referral_code
    BEFORE INSERT ON waitlist
    FOR EACH ROW
    EXECUTE FUNCTION set_referral_code();

-- Create view for public statistics (no personal info)
CREATE OR REPLACE VIEW waitlist_public_stats AS
SELECT 
    COUNT(*) as total_subscribers,
    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '7 days') as recent_signups,
    COALESCE(
        JSON_OBJECT_AGG(
            COALESCE(country, 'unknown'),
            country_count
        ) FILTER (WHERE country_count IS NOT NULL),
        '{}'::json
    ) as countries,
    COALESCE(
        JSON_OBJECT_AGG(
            COALESCE(source, 'unknown'),
            source_count
        ) FILTER (WHERE source_count IS NOT NULL),
        '{}'::json
    ) as sources
FROM (
    SELECT 
        country,
        COUNT(*) as country_count
    FROM waitlist 
    WHERE status IN ('pending', 'confirmed')
    GROUP BY country
) countries
CROSS JOIN (
    SELECT 
        source,
        COUNT(*) as source_count
    FROM waitlist 
    WHERE status IN ('pending', 'confirmed')
    GROUP BY source
) sources;

-- Enable RLS (Row Level Security)
ALTER TABLE waitlist ENABLE ROW LEVEL SECURITY;

-- Create policy for public read access to public stats only
CREATE POLICY "Public stats access" ON waitlist
    FOR SELECT USING (false); -- No direct access to waitlist table

-- Grant access to public stats view
GRANT SELECT ON waitlist_public_stats TO anon, authenticated;