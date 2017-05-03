#!/usr/bin/python


from collections import deque

from numpy import random
import simpy
import sys
import os

SIM_TIME = 100000


#******************************************************************************
# class representing the shared folders
#******************************************************************************
class SharedFolder(object):
    # cosftructor
    def __init__(self, id):
        self.id = id
        self.my_devices = []

    # fancy printing as string
    def __str__(self):
        return str(self.id)

    # add a device to the list of devices registering this shared folder
    def add_device(self, device):
        self.my_devices.append(device)

#******************************************************************************
# class representing devices
#******************************************************************************
class Device():
    # cosftructor
    def __init__(self, id):
        self.id = id
        self.my_shared_folders = []
        self.online = None
        self.pending_files = []

    # fancy printing as string
    def __str__(self):
        sf_str = ", ".join([str(i) for i in self.my_shared_folders])
        return "Device: " + str(self.id) + ", Shared Folders [" + sf_str + "]"

    # add a shared folder to this device
    def add_shared_folder(self, sf):
        self.my_shared_folders.append(sf)


#******************************************************************************
# Create the synthetic content synchronization network
#******************************************************************************
def generate_network(num_dv, devices, shared_folders):

    # shared folders per device - negative_binomial (s, mu)
    DV_DG = [0.470, 1.119]

    # device per shared folder - negative_binomial (s, mu)
    SF_DG = [0.231, 0.537]

    # derive the expected number of shared folders using the negative_binomials

    # this piece is just converting the parameterization of the
    # negative_binomials from (s, mu) to "p". Then, we use the rate between
    # the means to estimate the expected number of shared folders
    # from the given number of devices

    dv_s = DV_DG[0]
    dv_m = DV_DG[1]
    dv_p = dv_s / (dv_s + dv_m)
    nd = 1 + (dv_s * (1.0 - dv_p) / dv_p)

    sf_s = SF_DG[0]
    sf_m = SF_DG[1]
    sf_p = sf_s / (sf_s + sf_m)
    dn = 1 + (sf_s * (1.0 - sf_p) / sf_p)

    # the number of shared folders is finally derived
    num_sf = int(num_dv * nd / dn)

    # sample the number of devices per shared folder (shared folder degree)
    sf_dgr = [x + 1 for x in random.negative_binomial(sf_s, sf_p, num_sf)]

    # sample the number of shared folders per device (device degree)
    dv_dgr = [x + 1 for x in random.negative_binomial(dv_s, dv_p, num_dv)]

    # create the population of edges leaving shared folders
    l = [i for i, j in enumerate(sf_dgr) for k in range(min(j, num_dv))]
    random.shuffle(l)
    sf_pop = deque(l)

    # create empty shared folders
    for sf_id in range(num_sf):
        shared_folders[sf_id] = SharedFolder(sf_id)

    # first we pick a random shared folder for each device
    for dv_id in range(num_dv):
        devices[dv_id] = Device(dv_id)

        sf_id = sf_pop.pop()
        devices[dv_id].add_shared_folder(shared_folders[sf_id])
        shared_folders[sf_id].add_device(devices[dv_id])

    # then we complement the shared folder degree

    # we skip devices with degree 1 in a first pass, since they just got 1 sf
    r = 1

    # we might have less edges leaving devices than necessary
    while sf_pop:
        # create the population of edges leaving devices
        l = [i for i, j in enumerate(dv_dgr) for k in range(min(j - r, num_sf))]
        random.shuffle(l)
        dv_pop = deque(l)

        # if we need to recreate the population, we use devices w/ degree 1 too
        r = 0

        while sf_pop and dv_pop:
            dv = dv_pop.pop()
            sf = sf_pop.pop()

            # we are lazy and simply skip the unfortunate repetitions
            if not shared_folders[sf] in devices[dv].my_shared_folders:
                devices[dv].add_shared_folder(shared_folders[sf])
                shared_folders[sf].add_device(devices[dv])
            else:
                sf_pop.append(sf)
                

class DeviceLogin(object):

    # constructor
    def __init__(self, environ, mu_intersession, sigma_intersession, mu_sessionduration, sigma_sessionduration):
    
        # the inter-stellar time
        self.mu_intersession = mu_intersession
        self.sigma_intersession = sigma_intersession
        self.mu_sessionduration = mu_sessionduration
        self.sigma_sessionduration = sigma_sessionduration
        self.mu_interupload = 3.748
        self.sigma_interupload = 2.286
        
        # the environment
        self.env = environ
    
    # execute the process
    def arrival_process(self, device_obj):
        while True:
    
            # sample the time to next arrival
            inter_session_time = random.lognormal(self.mu_intersession, self.sigma_intersession)
            folder=random.choice(device_obj.my_shared_folders)
        
            # yield an event to the simulator
            yield self.env.timeout(inter_session_time)
            
            time_start=env.now
            device_obj.online=folder
            #print "Device: " + str(device_obj.id) + " starting session at time " + str(time_start) + " in folder: " + str(folder)

            session_time = random.lognormal(self.mu_sessionduration, self.sigma_sessionduration)
            inter_upload_time = random.lognormal(self.mu_interupload, self.sigma_interupload)
            sum=inter_upload_time
            tot_uploads=0
            while sum<session_time:
                yield self.env.timeout(inter_upload_time)
                time_upload=env.now
                FILE_ID=abs(hash(str(time_upload)))
                print "Upload at time: " + str(time_upload) + " DEVICE: " + str(device_obj.id) + " FILE: " + str(FILE_ID)
                
                for dev in folder.my_devices:
                    if dev != device_obj:
                        dev.pending_files.append(FILE_ID)
                        
                        
                inter_upload_time = random.lognormal(self.mu_interupload, self.sigma_interupload)
                sum=sum+inter_upload_time
                tot_uploads=tot_uploads+1
                 
            yield self.env.timeout(session_time-sum+inter_upload_time)
        
            time_end=env.now
            #print "Device: " + str(device_obj.id) + " ending session at time " + str(time_end) + " in folder: " + str(folder)
            print "Device: " + str(device_obj.id) + " START: " + str(time_start) + " END: " + str(time_end) + " FOLDER: " + str(folder) + " TOT UPLOADS: " + str(tot_uploads)
            device_obj.online=None

"""          
class DeviceSession(object):
    
    def __init__(self, environ, mu_sessionduration, sigma_sessionduration):

        # the session duration time
        self.mu_sessionduration = mu_sessionduration
        self.sigma_sessionduration = sigma_sessionduration
        
        # the environment
        self.env = environ
        
    def session(self, device_obj, folder):
        print "blah"
        
        session_time = random.lognormal(self.mu_sessionduration, self.sigma_sessionduration)
        
        yield self.env.timeout(session_time)
        
        time_now=env.now
        print "Device: " + str(device_obj.id) + " ending session at time " + str(time_now) + " in folder: " + str(folder)
"""    
    
            
#******************************************************************************
# implements the simulation
#******************************************************************************
if __name__ == '__main__':

    # number of devices in the simulation
    NUM_DEV = 10
    mu_intersession=7.971
    sigma_intersession=1.308
    
    mu_sessionduration=8.492
    sigma_sessionduration=1.545
    
    env = simpy.Environment()  
    
    #initializing the device login class
    device_login = DeviceLogin(env, mu_intersession,sigma_intersession, mu_sessionduration, sigma_sessionduration)
    

    # collection of devices
    devices = {}

    # collection of shared folders
    shared_folders = {}

    # create the content sharing network
    generate_network(NUM_DEV, devices, shared_folders)


    # DEBUG: dumping the network
    for dev_id in devices:
        print str(devices[dev_id])
         
    for dev_id in devices:
        env.process(device_login.arrival_process(devices[dev_id]))  
        
    env.run(until=SIM_TIME)
