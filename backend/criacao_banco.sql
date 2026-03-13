CREATE DATABASE IF NOT EXISTS marketing_db;
USE marketing_db;

CREATE TABLE IF NOT EXISTS metricas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_registro DATE,
    qtd_leads INT,
    qtd_vendas INT,
    taxa_conversao DECIMAL(5,2)
);