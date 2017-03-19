# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse

from food_planner_app.models import Recipe

def index(request):
	recipes = Recipe.objects.all()
	print(recipes[0])


	ingredient_list = [{"name":"ingredient test","quantity":"3"}]*25	
	example = (recipes[2].recipe_name,recipes[3].recipe_name,recipes[0].recipe_name)
	daily_meals = [
		("Lundi", example),
		("Mardi", example),
		("Mercredi", example),
		("Jeudi", example),
		("Vendredi", example),
	]
	
	
	
	context = {"ingredient_list": ingredient_list, "daily_meals": daily_meals}
	return render(request, 'index.html', context)