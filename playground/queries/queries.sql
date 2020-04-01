-- Obtain (cached) conversation participant info
SELECT thread_key,
       thread_name,
       other_participant_profile_picture_url,
       other_participant_url_expiration_timestamp_ms
FROM _cached_participant_thread_info

-- Obtain contacts and corresponding info (brief)
SELECT *
FROM user_contact_info

-- Obtain (first) message exchange request
SELECT *
FROM message_requests

-- Obtain conversation participant info
SELECT p.thread_key,
       p.contact_id,
       u.name,
       p.read_watermark_timestamp_ms,
       p.delivered_watermark_timestamp_ms,
       p.nickname
FROM participants AS p JOIN user_contact_info AS u ON u.contact_id = p.contact_id

-- Obtain contacts and corresponding info (deprecated)
SELECT c.id,
       c.name,
       c.profile_picture_large_url,
       u.phone_number,
       u.email_address
FROM contacts AS c JOIN user_contact_info AS u ON c.id = u.contact_id

-- Obtain messages per participant
SELECT m.thread_key,
       datetime((m.timestamp_ms)/1000,'unixepoch'),
       u.contact_id, m.sender_id,
       u.name,
       m.text
FROM messages AS m JOIN user_contact_info AS u ON m.sender_id = u.contact_id
ORDER BY m.timestamp_ms

-- Obtain messages (and any other content) per participant
SELECT m.thread_key,
       datetime((m.timestamp_ms)/1000,'unixepoch'), 
       u.contact_id,
       m.sender_id,
       u.name, m.text,
       a.preview_url,
       a.playable_url,
       a.title_text,
       a.subtitle_text,
       a.default_cta_type,
       a.playable_url_mime_type
FROM messages AS m LEFT JOIN attachments AS a ON m.message_id = a.message_id
                        JOIN user_contact_info AS u ON m.sender_id = u.contact_id
ORDER BY m.timestamp_ms

-- Obtain messages where there are reactions
SELECT r.thread_key,
       m.timestamp_ms,
       u.name,
       m.text,
       r.reaction
FROM reactions AS r JOIN messages AS m ON r.thread_key = m.thread_key
                    JOIN user_contact_info AS u ON r.actor_id = u.contact_id