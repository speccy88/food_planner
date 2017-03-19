from django.db import models

class Ingredient(models.Model):
	ingredient_name = models.CharField(max_length=200)
	
	def __str__(self):
		return self.ingredient_name
	
class RecipeIngredient(models.Model):
	recipe = models.ForeignKey('Recipe')
	ingredient = models.ForeignKey('Ingredient')
	quantity = models.IntegerField(default=1)
	
	def __str__(self):
		return str(self.recipe)+' : '+str(self.ingredient)+' ('+str(self.quantity)+')'
	
class Recipe(models.Model):
	recipe_name = models.CharField(max_length=200)
	breakfast = models.BooleanField(default=False)
	lunch = models.BooleanField(default=True)
	dinner = models.BooleanField(default=True)
	sunday = models.BooleanField(default=True)
	monday = models.BooleanField(default=True)
	tuesday = models.BooleanField(default=True)
	wednesday = models.BooleanField(default=True)
	thursday = models.BooleanField(default=True)
	friday = models.BooleanField(default=True)
	generate_lunch = models.BooleanField(default=True)
	quick_preparation = models.BooleanField(default=False)
	long_preparation = models.BooleanField(default=False)
	ingredients = models.ManyToManyField(Ingredient, through=RecipeIngredient)
	
	
	def __str__(self):
		return self.recipe_name