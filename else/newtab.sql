use rec;

CREATE TABLE `news` (
  `id` int(200) unsigned auto_increment primary key,
  `source` varchar(200) COLLATE utf8mb4_bin NOT NULL,
  `title` varchar(2000) COLLATE utf8mb4_bin NOT NULL,
  `content` text COLLATE utf8mb4_bin NOT NULL,
  `keyword` varchar(200) COLLATE utf8mb4_bin NOT NULL,
  `type` varchar(40) COLLATE utf8mb4_bin NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;