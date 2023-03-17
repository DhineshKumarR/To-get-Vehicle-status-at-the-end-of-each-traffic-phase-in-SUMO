import os
import csv
import time
import xml.etree.ElementTree as ET
import traci

# Start a SUMO simulation
sumoBinary = "sumo"
sumoConfig = "traffic.sumocfg"
sumoCmd = [sumoBinary, "-c", sumoConfig]
traci.start(sumoCmd)

# Define the phases
phases = ['phase1', 'phase2', 'phase3', 'phase4']

# Open a CSV file to write the data
with open('traffic.csv', mode='w', newline='') as csv_file:
    # Create a writer object
    writer = csv.writer(csv_file)

    # Write the header row
    writer.writerow(['Vehicle ID', 'Number of Vehicles', 'Speed', 'Phase'])

    # Loop through the phases
    for phase in phases:
        # Set the traffic light phase
        traci.trafficlight.setPhase(phase)

        # Wait for the phase to complete
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()

        # Get the list of vehicle IDs
        vehicle_ids = traci.vehicle.getIDList()

        # Parse the XML file
        tree = ET.parse('traffic.xml')

        # Get the root element
        root = tree.getroot()

        # Loop through the vehicle IDs and retrieve their information
        for vehicle_id in vehicle_ids:
            # Get the number of vehicles and speed
            num_vehicles = traci.vehicle.getParameter(vehicle_id, 'laneChangeModel')
            speed = traci.vehicle.getSpeed(vehicle_id)

            # Update the required elements in the XML file
            for phase_elem in root.findall('./intersection/' + phase):
                for lane_elem in phase_elem.findall('./lane'):
                    for vehicle_elem in lane_elem.findall('./vehicle'):
                        if vehicle_elem.get('id') == vehicle_id:
                            vehicle_elem.set('num', num_vehicles)
                            vehicle_elem.set('speed', str(speed))

            # Write the data to the CSV file
            writer.writerow([vehicle_id, num_vehicles, speed, phase])

        # Write the updated XML file to disk
        tree.write('traffic.xml')

# Close the CSV file
csv_file.close()

# Stop the SUMO simulation
traci.close()
