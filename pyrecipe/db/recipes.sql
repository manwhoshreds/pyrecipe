USE openrecipes;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS recipe_steps;
DROP TABLE IF EXISTS recipes;
DROP TABLE IF EXISTS regions;
DROP TABLE IF EXISTS dish_types;
DROP TABLE IF EXISTS ingredients;
DROP TABLE IF EXISTS recipe_ingredients;
DROP TABLE IF EXISTS recipe_named_ingredients;
DROP TABLE IF EXISTS quantity;
DROP TABLE IF EXISTS units;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;


CREATE TABLE `users` (
	`user_id` INT PRIMARY KEY AUTO_INCREMENT,
	`user_email` VARCHAR(25),
	`user_name` VARCHAR(25),
	`password` VARCHAR(50)
);

CREATE TABLE `dish_types` (
    `id` INT(11) PRIMARY KEY AUTO_INCREMENT,
    `dish_type` VARCHAR(25)
);

CREATE TABLE `regions` (
    `id` INT(11) PRIMARY KEY AUTO_INCREMENT,
    `region_name` VARCHAR(50)
);

CREATE TABLE recipes(
	`id` INT PRIMARY KEY AUTO_INCREMENT,
	`uuid` VARCHAR(36),
    `dish_type` INT(11),
    `region_id` INT(11),
    `recipe_name` VARCHAR(50),
    `author` VARCHAR(50),
	`description` VARCHAR(250),
    `prep_time` INT,
    `cook_time` INT,
	`bake_time` INT,
	UNIQUE (uuid),
	FOREIGN KEY (`dish_type`)
		REFERENCES `dish_types` (`id`),
	FOREIGN KEY (`region_id`)
		REFERENCES `regions` (`id`)
);

CREATE TABLE tags(
    `tag_id` INT PRIMARY KEY AUTO_INCREMENT, 
	`recipe_id` INT,
	`tag` VARCHAR(25),
	FOREIGN KEY (recipe_id)
		REFERENCES recipes(id)
);

	
CREATE TABLE recipe_ingredients(
	`recipe_id` INT(11) NOT NULL,
	`ingredient` VARCHAR(100) NOT NULL,
	FOREIGN KEY (recipe_id)
		REFERENCES recipes(id)
		
);

CREATE TABLE recipe_named_ingredients(
	`recipe_id` INT(11) NOT NULL,
	`name` VARCHAR(25) NOT NULL,
	`ingredient` VARCHAR(100) NOT NULL,
	FOREIGN KEY (recipe_id)
		REFERENCES recipes(id)
		
);

CREATE TABLE recipe_steps(
    `recipe_id` INT(11) NOT NULL,
    `step` VARCHAR(1000) NOT NULL,
	`note` VARCHAR(200),
	FOREIGN KEY (recipe_id)
		REFERENCES recipes(id)
);

--
-- insert data
--

INSERT INTO `dish_types` VALUES
(1, 'main'),
(2, 'salad dressing'),
(3, 'dip'),
(4, 'base'),
(5, 'sauce'),
(6, 'side'),
(7, 'dessert'),
(8, 'seasoning'),
(9, 'condiment'),
(10, 'prep'),
(11, 'garnish');

INSERT INTO `regions` VALUES
(1, 'south louisiana');

INSERT INTO `users` VALUES
(1, 'm.k.miller@gmx.com', 'manwhoshreds', '2389423849234234');

-- vim: syntax=sql
