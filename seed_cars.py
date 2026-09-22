import pandas as pd
import os
import json
import random
from datetime import datetime, timedelta
from app import app, db
from models import Car, User

# Create sample users first
def create_sample_users():
    users = [
        {"username": "rohit_sharma", "email": "rohit.sharma@example.com", "password": "password123"},
        {"username": "nikhil_jain", "email": "nikhil.jain@example.com", "password": "password123"},
        {"username": "priya_mehta", "email": "priya.mehta@example.com", "password": "password123"},
        {"username": "admin", "email": "admin@cardealhub.com", "password": "admin123"}
    ]
    
    created_users = []
    for user_data in users:
        # Check if user exists
        existing_user = User.query.filter_by(username=user_data["username"]).first()
        if not existing_user:
            user = User(username=user_data["username"], email=user_data["email"])
            user.set_password(user_data["password"])
            # Set admin flag for admin user
            if user_data["username"] == "admin":
                user.is_admin = True
                user.is_verified = True
            db.session.add(user)
            created_users.append(user)
        elif user_data["username"] == "admin" and not existing_user.is_admin:
            # Ensure existing admin user has admin privileges
            existing_user.is_admin = True
            existing_user.is_verified = True
            db.session.add(existing_user)
            print("Updated admin user with admin privileges")
    
    if created_users:
        db.session.commit()
        print(f"Created {len(created_users)} sample users")
    return User.query.all()

# Sample car data based on the prompt
def create_sample_cars():
    car_listings = [
        {
            "name": "Mahindra Thar LX",
            "company": "Mahindra",
            "year": 2021,
            "price": 1500000,
            "kms_driven": 25000,
            "fuel_type": "Diesel",
            "description": "Single owner, well-maintained Mahindra Thar LX. All service records available. 4WD capability with excellent off-road performance.",
            "image_path": "Mahindra Thar LX.jpg"
        },
        {
            "name": "Toyota Fortuner 2.8 Sigma",
            "company": "Toyota",
            "year": 2020,
            "price": 3500000,
            "kms_driven": 40000,
            "fuel_type": "Diesel",
            "description": "Premium Toyota Fortuner with all bells and whistles. Second owner, regularly serviced at authorized center. Excellent condition.",
            "image_path": "Toyota Fortuner 2.8 Sigma.jpg"
        },
        {
            "name": "Maruti Swift VXi",
            "company": "Maruti",
            "year": 2019,
            "price": 650000,
            "kms_driven": 45000,
            "fuel_type": "Petrol",
            "description": "Well-maintained Swift VXi with excellent mileage. First owner, complete service history available. New tires installed recently.",
            "image_path": "Maruti Swift VXi.jpg"
        },
        {
            "name": "Hyundai Creta SX",
            "company": "Hyundai",
            "year": 2020,
            "price": 1300000,
            "kms_driven": 35000,
            "fuel_type": "Petrol",
            "description": "Premium Hyundai Creta SX variant with sunroof and all features. First owner, complete service history. Excellent condition.",
            "image_path": "Hyundai Creta SX.jpg"
        },
        {
            "name": "Tata Nexon XZ+",
            "company": "Tata",
            "year": 2021,
            "price": 950000,
            "kms_driven": 28000,
            "fuel_type": "Diesel",
            "description": "5-Star safety rated Tata Nexon XZ+ with premium features. First owner, all service records available. Excellent fuel efficiency.",
            "image_path": "Tata Nexon XZ+.jpg"
        },
        {
            "name": "Honda City ZX",
            "company": "Honda",
            "year": 2018,
            "price": 850000,
            "kms_driven": 60000,
            "fuel_type": "Petrol",
            "description": "Sleek Honda City ZX with leather seats and sunroof. Second owner, regularly serviced. Excellent condition with all features working.",
            "image_path": "Honda City ZX.jpg"
        },
        {
            "name": "Kia Seltos HTX",
            "company": "Kia",
            "year": 2020,
            "price": 1400000,
            "kms_driven": 32000,
            "fuel_type": "Diesel",
            "description": "Feature-rich Kia Seltos HTX with connected car technology. First owner, all service history available. Premium condition.",
            "image_path": "Kia Seltos HTX.jpg"
        },
        {
            "name": "Renault Kwid Climber",
            "company": "Renault",
            "year": 2019,
            "price": 450000,
            "kms_driven": 38000,
            "fuel_type": "Petrol",
            "description": "Economical Renault Kwid Climber with excellent mileage. First owner, regularly serviced. Perfect city car with low maintenance.",
            "image_path": "Renault Kwid Climber.jpg"
        },
        {
            "name": "Maruti Baleno Zeta",
            "company": "Maruti",
            "year": 2020,
            "price": 750000,
            "kms_driven": 30000,
            "fuel_type": "Petrol",
            "description": "Premium hatchback Maruti Baleno Zeta with excellent mileage. First owner, all service records available. Great condition.",
            "image_path": "Maruti Baleno Zeta.jpg"
        },
        {
            "name": "MG Hector Sharp",
            "company": "MG",
            "year": 2020,
            "price": 1800000,
            "kms_driven": 35000,
            "fuel_type": "Diesel",
            "description": "Fully loaded MG Hector Sharp with panoramic sunroof and connected features. First owner, complete service history at authorized center.",
            "image_path": "MG Hector Sharp.jpg"
        },
        {
            "name": "Tata Harrier XT+",
            "company": "Tata",
            "year": 2021,
            "price": 1700000,
            "kms_driven": 25000,
            "fuel_type": "Diesel",
            "description": "Stunning Tata Harrier XT+ with panoramic sunroof. First owner, all service records available. Excellent condition with all features.",
            "image_path": "tata_harrier_xm_2019_grey.jpg"
        },
        {
            "name": "Hyundai Venue SX Turbo",
            "company": "Hyundai",
            "year": 2020,
            "price": 950000,
            "kms_driven": 32000,
            "fuel_type": "Petrol",
            "description": "Sporty Hyundai Venue SX Turbo with DCT transmission. First owner, regularly serviced at authorized center. Excellent condition.",
            "image_path": "hyundai_i20_asta_2018_red.jpg"
        }
    ]
    
    # Add default images for cars
    default_images = {
        "Mahindra": "mahindra_default.jpg",
        "Toyota": "toyota_default.jpg",
        "Maruti": "maruti_default.jpg",
        "Hyundai": "hyundai_default.jpg",
        "Tata": "tata_default.jpg",
        "Honda": "honda_default.jpg",
        "Kia": "kia_default.jpg",
        "Renault": "renault_default.jpg",
        "MG": "mg_default.jpg",
        "Ford": "ford_default.jpg",
        "Volkswagen": "volkswagen_default.jpg",
        "Nissan": "nissan_default.jpg",
        "Skoda": "skoda_default.jpg",
        "Jeep": "jeep_default.jpg"
    }
    
    # Ensure car images directory exists
    car_images_dir = os.path.join("static", "images", "cars")
    os.makedirs(car_images_dir, exist_ok=True)
    
    # Generate placeholder images for companies
    for company, image_file in default_images.items():
        image_path = os.path.join(car_images_dir, image_file)
        if not os.path.exists(image_path):
            # Create a simple placeholder text file indicating an image
            with open(image_path, 'w') as f:
                f.write(f"Placeholder for {company} car image")
    
    # Get users
    users = User.query.all()
    if not users:
        print("No users found, creating sample users")
        users = create_sample_users()
    
    # Add car listings to database
    cars_added = 0
    cars_updated = 0
    for car_data in car_listings:
        # Check if car already exists
        existing_car = Car.query.filter_by(
            name=car_data["name"],
            company=car_data["company"],
            year=car_data["year"]
        ).first()
        
        if existing_car:
            # Update existing car image
            car_img_path = car_data["image_path"]
            # Check if the image exists
            image_path = os.path.join(car_images_dir, car_img_path)
            if os.path.exists(image_path):
                existing_car.image_path = car_img_path
                cars_updated += 1
            continue
        
        # Create new car
        car = Car(
            name=car_data["name"],
            company=car_data["company"],
            year=car_data["year"],
            price=car_data["price"],
            kms_driven=car_data["kms_driven"],
            fuel_type=car_data["fuel_type"],
            description=car_data["description"],
            user_id=random.choice(users).id,
            created_at=datetime.now() - timedelta(days=random.randint(1, 30))
        )
        
        # Use default image if specified image doesn't exist
        image_path = os.path.join(car_images_dir, car_data["image_path"])
        if os.path.exists(image_path):
            car.image_path = car_data["image_path"]
        else:
            default_image = default_images.get(car_data["company"], "default_car.jpg")
            car.image_path = default_image
            image_path = os.path.join(car_images_dir, default_image)
            if not os.path.exists(image_path):
                with open(os.path.join(car_images_dir, default_image), 'w') as f:
                    f.write(f"Placeholder for {car_data['company']} car image")
        
        db.session.add(car)
        cars_added += 1
    
    if cars_added > 0 or cars_updated > 0:
        db.session.commit()
        if cars_added > 0:
            print(f"Added {cars_added} cars to the database")
        if cars_updated > 0:
            print(f"Updated {cars_updated} cars with new images")
    else:
        print("No cars added or updated")

if __name__ == "__main__":
    with app.app_context():
        create_sample_users()
        create_sample_cars()