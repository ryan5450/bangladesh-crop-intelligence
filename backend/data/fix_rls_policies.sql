-- ==============================================================================
-- Fix Row Level Security (RLS) Policies for Bangladesh Crop Intelligence
-- Run this in your Supabase SQL Editor:
-- https://supabase.com/dashboard/project/_/sql
-- ==============================================================================

-- Option A: Disable RLS on agronomy data tables so backend can update them freely
ALTER TABLE public.crops DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.growth_stages DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.diseases DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.regions DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.crop_images DISABLE ROW LEVEL SECURITY;

-- Option B (Alternative): If you prefer keeping RLS enabled, grant full access policies:
DO $$
BEGIN
    -- crops
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'crops' AND policyname = 'Allow all access to crops') THEN
        CREATE POLICY "Allow all access to crops" ON public.crops FOR ALL USING (true) WITH CHECK (true);
    END IF;

    -- growth_stages
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'growth_stages' AND policyname = 'Allow all access to growth_stages') THEN
        CREATE POLICY "Allow all access to growth_stages" ON public.growth_stages FOR ALL USING (true) WITH CHECK (true);
    END IF;

    -- diseases
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'diseases' AND policyname = 'Allow all access to diseases') THEN
        CREATE POLICY "Allow all access to diseases" ON public.diseases FOR ALL USING (true) WITH CHECK (true);
    END IF;

    -- regions
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'regions' AND policyname = 'Allow all access to regions') THEN
        CREATE POLICY "Allow all access to regions" ON public.regions FOR ALL USING (true) WITH CHECK (true);
    END IF;

    -- crop_images
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'crop_images' AND policyname = 'Allow all access to crop_images') THEN
        CREATE POLICY "Allow all access to crop_images" ON public.crop_images FOR ALL USING (true) WITH CHECK (true);
    END IF;
END $$;
