-- ============================================================
--  PARTIE 1 – Gestion des Jurys de Soutenances
--  Script de création des tables (MySQL)
-- ============================================================

CREATE DATABASE IF NOT EXISTS jury_soutenances CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE jury_soutenances;

-- ─────────────────────────────────────────
--  TABLE : SESSION
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS session (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    libelle     VARCHAR(100) NOT NULL,
    date_debut  DATE         NOT NULL,
    date_fin    DATE         NOT NULL,
    statut      ENUM('ouverte','planifiee','terminee') NOT NULL DEFAULT 'ouverte',
    CONSTRAINT chk_session_dates CHECK (date_fin >= date_debut)
) ENGINE=InnoDB;

-- ─────────────────────────────────────────
--  TABLE : ENSEIGNANT
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS enseignant (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nom         VARCHAR(100) NOT NULL,
    prenom      VARCHAR(100) NOT NULL,
    email       VARCHAR(150) NOT NULL UNIQUE,
    grade       VARCHAR(50)  NOT NULL,
    specialite  VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

-- ─────────────────────────────────────────
--  TABLE : DISPONIBILITE
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS disponibilite (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    enseignant_id   INT  NOT NULL,
    session_id      INT  NOT NULL,
    jour            DATE NOT NULL,
    heure_debut     TIME NOT NULL,
    heure_fin       TIME NOT NULL,
    CONSTRAINT fk_dispo_enseignant FOREIGN KEY (enseignant_id) REFERENCES enseignant(id) ON DELETE CASCADE,
    CONSTRAINT fk_dispo_session    FOREIGN KEY (session_id)    REFERENCES session(id)    ON DELETE CASCADE,
    CONSTRAINT chk_dispo_heures    CHECK (heure_fin > heure_debut)
) ENGINE=InnoDB;

-- ─────────────────────────────────────────
--  TABLE : ETUDIANT
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS etudiant (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    matricule   VARCHAR(20)  NOT NULL UNIQUE,
    nom         VARCHAR(100) NOT NULL,
    prenom      VARCHAR(100) NOT NULL,
    filiere     VARCHAR(80)  NOT NULL,
    niveau      VARCHAR(20)  NOT NULL
) ENGINE=InnoDB;

-- ─────────────────────────────────────────
--  TABLE : MEMOIRE
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS memoire (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    etudiant_id INT          NOT NULL,
    session_id  INT          NOT NULL,
    titre       VARCHAR(255) NOT NULL,
    type        VARCHAR(50)  NOT NULL,
    fichier_url VARCHAR(255) DEFAULT NULL,
    statut      ENUM('soumis','valide','rejete') NOT NULL DEFAULT 'soumis',
    CONSTRAINT fk_memoire_etudiant FOREIGN KEY (etudiant_id) REFERENCES etudiant(id) ON DELETE CASCADE,
    CONSTRAINT fk_memoire_session  FOREIGN KEY (session_id)  REFERENCES session(id)  ON DELETE CASCADE
) ENGINE=InnoDB;

-- ─────────────────────────────────────────
--  TABLE : SALLE
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS salle (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nom         VARCHAR(50) NOT NULL,
    capacite    INT         NOT NULL CHECK (capacite > 0),
    batiment    VARCHAR(80) NOT NULL,
    disponible  BOOLEAN     NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

-- ─────────────────────────────────────────
--  DONNÉES DE TEST
-- ─────────────────────────────────────────
INSERT INTO session (libelle, date_debut, date_fin, statut) VALUES
    ('Session Juin 2025',       '2025-06-01', '2025-06-30', 'ouverte'),
    ('Session Septembre 2025',  '2025-09-01', '2025-09-30', 'ouverte');

INSERT INTO enseignant (nom, prenom, email, grade, specialite) VALUES
    ('Ouédraogo', 'Moussa',  'moussa.ouedraogo@univ.bf', 'Professeur',        'Informatique'),
    ('Traoré',    'Aminata', 'aminata.traore@univ.bf',   'Maître de conf.',   'Génie Logiciel'),
    ('Kaboré',    'Issouf',  'issouf.kabore@univ.bf',    'Maître Assistant',  'Réseaux');

INSERT INTO salle (nom, capacite, batiment, disponible) VALUES
    ('Salle A',   30, 'Bloc Informatique', TRUE),
    ('Salle B',   25, 'Bloc Informatique', TRUE),
    ('Amphi 200', 200, 'Bâtiment Principal', TRUE);

INSERT INTO etudiant (matricule, nom, prenom, filiere, niveau) VALUES
    ('INF2025001', 'Sawadogo', 'Jean',    'Informatique', 'Master 2'),
    ('INF2025002', 'Zongo',    'Fatima',  'Informatique', 'Master 2'),
    ('GC2025001',  'Compaoré', 'Ibrahim', 'Génie Civil',  'Licence 3');
