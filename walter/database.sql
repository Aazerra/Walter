-- ************************************** `project_tbl`

CREATE TABLE `project_tbl`
(
 `id`       int NOT NULL AUTO_INCREMENT ,
 `name`     nvarchar(45) NOT NULL ,
 `language` nvarchar(30) NOT NULL ,
 `complete` boolean NOT NULL ,

PRIMARY KEY (`id`),
UNIQUE KEY `name` (`name`)
);
