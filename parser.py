import csv

rel_path = "./data/log_data.txt"
rel_path_protocolnum = "./data/protocol-numbers-1.csv"
rel_path_lookup = "./data/lookup.csv"


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
        if(len(row) == 3):
            lookup[(row[0], row[1])] = row[2]
            tag_count[row[2]] = 0
    tag_count["Untagged"] = 0


# Read log_data
with open(rel_path, "r") as f1:
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


# Write to output files: tag_out.csv and port_prot_out.csv

tag_outdir = "./data/tag_out.csv"
port_prot_outdir = "./data/port_prot_out.csv"

with open(tag_outdir, "w") as out1:
    writer = csv.writer(out1)
    for tag, count in tag_count.items():
        if (count > 0):
            writer.writerow([tag,count])

with open(port_prot_outdir, "w") as out2:
    writer = csv.writer(out2)
    for tuple, count in port_prot_count.items():
        writer.writerow([tuple[0],tuple[1],count])

             
            
print(tag_count)
print(port_prot_count)
            



# print(lookup)


# Based on lookup table
# field 1: dstport, field 2: protocol keyword, field 3: tag


