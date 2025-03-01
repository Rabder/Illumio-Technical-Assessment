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
    ├── .gitattributes
    ├── parser.py
    ├── README.md
    └── test_parser.py


## Expected use: 
    1) Clone repository into directory of choice
    2) Move your lookup csv file and your flow log data txt file to the data directory (log_data.txt and lookup.csv included by default).
    3) Navigate to assessment (cd <path-to-cloned-repository>/assessment). 
    4) Run from the terminal as python parser.py data/<Name of lookup file> data/<Name of flow log data file>.
    5) For testing, run from the terminal as python test_parser.py


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
- The user inputs non existing or incorrect file paths for the lookup file or the flow log data file.
- The script cannot find the protocol-numbers-1.csv file in the data directory
- The script reads a log with an unknown protocol 
- The lookup, log data or protocol numbers files are empty or malformed.

## Testing
The submission includes a tester script, test_parser.py, which runs different cases test cases and checks if the parser output
matches the expected output for those tests. 
The tests included in this submission encompass the following cases:
  - Correct overall functionality of parser
  - Invalid command arguments
  - Empty files (no content)
  - Lookup file with just a header
  - Malformed data 
  - Non existent files
  - Unknown protocol when reading logs
  - Case insensitivity
  - Handling of newlines and spaces

To run the tester, run from the terminal with python test_parser.py. 

## Assumptions
The script makes the following assumptions:
- The lookup file is a .csv file, while the log data file is a .txt file, both provided by the user.
- The file protocol-numbers-1.csv is provided by default.
- If the lookup table only has header rows (no content) or malformed, the script with classify all logs as "Untagged".
- The lookup csv file follows the structure outlined in the assessment (fields: dstport,protocol,tag).
- The script only supports default log format (version 2 only), not custom formats. The structure of each log is outlined in this website: https://docs.aws.amazon.com/vpc/latest/userguide/flow-log-records.html.
- The script will skip any rows of the log data txt file that are either malformed, empty or correspond to an unknown protocol number.
- The 7th entry of each log represents the destination port.
- The 8th entry of each log represents the protocol number.
- Since the lookup file can have up to 10,000 entries, the script loads the lookup table into memory without noticeable performance issues.


## Use of LLMs:
I implemented the error handling for this script, checking for issues in command line arguments, empty files and malformed inputs. I used Claude 3.7 Sonnet to refine my approach and incorporate some additional error handling measures. 
In particular, 
it incorporated measures to check if the protocols were valid or not based on the data/protocol-numbers-1.csv file and errors in reading and outputting files. 
For testing, I developed the script and tests with the help of the same LLM, using it facilitate writing the assertion logic 
and brainstorming different test case scenarios.