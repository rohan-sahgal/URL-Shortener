USE urlshortner;
CREATE TABLE IF NOT EXISTS urls (short_resource text, long_resource text, PRIMARY KEY (short_resource));
