# Network Flow Log Parser

Log parser that processes network data using a lookup table to classify and count the instances of specific network activity.

## Requirements
    1) Python 3.X
    2) Two files
        - lookup file -> csv file that contains mappings of destination port and protocol to a tag (e.g, 25,tcp -> sv_P1 )
        - log data -> txt file that contains network logs with their fields separated by spaces (" ").
          Example log: 2 123456789012 eni-7i8j9k0l 172.16.0.101 192.0.2.203 993 49157 6 8 5000 1620140761 1620140821 ACCEPT OK

## Default file hierarchy:

  assessment/
  ├── data/
  │   ├── log_data.txt
  │   ├── lookup.csv
  │   ├── protocol-numbers-1.csv
  ├── tests/
  │   ├── expected_out/
  ├── .gitattributes
  ├── parser.py
  └── README.md

The tests/ directory contains three different test cases, each containing their own lookup and log_data file. The expected_out/ subdirectory holds the expected output files for each test case, with both tagcount and portprotcount results.

## Expected use: 
    1) Clone repository into directory of choice
    2) Move your lookup csv file and your flow log data txt file to the data directory (log_data.txt and lookup.csv included by default).
    3) Ensure your working directory is /assessment
    4) Run from the terminal as python parser.py data/<Name of lookup file> data/<Name of flow log data file>.


## Functionality of the program
    1) Read lookup.csv and protocol-numbers-1.csv into two separate Python dictionaries.
    2) Read log_data line by line, extract dstport and protocol:
        - Check if the destination port and protocol exist in lookup
        - If match found, increment count for corresponding tag
        - Increase "Untagged" count by 1 otherwise.
        - Keep count of occurrence of (dstport, protocol) pairs
    3) Output the tag count and the (dstport, protocol) count as two separate csv files 
       (tag_count.csv and port_prot_count.csv) to /out, a directory created by the script. 


## Error handling
The code includes error handling for the following cases:
- User inputs non existing or incorrect file paths for the lookup file or the flow log data file.
- Script cannot find the protocol-numbers-1.csv file in the data directory

## Assumptions
The script makes the following assumptions:
- The lookup file is a .csv file, while the log data file is a .txt file, both provided by the user.
- The file protocol-numbers-1.csv is provided by default.
- The lookup and log data files are not empty.
- The lookup csv file follows the structure outlined in the assessment (fields: dstport,protocol,tag).
- The script only supports default log format (version 2 only), not custom formats. For more info, check out https://docs.aws.amazon.com/vpc/latest/userguide/flow-log-records.html.
- The 7th entry of each log represents the destination port.
- The 8th entry of each log represents the protocol number.
- Since the lookup file can have up to 10,000 entries, the script loads the lookup table into memory without noticeable performance issues.


## Use of LLMs:
I implemented the error handling for argument validation, with Claude 3.7 Sonnet helping to refine the approach.
To validate the error handling measures, I ran tests for each error scenario and determined if the error handling was implemented correctly. 
I also developed test cases for this script with the assistance of the sameeLLM (brainstorm different lookup tables and log data files). To validate the test cases, I compared the structure of the lookup and log data files with the structure provided in the outline of this assessment. For the log data files, I made sure that the structure of their logs was aligned with the table in the AWS website provided in the outline.
