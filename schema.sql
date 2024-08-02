CREATE TABLE IF NOT EXISTS visitorsdetail (
    id INT AUTO_INCREMENT PRIMARY KEY,
    borrowernumber INT NOT NULL,
    checkin_time DATETIME,
    checkout_time DATETIME,
    staff_checkin VARCHAR(255) DEFAULT NULL,
    staff_checkout VARCHAR(255) DEFAULT NULL,
    FOREIGN KEY (borrowernumber) REFERENCES koha_library.borrowers(borrowernumber) ON DELETE CASCADE
);
