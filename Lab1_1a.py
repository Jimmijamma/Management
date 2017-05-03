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
SIM_TIME = 1000000


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
	
	# execute the process
	def arrival_process(self, server):
	    while True:
	
	        # sample the time to next arrival
	        arrival_time = random.expovariate(lambd=1.0/self.LAMBDA)
	
	        # yield an event to the simulator
	        yield self.env.timeout(arrival_time)
	        
	        start = env.now
	        # a car has arrived - request server to do its job
	        self.env.process(server.serve(start))
	        
	        
			     

# **********************************************************************************************************************
# Car wash - it gets an waiting car (FCFS) and performs the service
# **********************************************************************************************************************
class Server(object):

    # constructor
    def __init__(self, environ, num_servers, MU):

		# the service time
		self.MU = MU

		# wash machines
		self.machines = simpy.Resource(env, num_servers)

		# the environment
		self.env = environ

		# number of cars in the shop
		self.qsize = 0

		self.response_time = []
		self.occupancies = []

    def serve(self, start):
        # print("Packets in the server on arrival: ", self.qsize)
		
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

			end = env.now

			resp_time = end-start
			#print "response time: " + str(resp_time)

			self.response_time.append(resp_time)

        # the "with" statement implicitly delete request here "releasing" the resource

# **********************************************************************************************************************
# the "main" of the simulation
# **********************************************************************************************************************
if __name__ == '__main__':
	
	SERVICE_TIME=100
	
	ros = []
	r_times = []
	theoretical_buf_occ = []
	theoretical_response_time = []
	mean_buf_occ = []
	
	for INTER_ARRIVAL in range(1000,100,-1):
		
		ro=1.0*SERVICE_TIME/INTER_ARRIVAL
		ros.append(ro)
		theoretical_response_time.append(1.0/((1.0/SERVICE_TIME)-(1.0/INTER_ARRIVAL)))
		bo = 1.0*(ro**2/(1-ro)) #theoretical formula for buffer occupancy
		theoretical_buf_occ.append(bo)
		
		random.seed(RANDOM_SEED)
		
		# ********************************
		# setup and perform the simulation
		# ********************************
		
	
		env = simpy.Environment()
		
		# car arrival
		car_arrival = RequestArrival(env, INTER_ARRIVAL)
		
		# server
		server = Server(env, NUM_SERVERS, SERVICE_TIME)
		
		# start the arrival process
		env.process(car_arrival.arrival_process(server))
		
		# simulate until SIM_TIME
		env.run(until=SIM_TIME)
		
		mean_rp=sum(server.response_time)/len(server.response_time)
		r_times.append(mean_rp)
		
		mean_buf_occ.append(sum(server.response_time)/SIM_TIME)
		
		
		
		print "mean response time: " + str(mean_rp) + "		ro: " + str(ro)
		print "n. of packets served: " + str(len(server.response_time))
	
	#plot del response time
	plt.plot(ros,r_times, label = "Real Response Time")
	plt.plot(ros, theoretical_response_time, label = "Theoretical Response Time")
	plt.ylabel("response time")
	plt.xlabel("ro")
	plt.legend(loc = 2)
	plt.savefig('myfig')
	plt.close()
	
	#dal grafico si vede che all'aumentare di ro ovvero l'utilization factor il response time ha un andamento asintotico e attorno al 90% va ad infinito, sopra 1 il sistema diventa instabile, si vede inoltre che sopra il 50% si ha una crescita esponenziale. al 50% si ha ancora 2 volte il tempo di servizio (il valore 200)
	
	#plot del buffer occupancy
	plt.plot(ros,theoretical_buf_occ, label = "Theoretical Buff Occ")
	plt.plot(ros, mean_buf_occ, label = "Real Buff Occ")
	plt.ylabel("buffer occupancy")
	plt.xlabel("ro")
	plt.legend(loc = 2)
	plt.savefig('myfig2')
	plt.close()
	
	
	#subplot delle figure
	fig, (r_t, buf) = plt.subplots(2,1)
	
	r_t.plot(ros, theoretical_response_time, label = "Theoretical Response Time")
	r_t.plot(ros, r_times, label = "Real Response Time")
	r_t.set_xlabel("ro")
	r_t.set_ylabel("response time")
	r_t.legend(loc = 2)
	
	buf.plot(ros, theoretical_buf_occ, label = "Theoretical Buff Occ")
	buf.plot(ros, mean_buf_occ, label = "Real Buff Occ")
	buf.set_xlabel("ro")
	buf.set_ylabel("buffer occupancy")
	buf.legend(loc = 2)

	plt.savefig('subplot')
	plt.close()
	
# per quanto riguarda il response time al crescere di ro il sistema diventa instabile e possiamo osservare che la varianza aumenta secondo il quadrato del valor medio quindi per ottenere simulazioni precise per ro grandi dobbiamo aumentare di molto il tempo di simulazione 
#nel buffer occupancy se calcolavamo quante persone arrivavano nella coda veniva un grafico a gradini.
		
