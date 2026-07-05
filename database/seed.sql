USE `roomloop`;

DELETE FROM `bookings`;
DELETE FROM `recurring_series`;
DELETE FROM `rooms`;

ALTER TABLE `bookings` AUTO_INCREMENT = 1;
ALTER TABLE `recurring_series` AUTO_INCREMENT = 1;
ALTER TABLE `rooms` AUTO_INCREMENT = 1;

INSERT INTO `rooms` (`id`, `name`, `capacity`, `timezone`) VALUES
  (1, 'Aurora', 8, 'Europe/Berlin'),
  (2, 'Summit', 12, 'America/Denver'),
  (3, 'Basalt', 4, 'Europe/Berlin'),
  (4, 'Harbor', 6, 'America/Denver');

INSERT INTO `recurring_series` (`id`, `room_id`, `user`, `repeat_weekday`, `repeat_until`, `start_time`, `end_time`) VALUES
  (1, 1, 'alice', 0, '2026-07-20', '09:00:00', '10:00:00'),
  (2, 2, 'bob', 0, '2026-11-09', '09:00:00', '10:00:00');

INSERT INTO `bookings` (`id`, `room_id`, `recurring_series_id`, `user`, `start_time`, `end_time`, `status`) VALUES
  (1, 1, NULL, 'carol', '2026-07-06 09:00:00', '2026-07-06 10:00:00', 'active'),
  (2, 1, NULL, 'dan', '2026-07-06 10:00:00', '2026-07-06 11:00:00', 'active'),
  (3, 3, NULL, 'erin', '2026-07-07 13:00:00', '2026-07-07 14:00:00', 'active'),
  (4, 3, NULL, 'frank', '2026-07-07 13:30:00', '2026-07-07 14:30:00', 'active'),
  (5, 2, NULL, 'grace', '2026-07-06 15:00:00', '2026-07-06 16:00:00', 'cancelled'),
  (6, 2, NULL, 'hannah', '2026-07-06 16:00:00', '2026-07-06 17:00:00', 'active'),
  (7, 1, 1, 'alice', '2026-06-08 09:00:00', '2026-06-08 10:00:00', 'active'),
  (8, 1, 1, 'alice', '2026-06-15 09:00:00', '2026-06-15 10:00:00', 'active'),
  (9, 1, 1, 'alice', '2026-06-22 09:00:00', '2026-06-22 10:00:00', 'active'),
  (10, 1, 1, 'alice', '2026-06-29 09:00:00', '2026-06-29 10:00:00', 'active'),
  (11, 1, 1, 'alice', '2026-07-06 09:00:00', '2026-07-06 10:00:00', 'active'),
  (12, 1, 1, 'alice', '2026-07-13 09:00:00', '2026-07-13 10:00:00', 'active'),
  (13, 1, 1, 'alice', '2026-07-20 09:00:00', '2026-07-20 10:00:00', 'active'),
  (14, 2, 2, 'bob', '2026-10-26 09:00:00', '2026-10-26 10:00:00', 'active'),
  (15, 2, 2, 'bob', '2026-11-02 09:00:00', '2026-11-02 10:00:00', 'active'),
  (16, 2, 2, 'bob', '2026-11-09 09:00:00', '2026-11-09 10:00:00', 'active');