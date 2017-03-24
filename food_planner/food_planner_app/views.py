# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from collections import OrderedDict

from food_planner_app.models import Recipe



def index(request):
    Daily_Meals.create_week()
    Daily_Meals.fill_week()
    recipes = Recipe.objects.all()
    
    print(Daily_Meals["monday"])
    print("-----------!!")
    ingredient_list = []
    for day_object in Daily_Meals:
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
    context = {"ingredient_list": ingredient_list, "daily_meals": list(Daily_Meals), "start_end_days": get_week_info()}
    return render(request, 'index.html', context)

def get_week_info():
    from datetime import datetime, timedelta
    now = datetime.now()
    weekday = now.weekday()
    next_sunday = now + timedelta(days=(6-weekday))
    next_friday = next_sunday + timedelta(days=5)
    return (next_sunday.day, next_friday.day)
    
    
class Week_Days:
    week_days = ("sunday","monday","tuesday","wednesday","thursday","friday")
    def __init__(self, today="sunday"):
        self.today = today
        self.index = self.week_days.index(today)
        self.number_of_days = len(self.week_days)

    def __getitem__(self,val):
        new_index = (val%self.number_of_days) + self.index
        if new_index >= self.number_of_days:
            new_index = new_index - self.number_of_days
        #print((self.index, val, new_index)) #Debug
        return self.week_days[new_index]

    def __iter__(self):
        return iter(self.week_days)
        
class Meta_Daily_Meals(type):
    def __getitem__(cls,val):
        return cls.days[val]
            
    def __iter__(cls):
        return iter(cls.days.values())   
    
class Daily_Meals(metaclass=Meta_Daily_Meals):
    days = OrderedDict()
    
    def __init__(self, day):
        self.day = day
        self.week_days = Week_Days(day)
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
    
    @property
    def next_day(self):
        return Daily_Meals[self.week_days[+1]]
        
    def create_week():
        for day in Week_Days():
            Daily_Meals.days[day] = Daily_Meals(day)
        
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
        for day in Week_Days().week_days[1:-1]: # Monday to Thursday
            print("day = "+day)
            step2_dinner_recipes = Recipe.objects.filter(dinner=True).exclude(id__in=Daily_Meals.used_recipes).order_by('?')
            
            step2_dinner_recipes = step2_dinner_recipes.filter(**{day: True})
            
            if day == "monday" or day == "thursday":
                print("quick prep")
                step2_dinner_recipe = step2_dinner_recipes.filter(quick_preparation=True).first()
            else:
                print("pas quick prep")
                step2_dinner_recipe = step2_dinner_recipes.first()
            
            Daily_Meals.fill_day(day, "dinner", step2_dinner_recipe)
            print(step2_dinner_recipe)
            
            next_day = Daily_Meals[day].next_day
            print("next day = "+str(next_day))
            if step2_dinner_recipe.generate_lunch:
                print("next day lunch generated")
                print(step2_dinner_recipe)
                Daily_Meals.fill_day(next_day, "lunch", step2_dinner_recipe)
            else:
                print("next day lunch not generated")
                step2_lunch_recipes = Recipe.objects.filter(lunch=True).exclude(id__in=Daily_Meals.used_recipes).order_by('?')
                step2_lunch_recipe = step2_lunch_recipes.filter(**{next_day.day: True}).first()
                print(step2_lunch_recipe)
                Daily_Meals.fill_day(next_day, "lunch", step2_lunch_recipes.first())
                
        Daily_Meals.view_week()
        print("Used recipes = "+str(Recipe.objects.filter(id__in=Daily_Meals.used_recipes)))
        
    def view_week():
        for item in Daily_Meals:
            print(item)
            print(type(item))
        print("----------viewer")
        for day in Daily_Meals:
            print(day)
            print(day.breakfast)
            print(day.lunch)
            print(day.dinner)
            print("----")
        
    def fill_day(day, meal, recipe):
        if isinstance(day, str) and (day in Week_Days()):
            day_to_fill = Daily_Meals[day]
        elif isinstance(day, Daily_Meals):
            day_to_fill = day
        else:
            raise Exception('fill_day expect a string with week day or instance of Daily_Meals')
            
        setattr(day_to_fill, meal, recipe)
        Daily_Meals.used_recipes.append(recipe.id)  