USE [master];
GO

-- Création du login Externe avec un mot de passe sécurisé
CREATE LOGIN [Externe] WITH PASSWORD = 'Secur3P@ssw0rd!';
GO

-- Attribution du rôle sysadmin pour donner tous les droits
ALTER SERVER ROLE sysadmin ADD MEMBER [Externe];
GO
