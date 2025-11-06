INSERT INTO exhibit (exhibit_id, name, type, year, materials, author_id)
SELECT
    g AS exhibit_id,
    (ARRAY[
        'Sunset','Portrait','Abstract','Still Life','The Thinker',
        'Starry Night','Venus','Monument','Landscape','Self-Portrait',
        'The Scream','David','Mona Lisa','The Kiss','The Wave'
    ])[ceil(random()*15)] AS name,
    (ARRAY['Painting','Statue','Sculpture','Drawing','Engraving'])[ceil(random()*5)] AS type,
    (1700 + (random()*300)::int) AS year,
    (ARRAY['Canvas','Bronze','Marble','Wood','Acrylic','Cardboard','Metal','Ceramic'])[ceil(random()*8)] AS materials,
    (ARRAY(SELECT author_id FROM author))[ceil(random() * (SELECT COUNT(*) FROM author))] AS author_id
FROM generate_series(1,50) AS g;

SELECT * FROM public.exhibit
ORDER BY exhibit_id ASC;