import time as time
import tkinter as tk
from tkinter import simpledialog
from typing import Dict

from src.core.floor import DefaultFloor
from src.core.lift import Lift


class Elevator:
    """Represents a visual elevator object that mirrors a Lift object's state.

    Attributes:
        lift (Lift): The underlying Lift object being visualized
        position (int): Current floor position of the elevator
        people_on_elevator (int): Number of passengers currently in the elevator
    """

    def __init__(self, lift: Lift) -> None:
        """Initializes an Elevator visualization object.

        Args:
            lift (Lift): The Lift object to visualize
        """
        self.lift = lift
        self.position = lift.current_floor
        self.people_on_elevator = lift.lift_queue.check_size()

    def update_people(self) -> None:
        """Updates the count of people in the elevator from the lift queue."""
        self.people_on_elevator = self.lift.lift_queue.check_size()

    def update_location(self) -> None:
        """Updates the elevator's position from the lift's current floor."""
        self.position = self.lift.current_floor


class ElevatorGUI:
    """Manages the graphical interface for visualizing multiple elevators.

    Attributes:
        root (tk.Tk): The root window for the GUI
        floors (Dict[int, DefaultFloor]): Dictionary of floor objects
        num_floors (int): Total number of floors in building
        elevators (Dict[str, Elevator]): Dictionary of elevator visualization objects
        people_per_floor (Dict[int, int]): Number of waiting people on each floor
        canvas (tk.Canvas): Main drawing canvas for visualization
        frame (tk.Frame): Frame containing canvas and scrollbar
        scrollable_frame (tk.Frame): Inner frame for scrollable content
    """

    def __init__(
        self,
        root: tk.Tk,
        num_floors: int,
        lifts: Dict[str, Lift],
        floors: Dict[int, DefaultFloor],
    ) -> None:
        """Initializes the elevator visualization GUI.

        Args:
            root (tk.Tk): The root window for the GUI
            num_floors (int): Total number of floors in building
            lifts (Dict[str, Lift]): Dictionary of lift objects to visualize
            floors (Dict[int, DefaultFloor]): Dictionary of floor objects
        """
        self.root = root
        self.floors = floors
        self.num_floors = num_floors
        self.elevators = {
            lift_name: Elevator(lift) for lift_name, lift in lifts.items()
        }
        self.people_per_floor = {
            floor.floor_number: floor.num_waiting() for floor in floors.values()
        }

        self.create_widgets()
        self.create_control_buttons()
        self.start_time = time.time()

        self.update_display()

    def create_widgets(self) -> None:
        """Creates and configures the GUI widgets including canvas and scrollbar."""
        # Create a frame for the canvas and scrollbar
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas for scrolling
        self.canvas = tk.Canvas(self.frame, bg="#EAEAEA")
        self.scrollbar = tk.Scrollbar(
            self.frame, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Set the window size based on the number of floors and elevators
        self.root.geometry(
            f"1200x{50 + (self.num_floors * 85) + 100}"
        )  # Adjust height for bottom space and top space

    def update_scroll_region(self) -> None:
        """Updates the scrollable region of the canvas to match content size."""
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_elevator_position(self, lift_name: str) -> None:
        """Updates an elevator's visual position based on its lift data.

        Args:
            lift_name (str): Name/identifier of the elevator to update
        """
        elevator = self.elevators.get(lift_name)
        if elevator and elevator.lift:
            elevator.update_location()

    def update_elevator_people(self, lift_name: str) -> None:
        """Updates passenger count display for an elevator.

        Args:
            lift_name (str): Name/identifier of the elevator to update
        """
        self.elevators[lift_name].update_people()

    def update_people_per_floor(self) -> None:
        """Updates the count of waiting people on each floor."""
        self.people_per_floor = {
            floor.floor_number: floor.num_waiting() for floor in self.floors.values()
        }

    def update_display(self) -> None:
        """Redraws the entire visualization including building, shafts, and elevators.

        Clears and redraws:
        - Building outline
        - Elevator shafts
        - Floor indicators
        - Elevator positions
        - Passenger counts
        """
        self.canvas.delete("all")

        building_width = 300
        building_height = self.num_floors * 80
        building_x = 50
        building_y = 50

        # Draw the building outline with a softer color
        self.canvas.create_rectangle(
            building_x,
            building_y,
            building_x + building_width,
            building_y + building_height,
            outline="#333",
            fill="#F0F0F0",
            width=2,
        )

        shaft_width = 100
        spacing = 5
        shaft_top = building_y

        distance_to_first_elevator = 160

        for index, elevator in enumerate(self.elevators.values()):
            shaft_left = (
                building_x
                + building_width
                + distance_to_first_elevator
                + index * (shaft_width + spacing)
            )

            # Draw the elevator shaft with a modern look
            self.canvas.create_rectangle(
                shaft_left,
                shaft_top,
                shaft_left + shaft_width,
                shaft_top + building_height,
                outline="#555",
                fill="#E0E0E0",
                width=2,
            )
            self.canvas.create_text(
                shaft_left + shaft_width / 2,
                shaft_top - 25,
                text=f"{elevator.lift.name.capitalize()}",
                font=("Arial", 16, "bold"),
                fill="#222",
            )

            for i in self.people_per_floor.keys():
                y = (
                    shaft_top + (self.num_floors - i) * 80
                )  # Adjusted for smoother scaling

                # Draw floor rectangles with a light gray color
                self.canvas.create_rectangle(
                    0, y, 500, y + 80, outline="#BBB", fill="#FFFFFF", width=2
                )
                self.canvas.create_text(
                    50, y + 40, text=f"F{i}", font=("Arial", 14, "bold"), fill="#333"
                )

                # Draw the elevator at its current position with a gradient effect
                if i == elevator.position:
                    self.canvas.create_rectangle(
                        shaft_left,
                        y,
                        shaft_left + shaft_width,
                        y + 80,
                        outline="#444",
                        fill="#777",
                        width=2,
                    )
                    self.canvas.create_rectangle(
                        shaft_left + 20,
                        y + 20,
                        shaft_left + shaft_width - 20,
                        y + 60,
                        fill="#999",
                        outline="",
                    )

                    inside_people_text = f"Inside: {elevator.people_on_elevator}"
                    self.canvas.create_text(
                        shaft_left + shaft_width / 2,
                        y + 60,
                        text=inside_people_text,
                        font=("Arial", 14),
                        fill="#FFF",
                    )

                # Display waiting people on each floor with better text alignment
                waiting_people_text = f"Waiting: {self.people_per_floor[i]}"
                self.canvas.create_text(
                    200,
                    y + 40,
                    text=waiting_people_text,
                    font=("Arial", 14),
                    fill="#444",
                )

        stats_x = shaft_left + shaft_width + 250
        stats_y = shaft_top + 50
        total_people_waiting = sum(self.people_per_floor.values())
        total_people_in_elevators = sum(
            elevator.people_on_elevator for elevator in self.elevators.values()
        )
        total_people = total_people_waiting + total_people_in_elevators

        self.canvas.create_text(
            stats_x,
            stats_y,
            text=f"Total Waiting on Floors: {total_people_waiting}",
            font=("Arial", 14, "bold"),
            fill="#222",
        )

        self.canvas.create_text(
            stats_x,
            stats_y + 30,
            text=f"Total In Elevators: {total_people_in_elevators}",
            font=("Arial", 14, "bold"),
            fill="#222",
        )

        self.canvas.create_text(
            stats_x,
            stats_y + 60,
            text=f"Total People: {total_people}",
            font=("Arial", 14, "bold"),
            fill="#222",
        )
        elapsed_time = time.time() - self.start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        elapsed_time_text = f"Elapsed Time: {minutes}m {seconds}s"
        self.canvas.create_text(
            stats_x,
            stats_y + 90,
            text=elapsed_time_text,
            font=("Arial", 14, "bold"),
            fill="#222",
        )

        self.update_scroll_region()

    def create_control_buttons(self) -> None:
        """Creates control buttons for manual elevator control.

        Currently a placeholder for future implementation of:
        - Start/Stop buttons
        - Pause/Resume buttons
        - Speed control
        """
        # PLACEHOLDER FOR PAUSE/RESUME/START/STOP/SPEED SCALING BUTTONS
        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # for index in range(len(self.elevators)):
        #     up_button = tk.Button(button_frame, text=f"Elevator {index + 1} Up", command=lambda i=index: controller.call_elevator_up(i))
        #     down_button = tk.Button(button_frame, text=f"Elevator {index + 1} Down", command=lambda i=index: controller.call_elevator_down(i))
        #     up_button.pack(side=tk.LEFT)
        #     down_button.pack(side=tk.LEFT)


class ElevatorController:
    def __init__(self, elevators, gui):
        self.elevators = elevators
        self.elevator_names = list(self.elevators.keys())
        self.gui = gui  # Reference to the ElevatorGUI to update the display

    def call_elevator_up(self, elevator_index):
        """Calls the move_up method on the specified elevator and updates the display."""
        if 0 <= elevator_index < len(self.elevators):
            elevator_name = self.elevator_names[elevator_index]
            self.elevators[elevator_name].move_up()
            self.gui.update_display()  # Update the GUI after moving the elevator
            return True
        return False

    def call_elevator_down(self, elevator_index):
        """Calls the move_down method on the specified elevator and updates the display."""
        if 0 <= elevator_index < len(self.elevators):
            elevator_name = self.elevator_names[elevator_index]
            self.elevators[elevator_name].move_down()
            self.gui.update_display()  # Update the GUI after moving the elevator
            return True
        return False


# Function to get user input for number of elevators and floors
def get_user_input():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Prompt for number of floors
    num_floors = simpledialog.askinteger(
        "Input", "How many floors?", minvalue=1, maxvalue=20
    )
    if num_floors is None:
        return None, None  # User canceled the input

    # Prompt for number of elevators
    num_elevators = simpledialog.askinteger(
        "Input", "How many elevators?", minvalue=1, maxvalue=10
    )
    if num_elevators is None:
        return None, None  # User canceled the input

    return num_floors, num_elevators
