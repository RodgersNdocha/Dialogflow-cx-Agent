CREATE TABLE `booking` (
  `phone_number` bigint DEFAULT NULL,
  `booking_date` date DEFAULT NULL,
  `room_type` varchar(255) DEFAULT NULL
);

CREATE TABLE `room_type` (
  `id` varchar(255) DEFAULT NULL,
  `room_type` varchar(255) DEFAULT NULL,
  `num_of_rooms` int DEFAULT NULL
) ;
