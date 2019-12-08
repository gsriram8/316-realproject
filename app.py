import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, current_app
from flask_sqlalchemy import SQLAlchemy

from random import random

app = Flask(__name__)

app.config.from_object('config.DevelopmentConfig')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///data.db")

from models import Restaurant, User, UserReactsTo, AllergyGroups

@app.route("/penis")
def penis():
    return jsonify({"Message":"poop"})

@app.route("/add", methods = ["POST"])
def add_user():
    name=request.args.get('name')
    address=request.args.get('address')
    allergies=request.args.get('allergies')
    try:
        user=User(
            full_name=name,
            address=address
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({"Message":"User added... user id={}".format(user.uid)})
    except Exception as e:
        print(",,")
        db.session.rollback()
        return(str(e))


@app.route("/add/form",methods=['GET', 'POST'])
def add_user_form():
    if request.method == 'POST':

        uid = db.session.query(User).count() + 1 # new uid
        
        # what we get now 
        name = request.form.get('name')
        email = request.form.get('email')
        street_address = request.form.get('address')

        # what we will properly get later
        city = 'Durham'
        state = 'North Carolina'
        password = "CS316Project"
        radius = 5

        user_allergies = request.form.getlist('allergy_groups')
        print(user_allergies)

        try:
            user=User(
            	uid = uid,
    			full_name = name,
        		email = email,
        		street_address = street_address,
        		city = city,
        		state = state,
        		password =  password,
        		radius = radius
            )

            db.session.add(user)
            db.session.commit()

            for allergy in user_allergies:
            	print(uid, allergy)
            	user_reacts_to = UserReactsTo(
            		uid = uid,
            		food_group = allergy
            	)
            	db.session.add(user_reacts_to)
            	db.session.commit()


            ## ADD USER BASED ON INPUT
            ## ADD ALLERGY GROUP BASED ON INPUT

            ## DO QUERY... PASSING IN THE CORRECT USER AND USERREACTSTO COLUMNS
            	## SEQUELIZE

            ## DISLLAY THAT QUERY 
            ## return render_template("query_results.html", title="Results!", restaurants=restaurants)

            ##return "User added... {}, User's Allergy Groups added... {}".format(user.full_name, user_allergies)

            return redirect(url_for('query_result', uid=uid, user_allergies=user_allergies))

        except Exception as e:
        	db.session.rollback()
        	return( str(e) )
    if request.method == 'GET':
        return render_template("add_user.html")

@app.route("/query_result",methods=['GET', 'POST'])
def query_result():
    try:

        uid = request.args['uid']

        sql_query = '''with c1 as 
                        (with r1 as (select restaurants.name, restaurants.restaurant_id, dishcontains.dish_name, ingredientbelongsto.food_group 
                        from userreactsto, restaurants, dishcontains, ingredientbelongsto 
                        where (userreactsto.uid={}) 
                        and restaurants.restaurant_id=dishcontains.restaurant_id 
                        and restaurants.restaurant_id=dishcontains.restaurant_id 
                        and dishcontains.ingredient_name=ingredientbelongsto.ingredient_name
                        and ingredientbelongsto.food_group  = userreactsto.food_group 
                        group by restaurants.name, restaurants.restaurant_id, dishcontains.dish_name, ingredientbelongsto.food_group)
                        select name, restaurant_id, food_group, count(*) 
                        from r1 group by name, restaurant_id, food_group),
                        c2 as (select restaurant_id, count(*) 
                        from dishes group by restaurant_id order by restaurant_id)
                        select c1.name, c1.food_group, cast(c1.count as float)/cast(c2.count as float) as risk_level 
                        from c1,c2 
                        where c1.restaurant_id=c2.restaurant_id order by risk_level desc'''.format(uid)

        restaurants = db.get_engine(current_app).execute(sql_query)
        result = []
        for r in restaurants:
            print(r)
            name = r[0]
            b = r[1]
            c = r[2]
            result.append((name, b, c))
        print (restaurants)
        # return(str(result))

        #restaurants=Restaurant.query.all()
        return render_template("display_restaurants.html", data=restaurants)
    
    except Exception as e:
        return(str(e))


if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run()










