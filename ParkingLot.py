from enum import Enum
from abc import ABC, abstractmethod
import uuid
import time
import threading

class SlotStatus(Enum):
    AVAILABLE = 1
    BOOKED = 2

class VehicleCategory(Enum):
    CAR = 1
    BIKE = 2

class Vehicle:
    def __init__(self, vehicle_id, vehicle_type):
        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type

class Car(Vehicle):
    def __init__(self, vehicle_id):
        super().__init__(vehicle_id, VehicleCategory.CAR)

class Bike(Vehicle):
    def __init__(self, vehicle_id):
        super().__init__(vehicle_id, VehicleCategory.BIKE)

class Slot:
    def __init__(self, slot_id, vehicle_type):
        self.slot_id = slot_id
        self.vehicle_type = vehicle_type
        self.slot_status = SlotStatus.AVAILABLE
        self.vehicle = None
        self.lock = threading.Lock()
    
    def park(self, vehicle):
        self.vehicle = vehicle
        self.slot_status = SlotStatus.BOOKED
    
    def unpark(self):
        self.vehicle = None
        self.slot_status = SlotStatus.AVAILABLE

class ParkingFloor:
    def __init__(self, floor_id, slots):
        self.floor_id = floor_id
        self.slots = slots

    def get_free_slot(self, vehicle_type):
        for slot in self.slots:
            if slot.slot_status == SlotStatus.AVAILABLE and slot.vehicle_type == vehicle_type:
                return slot
        return None

class SlotAllocationStrategy(ABC):
    @abstractmethod
    def allocate_slot(self, floors, vehicle_type):
        pass

class NearestSlotAllocationStrategy(SlotAllocationStrategy):
    def allocate_slot(self, floors, vehicle_type):
        for floor in floors:
            for slot in floor.slots:
                if slot.vehicle_type != vehicle_type:
                    continue
                acquired = slot.lock.acquire(blocking=False)
                if not acquired:
                    continue
                if slot.slot_status == SlotStatus.AVAILABLE :
                    print(f"Got free slot {slot.slot_id} on floor {floor.floor_id}")
                    return slot
                slot.lock.release()
        return None

class Ticket:
    def __init__(self, slot, vehicle):
        self.ticket_id = str(uuid.uuid4())
        self.slot = slot
        self.vehicle = vehicle
        self.entry_time = time.time()

class PricingService:
    def calculate_price(self, entry_time, exit_time):
        hours = max(1, (exit_time - entry_time)/3600)
        return hours * 50

class ParkingService:
    def __init__(self, floors, slot_allocation_strategy, pricing_service):
        self.floors = floors
        self.allocation_strategy = slot_allocation_strategy
        self.pricing_service = pricing_service
        self.active_tickets = {}
    
    def park_vehicle(self, vehicle):
        # slot lock is already held here
        slot = self.allocation_strategy.allocate_slot(self.floors, vehicle.vehicle_type)
        if not slot:
            print("No available slot")
            return
        # with slot.lock:
        try:
            if slot.slot_status != SlotStatus.AVAILABLE:
                return None
            slot.park(vehicle)
            ticket = Ticket(slot, vehicle)
            self.active_tickets[ticket.ticket_id] = ticket
            print(f"{vehicle.vehicle_type} with vehicle Number {vehicle.vehicle_id} parked successfully on slot {slot.slot_id}")
            return ticket
        finally:
            slot.lock.release()

    def unpark_vehicle(self, ticket):
        if ticket.ticket_id not in self.active_tickets:
            raise Exception("Invalid or expired ticket")
        slot = ticket.slot
        # with slot.lock:
        slot.lock.acquire()
        try:
            parking_fee = self.pricing_service.calculate_price(ticket.entry_time, time.time())
            ticket.slot.unpark()
            print(f"Parking fee for {ticket.vehicle.vehicle_id} at {ticket.entry_time} is {parking_fee}")
            ticket = self.active_tickets.pop(ticket.ticket_id)
            return parking_fee
        finally:
            slot.lock.release()

"""
I use slot-level locking because a parking slot is the smallest shared mutable resource.

Slot allocation acquires the lock in a non-blocking manner to prevent multiple threads from selecting the same slot.

The lock ownership is intentionally transferred to the parking operation, which completes the booking and releases the lock using a finally block to avoid deadlocks.

Unparking follows the same locking discipline to ensure consistency.
"""

def main():
    car1 = Car("KA-123-456-89")
    car2 = Car("UP-92-123-456")
    car3 = Car("UP-92-123-457")
    car4 = Car("UP-92-123-458")
    bike1 = Bike("KA-987-65-432")
    bike2 = Bike("UP-92-987-65")
    bike3 = Bike("KA-987-65-431")
    bike4 = Bike("UP-92-987-66")
    slot1 = Slot(1,VehicleCategory.CAR)
    slot2 = Slot(2, VehicleCategory.CAR)
    slot3 = Slot(3,VehicleCategory.CAR)
    slot4 = Slot(4, VehicleCategory.BIKE)
    slot5 = Slot(5,VehicleCategory.BIKE)
    slot6 = Slot(6, VehicleCategory.BIKE)
    floor1 = ParkingFloor(1, [slot6,slot3, slot1])
    floor2 = ParkingFloor(2, [slot2,slot4, slot5])
    floors = []
    floors.append(floor1)
    floors.append(floor2)
    slot_allocation_strategy = NearestSlotAllocationStrategy()
    pricing_service = PricingService()
    ps = ParkingService(floors, slot_allocation_strategy, pricing_service)

    ticket1 = ps.park_vehicle(car1)
    ticket2 = ps.park_vehicle(car2)
    ticket3 = ps.park_vehicle(car3)
    ticket4 = ps.park_vehicle(car4)
    fee = ps.unpark_vehicle(ticket1)
    ticket5 = ps.park_vehicle(car4)
    ticket6 = ps.park_vehicle(bike1)
    ticket7 = ps.park_vehicle(bike2)
    ticket8 = ps.park_vehicle(bike3)
    ticket9 = ps.park_vehicle(bike4)
    fee = ps.unpark_vehicle(ticket7)
    ticket10 = ps.park_vehicle(bike4)
main()
            