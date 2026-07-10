-- Geography schema

DROP TABLE IF EXISTS seccion;
DROP TABLE IF EXISTS municipality;
DROP TABLE IF EXISTS state;

CREATE TABLE state (
    state_id INTEGER PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    capital VARCHAR(128),
    geometry GEOMETRY(MULTIPOLYGON, 4326)
);

CREATE TABLE municipality (
    id INTEGER PRIMARY KEY,
    municipality_id INTEGER,
    state_id INTEGER NOT NULL,
    name VARCHAR(128) NOT NULL,
    geometry GEOMETRY(MULTIPOLYGON, 4326),

    CONSTRAINT fk_municipality_state
        FOREIGN KEY (state_id)
        REFERENCES state(state_id)
        ON DELETE CASCADE
);

CREATE TABLE seccion (
    seccion_id INTEGER PRIMARY KEY,
    state_id INTEGER NOT NULL,
    municipality_id INTEGER NOT NULL,
    distrito_f INTEGER NOT NULL,
    distrito_l INTEGER NOT NULL,
    geometry GEOMETRY(MULTIPOLYGON, 4326),

    CONSTRAINT fk_seccion_state
        FOREIGN KEY (state_id)
        REFERENCES state(state_id)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_seccion_municipality
        FOREIGN KEY (municipality_id)
        REFERENCES municipality(id)
        ON DELETE CASCADE
);