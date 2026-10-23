PRAGMA journal_mode=DELETE;
BEGIN IMMEDIATE;
CREATE TABLE ip_dictionary(ip_id INTEGER PRIMARY KEY,ip TEXT NOT NULL UNIQUE);
INSERT INTO ip_dictionary(ip) SELECT DISTINCT ip FROM ip_drops ORDER BY ip;
CREATE TABLE ip_events(event_id INTEGER PRIMARY KEY,timestamp INTEGER,ip_id INTEGER NOT NULL,count INTEGER,list_type TEXT);
INSERT INTO ip_events SELECT e.rowid,e.timestamp,d.ip_id,e.count,e.list_type FROM ip_drops e JOIN ip_dictionary d ON d.ip=e.ip ORDER BY e.rowid;
DROP TABLE ip_drops;
CREATE INDEX events_ts ON ip_events(timestamp);
CREATE INDEX events_ip ON ip_events(ip_id);
CREATE INDEX events_list_ts_ip ON ip_events(list_type,timestamp,ip_id);
CREATE VIEW ip_drops AS SELECT e.timestamp,d.ip,e.count,e.list_type,e.event_id FROM ip_events e JOIN ip_dictionary d USING(ip_id);
CREATE TRIGGER ip_drops_insert INSTEAD OF INSERT ON ip_drops BEGIN
 INSERT OR IGNORE INTO ip_dictionary(ip) VALUES(NEW.ip);
 INSERT INTO ip_events(timestamp,ip_id,count,list_type) VALUES(NEW.timestamp,(SELECT ip_id FROM ip_dictionary WHERE ip=NEW.ip),NEW.count,NEW.list_type);
END;
CREATE TRIGGER ip_drops_delete INSTEAD OF DELETE ON ip_drops BEGIN
 DELETE FROM ip_events WHERE event_id=OLD.event_id;
END;
CREATE TRIGGER ip_drops_update INSTEAD OF UPDATE ON ip_drops BEGIN
 INSERT OR IGNORE INTO ip_dictionary(ip) VALUES(NEW.ip);
 UPDATE ip_events SET timestamp=NEW.timestamp,ip_id=(SELECT ip_id FROM ip_dictionary WHERE ip=NEW.ip),count=NEW.count,list_type=NEW.list_type WHERE event_id=OLD.event_id;
END;
COMMIT;
VACUUM;
