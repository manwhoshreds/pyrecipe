
--CREATE VIRTUAL TABLE IF NOT EXISTS RecipeSearch
--    USING FTS5(name, author, tags, categories)
--;

--CREATE VIRTUAL TABLE IF NOT EXISTS IngredientSearch
--    USING FTS5(name, ingredient)
--;

CREATE TABLE IF NOT EXISTS Recipes (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	uuid TEXT NOT NULL UNIQUE,
	dish_type TEXT,
	description TEXT,
	name TEXT NOT NULL UNIQUE,
	author TEXT,
	source TEXT,
	tags TEXT,
	categories TEXT,
	price TEXT,
	url TEXT
);

CREATE TABLE IF NOT EXISTS RecipeIngredients (
	recipe_ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT, 
	recipe_id INTEGER,
	amount TEXT,
	size_id INTEGER,
	unit_id INTEGER,
	ingredient_id INTEGER,
	prep_id INTEGER,
	CONSTRAINT fk_recipes
		FOREIGN KEY(recipe_id) 
		REFERENCES Recipes(id)
		ON DELETE CASCADE
	FOREIGN KEY(size_id) REFERENCES IngredientSizes(id)
	FOREIGN KEY(unit_id) REFERENCES Units(id)
	FOREIGN KEY(ingredient_id) REFERENCES Ingredients(id)
	FOREIGN KEY(prep_id) REFERENCES IngredientPrep(id)
);

CREATE TABLE IF NOT EXISTS Ingredients (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS NamedIngredients (
	recipe_ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT, 
	named_ingredient_id INTEGER, 
	recipe_id INTEGER,
	amount TEXT,
	unit_id INTEGER,
	ingredient_id INTEGER, 
	size_id INTEGER,
	prep_id INTEGER,
	FOREIGN KEY(named_ingredient_id) REFERENCES NamedIngredientsNames(id)
	FOREIGN KEY(recipe_id) REFERENCES Recipes(id)
		ON DELETE CASCADE
	FOREIGN KEY(size_id) REFERENCES IngredientSizes(id)
	FOREIGN KEY(unit_id) REFERENCES Units(id)
	FOREIGN KEY(ingredient_id) REFERENCES Ingredients(id)
	FOREIGN KEY(prep_id) REFERENCES IngredientPrep(id)
);

CREATE TABLE IF NOT EXISTS NamedIngredientsNames (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	recipe_id INTEGER,
	alt_name TEXT
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
	FOREIGN KEY(recipe_id) REFERENCES Recipes(id)
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
	FOREIGN KEY(recipe_id) REFERENCES Recipes(id)
		ON DELETE CASCADE
);
