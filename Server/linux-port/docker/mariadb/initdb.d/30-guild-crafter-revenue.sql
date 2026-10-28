-- MT2009_PLUS_CRAFTER_REVENUE_V1: Tabela gromadzaca utarg rzemieslnikow gildyjnych (do wyplaty dla Lidera)
CREATE TABLE IF NOT EXISTS player.guild_crafter_revenue (
    guild_id INT UNSIGNED NOT NULL PRIMARY KEY,
    payout_available BIGINT NOT NULL DEFAULT 0,
    total_earned BIGINT NOT NULL DEFAULT 0,
    total_withdrawn BIGINT NOT NULL DEFAULT 0,
    last_withdrawal_time DATETIME DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
