pyrecipe
########

The python recipe management program
------------------------------------


::
        >>> from pyrecipe.recipe import Recipe
        >>> r = Recipe('pesto')
        >>> r.print_recipe()
        
        [1;36mPesto[m

        Dish Type: sauce
        Prep time: 10 m
        Ready in: 10 m
        [1;37m~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[36m
        Ingredients:[m
        [1;33m3[m ounces parmesan cheese, freshly grated
        [1;33m3[m garlic cloves, peeled
        [1;33m2[m cups fresh basil, tightly packed
        [1;33m1/4[m cup pine nuts
        [1;33m1/2[m teaspoon salt
        [1;33m1/4[m cup olive oil

        [1;37m~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[36m
        Method:[m
        [1;33m1.[m Place cheese and garlic in a food processor and chop for
           about 30 seconds.
        [1;33m2.[m Add remaining ingredients except oil and process unitl
           combined.
        [1;33m3.[m With the machine running, pour oil through feed tube and
           process until smooth.
