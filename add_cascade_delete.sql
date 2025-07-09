-- Script pour ajouter ON DELETE CASCADE aux contraintes de clé étrangère
-- Exécutez ce script sur votre base de données existante

-- Supprimer les contraintes existantes
ALTER TABLE `Agent` DROP FOREIGN KEY `fk_agent_company`;
ALTER TABLE `Report` DROP FOREIGN KEY `Report_ibfk_1`;
ALTER TABLE `Report` DROP FOREIGN KEY `Report_ibfk_2`;
ALTER TABLE `User_` DROP FOREIGN KEY `User__ibfk_1`;

-- Recréer les contraintes avec ON DELETE CASCADE
ALTER TABLE `Agent` 
ADD CONSTRAINT `fk_agent_company` 
FOREIGN KEY (`id_company`) REFERENCES `Company` (`id_company`) ON DELETE CASCADE;

ALTER TABLE `Report` 
ADD CONSTRAINT `Report_ibfk_1` 
FOREIGN KEY (`id_agent`) REFERENCES `Agent` (`id_agent`) ON DELETE CASCADE;

ALTER TABLE `Report` 
ADD CONSTRAINT `Report_ibfk_2` 
FOREIGN KEY (`id_company`) REFERENCES `Company` (`id_company`) ON DELETE CASCADE;

ALTER TABLE `User_` 
ADD CONSTRAINT `User__ibfk_1` 
FOREIGN KEY (`id_company`) REFERENCES `Company` (`id_company`) ON DELETE CASCADE; 