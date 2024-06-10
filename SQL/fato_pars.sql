DROP TABLE IF EXISTS fato_pars;
CREATE TABLE fato_pars AS (SELECT * FROM pars LIMIT 1);

DELETE FROM fato_pars;

INSERT INTO fato_pars (SELECT * FROM pars WHERE pa_cidpri LIKE 'V%');
