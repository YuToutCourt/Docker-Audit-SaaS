CREATE TABLE Company (
   id_company BIGINT AUTO_INCREMENT,
   name VARCHAR(255),
   PRIMARY KEY(id_company)
);

CREATE TABLE Agent (
   id_agent BIGINT AUTO_INCREMENT,
   date_ DATETIME,
   enabled TINYINT(1),
   health_check VARCHAR(50),
   PRIMARY KEY(id_agent)
);

CREATE TABLE User_ (
   id BIGINT AUTO_INCREMENT,
   username VARCHAR(255),
   password VARCHAR(255),
   email VARCHAR(255),
   enabled TINYINT(1),
   id_company BIGINT,
   PRIMARY KEY(id),
   FOREIGN KEY(id_company) REFERENCES Company(id_company)
);

CREATE TABLE Report (
   id BIGINT AUTO_INCREMENT,
   date_ DATETIME,
   dataB64 TEXT,
   id_agent BIGINT NOT NULL,
   id_company BIGINT NOT NULL,
   PRIMARY KEY(id),
   FOREIGN KEY(id_agent) REFERENCES Agent(id_agent),
   FOREIGN KEY(id_company) REFERENCES Company(id_company)
);
