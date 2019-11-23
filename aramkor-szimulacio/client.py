from sys import argv, exit
import json

if len(argv) < 2:
	print("Error: input file name missing\nAdd a filename as parameter")
	exit()

with open(argv[1], "r") as input_file:
	input_data = json.load(input_file)
	event_counter = 0
	
	# every sim will have a list for used links, used to decrease and increase links' capacity depending on event type
	for sim in input_data["simulation"]["demands"]:
		sim["used-links"] = []

	for t in range(1, input_data["simulation"]["duration"]+1):
		# print("Time: ", t)
		for sim in input_data["simulation"]["demands"]:
			if sim["end-time"] == t:
				# if connection was successful free occupied links
				if not sim["success"]:
					break
				# if used links list is empty we are in big trouble
				if not sim["used-links"]:
					print("WTF: What a terrible failure")
				else:
					for i in sim["used-links"]:
						input_data["links"][i]["capacity"] += sim["demand"]
				event_counter += 1
				print("%d. igény felszabadítás: %s<->%s st:%d" % (event_counter, sim["end-points"][0], sim["end-points"][1], t))
			elif sim["start-time"] == t:
				# find first free circuit, occupy it and store links, 
				possible_circuits = [circ for circ in input_data["possible-circuits"] if (circ[0]==sim["end-points"][0] and circ[-1]==sim["end-points"][1])]
				sim["success"] = False
				for circuit in possible_circuits:
					# if sim success true then we already found a free path, no need to continue
					if sim["success"]:
						break
					# check if every link has capacity, also store found links' indexes
					sim["success"] = True
					for ep_from, ep_to in zip(circuit, circuit[1:]):
						for link_index, link in enumerate(input_data["links"]):
							if link["points"] in [[ep_from, ep_to], [ep_to, ep_from]]:
								if link["capacity"] < sim["demand"]:
									sim["success"] = False
								else:
									sim["used-links"].append(link_index)
					# if every link has capacity, decrease it by sim's demand
					if sim["success"]:
						for i in sim["used-links"]:
							input_data["links"][i]["capacity"] -= sim["demand"]
				event_counter += 1
				print("%d. igény foglalás: %s<->%s st:%d - %s" % (event_counter, sim["end-points"][0], sim["end-points"][1], t, "sikeres" if sim["success"] else "sikertelen"))
