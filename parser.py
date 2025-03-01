import csv
import os
import sys

if len(sys.argv) != 3:
    print("ERROR: Invalid number of arguments. Expected: python parser.py data/<lookup-csv-filename> data/<flog-low-txt-filename>")
    sys.exit(1)

rel_path_lookup = sys.argv[1]
rel_path_data = sys.argv[2]
rel_path_protocolnum = "./data/protocol-numbers-1.csv"

# Command argument validation
if not os.path.exists(rel_path_lookup):
    print(f"ERROR: Lookup file at {rel_path_lookup} does not exist.")
    sys.exit(1)
if not os.path.exists(rel_path_data):
    print(f"ERROR: Lookup file at {rel_path_data} does not exist.")
    sys.exit(1)
if not os.path.exists(rel_path_protocolnum):
    print(f"ERROR: Lookup file at {rel_path_protocolnum} does not exist.")
    sys.exit(1)

# Check if files are empty
if os.path.getsize(rel_path_lookup) == 0:
    print(f"ERROR: Lookup file {rel_path_lookup} is empty.")
    sys.exit(1)
if os.path.getsize(rel_path_data) == 0:
    print(f"ERROR: Data file {rel_path_data} is empty.")
    sys.exit(1)
if os.path.getsize(rel_path_protocolnum) == 0:
    print(f"ERROR: Protocol file {rel_path_protocolnum} is empty.")
    sys.exit(1)

# Initialize dictionaries
protocols = {}
lookup = {}
tag_count = {}
port_prot_count = {}

# Read protocol csv file (Decimal to Keyword mapping), save to dict
try:
    with open(rel_path_protocolnum, "r") as f2:
        csvreader = csv.reader(f2)
        for row in csvreader:
            # Basic validation of protocol file format
            if len(row) < 2:
                print(f"WARNING: Skipping invalid row in protocol file: {row}")
                continue
            # row[0] is the decimal field, row[1] is the protocol keyword field
            keyword_lower = row[1].lower()
            protocols[row[0]] = keyword_lower
except Exception as e:
    print(f"ERROR: Failed to read protocol file: {e}")
    sys.exit(1)

if not protocols:
    print("ERROR: No valid protocols loaded from protocol file.")
    sys.exit(1)

# Load lookup table -> dictionary, keys are tuples
try:
    with open(rel_path_lookup, "r") as f3:
        csvreader = csv.reader(f3)
        fields = next(csvreader)
        for row in csvreader:
            if(len(row) == 3):
                lookup[(row[0], row[1].lower())] = row[2]
                tag_count[row[2]] = 0
        tag_count["Untagged"] = 0
except Exception as e:
    print(f"ERROR: Failed to read lookup file: {e}")
    sys.exit(1)
if not lookup:
    print("WARNING: Lookup table only has header row, but no contents. All entries will be tagged as 'Untagged'.")

# Read log_data
try:
    with open(rel_path_data, "r") as f1:
        for line in f1:
            log = line.rstrip()
            log_lst = log.split(" ")
            tag_flag = False
            
            # Skip malformed log entries
            if len(log_lst) <= 7:
                print(f"WARNING: Skipping malformed/empty log entry: {log}")
                continue
                
            # Skip if protocol number doesn't exist
            if log_lst[7] not in protocols:
                print(f"WARNING: Unknown protocol number {log_lst[7]} in log entry")
                continue
                
            if (len(log_lst) > 1):  
                for tuple_key in lookup:
                    if(log_lst[6] == tuple_key[0] and protocols[log_lst[7]] == tuple_key[1].lower()):
                        tag_count[lookup[tuple_key]] += 1
                        tag_flag = True
                if (not tag_flag):
                    tag_count["Untagged"] += 1
                    tag_flag = False
                if (port_prot_count.get((log_lst[6], protocols[log_lst[7]])) == None):
                    port_prot_count[(log_lst[6], protocols[log_lst[7]])] = 1
                else:
                    port_prot_count[(log_lst[6], protocols[log_lst[7]])] += 1
except Exception as e:
    print(f"ERROR: Failed to process log data: {e}")
    sys.exit(1)

# Write to output files: tag_out.csv and port_prot_out.csv, store them in out directory
out_dir = "out"
try:
    os.makedirs(out_dir, exist_ok=True)

    filename = os.path.basename(sys.argv[2])  # get filename.txt from command arg
    base_name = os.path.splitext(filename)[0]  # get filename from filename.txt

    tag_outdir = f"{out_dir}/tagcount_{base_name}.csv"
    port_prot_outdir = f"{out_dir}/portprotcount_{base_name}.csv"

    with open(tag_outdir, "w", newline="") as out1:
        writer = csv.writer(out1)
        for tag, count in tag_count.items():
            if (count > 0):
                writer.writerow([tag,count])

    with open(port_prot_outdir, "w", newline="") as out2:
        writer = csv.writer(out2)
        for tuple, count in port_prot_count.items():
            writer.writerow([tuple[0],tuple[1],count])
            
    print(f"Output files successfully created: {tag_outdir} and {port_prot_outdir}")
except Exception as e:
    print(f"ERROR: Failed to write output files: {e}")
    sys.exit(1)