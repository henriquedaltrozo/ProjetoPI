-- Dim Estabelecimento
-- =============================================
DROP VIEW IF EXISTS dim_estabelecimento;
CREATE VIEW dim_estabelecimento AS
SELECT 
    estab.CNES     AS id,
    estab.FANTASIA AS nome,
    -- estab.CODUFMUN AS mun_id
FROM
    cadgerrs estab;

-- Dim Tipo Estabelecimento
-- =============================================
DROP VIEW IF EXISTS dim_tipo_estabelecimento;
CREATE VIEW dim_tipo_estabelecimento AS
SELECT 
    codigo AS id,
    descr  AS nome
FROM
    tp_estab;

-- Dim Tempo (DRILL-UP e ROLL-DOWN)
-- =============================================
CREATE OR REPLACE VIEW dim_tempo AS
WITH RECURSIVE periodo AS (
    SELECT DATE '2016-01-01' AS data
    UNION ALL
    SELECT data + INTERVAL '1 month'
    FROM periodo
    WHERE data < DATE '2024-12-01'
)
SELECT
    EXTRACT(YEAR FROM data) * 100 + EXTRACT(MONTH FROM data) AS id,
    EXTRACT(MONTH FROM data) AS mes,
    CEIL(EXTRACT(MONTH FROM data) / 3.0) AS trimestre,
    EXTRACT(YEAR FROM data) AS ano
FROM
    periodo;

-- Dim Procedimento
-- =============================================
DROP VIEW IF EXISTS dim_procedimento;
CREATE VIEW dim_procedimento AS
SELECT 
    ip_cod  AS id,
    ip_dscr AS nome
FROM
    tb_sigtaw;

-- Dim Complexidade
-- =============================================
DROP VIEW IF EXISTS dim_complexidade;
CREATE VIEW dim_complexidade AS
SELECT 
    codigo AS id,
    descr  AS nome
FROM
    complex;

-- Dim Localizacao (DRILL-UP e ROLL-DOWN)
-- =============================================
DROP VIEW IF EXISTS dim_localizacao;
CREATE VIEW dim_localizacao AS
SELECT
    mun.codigo    AS mun_id,
    mun.descr[7:] AS mun_nome,
    (SELECT codigo FROM rs_municip WHERE descr[7:] = mic.descr[6:]) AS mic_id,
    mic.descr[6:] AS mic_nome
FROM 
    rs_municip mun
JOIN 
    rs_micibge mic ON CAST(mun.codigo AS VARCHAR) = mic.codigo;

-- Dim Sexo
-- =============================================
DROP VIEW IF EXISTS dim_sexo;
CREATE VIEW dim_sexo AS
SELECT 
    codigo AS id,
    descr  AS nome
FROM
    sexo;

-- Dim Idade (DRILL-UP e ROLL-DOWN)
-- =============================================
DROP VIEW IF EXISTS dim_idade;
CREATE VIEW dim_idade AS
WITH RECURSIVE range AS (
    SELECT 0 AS idade
    UNION ALL
    SELECT idade + 1 FROM range WHERE idade < 130
)
SELECT 
    idade,
    CASE
        WHEN idade BETWEEN 0 AND 12  THEN 'Criança'
        WHEN idade BETWEEN 13 AND 17 THEN 'Adolescente'
        WHEN idade BETWEEN 18 AND 34 THEN 'Jovem Adulto'
        WHEN idade BETWEEN 35 AND 49 THEN 'Adulto'
        WHEN idade BETWEEN 50 AND 64 THEN 'Meia Idade'
        WHEN idade >= 65             THEN 'Idoso'
        ELSE 'Unknown'
    END AS faixa_etaria
FROM 
    range;

-- Dim CID
-- =============================================
DROP VIEW IF EXISTS dim_cid;
CREATE VIEW dim_cid AS
SELECT 
    cd_cod       AS id,
    cd_descr[6:] AS nome -- TODO: Ta cortando no CID NAO IDENTIFICADO
FROM
    s_cid;

-- Dim Saida
-- =============================================
DROP VIEW IF EXISTS dim_saida;
CREATE VIEW dim_saida AS
SELECT 
    codigo AS id,
    descr  AS nome
FROM
    motsaipe;

-- Dim Ocupacao
-- =============================================
DROP VIEW IF EXISTS dim_ocupacao;
CREATE VIEW dim_ocupacao AS
SELECT 
    cbo    AS id,
    ds_cbo AS nome
FROM
    cbo;
