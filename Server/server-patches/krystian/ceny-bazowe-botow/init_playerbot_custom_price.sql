-- MT2009_PLUS_PLAYERBOT_CUSTOM_PRICES_V1
-- Tabela nadpisań bazowych cen skupu/sprzedaży playerbotów

CREATE TABLE IF NOT EXISTS player.playerbot_custom_price (
  price_type VARCHAR(16) NOT NULL,
  target_id INT UNSIGNED NOT NULL,
  price INT UNSIGNED NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (price_type, target_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
