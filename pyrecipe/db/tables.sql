
--CREATE VIRTUAL TABLE IF NOT EXISTS RecipeSearch
--    USING FTS5(name, author, tags, categories)
--;

--CREATE VIRTUAL TABLE IF NOT EXISTS IngredientSearch
--    USING FTS5(name, ingredient)
--;

CREATE TABLE IF NOT EXISTS Recipes (
	recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
	recipe_uuid TEXT NOT NULL UNIQUE,
	dish_type TEXT,
	description TEXT,
	name TEXT NOT NULL UNIQUE,
	author TEXT,
	source TEXT,
	tags TEXT,
	categories TEXT,
	price TEXT,
	source_url TEXT
);

CREATE TABLE IF NOT EXISTS RecipeIngredients (
	recipe_ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT, 
	recipe_id INTEGER,
	amount INTEGER,
	unit_id INTEGER,
	ingredient_id INTEGER, 
	ingredient_size_id INTEGER,
	FOREIGN KEY (recipe_id)
	REFERENCES Recipes (recipe_id)
		ON DELETE CASCADE
	FOREIGN KEY (unit_id)
	REFERENCES Units (unit_id)
);

CREATE TABLE IF NOT EXISTS NamedIngredients (
	recipe_id INTEGER,
	alt_name TEXT,
	ingredient_str TEXT,
	FOREIGN KEY (recipe_id)
	REFERENCES Recipes (recipe_id)
		ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Ingredients (
	ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT
);

CREATE TABLE IF NOT EXISTS IngredientSizes (
	ingredient_size_id INTEGER PRIMARY KEY,
	step TEXT
);

CREATE TABLE IF NOT EXISTS Units (
	unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
	step TEXT
);

CREATE TABLE IF NOT EXISTS IngredientNotes (
	recipe_id INTEGER,
	step TEXT,
	FOREIGN KEY (recipe_id) 
	REFERENCES Recipes (recipe_id)
		ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS DishTypes (
	dishtype_id INTEGER PRIMARY KEY AUTOINCREMENT,
	dishtype TEXT
);

CREATE TABLE IF NOT EXISTS Category (
	category_id INTEGER PRIMARY KEY AUTOINCREMENT,
	category TEXT
);

CREATE TABLE IF NOT EXISTS RecipeSteps (
	recipe_id INTEGER,
	step TEXT,
	FOREIGN KEY (recipe_id) 
	REFERENCES Recipes (recipe_id)
		ON DELETE CASCADE
);
