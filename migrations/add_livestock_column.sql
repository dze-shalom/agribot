-- Add mentioned_livestock column to conversations table
-- Migration: add_livestock_column
-- Date: 2025-01-05

ALTER TABLE conversations
ADD COLUMN mentioned_livestock TEXT;

-- Add comment
COMMENT ON COLUMN conversations.mentioned_livestock IS 'JSON array of livestock animals discussed in conversation';
