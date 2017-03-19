# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse

from food_planner_app.models import Recipe



def index(request):
	Daily_Meals.create_week()
	Daily_Meals.fill_week()
	recipes = Recipe.objects.all()
	
	ingredient_list = []
	for day_object in Daily_Meals.days:
		if day_object.lunch:
			for ingredient in day_object.lunch.recipeingredient_set.all():
				print(str(ingredient.ingredient)+" -- "+str(ingredient.quantity))
				if len(ingredient_list) == 0:
					ingredient_list.append([ingredient.ingredient, ingredient.quantity])
					
				ingredient_found = False
				for item in ingredient_list:
					if ingredient.ingredient == item[0]:
						item[1] = item[1] + ingredient.quantity
						ingredient_found = True
				if not ingredient_found:
					ingredient_list.append([ingredient.ingredient, ingredient.quantity])
		if day_object.dinner:
			for ingredient in day_object.dinner.recipeingredient_set.all():
				print(str(ingredient.ingredient)+" -- "+str(ingredient.quantity))
				if len(ingredient_list) == 0:
					ingredient_list.append([ingredient.ingredient, ingredient.quantity])
					
				ingredient_found = False
				for item in ingredient_list:
					if ingredient.ingredient == item[0]:
						item[1] = item[1] + ingredient.quantity
						ingredient_found = True
				if not ingredient_found:
					ingredient_list.append([ingredient.ingredient, ingredient.quantity])
	print(ingredient_list)
	
	# slow ordering to change asap
	for day_object in Daily_Meals.days:
		if day_object.day == "sunday":
				sunday = day_object
	for day_object in Daily_Meals.days:
		if day_object.day == "monday":
				monday = day_object
	for day_object in Daily_Meals.days:
		if day_object.day == "tuesday":
				tuesday = day_object
	for day_object in Daily_Meals.days:
		if day_object.day == "wednesday":
				wednesday = day_object
	for day_object in Daily_Meals.days:
		if day_object.day == "thursday":
				thursday = day_object
	for day_object in Daily_Meals.days:
		if day_object.day == "friday":
				friday = day_object
	
	daily_meals = (sunday,monday,tuesday,wednesday,thursday,friday)
	
	context = {"ingredient_list": ingredient_list, "daily_meals": daily_meals}
	return render(request, 'index.html', context)


class Daily_Meals():
	days = []
	week_days = ("sunday",
				 "monday",
				 "tuesday",
				 "wednesday",
				 "thursday",
				 "friday")	
			 
	def __init__(self, day, next_day):
		self.day = day
		self.next_day = next_day
		self.breakfast = None
		self.lunch = None
		self.dinner = None

	def __str__(self):
		if self.next_day:
			return self.day+"->"+self.next_day.day
		else:
			return self.day
	
	def __repr__(self):
		return str(self)
			
	def create_week():
		Daily_Meals.days = []
		for day in reversed(Daily_Meals.week_days):
			print(day)
			if day == "friday":
				Daily_Meals.days.append(Daily_Meals(day, None))
			else:
				Daily_Meals.days.append(Daily_Meals(day, Daily_Meals.days[-1]))
		print(Daily_Meals.days)
	
	used_recipes = []
	def fill_week():
		Daily_Meals.used_recipes = []
		# step 1 : fill sunday dinner and monday lunch
		step1_recipe = Recipe.objects.filter(long_preparation=True).order_by('?').first()
		print(step1_recipe)
		Daily_Meals.fill_day("sunday", "dinner", step1_recipe)
		
		if step1_recipe.generate_lunch:
			Daily_Meals.fill_day("monday", "lunch", step1_recipe)
		else:
			step1_recipe = Recipe.objects.filter(lunch=True).exclude(id__in=Daily_Meals.used_recipes).order_by('?').first()
			Daily_Meals.fill_day("monday", "lunch", step1_recipe)
			
		# step 2 : fill sunday dinner and monday lunch
		for day in Daily_Meals.week_days[1:-1]: # Monday to Thursday
			print("day = "+day)
			step2_dinner_recipes = Recipe.objects.filter(dinner=True).exclude(id__in=Daily_Meals.used_recipes).order_by('?')
			if day == "monday":
				step2_dinner_recipes = step2_dinner_recipes.filter(monday=True)
			if day == "tuesday":
				step2_dinner_recipes = step2_dinner_recipes.filter(tuesday=True)
			if day == "wednesday":
				step2_dinner_recipes = step2_dinner_recipes.filter(wednesday=True)
			if day == "thursday":
				step2_dinner_recipes = step2_dinner_recipes.filter(thursday=True)
			if day == "friday":
				step2_dinner_recipes = step2_dinner_recipes.filter(friday=True)
			
			if day == "monday" or day == "thursday":
				print("quick prep")
				step2_dinner_recipe = step2_dinner_recipes.filter(quick_preparation=True).first()
			else:
				print("pas quick prep")
				step2_dinner_recipe = step2_dinner_recipes.first()
			
			Daily_Meals.fill_day(day, "dinner", step2_dinner_recipe)
			print(step2_dinner_recipe)
			
			next_day_index = Daily_Meals.week_days.index(day) + 1
			next_day = Daily_Meals.week_days[next_day_index]
			print("next day = "+next_day)
			if step2_dinner_recipe.generate_lunch:
				print("next day lunch generated")
				print(step2_dinner_recipe)
				Daily_Meals.fill_day(next_day, "lunch", step2_dinner_recipe)
			else:
				print("next day lunch not generated")
				step2_lunch_recipes = Recipe.objects.filter(lunch=True).exclude(id__in=Daily_Meals.used_recipes).order_by('?')
				if next_day == "monday":
					step2_lunch_recipes = step2_lunch_recipes.filter(monday=True)
				if next_day == "tuesday":
					step2_lunch_recipes = step2_lunch_recipes.filter(tuesday=True)
				if next_day == "wednesday":
					step2_lunch_recipes = step2_lunch_recipes.filter(wednesday=True)
				if next_day == "thursday":
					step2_lunch_recipes = step2_lunch_recipes.filter(thursday=True)
				if next_day == "friday":
					step2_lunch_recipes = step2_lunch_recipes.filter(friday=True)
				step2_lunch_recipe = step2_lunch_recipes.first()
				print(step2_lunch_recipe)
				Daily_Meals.fill_day(next_day, "lunch", step2_lunch_recipes.first())
				
		Daily_Meals.view_week()
		print("Used recipes = "+str(Recipe.objects.filter(id__in=Daily_Meals.used_recipes)))
		
	def view_week():
		print("----------viewer")
		for day in Daily_Meals.days:
			print(day.day)
			print(day.breakfast)
			print(day.lunch)
			print(day.dinner)
			print("----")
		
	def fill_day(day, meal, recipe):
		for day_object in Daily_Meals.days:
			if day_object.day == day:
				print("day to fill")
				day_to_fill = day_object
		if meal=="breakfast":
			day_to_fill.breakfast = recipe
		elif meal=="lunch":
			day_to_fill.lunch = recipe
		elif meal=="dinner":
			day_to_fill.dinner = recipe
		else:
			return
		Daily_Meals.used_recipes.append(recipe.id)
		