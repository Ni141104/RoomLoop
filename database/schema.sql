CREATE DATABASE IF NOT EXISTS `roomloop`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE `roomloop`;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `bookings`;
DROP TABLE IF EXISTS `recurring_series`;
DROP TABLE IF EXISTS `rooms`;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `rooms` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `capacity` INT NOT NULL,
  `timezone` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `recurring_series` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `room_id` INT NOT NULL,
  `user` VARCHAR(255) NOT NULL,
  `repeat_weekday` TINYINT NOT NULL,
  `repeat_until` DATE NOT NULL,
  `start_time` TIME NOT NULL,
  `end_time` TIME NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_recurring_series_room`
    FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`),
  CONSTRAINT `chk_recurring_series_weekday`
    CHECK (`repeat_weekday` BETWEEN 0 AND 6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `bookings` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `room_id` INT NOT NULL,
  `recurring_series_id` INT NULL,
  `user` VARCHAR(255) NOT NULL,
  `start_time` DATETIME NOT NULL,
  `end_time` DATETIME NOT NULL,
  `status` VARCHAR(20) NOT NULL DEFAULT 'active',
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_bookings_room`
    FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`),
  CONSTRAINT `fk_bookings_recurring_series`
    FOREIGN KEY (`recurring_series_id`) REFERENCES `recurring_series` (`id`),
  CONSTRAINT `chk_bookings_time_order`
    CHECK (`start_time` < `end_time`),
  CONSTRAINT `chk_bookings_status`
    CHECK (`status` IN ('active', 'cancelled')),
  INDEX `idx_bookings_room_start_end` (`room_id`, `start_time`, `end_time`),
  INDEX `idx_bookings_recurring_series_id` (`recurring_series_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;