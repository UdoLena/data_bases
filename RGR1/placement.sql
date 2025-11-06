INSERT INTO placement (exhibit_id, room_id)
SELECT 
    e.exhibit_id,
    r.room_id
FROM exhibit e
-- Виконуємо підзапит окремо для кожного exhibit
JOIN LATERAL (
    SELECT room_id
    FROM room
    ORDER BY random() + e.exhibit_id * random()
    LIMIT 1
) AS r ON TRUE;

-- Перевірка результату
SELECT * FROM placement ORDER BY exhibit_id;