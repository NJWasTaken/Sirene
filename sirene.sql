-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: sirene
-- ------------------------------------------------------
-- Server version	8.0.43

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
-- Table structure for table `award`
--

DROP TABLE IF EXISTS `award`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `award` (
  `AwardID` int NOT NULL AUTO_INCREMENT,
  `AwardName` varchar(255) NOT NULL,
  `AwardCategory` varchar(255) NOT NULL,
  PRIMARY KEY (`AwardID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `award`
--

LOCK TABLES `award` WRITE;
/*!40000 ALTER TABLE `award` DISABLE KEYS */;
INSERT INTO `award` VALUES (1,'Primetime Emmy Award','Outstanding Lead Actor in a Drama Series'),(2,'Academy Award','Best Picture');
/*!40000 ALTER TABLE `award` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `awardwon`
--

DROP TABLE IF EXISTS `awardwon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `awardwon` (
  `AwardWonID` int NOT NULL AUTO_INCREMENT,
  `AwardID` int NOT NULL,
  `MediaID` int NOT NULL,
  `PersonID` int DEFAULT NULL,
  `YearWon` int NOT NULL,
  PRIMARY KEY (`AwardWonID`),
  UNIQUE KEY `AwardID` (`AwardID`,`MediaID`,`PersonID`,`YearWon`),
  KEY `MediaID` (`MediaID`),
  KEY `PersonID` (`PersonID`),
  CONSTRAINT `awardwon_ibfk_1` FOREIGN KEY (`AwardID`) REFERENCES `award` (`AwardID`) ON DELETE CASCADE,
  CONSTRAINT `awardwon_ibfk_2` FOREIGN KEY (`MediaID`) REFERENCES `media` (`MediaID`) ON DELETE CASCADE,
  CONSTRAINT `awardwon_ibfk_3` FOREIGN KEY (`PersonID`) REFERENCES `person` (`PersonID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `awardwon`
--

LOCK TABLES `awardwon` WRITE;
/*!40000 ALTER TABLE `awardwon` DISABLE KEYS */;
INSERT INTO `awardwon` VALUES (1,1,1,2,2014),(2,2,7,NULL,2020);
/*!40000 ALTER TABLE `awardwon` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `episode`
--

DROP TABLE IF EXISTS `episode`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `episode` (
  `EpisodeID` int NOT NULL AUTO_INCREMENT,
  `MediaID` int NOT NULL,
  `SeasonNumber` int DEFAULT NULL,
  `EpisodeNumber` int DEFAULT NULL,
  `Title` varchar(255) DEFAULT NULL,
  `ReleaseDate` date DEFAULT NULL,
  PRIMARY KEY (`EpisodeID`),
  KEY `MediaID` (`MediaID`),
  CONSTRAINT `episode_ibfk_1` FOREIGN KEY (`MediaID`) REFERENCES `media` (`MediaID`) ON DELETE CASCADE,
  CONSTRAINT `episode_ibfk_2` FOREIGN KEY (`MediaID`) REFERENCES `media` (`MediaID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `episode`
--

LOCK TABLES `episode` WRITE;
/*!40000 ALTER TABLE `episode` DISABLE KEYS */;
INSERT INTO `episode` VALUES (1,1,1,1,'Pilot','2008-01-20'),(2,1,1,2,'Cat\'s in the Bag...','2008-01-27'),(3,1,1,3,'...And the Bag\'s in the River','2008-02-10');
/*!40000 ALTER TABLE `episode` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `genre`
--

DROP TABLE IF EXISTS `genre`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `genre` (
  `GenreID` int NOT NULL AUTO_INCREMENT,
  `GenreName` varchar(100) NOT NULL,
  PRIMARY KEY (`GenreID`),
  UNIQUE KEY `GenreName` (`GenreName`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `genre`
--

LOCK TABLES `genre` WRITE;
/*!40000 ALTER TABLE `genre` DISABLE KEYS */;
INSERT INTO `genre` VALUES (5,'Action'),(10,'Adventure'),(4,'Anime'),(11,'Comedy'),(1,'Crime'),(6,'Dark Fantasy'),(2,'Drama'),(7,'Post-apocalyptic'),(9,'Satire'),(8,'Superhero'),(3,'Thriller');
/*!40000 ALTER TABLE `genre` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `media`
--

DROP TABLE IF EXISTS `media`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `media` (
  `MediaID` int NOT NULL AUTO_INCREMENT,
  `Title` varchar(255) NOT NULL,
  `Synopsis` text,
  `MediaType` enum('Movie','TV Show','Anime','Video Game') NOT NULL,
  `ReleaseDate` date DEFAULT NULL,
  `DurationMinutes` int DEFAULT NULL,
  PRIMARY KEY (`MediaID`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `media`
--

LOCK TABLES `media` WRITE;
/*!40000 ALTER TABLE `media` DISABLE KEYS */;
INSERT INTO `media` VALUES (1,'Breaking Bad','A high school chemistry teacher diagnosed with inoperable lung cancer turns to manufacturing and selling methamphetamine in order to secure his family\'s future.','TV Show','2008-01-20',49),(2,'Chainsaw Man ? The Movie: Reze Arc','The story will focus on Denji\'s relationship with Reze, the Bomb Devil hybrid from the Soviet Union.','Movie','2025-01-01',120),(3,'Attack on Titan','After his hometown is destroyed and his mother is killed, young Eren Yeager vows to cleanse the earth of the giant humanoid Titans that have brought humanity to the brink of extinction.','Anime','2013-04-07',24),(4,'Daredevil','A blind lawyer by day, vigilante by night. Matt Murdock fights the crime of New York as Daredevil.','TV Show','2015-04-10',54),(5,'Succession','The Roy family is known for controlling the biggest media and entertainment company in the world. However, their world changes when their father steps down from the company.','TV Show','2018-06-03',60),(6,'One Piece','In a seafaring world, a young pirate captain sets out with his crew to attain the title of Pirate King and discover the mythical treasure known as the \"One Piece.\"','TV Show','2023-08-31',50),(7,'Parasite','Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.','Movie','2019-05-30',132);
/*!40000 ALTER TABLE `media` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `media_genre`
--

DROP TABLE IF EXISTS `media_genre`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `media_genre` (
  `MediaID` int NOT NULL,
  `GenreID` int NOT NULL,
  PRIMARY KEY (`MediaID`,`GenreID`),
  KEY `GenreID` (`GenreID`),
  CONSTRAINT `media_genre_ibfk_1` FOREIGN KEY (`MediaID`) REFERENCES `media` (`MediaID`) ON DELETE CASCADE,
  CONSTRAINT `media_genre_ibfk_2` FOREIGN KEY (`GenreID`) REFERENCES `genre` (`GenreID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `media_genre`
--

LOCK TABLES `media_genre` WRITE;
/*!40000 ALTER TABLE `media_genre` DISABLE KEYS */;
INSERT INTO `media_genre` VALUES (1,1),(4,1),(1,2),(5,2),(7,2),(1,3),(7,3),(2,4),(3,4),(2,5),(3,5),(4,5),(6,5),(2,6),(3,6),(3,7),(4,8),(5,9),(6,10),(6,11),(7,11);
/*!40000 ALTER TABLE `media_genre` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `media_person_role`
--

DROP TABLE IF EXISTS `media_person_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `media_person_role` (
  `MediaID` int NOT NULL,
  `PersonID` int NOT NULL,
  `Role` varchar(100) NOT NULL,
  PRIMARY KEY (`MediaID`,`PersonID`,`Role`),
  KEY `PersonID` (`PersonID`),
  CONSTRAINT `media_person_role_ibfk_1` FOREIGN KEY (`MediaID`) REFERENCES `media` (`MediaID`) ON DELETE CASCADE,
  CONSTRAINT `media_person_role_ibfk_2` FOREIGN KEY (`PersonID`) REFERENCES `person` (`PersonID`) ON DELETE CASCADE,
  CONSTRAINT `media_person_role_ibfk_3` FOREIGN KEY (`MediaID`) REFERENCES `media` (`MediaID`) ON DELETE CASCADE,
  CONSTRAINT `media_person_role_ibfk_4` FOREIGN KEY (`PersonID`) REFERENCES `person` (`PersonID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `media_person_role`
--

LOCK TABLES `media_person_role` WRITE;
/*!40000 ALTER TABLE `media_person_role` DISABLE KEYS */;
INSERT INTO `media_person_role` VALUES (1,1,'Creator'),(1,1,'Director'),(1,2,'Actor'),(1,3,'Actor'),(3,4,'Creator'),(4,5,'Actor'),(5,6,'Creator'),(5,7,'Actor'),(6,8,'Creator'),(6,9,'Actor'),(7,10,'Director'),(7,10,'Writer');
/*!40000 ALTER TABLE `media_person_role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `media_platform`
--

DROP TABLE IF EXISTS `media_platform`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `media_platform` (
  `MediaID` int NOT NULL,
  `PlatformID` int NOT NULL,
  PRIMARY KEY (`MediaID`,`PlatformID`),
  KEY `PlatformID` (`PlatformID`),
  CONSTRAINT `media_platform_ibfk_1` FOREIGN KEY (`MediaID`) REFERENCES `media` (`MediaID`) ON DELETE CASCADE,
  CONSTRAINT `media_platform_ibfk_2` FOREIGN KEY (`PlatformID`) REFERENCES `platform` (`PlatformID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `media_platform`
--

LOCK TABLES `media_platform` WRITE;
/*!40000 ALTER TABLE `media_platform` DISABLE KEYS */;
INSERT INTO `media_platform` VALUES (1,1),(6,1),(3,2),(3,3),(4,4),(5,5),(7,6);
/*!40000 ALTER TABLE `media_platform` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `media_productioncompany`
--

DROP TABLE IF EXISTS `media_productioncompany`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `media_productioncompany` (
  `MediaID` int NOT NULL,
  `CompanyID` int NOT NULL,
  PRIMARY KEY (`MediaID`,`CompanyID`),
  KEY `CompanyID` (`CompanyID`),
  CONSTRAINT `media_productioncompany_ibfk_1` FOREIGN KEY (`MediaID`) REFERENCES `media` (`MediaID`) ON DELETE CASCADE,
  CONSTRAINT `media_productioncompany_ibfk_2` FOREIGN KEY (`CompanyID`) REFERENCES `production_company` (`CompanyID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `media_productioncompany`
--

LOCK TABLES `media_productioncompany` WRITE;
/*!40000 ALTER TABLE `media_productioncompany` DISABLE KEYS */;
INSERT INTO `media_productioncompany` VALUES (1,1),(2,2),(3,2),(3,3),(4,4),(5,5),(6,6),(7,7);
/*!40000 ALTER TABLE `media_productioncompany` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `person`
--

DROP TABLE IF EXISTS `person`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `person` (
  `PersonID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(255) NOT NULL,
  `DateOfBirth` date DEFAULT NULL,
  `Country` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`PersonID`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `person`
--

LOCK TABLES `person` WRITE;
/*!40000 ALTER TABLE `person` DISABLE KEYS */;
INSERT INTO `person` VALUES (1,'Vince Gilligan','1967-02-10','USA'),(2,'Bryan Cranston','1956-03-07','USA'),(3,'Aaron Paul','1979-08-27','USA'),(4,'Hajime Isayama','1986-08-29','Japan'),(5,'Charlie Cox','1982-12-15','UK'),(6,'Jesse Armstrong','1970-12-13','UK'),(7,'Brian Cox','1946-06-01','UK'),(8,'Eiichiro Oda','1975-01-01','Japan'),(9,'Iñaki Godoy','2003-08-25','Mexico'),(10,'Bong Joon-ho','1969-09-14','South Korea');
/*!40000 ALTER TABLE `person` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `platform`
--

DROP TABLE IF EXISTS `platform`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `platform` (
  `PlatformID` int NOT NULL AUTO_INCREMENT,
  `PlatformName` varchar(100) NOT NULL,
  `PlatformType` enum('Streaming','Gaming Console','PC Storefront','Cinema') DEFAULT NULL,
  PRIMARY KEY (`PlatformID`),
  UNIQUE KEY `PlatformName` (`PlatformName`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `platform`
--

LOCK TABLES `platform` WRITE;
/*!40000 ALTER TABLE `platform` DISABLE KEYS */;
INSERT INTO `platform` VALUES (1,'Netflix','Streaming'),(2,'Hulu','Streaming'),(3,'Crunchyroll','Streaming'),(4,'Disney+','Streaming'),(5,'Max','Streaming'),(6,'Cinema','Cinema');
/*!40000 ALTER TABLE `platform` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `production_company`
--

DROP TABLE IF EXISTS `production_company`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `production_company` (
  `CompanyID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(255) NOT NULL,
  `Country` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`CompanyID`),
  UNIQUE KEY `Name` (`Name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `production_company`
--

LOCK TABLES `production_company` WRITE;
/*!40000 ALTER TABLE `production_company` DISABLE KEYS */;
INSERT INTO `production_company` VALUES (1,'Sony Pictures Television','USA'),(2,'MAPPA','Japan'),(3,'Wit Studio','Japan'),(4,'Marvel Television','USA'),(5,'HBO Entertainment','USA'),(6,'Tomorrow Studios','USA'),(7,'Barunson E&A','South Korea');
/*!40000 ALTER TABLE `production_company` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `review`
--

DROP TABLE IF EXISTS `review`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `review` (
  `ReviewID` int NOT NULL AUTO_INCREMENT,
  `UserID` int NOT NULL,
  `MediaID` int NOT NULL,
  `Rating` decimal(3,1) NOT NULL,
  `Comment` text,
  `ReviewDate` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ReviewID`),
  UNIQUE KEY `UserID` (`UserID`,`MediaID`),
  UNIQUE KEY `UserID_2` (`UserID`,`MediaID`),
  KEY `MediaID` (`MediaID`),
  CONSTRAINT `review_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `users` (`UserID`) ON DELETE CASCADE,
  CONSTRAINT `review_ibfk_2` FOREIGN KEY (`MediaID`) REFERENCES `media` (`MediaID`) ON DELETE CASCADE,
  CONSTRAINT `review_ibfk_3` FOREIGN KEY (`UserID`) REFERENCES `users` (`UserID`) ON DELETE CASCADE,
  CONSTRAINT `review_ibfk_4` FOREIGN KEY (`MediaID`) REFERENCES `media` (`MediaID`) ON DELETE CASCADE,
  CONSTRAINT `review_chk_1` CHECK (((`Rating` >= 0) and (`Rating` <= 10)))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `review`
--

LOCK TABLES `review` WRITE;
/*!40000 ALTER TABLE `review` DISABLE KEYS */;
INSERT INTO `review` VALUES (1,1,1,9.5,'One of the greatest TV shows ever made. Incredible writing and acting.','2025-10-15 07:04:18'),(2,3,3,9.0,'A masterpiece of storytelling and animation. The final season was epic!','2025-10-15 07:04:18'),(3,2,5,8.8,'Brilliantly written satire. The characters are awful people, but you can\'t stop watching.','2025-10-15 07:04:18'),(4,1,7,9.2,'A thrilling movie that keeps you on the edge of your seat. A must-watch.','2025-10-15 07:04:18');
/*!40000 ALTER TABLE `review` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `UserID` int NOT NULL AUTO_INCREMENT,
  `Username` varchar(100) NOT NULL,
  `Email` varchar(255) NOT NULL,
  `PasswordHash` varchar(255) NOT NULL,
  `CreatedAt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`UserID`),
  UNIQUE KEY `Username` (`Username`),
  UNIQUE KEY `Email` (`Email`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'moviefanatic','fanatic@email.com','hashed_password_123','2025-10-15 07:03:36'),(2,'serieswatcher','watcher@email.com','hashed_password_456','2025-10-15 07:03:36'),(3,'animeguru','guru@email.com','hashed_password_789','2025-10-15 07:03:36');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-15 12:43:04
