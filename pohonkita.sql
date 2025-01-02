-- MySQL dump 10.13  Distrib 8.0.35, for Linux (x86_64)
--
-- Host: 127.0.0.1    Database: pohonkita
-- ------------------------------------------------------
-- Server version	8.0.35-0ubuntu0.20.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `activitylog`
--

DROP TABLE IF EXISTS `activitylog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `activitylog` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `action` varchar(255) NOT NULL,
  `timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `activitylog_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activitylog`
--

/*!40000 ALTER TABLE `activitylog` DISABLE KEYS */;
/*!40000 ALTER TABLE `activitylog` ENABLE KEYS */;

--
-- Table structure for table `goal`
--

DROP TABLE IF EXISTS `goal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `goal` (
  `id` int NOT NULL AUTO_INCREMENT,
  `trees_id` int NOT NULL,
  `goal_name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `trees_id` (`trees_id`),
  CONSTRAINT `goal_ibfk_1` FOREIGN KEY (`trees_id`) REFERENCES `tree` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `goal`
--

/*!40000 ALTER TABLE `goal` DISABLE KEYS */;
/*!40000 ALTER TABLE `goal` ENABLE KEYS */;

--
-- Table structure for table `leaderboard`
--

DROP TABLE IF EXISTS `leaderboard`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `leaderboard` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `total_trees` int DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `leaderboard_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `leaderboard`
--

/*!40000 ALTER TABLE `leaderboard` DISABLE KEYS */;
/*!40000 ALTER TABLE `leaderboard` ENABLE KEYS */;

--
-- Table structure for table `submission`
--

DROP TABLE IF EXISTS `submission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `submission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `tree_id` int DEFAULT NULL,
  `full_name` varchar(255) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `planned_planting_date` date DEFAULT NULL,
  `required_seeds` int DEFAULT NULL,
  `supporting_image` varchar(255) DEFAULT NULL,
  `notes` text,
  `status` enum('pending','approved','rejected','banned') DEFAULT 'pending',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `tree_id` (`tree_id`),
  CONSTRAINT `submission_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `submission_ibfk_2` FOREIGN KEY (`tree_id`) REFERENCES `tree` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `submission`
--

/*!40000 ALTER TABLE `submission` DISABLE KEYS */;
INSERT INTO `submission` VALUES (1,NULL,9,'Zakki','Jogja','2025-01-01',20,'Screenshot_from_2024-12-31_15-11-44.png','mantap','approved','2024-12-31 14:37:58','2024-12-31 15:07:54'),(2,5,9,'Haycal Gusti','Bantul','2024-12-31',10,'menanam.jpg','Oke','approved','2024-12-31 14:41:04','2024-12-31 14:41:16'),(3,5,9,'Haycal Gusti','Bantul','2025-03-01',12,'menanam.jpg','','approved','2024-12-31 14:41:58','2024-12-31 14:42:07'),(4,6,10,'Zakki Varian','Jambi','2025-01-02',10,'742dcbb1b494bc96403bb305e3a76048.jpg','','approved','2024-12-31 16:55:36','2024-12-31 16:56:03'),(5,6,9,'Zakki Farian','Jambi','2023-12-12',10,'Screenshot_from_2024-12-31_15-11-44.png','good','approved','2024-12-31 16:58:03','2024-12-31 16:58:26');
/*!40000 ALTER TABLE `submission` ENABLE KEYS */;

--
-- Table structure for table `tree`
--

DROP TABLE IF EXISTS `tree`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tree` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `jenis` varchar(100) DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL,
  `jumlah_bibit` int NOT NULL,
  `rata_rata_tumbuh` varchar(50) DEFAULT NULL,
  `waktu_tumbuh` varchar(50) DEFAULT NULL,
  `manfaat` text,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `tree_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tree`
--

/*!40000 ALTER TABLE `tree` DISABLE KEYS */;
INSERT INTO `tree` VALUES (9,4,'Pohon Jeruk','Pohon Buah','672c61f596704889b3343637ca87fa1b_pohon-jeruk.jpg',230,'5 Meter','2-4 Tahun','Menghasilkan Buah'),(10,4,'Pohon Cemara','Pohon Teduh','8e9418ceb1d84d4aa0f697e413271348_742dcbb1b494bc96403bb305e3a76048.jpg',100,'10 meter','5-10 Tahun','Peneduh');
/*!40000 ALTER TABLE `tree` ENABLE KEYS */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `total_trees` int DEFAULT '0',
  `role` enum('admin','user') DEFAULT 'user',
  `status` enum('active','deactive') DEFAULT 'active',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (4,'admin','admin@mail.com','scrypt:32768:8:1$vEXb24YoPO7vAAGX$71c9dd75ab852650231b0dcc7aec7bd10b478884da6b4f5148d530d990194c8a2f94ee5aaeb51168aac0c09bd0f792a699cba2cebd8a2b4665af6466c4ecd679',0,'admin','active'),(5,'user2','user2@gmail.com','scrypt:32768:8:1$noBojI5sfgnnEQsm$5293b81d50cf308be0b8c2fff93c45bd1125d2aa9abd8dd3d8d59df7cdbbd9e65542f384a5a303d1ac386ee6c94dc203006a876a2ae02097495f281c6a313d63',0,'user','active'),(6,'zakki','zakki@gmail.com','scrypt:32768:8:1$R9BLde2cR72tIHz1$47ca05e77500f1f1628b859fc14598e8c8c5b58d594c66e820d7a58a7956963a14c9ed69d3e36a8e710520f01218350f10f1a3627fc35f3c0617c9184ce930e4',0,'user','active');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;

--
-- Dumping routines for database 'pohonkita'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-02 12:25:14
