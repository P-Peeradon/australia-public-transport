CREATE TABLE state_capital (
    gcc_code CHAR(5) PRIMARY KEY, 
    gcc_name VARCHAR(20),
    geometry POLYGON NOT NULL
);

CREATE TABLE suburb (
    sal_code CHAR(5) PRIMARY KEY,
    sal_name VARCHAR(50),
    geometry POLYGON NOT NULL,
    sal_state VARCHAR(3),
    sal_base VARCHAR(30),
    sal_direction VARCHAR(7),
    lga_code CHAR(5) FOREIGN KEY REFERENCES council(lga_code)
);

CREATE SPATIAL INDEX idx_suburb_geometry ON suburb(geometry);
CREATE INDEX idx_suburb_state ON suburb(sal_state);

CREATE TABLE council (
    lga_code CHAR(5) PRIMARY KEY,
    lga_name VARCHAR(50),
    geometry POLYGON NOT NULL,
);