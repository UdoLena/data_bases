INSERT INTO author (author_id, first_name, last_name, birth_year, death_year)
SELECT 
    g AS author_id,
    (ARRAY['Olena','Ivan','Maria','Petro','Anna','Mykola','Kateryna','Dmytro','Sofia','Andriy'])[ceil(random()*10)],
    (ARRAY['Shevchenko','Kovalenko','Melnyk','Boyko','Tkachenko','Bondarenko','Kruglyak','Hryhorenko','Khmara','Lysenko'])[ceil(random()*10)],
    (1800 + (random() * 200)::int),
    CASE WHEN random() > 0.5 THEN (1900 + (random() * 120)::int) ELSE NULL END
FROM generate_series(1, 50) AS g;

SELECT * FROM public.author
ORDER BY author_id ASC;
