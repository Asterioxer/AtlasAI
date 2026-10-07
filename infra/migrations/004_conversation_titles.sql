ALTER TABLE public.conversations
  ADD COLUMN IF NOT EXISTS title varchar(120);

UPDATE public.conversations c
SET title = sub.title
FROM (
  SELECT DISTINCT ON (conversation_id)
    conversation_id,
    LEFT(content, 120) AS title
  FROM public.messages
  WHERE role = 'user'
  ORDER BY conversation_id, created_at ASC
) sub
WHERE c.id = sub.conversation_id
  AND c.title IS NULL;
