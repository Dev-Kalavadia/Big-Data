# Lab on Cassandra:
# After installing Cassandra, run the cqlsh client.

create keyspace bds with replication = {'class': 'NetworkTopologyStrategy', 'replication_factor': '1'};

use bds;

CREATE TABLE IF NOT EXISTS students ( 
  sid         int,
  name        TEXT,
  email       TEXT,
  PRIMARY KEY (( email ))
);


INSERT INTO b1 (sid, name, email) VALUES (
  1, 'John Doe', 'jd@gmail.com'
);



CREATE TABLE IF NOT EXISTS b1 ( 
  sid         int,
  name        TEXT,
  email       TEXT,
  PRIMARY KEY (( email ), sid)
);


CREATE TABLE IF NOT EXISTS b2 ( 
  sid         int,
  name        TEXT,
  email       TEXT,
  PRIMARY KEY (( email, sid), name)
);

CREATE TABLE IF NOT EXISTS b4 ( 
  sid         int,
  name        TEXT,
  email       TEXT,
  PRIMARY KEY (email, sid, name)
);



CREATE TABLE IF NOT EXISTS b4 ( 
  sid         int,
  name        TEXT,
  email       TEXT,
  PRIMARY KEY (email, sid, name)
);


CREATE TABLE IF NOT EXISTS b5 ( 
  sid         int,
  name        TEXT,
  email       TEXT,
  PRIMARY KEY (sid)
);
