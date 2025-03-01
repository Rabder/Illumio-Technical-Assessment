import os
import sys
import subprocess
import csv
import unittest

class ParserTester(unittest.TestCase):

    # Setup environment for testing
    @classmethod
    def setUpClass(cls):
        cls.test_dir = os.getcwd()
        cls.data_dir = os.path.join(cls.test_dir, "data")
        cls.out_dir = os.path.join(cls.test_dir, "out")
        
        os.makedirs(cls.data_dir, exist_ok=True)
        os.makedirs(cls.out_dir, exist_ok=True)
        
        # Path of parser script
        cls.parser_path = os.path.join(cls.test_dir, "parser.py")
        
    
    def setup(self):
        # Clean out directory before starting
        if os.path.exists(self.out_dir):
            for file in os.listdir(self.out_dir):
                os.remove(os.path.join(self.out_dir, file))
    
    def create_lookup_file(self, content, filename="test_lookup.csv"):
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, "w", newline="") as f:
            if isinstance(content, list):
                writer = csv.writer(f)
                for row in content:
                    writer.writerow(row)
            else:
                f.write(content)
        return filepath
    
    def create_log_file(self, content, filename="test_flowlog.txt"):
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, "w") as f:
            if isinstance(content, list):
                for line in content:
                    f.write(line + "\n")
            else:
                f.write(content)
        return filepath
    
    def run_parser(self, lookup_file, log_file, expected_returncode=0, check_output=False):
        cmd = [sys.executable, self.parser_path, lookup_file, log_file]
        if check_output:
            return subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if expected_returncode is not None:
                self.assertEqual(result.returncode, expected_returncode, 
                                f"Expected return code {expected_returncode}, got {result.returncode}. Output: {result.stdout}")
            return result
    
    def read_output_file(self, filename):
        filepath = os.path.join(self.out_dir, filename)
        self.assertTrue(os.path.exists(filepath), f"Output file {filepath} does not exist")
        
        rows = []
        with open(filepath, "r", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                rows.append(row)
        return rows
    
    # Test for "ERROR: Invalid number of arguments"
    def test_invalid_args(self):
        result = subprocess.run([sys.executable, self.parser_path], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("ERROR: Invalid number of arguments", result.stdout)
    
    # Test for nonexistent lookup file: "ERROR: Lookup file at nonexistent_file.csv does not exist"
    def test_nonexistent_lookup(self):
        log_file = self.create_log_file("some log data")
        result = self.run_parser("nonexistent_file.csv", log_file, expected_returncode=1)
        self.assertIn("ERROR: Lookup file at nonexistent_file.csv does not exist", result.stdout)
    
    # Test for nonexistent log file: "ERROR: Lookup file at nonexistent_file.txt does not exist"
    def test_nonexistent_log(self):
        """Test script behavior with nonexistent log file"""
        lookup_file = self.create_lookup_file([["dstport", "protocol", "tag"]])
        result = self.run_parser(lookup_file, "nonexistent_file.txt", expected_returncode=1)
        self.assertIn("ERROR: Lookup file at nonexistent_file.txt does not exist", result.stdout)
    
    def test_empty_lookup(self):
        lookup_file = self.create_lookup_file("")
        log_file = self.create_log_file("some log data")
        result = self.run_parser(lookup_file, log_file, expected_returncode=1)
        self.assertIn("ERROR: Lookup file", result.stdout)
        self.assertIn("is empty", result.stdout)
    
    def test_empty_log(self):
        """Test script behavior with empty log file"""
        lookup_file = self.create_lookup_file([["dstport", "protocol", "tag"]])
        log_file = self.create_log_file("")
        result = self.run_parser(lookup_file, log_file, expected_returncode=1)
        self.assertIn("ERROR: Data file", result.stdout)
        self.assertIn("is empty", result.stdout)
    
    def test_lookup_only_header(self):
        """Test script behavior with lookup file containing only header row"""
        lookup_file = self.create_lookup_file([["dstport", "protocol", "tag"]])
        
        log_data = [
            "2 123456789010 eni-11111111111111111 123.45.67.89 10.0.0.1 39812 80 6 10 840 1559650489 1559650499 ACCEPT OK"
        ]
        log_file = self.create_log_file(log_data)
        
        result = self.run_parser(lookup_file, log_file)
        self.assertIn("WARNING: Lookup table only has header row", result.stdout)
        
        # Were all entries tagged as Untagged?
        tag_count_file = self.read_output_file(f"tagcount_{os.path.basename(log_file).split('.')[0]}.csv")
        self.assertEqual(len(tag_count_file), 1)
        self.assertEqual(tag_count_file[0][0], "Untagged")
        self.assertEqual(tag_count_file[0][1], "1")
    

    def test_malformed_log(self):
        lookup_file = self.create_lookup_file([
            ["dstport", "protocol", "tag"],
            ["80", "TCP", "Web"]
        ])
        
        log_data = [
            "2 123456789010 eni-11111111111111111",  # Malformed entry
            "2 123456789010 eni-11111111111111111 123.45.67.89 10.0.0.1 39812 80 6 10 840 1559650489 1559650499 ACCEPT OK"  # Valid entry
        ]
        log_file = self.create_log_file(log_data)
        
        result = self.run_parser(lookup_file, log_file)
        self.assertIn("WARNING: Skipping malformed/empty log entry", result.stdout)
        
        # Was the valid entry processed correctly?
        tag_count_file = self.read_output_file(f"tagcount_{os.path.basename(log_file).split('.')[0]}.csv")
        self.assertEqual(len(tag_count_file), 1)
        self.assertEqual(tag_count_file[0][0], "Web")
        self.assertEqual(tag_count_file[0][1], "1")
    
    def test_unknown_protocol(self):
        lookup_file = self.create_lookup_file([
            ["dstport", "protocol", "tag"],
            ["80", "TCP", "Web"]
        ])
        
        log_data = [
            "2 123456789010 eni-11111111111111111 123.45.67.89 10.0.0.1 39812 80 2077 10 840 1559650489 1559650499 ACCEPT OK",  # Unknown protocol
            "2 123456789010 eni-11111111111111111 123.45.67.89 10.0.0.1 39812 80 6 10 840 1559650489 1559650499 ACCEPT OK"  # Valid entry
        ]
        log_file = self.create_log_file(log_data)
        
        result = self.run_parser(lookup_file, log_file)
        self.assertIn("WARNING: Unknown protocol number 2077 in log entry", result.stdout)
        
        # Was the valid entry processed correctly?
        tag_count_file = self.read_output_file(f"tagcount_{os.path.basename(log_file).split('.')[0]}.csv")
        self.assertEqual(len(tag_count_file), 1)
        self.assertEqual(tag_count_file[0][0], "Web")
        self.assertEqual(tag_count_file[0][1], "1")
    
    
    def test_basic_functionality(self):
        lookup_data = [
            ["dstport", "protocol", "tag"],
            ["80", "TCP", "Web"],
            ["443", "TCP", "SecureWeb"],
            ["53", "UDP", "DNS"]
        ]
        lookup_file = self.create_lookup_file(lookup_data)
        
        log_data = [
            "2 123456789010 eni-11111111111111111 123.45.67.89 10.0.0.1 39812 80 6 10 840 1559650489 1559650499 ACCEPT OK",  # Web
            "2 123456789010 eni-11111111111111111 123.45.67.89 10.0.0.1 39812 443 6 10 840 1559650489 1559650499 ACCEPT OK",  # SecureWeb
            "2 123456789010 eni-11111111111111111 123.45.67.89 10.0.0.1 39812 53 17 10 840 1559650489 1559650499 ACCEPT OK",  # DNS
            "2 123456789010 eni-11111111111111111 123.45.67.89 10.0.0.1 39812 22 6 10 840 1559650489 1559650499 ACCEPT OK"   # Untagged
        ]
        log_file = self.create_log_file(log_data)
        
        result = self.run_parser(lookup_file, log_file)
        self.assertIn("Output files successfully created", result.stdout)
        
        # Check tag count output
        tag_count_file = self.read_output_file(f"tagcount_{os.path.basename(log_file).split('.')[0]}.csv")
        expected_tags = {"Web": "1", "SecureWeb": "1", "DNS": "1", "Untagged": "1"}
        
        self.assertEqual(len(tag_count_file), 4)
        for row in tag_count_file:
            self.assertEqual(row[1], expected_tags[row[0]])
        
        # Check port protocol count output
        port_prot_file = self.read_output_file(f"portprotcount_{os.path.basename(log_file).split('.')[0]}.csv")
        expected_port_prot = [
            ["80", "tcp", "1"],
            ["443", "tcp", "1"],
            ["53", "udp", "1"],
            ["22", "tcp", "1"]
        ]
        
        self.assertEqual(len(port_prot_file), 4)
        for row in port_prot_file:
            self.assertTrue(any(row[0] == e[0] and row[1] == e[1] and row[2] == e[2] for e in expected_port_prot))
    
    def test_case_insensitivity(self):
        lookup_data = [
            ["dstport", "protocol", "tag"],
            ["80", "TCP", "Web"],  # Uppercase
            ["443", "tcp", "SecureWeb"],  # Lowercase
            ["53", "UdP", "DNS"]  # Mixed case
        ]
        lookup_file = self.create_lookup_file(lookup_data)
        
        log_data = [
            "2 123456789010 eni-11111111111111111 123.45.67.89 10.0.0.1 39812 80 6 10 840 1559650489 1559650499 ACCEPT OK",  # Should match TCP
            "2 123456789010 eni-11111111111111111 123.45.67.89 10.0.0.1 39812 443 6 10 840 1559650489 1559650499 ACCEPT OK",  # Should match tcp
            "2 123456789010 eni-11111111111111111 123.45.67.89 10.0.0.1 39812 53 17 10 840 1559650489 1559650499 ACCEPT OK"   # Should match UdP
        ]
        log_file = self.create_log_file(log_data)
        
        self.run_parser(lookup_file, log_file)
        
        # Check tag count output: all should be matched
        tag_count_file = self.read_output_file(f"tagcount_{os.path.basename(log_file).split('.')[0]}.csv")
        expected_tags = {"Web": "1", "SecureWeb": "1", "DNS": "1"}
        
        self.assertEqual(len(tag_count_file), 3)
        for row in tag_count_file:
            self.assertEqual(row[1], expected_tags[row[0]])
    
    def test_multiple_entries_same_tag(self):
        lookup_data = [
            ["dstport", "protocol", "tag"],
            ["80", "TCP", "Web"],
            ["8080", "TCP", "Web"],  # Same tag as port 80
            ["443", "TCP", "SecureWeb"]
        ]
        lookup_file = self.create_lookup_file(lookup_data)
        
        log_data = [
            "2 123456789010 eni-11111111111111111 123.45.67.89 10.0.0.1 39812 80 6 10 840 1559650489 1559650499 ACCEPT OK",
            "2 123456789010 eni-11111111111111111 123.45.67.89 10.0.0.1 39812 8080 6 10 840 1559650489 1559650499 ACCEPT OK",
            "2 123456789010 eni-11111111111111111 123.45.67.89 10.0.0.1 39812 443 6 10 840 1559650489 1559650499 ACCEPT OK"
        ]
        log_file = self.create_log_file(log_data)
        
        self.run_parser(lookup_file, log_file)
        
        # Is Web tag counted correctly? (should be 2)
        tag_count_file = self.read_output_file(f"tagcount_{os.path.basename(log_file).split('.')[0]}.csv")
        expected_tags = {"Web": "2", "SecureWeb": "1"}
        
        self.assertEqual(len(tag_count_file), 2)
        for row in tag_count_file:
            self.assertEqual(row[1], expected_tags[row[0]])
    
    def test_trailing_spaces_newlines(self):
        lookup_data = [
            ["dstport", "protocol", "tag"],
            ["80", "TCP", "Web"]
        ]
        lookup_file = self.create_lookup_file(lookup_data)
        
        # Add trailing spaces and extra newlines
        log_data = [
            "2 123456789010 eni-11111111111111111 123.45.67.89 10.0.0.1 39812 80 6 10 840 1559650489 1559650499 ACCEPT OK    ",
            "",
            "2 123456789010 eni-11111111111111111 123.45.67.89 10.0.0.1 39812 80 6 10 840 1559650489 1559650499 ACCEPT OK"
        ]
        log_file = self.create_log_file(log_data)
        
        result = self.run_parser(lookup_file, log_file)
        
        # Check single warning for empty line
        self.assertIn("WARNING: Skipping malformed/empty log entry", result.stdout)
        
        # Is Web tag counted correctly? (should be 2)
        tag_count_file = self.read_output_file(f"tagcount_{os.path.basename(log_file).split('.')[0]}.csv")
        self.assertEqual(len(tag_count_file), 1)
        self.assertEqual(tag_count_file[0][0], "Web")
        self.assertEqual(tag_count_file[0][1], "2")

if __name__ == "__main__":
    unittest.main()