
CREATE VIRTUAL TABLE IF NOT EXISTS RecipeSearch
    USING FTS5(name, author, tags, categories)
;

CREATE VIRTUAL TABLE IF NOT EXISTS IngredientSearch
    USING FTS5(name, ingredient)
;

CREATE TABLE IF NOT EXISTS Recipes (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
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
	id INT, 
	CONSTRAINT fk_ingredients
		FOREIGN KEY(recipe_id)
		REFERENCES Recipes(id)
		ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS NamedIngredients (
	recipe_id INTEGER,
	alt_name TEXT,
	ingredient_str TEXT,
	FOREIGN KEY(recipe_id)
	REFERENCES Recipes(id)
);

CREATE TABLE IF NOT EXISTS Ingredients (
	recipe_id INTEGER,
	step TEXT,
	FOREIGN KEY(recipe_id) 
	REFERENCES Recipes(id)
);

CREATE TABLE IF NOT EXISTS IngredientSizes (
	recipe_id INTEGER,
	step TEXT,
	FOREIGN KEY(recipe_id) 
	REFERENCES Recipes(id)
);

CREATE TABLE IF NOT EXISTS IngredientAmounts (
	recipe_id INTEGER,
	step TEXT,
	FOREIGN KEY(recipe_id) 
	REFERENCES Recipes(id)
);

CREATE TABLE IF NOT EXISTS Units (
	recipe_id INTEGER,
	step TEXT,
	FOREIGN KEY(recipe_id) 
	REFERENCES Recipes(id)
);

CREATE TABLE IF NOT EXISTS IngredientNotes (
	recipe_id INTEGER,
	step TEXT,
	FOREIGN KEY(recipe_id) 
	REFERENCES Recipes(id)
);

CREATE TABLE IF NOT EXISTS DishTypes (
	recipe_id INTEGER,
	step TEXT,
	FOREIGN KEY(recipe_id) 
	REFERENCES Recipes(id)
);

CREATE TABLE IF NOT EXISTS Category (
	recipe_id INTEGER,
	step TEXT,
	FOREIGN KEY(recipe_id) 
	REFERENCES Recipes(id)
);

CREATE TABLE IF NOT EXISTS RecipeSteps (
	recipe_id INTEGER,
	step TEXT,
	FOREIGN KEY(recipe_id) 
	REFERENCES Recipes(id)
);
