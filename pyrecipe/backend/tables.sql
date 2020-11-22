
--CREATE VIRTUAL TABLE IF NOT EXISTS RecipeSearch
--    USING FTS5(name, author, tags, categories)
--;

--CREATE VIRTUAL TABLE IF NOT EXISTS IngredientSearch
--    USING FTS5(name, ingredient)
--;

CREATE TABLE IF NOT EXISTS Recipes (
	recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
	uuid TEXT NOT NULL UNIQUE,
	dish_type TEXT,
	name TEXT NOT NULL UNIQUE,
	author TEXT,
	source_url TEXT,
	prep_time INTEGER,
	cook_time INTEGER
);

CREATE TABLE IF NOT EXISTS RecipeIngredients (
	recipe_ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT, 
	recipe_id INTEGER,
	group_id INTEGER,
	amount TEXT,
	portion_id INTEGER,
	size_id INTEGER,
	unit_id INTEGER,
	ingredient_id INTEGER,
	prep_id INTEGER,
	CONSTRAINT fk_recipes
		FOREIGN KEY(recipe_id) 
		REFERENCES Recipes(recipe_id)
		ON DELETE CASCADE
	FOREIGN KEY(portion_id) REFERENCES IngredientPortions(id)
	FOREIGN KEY(size_id) REFERENCES IngredientSizes(id)
	FOREIGN KEY(unit_id) REFERENCES Units(id)
	FOREIGN KEY(ingredient_id) REFERENCES Ingredients(id)
	FOREIGN KEY(prep_id) REFERENCES IngredientPrep(id)
	FOREIGN KEY(group_id) REFERENCES IngredientGroups(id)
);

CREATE TABLE IF NOT EXISTS Ingredients (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS IngredientGroups (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	group_name TEXT UNIQUE
);

		
CREATE TABLE IF NOT EXISTS IngredientPortions (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	portion TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS IngredientSizes (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	ingredient_size TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS Units (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	unit TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS IngredientPrep (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	prep TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS IngredientNotes (
	recipe_id INTEGER,
	step TEXT,
	FOREIGN KEY(recipe_id) REFERENCES Recipes(recipe_id)
);

CREATE TABLE IF NOT EXISTS DishTypes (
	dishtype_id INTEGER PRIMARY KEY AUTOINCREMENT,
	dishtype TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS Category (
	category_id INTEGER PRIMARY KEY AUTOINCREMENT,
	category TEXT
);

CREATE TABLE IF NOT EXISTS RecipeSteps (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	recipe_id INTEGER,
	step TEXT,
	FOREIGN KEY(recipe_id) REFERENCES Recipes(recipe_id)
		ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS RecipeNotes (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	recipe_id INTEGER,
	note TEXT,
	FOREIGN KEY(recipe_id) REFERENCES Recipes(recipe_id)
		ON DELETE CASCADE
);
