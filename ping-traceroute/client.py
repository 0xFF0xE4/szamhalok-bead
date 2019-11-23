from subprocess import PIPE, Popen
import sys, datetime, json

# 0) check parameters 
if len(sys.argv) < 2:
	print("Error: input file name missing\nAdd a filename as parameter")
	sys.exit()

# 1) read hosts from file, convert output and chunk unwanted parts
head_out = str(Popen(["head", "-10", sys.argv[1]], stdout=PIPE).communicate()[0])[2:-3].split('\\n')
tail_out = str(Popen(["tail", "-10", sys.argv[1]], stdout=PIPE).communicate()[0])[2:-3].split('\\n')
# and create list of hosts
addresses = [line.split(',')[1] for line in head_out]
addresses += [line.split(',')[1] for line in tail_out]
# 2) execute traceroute and ping commands for every host
trace_output = []
ping_output = []
for host in addresses:
	# again: convert command output and chunk unnecessary parts
	print("tracing "+host)
	trace_out = str(Popen(["traceroute", "-m", "30", host], stdout=PIPE).communicate()[0])[2:-1]
	trace_output.append(trace_out.replace('\\n', '\n'))

	print("pinging "+host)
	ping_out = str(Popen(["ping", "-c", "10", host], stdout=PIPE).communicate()[0])[2:-1]
	ping_output.append(ping_out.replace('\\n', '\n'))
print("***** tracing and routing completed *****")

# 3) convert output to JSON string
trace_listdict = [{'target': host, 'output': output} for (host, output) in zip(addresses, trace_output)]
ping_listdict = [{'target': host, 'output': output} for (host, output) in zip(addresses, ping_output)]

today = datetime.datetime.today().strftime("%Y%m%d")

# 4) write JSON to files
with open("traceroute.json", "w") as trace_file:
	json.dump({'time':today, "system":'linux', 'traces': trace_listdict}, trace_file, indent=4)
with open("ping.json", "w") as ping_file:
	json.dump({'time':today, "system":'linux', 'pings': ping_listdict}, ping_file, indent=4)
