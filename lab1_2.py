###############LAB 1 LETTERA a#############

import simpy
import random
#from matplotlib import pyplot
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# **********************************************************************************************************************
# Constants
# **********************************************************************************************************************
RANDOM_SEED = 42
  # TRY WITH OTHER VALUES OF THESE PARAMETERS
					# TRY TO SEE HOW THE RESPONSE TIME CHANGES WITH THE UTILIZATION E[N]=ro/(1-ro) that is the percentage of time
						# in which the server is actually being used
NUM_SERVERS = 1
SIM_TIME = 100000



# **********************************************************************************************************************
# Car arrival
# **********************************************************************************************************************
class RequestArrival(object):
    # constructor
    def __init__(self, environ, LAMBDA):
    
        # the inter-arrival time
        self.LAMBDA = LAMBDA
    
        # the environment
        self.env = environ
        self.n_arrivals = 0

    
    # execute the process
    def arrival_process(self, server):
        while True:
            # sample the time to next arrival
            arrival_time = random.expovariate(lambd=1.0/self.LAMBDA)
            
            batch_size=int(random.uniform(1,5))
            self.n_arrivals=self.n_arrivals+batch_size
            
            # yield an event to the simulator
            yield self.env.timeout(arrival_time)
            
            start = env.now
            # a car has arrived - request server to do its job
            for arrival in range(batch_size):
                self.env.process(server.serve(start))
                

# **********************************************************************************************************************
# Car wash - it gets an waiting car (FCFS) and performs the service
# **********************************************************************************************************************
class Server_1(object):

    # constructor
    def __init__(self, environ, num_servers, MU, capacity, server_2):

		# the service time
        self.MU = MU
        self.capacity = capacity
        self.server_2=server_2
        self.p = 0.2
        
        # the environment
        self.env = environ
        
        # wash machines
        self.machines = simpy.Resource(self.env, num_servers)
        
        # number of cars in the shop
        self.qsize = 0
        
        self.response_time = []
        self.occupancies = []
        self.n_discarded = 0

    def serve(self, start):
    # print("Packets in the server on arrival: ", self.qsize)
    
        if self.qsize<self.capacity:
            
            self.qsize += 1
            self.occupancies.append(self.qsize-1) #to see how many guys are in the queue so the real buffer occupancy
            
            rand=random.uniform(0,1)
            
            if rand<self.p:
                self.env.process(self.server_2.serve(start))
                
            else:
                # request a machine to wash the new coming car
                with self.machines.request() as request:
                	yield request
                
                	# once the machine is free, wait until service is finished
                	service_time = random.expovariate(lambd=1.0/self.MU)
                
                	# yield an event to the simulator
                	yield self.env.timeout(service_time)
                
                	# release the wash machine
                	self.qsize -= 1
                
                	end = self.env.now
                
                	resp_time = end-start
                	#print "response time: " + str(resp_time)
                
                	self.response_time.append(resp_time)
                
    
        else:
            # discard packet
            self.n_discarded=self.n_discarded+1
    
    # the "with" statement implicitly delete request here "releasing" the resource
    
class Server_2(object):

    # constructor
    def __init__(self, environ, num_servers, MU, capacity):

        # the service time
        self.MU = MU
        self.capacity = capacity
        
        # the environment
        self.env = environ
        
        # wash machines
        self.machines = simpy.Resource(self.env, num_servers)
        
        # number of cars in the shop
        self.qsize = 0
        
        self.response_time = []
        self.occupancies = []
        self.n_discarded = 0

    def serve(self, start):
    # print("Packets in the server on arrival: ", self.qsize)
    
        if self.qsize<self.capacity:
            
            self.qsize += 1
            self.occupancies.append(self.qsize-1) #to see how many guys are in the queue so the real buffer occupancy
            
            
            # request a machine to wash the new coming car
            with self.machines.request() as request:
                yield request
        
                # once the machine is free, wait until service is finished
                service_time = random.expovariate(lambd=1.0/self.MU)
        
                # yield an event to the simulator
                yield self.env.timeout(service_time)
        
                # release the wash machine
                self.qsize -= 1
        
                end = self.env.now
        
                resp_time = end-start
                #print "response time: " + str(resp_time)
        
                self.response_time.append(resp_time)
                
    
        else:
            # discard packet
            self.n_discarded=self.n_discarded+1
    
    # the "with" statement implicitly delete request here "releasing" the resource

# **********************************************************************************************************************
# the "main" of the simulation
# **********************************************************************************************************************
if __name__ == '__main__':
	
    SERVICE_TIME_1=100
    SERVICE_TIME_2=10000
    
    CAPACITY_1=20
    CAPACITY_2=38
    
    INTER_ARRIVAL=250
    	
    rho_1=1.0*SERVICE_TIME_1/INTER_ARRIVAL
    
    random.seed(RANDOM_SEED)
    
    # ********************************
    # setup and perform the simulation
    # ********************************
    
    env = simpy.Environment()
    
    # request arrival
    request_arrival = RequestArrival(env, INTER_ARRIVAL)
    
    # server
    server_2 = Server_2(env, NUM_SERVERS, SERVICE_TIME_2)
    server_1 = Server_1(env, NUM_SERVERS, SERVICE_TIME_1, server_2)

    
    # start the arrival process
    env.process(request_arrival.arrival_process(server_1))
    
    # simulate until SIM_TIME
    env.run(until=SIM_TIME)
    
    