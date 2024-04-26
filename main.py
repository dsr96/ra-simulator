import numpy as np
import matplotlib.pyplot as plt
import random
import pandas as pd

N_ITERATIONS = 1000  # Number of iterations for each N_DEVICE variable
N_PREAMBLES = 60  # Number of preambles available for Contention-RA
N_DEVICES = 1000  # Number of devices from 1 to N_DEVICES to iterate
N_ARRAY_DEVICES = [250, 500, 1000]  # Number of devices to iterate. Only the these values, not continuous
N_SIM_TIME = 1  # Simulation time in seconds
N_PREAMBLE_TRANS_MAX = 10  # Number of preambleTransMax. For a value lower than this, the device can make
                           # a preamble retransmission
N_BACKOFF = 20  # Backoff time in ms for another random access attempt
ALWAYS_TRANSMIT = 1  # All devices transmit a RA preamble at the start

RAR_WINDOW = 5  # Value in ms to receive RAR - 5 Sub-frames
N_FRAMES = 1000  # Simulation time in radio frames

class DeviceNode:

    def __init__(self):
        self.transmit = 0
        self.preambleSelected = 0
        self.preambleCollision = 0
        self.preambleTransMax = 0
        self.rarWindow = 0
        self.backoff = 0
        self.finish = 0
        self.frame = 0  # Subframe when finish = 1 to compute average delay
        self.subframe = 0  # Subframe when finish = 1

    def decreaseBackoff(self):
        self.backoff = self.backoff - 1

    def decreaseRarWindow(self):
        self.rarWindow = self.rarWindow - 1

    def incrementPreambleTransMax(self):
        self.preambleTransMax = self.preambleTransMax + 1

    def resetPreambleTransMax(self):
        self.preambleTransMax = 0

    def setBackoffRAO(self, backoff):
        self.backoff = backoff

    def setRARWindow(self, rarWindow):
        self.rarWindow = rarWindow


def run_preambles(i, N):
    random.seed(i)
    # Create instances of DeviceNodes (0 to N - 1)
    list_nodes = [DeviceNode() for _ in range(N)]

    # Variables to compute
    device_collisions_in_rao = [0] * N_RAO
    probability_device_collisions_in_rao = [0] * N_RAO
    preamble_collisions_in_rao = [0] * N_RAO
    probability_preamble_collisions_in_rao = [0] * N_RAO
    transmitted_devices_in_rao = [0] * N_RAO
    remaining_devices = N
    preamble_trans_max_devices = 0
    number_of_preamble_retransmissions = 0
    delay = []

    rao = 0

    # loop for each frame (1 frame is 10 ms)
    for frame in range(N_FRAMES):
        if remaining_devices == 0:
            # print(remaining_devices)
            break
        for subframe in range(0, 10):  # 1 subframe is 1 ms
            # statement for PRACH Configuration Index 0 (only even frames have RAO)
            if configuration_index == 0:
                if frame % 2 == 0 and PRACH_CONFIGURATION_INDEX.count(subframe) == 1:

                    device_collisions_in_rao[rao] = 0
                    preamble_collisions_in_rao[rao] = 0
                    transmitted_devices_in_rao[rao] = 0
                    list_preambles = [0] * N_PREAMBLES  # stores a list of preambles used in this rao

                    # If all devices transmitted RA successfully, exit from for loop
                    if remaining_devices == 0:
                        break

                    # Preamble selection for each device
                    for device in range(N):
                        # at the start, all devices have the possibility to transmit a preamble
                        # if one device transmit successfully without collision, then
                        # it does not transmit until a period of backoff
                        if list_nodes[device].rarWindow == 0 and list_nodes[device].backoff == 0 \
                                and list_nodes[device].finish == 0 \
                                and list_nodes[device].preambleTransMax < N_PREAMBLE_TRANS_MAX + 1:

                            # For retransmission attempts, always transmit
                            if list_nodes[device].preambleCollision == 1:
                                list_nodes[device].transmit = 1
                                list_nodes[device].preambleCollision = 0
                            else:
                                # Each device decides if transmits preamble
                                if ALWAYS_TRANSMIT == 0:
                                    list_nodes[device].transmit = random.randint(0, 1)
                                else:
                                    list_nodes[device].transmit = 1

                            if list_nodes[device].transmit == 1:
                                # Select a randomly preamble
                                preamble = random.randint(0, N_PREAMBLES - 1)
                                list_nodes[device].preambleSelected = preamble
                                list_preambles[preamble] = list_preambles[preamble] + 1

                    # Count the preamble collisions after all devices have selected a preamble
                    for device in range(N):
                        if list_nodes[device].transmit == 1:
                            transmitted_devices_in_rao[rao] = transmitted_devices_in_rao[rao] + 1
                            # If preamble list count is one for the preamble selected
                            # then no collision
                            if list_preambles[list_nodes[device].preambleSelected] == 1:
                                list_nodes[device].preambleCollision = 0
                                # Count the number of preamble_retransmission that made this device
                                # to obtain later the average value
                                number_of_preamble_retransmissions = number_of_preamble_retransmissions + \
                                                                     list_nodes[device].preambleTransMax
                                # print (list_nodes[device].preambleTransMax)
                                list_nodes[device].resetPreambleTransMax()
                                # In this version, only one successful RA
                                # is performed per device
                                list_nodes[device].transmit = 0
                                list_nodes[device].finish = 1
                                # Sum of delay values, later it will be divided by
                                # successful devices (N - remaining_devices)
                                # Processing time emulating Msg3 + Msg4 reception - 40 ms
                                if frame == 0:
                                    delay.append(10 + 2*10)
                                else:
                                    delay.append(frame*10 + subframe + 2*10)  # 1 frame is 10 ms
                                remaining_devices = remaining_devices - 1
                            else:
                                list_nodes[device].transmit = 0
                                list_nodes[device].preambleCollision = 1
                                list_nodes[device].incrementPreambleTransMax()
                                # 2 subframes + RAR_WINDOW
                                list_nodes[device].setRARWindow(random.randint(2, RAR_WINDOW))
                                list_nodes[device].setBackoffRAO(random.randint(0, N_BACKOFF))
                                device_collisions_in_rao[rao] = device_collisions_in_rao[rao] + 1

                                if list_nodes[device].preambleTransMax == N_PREAMBLE_TRANS_MAX:
                                    preamble_trans_max_devices = preamble_trans_max_devices + 1

                                # print('Device ' + str(device) + ' with preamble ' + str(
                                # list_nodes[device].preambleSelected) + ' had collision in RAO ' + str(rao))

                    # Compute statistics
                    preamble_collisions_in_rao[rao] = len(list_preambles) - (
                            list_preambles.count(0) + list_preambles.count(1))

                    # Probability collisions
                    if transmitted_devices_in_rao[rao] > 0:
                        probability_device_collisions_in_rao[rao] = device_collisions_in_rao[rao] / \
                                                                    transmitted_devices_in_rao[rao]
                    else:
                        probability_device_collisions_in_rao[rao] = 0
                    probability_preamble_collisions_in_rao[rao] = preamble_collisions_in_rao[rao] / len(list_preambles)

                    # print('Number of transmitted devices in rao ' + str(rao) + ': ' + str(transmitted_devices_in_rao[rao]))
                    # print('Number of preambles with collisions in rao ' + str(rao) + ': ' + str(preamble_collisions_in_rao[rao]))
                    # print('Number of devices with collisions in rao ' + str(rao) + ': ' + str(device_collisions_in_rao[rao]))

                    # print('Remaining devices:', remaining_devices)
                    # print('Devices that achieved preambleTransMax', preamble_trans_max_devices)

                    rao = rao + 1  # Increment RAO

            # Rest of PRACH Configuration index
            else:
                # check if there is a RAO in this subframe for the PRACH CONFIGURATION INDEX configuration selected
                if PRACH_CONFIGURATION_INDEX.count(subframe) == 1:

                    device_collisions_in_rao[rao] = 0
                    preamble_collisions_in_rao[rao] = 0
                    transmitted_devices_in_rao[rao] = 0
                    list_preambles = [0] * N_PREAMBLES  # stores a list of preambles used in this rao

                    # If all devices transmitted RA successfully, exit from for loop
                    if remaining_devices == 0:
                        break

                    # Preamble selection for each device
                    for device in range(N):
                        # at the start, all devices have the possibility to transmit a preamble
                        # if one device transmit successfully without collision, then
                        # it does not transmit until a period of backoff
                        if list_nodes[device].rarWindow == 0 and list_nodes[device].backoff == 0 \
                                and list_nodes[device].finish == 0 \
                                and list_nodes[device].preambleTransMax < N_PREAMBLE_TRANS_MAX + 1:

                            # For retransmission attempts, always transmit
                            if list_nodes[device].preambleCollision == 1:
                                list_nodes[device].transmit = 1
                                list_nodes[device].preambleCollision = 0
                            else:
                                # Each device decides if transmits preamble
                                if ALWAYS_TRANSMIT == 0:
                                    list_nodes[device].transmit = random.randint(0, 1)
                                else:
                                    list_nodes[device].transmit = 1

                            if list_nodes[device].transmit == 1:
                                # Select a randomly preamble
                                preamble = random.randint(0, N_PREAMBLES - 1)
                                list_nodes[device].preambleSelected = preamble
                                list_preambles[preamble] = list_preambles[preamble] + 1

                    # Count the preamble collisions after all devices have selected a preamble
                    for device in range(N):
                        if list_nodes[device].transmit == 1:
                            transmitted_devices_in_rao[rao] = transmitted_devices_in_rao[rao] + 1
                            # If preamble list count is one for the preamble selected
                            # then no collision
                            if list_preambles[list_nodes[device].preambleSelected] == 1:
                                list_nodes[device].preambleCollision = 0
                                # Count the number of preamble_retransmission that made this device
                                # to obtain later the average value
                                number_of_preamble_retransmissions = number_of_preamble_retransmissions + \
                                                                     list_nodes[device].preambleTransMax
                                # print (list_nodes[device].preambleTransMax)
                                list_nodes[device].resetPreambleTransMax()
                                # In this version, only one successful RA
                                # is performed per device
                                list_nodes[device].transmit = 0
                                list_nodes[device].finish = 1
                                # Sum of delay values, later it will be divided by
                                # successful devices (N - remaining_devices)
                                # Processing time emulating Msg3 + Msg4 reception - 40 ms
                                if frame == 0:
                                    delay.append(10 + 2*10)
                                else:
                                    delay.append(frame * 10 + subframe + 2*10)  # 1 frame is 10 ms
                                remaining_devices = remaining_devices - 1
                            else:
                                list_nodes[device].transmit = 0
                                list_nodes[device].preambleCollision = 1
                                list_nodes[device].incrementPreambleTransMax()
                                # 2 subframes + RAR_WINDOW
                                list_nodes[device].setRARWindow(random.randint(2, RAR_WINDOW))
                                list_nodes[device].setBackoffRAO(random.randint(0, N_BACKOFF))
                                device_collisions_in_rao[rao] = device_collisions_in_rao[rao] + 1

                                if list_nodes[device].preambleTransMax == N_PREAMBLE_TRANS_MAX:
                                    preamble_trans_max_devices = preamble_trans_max_devices + 1

                                # print('Device ' + str(device) + ' with preamble ' + str(
                                # list_nodes[device].preambleSelected) + ' had collision in RAO ' + str(rao))

                    # Compute statistics
                    preamble_collisions_in_rao[rao] = len(list_preambles) - (
                            list_preambles.count(0) + list_preambles.count(1))

                    # Probability collisions
                    if transmitted_devices_in_rao[rao] > 0:
                        probability_device_collisions_in_rao[rao] = device_collisions_in_rao[rao] / \
                                                                    transmitted_devices_in_rao[rao]
                    else:
                        probability_device_collisions_in_rao[rao] = 0
                    probability_preamble_collisions_in_rao[rao] = preamble_collisions_in_rao[rao] / len(list_preambles)

                    # print('Number of transmitted devices in rao ' + str(rao) + ': ' + str(transmitted_devices_in_rao[rao]))
                    # print('Number of preambles with collisions in rao ' + str(rao) + ': ' + str(preamble_collisions_in_rao[rao]))
                    # print('Number of devices with collisions in rao ' + str(rao) + ': ' + str(device_collisions_in_rao[rao]))

                    # print('Remaining devices:', remaining_devices)
                    # print('Devices that achieved preambleTransMax', preamble_trans_max_devices)

                    rao = rao + 1  # Increment RAO

            # Decrease RAR window backoff
            for device in range(N):
                if list_nodes[device].rarWindow > 0:
                    list_nodes[device].decreaseRarWindow()

            # Decrease the backoff for the devices
            for device in range(N):
                if list_nodes[device].rarWindow == 0 and list_nodes[device].backoff > 0:
                    list_nodes[device].decreaseBackoff()

    successful_devices = N - remaining_devices
    # print(successful_devices)
    if successful_devices == 0:
        average_number_of_preamble_retransmissions = 0
    else:
        average_number_of_preamble_retransmissions = number_of_preamble_retransmissions / successful_devices
    # print (average_number_of_preamble_retransmissions)

    # Average delay
    avg_delay = np.sum(delay) / successful_devices

    return device_collisions_in_rao, preamble_collisions_in_rao, probability_device_collisions_in_rao, \
           probability_preamble_collisions_in_rao, preamble_trans_max_devices, average_number_of_preamble_retransmissions,\
           avg_delay


def plot_device_collisions(device_collisions_in_rao, N):
    # Plot results
    # fig, ax = plt.subplots()
    plt.figure(0)
    plt.plot(device_collisions_in_rao, label=N)


def plot_preamble_collisions(preamble_collisions_in_rao, N):
    # Plot results
    plt.figure(1)
    plt.plot(preamble_collisions_in_rao, label=N)


def plot_probability_device_collisions(probability_device_collisions_in_rao, N):
    # Plot results
    plt.figure(2)
    plt.plot(probability_device_collisions_in_rao, label=N)


def plot_probability_preamble_collisions(probability_preamble_collisions_in_rao, N):
    # Plot results
    plt.figure(3)
    plt.plot(probability_preamble_collisions_in_rao, label=N)


def plot_preamble_trans_max_devices(prob_preamble_trans_max_devices, lab):
    # Plot results
    plt.figure(4)
    plt.plot(N_ARRAY_DEVICES, prob_preamble_trans_max_devices, marker='o', label=lab)


def plot_average_preamble_retransmissions(average_preamble_retransmissions, lab):
    # Plot results
    plt.figure(5)
    plt.plot(N_ARRAY_DEVICES, average_preamble_retransmissions, marker='o', label=lab)


def plot_average_delay(average_delay, min_delay, max_delay, lab):
    # Plot results
    plt.figure(6)
    lower_error = np.array(average_delay) - np.array(min_delay)
    upper_error = np.array(max_delay) - np.array(average_delay)
    error = [lower_error, upper_error]

    line_style_2_2 = {"linestyle": "-", "linewidth": 2, "markeredgewidth": 2, "elinewidth": 2, "capsize": 3,
                        "fmt": 'o'}
    plt.errorbar(N_ARRAY_DEVICES, average_delay, yerr=error, **line_style_2_2, label=lab)


def configure_figure(ylabel, xlabel, figure, name, legend, xticks, yticks):
    plt.figure(figure)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)

    if legend == 1:
        plt.legend()

    plt.grid()


probability_preamble_trans_max_devices = []
total_average_number_of_preamble_retransmissions = []
total_average_delay = []
total_min_delay = []
total_max_delay = []


def main(N):
    device_collisions = []
    preamble_collisions = []
    probability_device_collisions = []
    probability_preamble_collisions = []
    preamble_trans_max_devices_list = []
    average_number_of_preamble_retransmissions_list = []
    average_delay_list = []

    # Multiple iterations for N devices to obtain statistical results
    for i in range(N_ITERATIONS):
        device_collisions_in_rao, preamble_collisions_in_rao, probability_device_collisions_in_rao, \
        probability_preamble_collisions_in_rao, preamble_trans_max_devices, average_number_of_preamble_retransmissions, \
        average_delay = run_preambles(i, N)

        device_collisions.append(device_collisions_in_rao)
        preamble_collisions.append(preamble_collisions_in_rao)
        probability_device_collisions.append(probability_device_collisions_in_rao)
        probability_preamble_collisions.append(probability_preamble_collisions_in_rao)
        preamble_trans_max_devices_list.append(preamble_trans_max_devices)
        average_number_of_preamble_retransmissions_list.append(average_number_of_preamble_retransmissions)
        average_delay_list.append(average_delay)

    # Calculate average results (iterations) for each component
    device_collisions = (np.sum(device_collisions, axis=0)) / N_ITERATIONS
    preamble_collisions = (np.sum(preamble_collisions, axis=0)) / N_ITERATIONS
    probability_device_collisions = (np.sum(probability_device_collisions, axis=0)) / N_ITERATIONS
    probability_preamble_collisions = (np.sum(probability_preamble_collisions, axis=0)) / N_ITERATIONS
    probability_preamble_trans_max_devices.append((np.sum(preamble_trans_max_devices_list) / N_ITERATIONS) / N)
    total_average_number_of_preamble_retransmissions.append(
        np.sum(average_number_of_preamble_retransmissions_list) / N_ITERATIONS)
    total_average_delay.append(np.sum(average_delay_list) / N_ITERATIONS)
    total_min_delay.append(np.min(average_delay_list))
    total_max_delay.append(np.max(average_delay_list))


if __name__ == '__main__':

    mode = 'ARRAY'  # CONTINUOUS or ARRAY
    label = ''
    configuration_index = 0  # Variable to use when PRACH index 0 is used, to indentify odd and even frames

    for i in range(1, 4):
        match i:
            case 0:
                PRACH_CONFIGURATION_INDEX = [1]  # PRACH Configuration index 0
                label = '1 RA slot every 2 frames'
            case 1:
                PRACH_CONFIGURATION_INDEX = [1]  # PRACH Configuration index 3
                configuration_index = 1  # This variable is not used from this point
                label = '1 RA slot every frame'
            case 2:
                PRACH_CONFIGURATION_INDEX = [1, 6]  # PRACH Configuration index 6
                label = '2 RA slots every frame'
            case 3:
                PRACH_CONFIGURATION_INDEX = [1, 4, 7]  # PRACH Configuration index 9
                label = '3 RA slots every frame'
            case 4:
                PRACH_CONFIGURATION_INDEX = [0, 2, 4, 6, 8]  # PRACH Configuration index 12
                label = '5 RA slots every frame'
            case 5:
                PRACH_CONFIGURATION_INDEX = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]  # PRACH Configuration index 14
                label = '10 RA slots every frame'

        N_RAO = len(PRACH_CONFIGURATION_INDEX) * N_FRAMES  # Number of RAO to simulate
        probability_preamble_trans_max_devices = []
        total_average_number_of_preamble_retransmissions = []
        total_average_delay = []
        total_min_delay = []
        total_max_delay = []

        # Multiple iterations between total devices from 1 to N_DEVICES
        if mode == 'CONTINUOUS':
            for N in range(1, N_DEVICES + 1):
                main(N)
        else:  # ARRAY_DEVICES
            for N in N_ARRAY_DEVICES:
                print(N, i)
                main(N)

        # Blocking probability --> probability that a device
        # reaches the maximum number of transmission attempts
        # and is unable to complete an access process
        plot_preamble_trans_max_devices(probability_preamble_trans_max_devices, label)
        pd.DataFrame(data=probability_preamble_trans_max_devices, index=N_ARRAY_DEVICES).to_csv(
            'blocking-Probability-CI-'+str(i) + '-' + str(N_ITERATIONS) + '.csv', header=False)

        # Average number of preamble retransmissions required to
        # have a successful access request
        plot_average_preamble_retransmissions(total_average_number_of_preamble_retransmissions, label)
        pd.DataFrame(data=total_average_number_of_preamble_retransmissions, index=N_ARRAY_DEVICES).to_csv(
            'avgPreambleRtx-CI-' + str(i) + '-' + str(N_ITERATIONS) + '.csv', header=False)

        # Average access delay
        plot_average_delay(total_average_delay, total_min_delay, total_max_delay, label)
        pd.DataFrame(data=total_average_delay, index=N_ARRAY_DEVICES).to_csv(
            'avgDelay-CI-' + str(i) + '-' + str(N_ITERATIONS) + '.csv', header=False)
        pd.DataFrame(data=total_min_delay, index=N_ARRAY_DEVICES).to_csv(
            'minDelay-CI-' + str(i) + '-' + str(N_ITERATIONS) + '.csv', header=False)
        pd.DataFrame(data=total_max_delay, index=N_ARRAY_DEVICES).to_csv(
            'maxDelay-CI-' + str(i) + '-' + str(N_ITERATIONS) + '.csv', header=False)

    configure_figure('Blocking probability', 'Simultaneous arrivals', 4, 'blocking_probability', 1,
                     N_ARRAY_DEVICES, [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    configure_figure('Average number of preamble retransmissions', 'Simultaneous arrivals', 5, 'avg_preamble_rtx', 1,
                     N_ARRAY_DEVICES, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    configure_figure('Average Access Delay (ms)', 'Simultaneous arrivals', 6, 'avg_access_delay', 1,
                     N_ARRAY_DEVICES, [50, 100, 150, 200, 250, 300, 350])

    plt.show()