from django.contrib import admin

from .models import Recipe, Ingredient, RecipeIngredient

class RecipeIngredientInline(admin.TabularInline):
	model = RecipeIngredient
	extra = 2
	
class RecipeAdmin(admin.ModelAdmin):
	inlines = (RecipeIngredientInline,)

admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient)