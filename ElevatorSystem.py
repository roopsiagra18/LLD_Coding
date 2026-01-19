"""Requirements (clarify in interview)
Functional

Multiple elevators
Multiple floors
Requests:
External: floor + direction (UP / DOWN)
Internal: destination floor inside elevator
Elevator moves up / down / idle
Simple scheduling (nearest / direction based)

Non-functional

Scalable (add elevators easily)
Extendable (priority, VIP, maintenance mode)
Thread-safe (later)

Enums

Direction (Up/Down)
ElevatorState (Moving/Idle)

Entities
Elevator Controller
Elevator
User
Floors
Elevator System

Conceptual Class Diagram

ElevatorSystem
   |
   --> ElevatorController
           |
           --> Scheduler
           --> [Elevator]

Elevator
   - current_floor
   - direction
   - state
   - requests (min/max heap)
"""

from enum import Enum
from abc import ABC, abstractmethod
import heapq

class ElevatorState:
    IDLE = 1
    MOVING = 2

class ElevatorDirection:
    UP = 1
    DOWN = -1
    IDLE = 0

class ExternalRequest:
    def __init__(self, floor: int, direction: ElevatorDirection):
        self.floor = floor
        self.direction = direction

class InternalRequest:
    def __init__(self, floor:int):
        self.floor = floor
        

class Elevator:
    def __init__(self, elevator_id, current_floor=0):
        self.elevator_id = elevator_id
        self.current_floor = current_floor
        self.up_requests = []
        self.direction = ElevatorDirection.IDLE
        self.state = ElevatorState.IDLE
        self.down_requests = []
    
    def add_request(self, requested_floor):
        if self.state == ElevatorState.MOVING:
            if self.direction == ElevatorDirection.UP and requested_floor < self.current_floor:
                return
            if self.direction == ElevatorDirection.DOWN and requested_floor > self.current_floor:
                return
        if requested_floor > self.current_floor:
            heapq.heappush(self.up_requests, requested_floor)
        elif requested_floor < self.current_floor:
            heapq.heappush(self.down_requests, -requested_floor)
    
    def step(self):
        if self.up_requests:
            next_floor = heapq.heappop(self.up_requests)
            self.state = ElevatorState.MOVING
            self.direction = ElevatorDirection.UP
        
        elif self.down_requests:
            next_floor = - heapq.heappop(self.down_requests)
            self.state = ElevatorState.MOVING
            self.direction = ElevatorDirection.DOWN
        
        else:
            self.direction = ElevatorDirection.IDLE
            self.state = ElevatorState.IDLE
            return
        
        self.move_to(next_floor)
    
    def move_to(self, floor):
        print(f"Elevator {self.elevator_id} moving from {self.current_floor} to {floor}")
        self.current_floor = floor

class Scheduler:
    def assign_elevator(self, elevators, request):
        best_elevator = None
        min_distance = float('inf')

        for elevator in elevators:
            # Prefer idle elevators or elevators moving in same direction
            if elevator.state != ElevatorState.IDLE and elevator.direction != request.direction:
                continue
            if abs(elevator.current_floor - request.floor) < min_distance:
                min_distance = abs(elevator.current_floor - request.floor)
                best_elevator = elevator
        
        # Fallback: any nearest elevator
        if not best_elevator:
            for elevator in elevators:
                distance = abs(elevator.current_floor - request.floor)
                if distance < min_distance:
                    min_distance = distance
                    best_elevator = elevator

        return best_elevator


class ElevatorController:
    def __init__(self, elevators, scheduler):
        self.elevators = elevators
        self.scheduler = scheduler

    def handle_external_request(self, request: ExternalRequest):
        elevator = self.scheduler.assign_elevator(self.elevators, request)
        elevator.add_request(request.floor)
    
    def handle_internal_request(self, elevator_id: int, floor: int):
        self.elevators[elevator_id].add_request(floor)
    
    def step(self):
        for elevator in self.elevators:
            elevator.step()

class ElevatorSystem:
    def __init__(self, num_elevators):
        self.elevators = [Elevator(i) for i in range(num_elevators)]
        self.controller = ElevatorController(self.elevators, Scheduler())
    
    def request_elevator(self, floor, direction):
        self.controller.handle_external_request(ExternalRequest(floor, direction))
    
    def request_floor(self, elevator_id: int, floor: int):
        self.controller.handle_internal_request(elevator_id, floor)
    
    def step(self):
        self.controller.step()

system = ElevatorSystem(6)
system.request_elevator(7, ElevatorDirection.UP)
system.request_elevator(-3, ElevatorDirection.DOWN)
system.request_floor(1, 8)
for _ in range(6):
    system.step()


    