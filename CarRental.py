"""Functional Requirements
- Rental system should manage different vehicles across different locations
- User should be able to search vehicle based on date, vehicle preferences
- User should be able to search vehicle based on date, vehicle preferences
- User should be able to pay for the booking
- Rental system should be able to track vehicles
- Rental system should be able to prevent booking conflicts
- Rental system should be able to expand based on different location and vehicles

Entities
Rental System
Reservation
Reservation Manager
vehicle
Rental Stores

Design Patterns

Rental System - Singleton
Payment - Strategy
Rental Pricing - TimeRentalPricing, DistanceBasedPricing - Strategy
BookingStatus, Vehicle Status, Vehicle Type - State Design"""

from enum import Enum
import uuid
from abc import ABC, abstractmethod
import threading

class VehicleStatus(Enum):
    AVAILABLE = 1
    BOOKED = 2
    IN_SERVICE = 3

class VehicleCategory(Enum):
    CAR = 1
    BIKE = 2

class VehicleType(Enum):
    # Cars
    HATCHBACK = 1
    SEDAN = 2
    SUV = 3

    # Bikes
    SCOOTY = 4
    BIKE = 5
    EV = 6

class Vehicle:
    def __init__(self, vehicle_id, vehicle_type, vehicle_category):
        self.vehicle_id = vehicle_id
        self.vehicle_category = vehicle_category
        self.vehicle_type = vehicle_type
        self.vehicle_status = VehicleStatus.AVAILABLE
        self.lock = threading.Lock()

class Car(Vehicle):
    def __init__(self, vehicle_id, vehicle_type):
        super().__init__(vehicle_id, vehicle_type, VehicleCategory.CAR)

class Bike(Vehicle):
    def __init__(self, vehicle_id, vehicle_type):
        super().__init__(vehicle_id, vehicle_type, VehicleCategory.BIKE)

class PricingStrategy(ABC):
    @abstractmethod
    def calculate(self, vehicle, hours):
        pass

class DefaultPricing(PricingStrategy):
    PRICE_MAP = {
        VehicleType.HATCHBACK: 100,
        VehicleType.SEDAN: 150,
        VehicleType.SUV: 200,
        VehicleType.SCOOTY: 40,
        VehicleType.BIKE: 60,
        VehicleType.EV: 80
    }
    def calculate(self, vehicle, hours):
        return self.PRICE_MAP[vehicle.vehicle_type] * hours

class BookingService:
    def __init__(self, vehicles, pricing_strategy):
        self.vehicles = vehicles
        self.pricing_strategy = pricing_strategy
    
    def book(self, user_id, vehicle_id, hours):
        vehicle = self.vehicles[vehicle_id]
        if not vehicle:
            print("Vehicle not found")
            return
        with vehicle.lock:
            if vehicle.vehicle_status != VehicleStatus.AVAILABLE:
                print("Vehicle not available for booking now.")
                return
            price = self.pricing_strategy.calculate(vehicle, hours)
            vehicle.vehicle_status = VehicleStatus.BOOKED
            print(f"Booked Vehicle {vehicle_id} successfully")
            return price

class VehicleRepository:
    def __init__(self):
        self.vehicles = {}
    
    def add_vehicle(self, vehicle):
        self.vehicles[vehicle.vehicle_id] = vehicle
    
    def get_vehicle(self, vehicle_id):
        return self.vehicles.get(vehicle_id)


sedan = Car(1,VehicleType.SEDAN)
suv = Car(2,VehicleType.SUV)
hatchback = Car(3,VehicleType.HATCHBACK)

bike = Bike(4,VehicleType.SCOOTY)
bike2 = Bike(5,VehicleType.EV)

vehicle_repo = VehicleRepository()
vehicle_repo.add_vehicle(sedan)
vehicle_repo.add_vehicle(suv)
vehicle_repo.add_vehicle(hatchback)
vehicle_repo.add_vehicle(bike)
vehicle_repo.add_vehicle(bike2)

vehicles = vehicle_repo.vehicles
print(vehicles)
pricing_strategy = DefaultPricing()
booking1 = BookingService(vehicles, pricing_strategy)
booking1.book(1, sedan.vehicle_id, 12)
booking1.book(2, sedan.vehicle_id, 36)
booking2 = BookingService(vehicles, pricing_strategy)
booking2.book(3, bike.vehicle_id, 24)
booking2.book(4, bike2.vehicle_id, 12)

import threading

def try_booking(user_id, booking_service, vehicle_id, hours):
    try:
        price = booking_service.book(user_id, vehicle_id, hours)
        print(f"User {user_id} booked successfully. Price = {price}")
    except Exception as e:
        print(f"User {user_id} failed: {e}")


vehicle_ids = [1, 2, 3, 4, 5]
threads = []
booking_service = BookingService(vehicles, pricing_strategy)
for i, vid in enumerate(vehicle_ids):
    t = threading.Thread(
        target=try_booking,
        args=(i+1, booking_service, vid, 10)
    )
    threads.append(t)
    t.start()
for t in threads:
    t.join()