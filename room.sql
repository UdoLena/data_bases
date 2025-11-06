INSERT INTO room (room_id, floor, name, time_start, time_end)
SELECT
    g AS room_id,
    (1 + floor(random()*5))::int AS floor,  -- Floors 1-5
    (ARRAY[
        'Gallery A','Gallery B','Gallery C','Gallery D','Gallery E',
        'Exhibition Hall 1','Exhibition Hall 2','Sculpture Room','Painting Room','Special Exhibit'
    ])[ceil(random()*10)] AS name,
    TIME '09:00' AS time_start,  -- start time
    TIME '18:00' AS time_end     -- end time
FROM generate_series(1,20) AS g;

SELECT * FROM public.room
ORDER BY room_id ASC;