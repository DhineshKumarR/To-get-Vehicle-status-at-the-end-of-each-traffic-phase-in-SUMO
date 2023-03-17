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

# Define the lanes and phases
lanes = ['lane1', 'lane2', 'lane3', 'lane4']
phases = ['green', 'yellow', 'red']

# Define the traffic light states for each phase
tl_states = {
    'green': 'GGGG',
    'yellow': 'YYYY',
    'red': 'RRRR'
}

# Open a CSV file to write the data
with open('traffic.csv', mode='w', newline='') as csv_file:
    # Create a writer object
    writer = csv.writer(csv_file)

    # Write the header row
    writer.writerow(['Vehicle ID', 'Number of Vehicles', 'Speed', 'Lane', 'Phase'])

    # Loop through the lanes
    for lane in lanes:
        # Get the traffic light definition for the lane
        tl_def = traci.trafficlight.getCompleteRedYellowGreenDefinition(lane)

        # Get the traffic light ID
        tl_id = tl_def._tlid

        # Get the list of traffic light phases
        tl_phases = tl_def._phases

        # Loop through the traffic light phases
        for i, phase in enumerate(tl_phases):
            # Set the traffic light state for the current phase
            traci.trafficlight.setRedYellowGreenState(tl_id, tl_states[phase])

            # Wait for the phase to complete
            while traci.simulation.getMinExpectedNumber() > 0:
                traci.simulationStep()

            # Get the list of vehicle IDs in the lane
            vehicle_ids = traci.lane.getLastStepVehicleIDs(lane)

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
                for tl_elem in root.findall('./intersection/' + lane + '/' + phase + '/tl'):
                    for vehicle_elem in tl_elem.findall('./vehicle'):
                        if vehicle_elem.get('id') == vehicle_id:
                            vehicle_elem.set('num', num_vehicles)
                            vehicle_elem.set('speed', str(speed))

                # Write the data to the CSV file
                writer.writerow([vehicle_id, num_vehicles, speed, lane, phase])

            # Write the updated XML file to disk
            tree.write('traffic.xml')

# Close the CSV file
csv_file.close()

# Stop the SUMO simulation
traci.close()
