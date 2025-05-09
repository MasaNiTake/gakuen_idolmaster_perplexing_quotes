-- テーブルの再作成（既存のテーブルがある場合は削除）
DROP TABLE IF EXISTS gakuen_idolmaster_perplexing_quotes;

CREATE TABLE gakuen_idolmaster_perplexing_quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    sub_category TEXT NOT NULL,
    event_name TEXT,
    commu_idol_name TEXT,
    affinity TEXT,
    episode TEXT,
    idol_name TEXT NOT NULL,
    quote TEXT NOT NULL,
    note TEXT
);