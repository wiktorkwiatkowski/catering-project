CREATE DATABASE IF NOT EXISTS catering;
USE catering;

CREATE TABLE IF NOT EXISTS menu (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    price DECIMAL(10,2)
);

INSERT INTO menu (name, price) VALUES
('Pizza Margherita', 25.99),
('Burger Wołowy', 22.50),
('Sałatka Cezar', 18.00);
