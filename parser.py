import csv
import os
import sys


# EXPECTED USAGE: 
# 1) Run as python parser.py lookup.csv log_data.txt
# 2) argv[1] -> location of lookup.csv, argv[2] -> location of log_data.txt

if len(sys.argv) != 3:
    print("ERROR: Invalid number of arguments. Expected: python parser.py data/<lookup-csv-filename> data/<flog-low-txt-filename>")
    sys.exit(1)


rel_path_lookup = sys.argv[1]
rel_path_data = sys.argv[2]
rel_path_protocolnum = "./data/protocol-numbers-1.csv"

if not os.path.exists(rel_path_lookup):
    print(f"ERROR: Lookup file at {rel_path_lookup} does not exist.")
    sys.exit(1)
if not os.path.exists(rel_path_data):
    print(f"ERROR: Lookup file at {rel_path_data} does not exist.")
    sys.exit(1)
if not os.path.exists(rel_path_protocolnum):
    print(f"ERROR: Lookup file at {rel_path_protocolnum} does not exist.")
    sys.exit(1)


protocols = {}
lookup = {}

tag_count = {}
port_prot_count = {}


# Read protocol csv file (Decimal to Keyword mapping), save to dict
with open(rel_path_protocolnum, "r") as f2:
    csvreader = csv.reader(f2)
    for row in csvreader:
        # row[0] is the decimal field, row[1] is the protocol keyword field
        keyword_lower = row[1].lower()
        protocols[row[0]] = keyword_lower

#print(protocols)

# Load lookup table -> dictionary, keys are tuples
with open(rel_path_lookup, "r") as f3:
    csvreader = csv.reader(f3)
    fields = next(csvreader)
    for row in csvreader:
        #print(row)
        if(len(row) == 3):
            lookup[(row[0], row[1].lower())] = row[2]
            tag_count[row[2]] = 0
    tag_count["Untagged"] = 0


# Read log_data
with open(rel_path_data, "r") as f1:
    # content = f1.read()
    # indexed_data = content.split(" ")
    for line in f1:
        log = line.rstrip()
        log_lst = log.split(" ")
        tag_flag = False
        if (len(log_lst) > 1):  
            #print(log_lst)  
            for tuple_key in lookup:
                if(log_lst[6] == tuple_key[0] and protocols[log_lst[7]] == tuple_key[1].lower()):
                    tag_count[lookup[tuple_key]] += 1
                    #print("MATCH")
                    tag_flag = True
            if (not tag_flag):
                tag_count["Untagged"] += 1
                tag_flag = False
            if (port_prot_count.get((log_lst[6], protocols[log_lst[7]])) == None):
                port_prot_count[(log_lst[6], protocols[log_lst[7]])] = 1
            else:
                port_prot_count[(log_lst[6], protocols[log_lst[7]])] += 1


# Write to output files: tag_out.csv and port_prot_out.csv, store them in out directory
out_dir = "out"
os.makedirs(out_dir, exist_ok=True)

filename = os.path.basename(sys.argv[2])  # get filename.txt from command arg
base_name = os.path.splitext(filename)[0]  # get filename from filename.txt

tag_outdir = f"{out_dir}/tagcount_{base_name}.csv"
port_prot_outdir = f"{out_dir}/portprotcount_{base_name}.csv"

with open(tag_outdir, "w") as out1:
    writer = csv.writer(out1)
    for tag, count in tag_count.items():
        if (count > 0):
            writer.writerow([tag,count])

with open(port_prot_outdir, "w") as out2:
    writer = csv.writer(out2)
    for tuple, count in port_prot_count.items():
        writer.writerow([tuple[0],tuple[1],count])

             
            
#print(tag_count)
#print(port_prot_count)
            



# print(lookup)


# Based on lookup table
# field 1: dstport, field 2: protocol keyword, field 3: tag


