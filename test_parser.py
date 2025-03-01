import unittest
import subprocess
import os

class TestLogParser(unittest.TestCase):
    def setUp(self):
        self.out_dir = "out"
        os.makedirs(self.out_dir, exist_ok=True)

        self.test_cases = [
            ("tests/lookt1.csv", "tests/datat1.txt"),
            ("tests/lookt2.csv", "tests/datat2.txt"),
            ("tests/lookt3.csv", "tests/datat3.txt")
        ]

    def files_match(self, file1, file2):
        # Compare CSV files ignoring newlines 
        with open(file1, "r") as f1, open(file2, "r") as f2:
            lines1 = [line.rstrip() for line in f1.readlines()]
            lines2 = [line.rstrip() for line in f2.readlines()]
            return lines1 == lines2

    def test_parser_output(self):
        # run parser and compare outputs to expected results.
        for lookup_file, log_file in self.test_cases:
            base_name = os.path.splitext(os.path.basename(log_file))[0]
            tag_output = f"{self.out_dir}/tagcount_{base_name}.csv"
            portprot_output = f"{self.out_dir}/portprotcount_{base_name}.csv"
            
            expected_tag_output = f"tests/expected_out/tagcount_{base_name}.csv"
            expected_portprot_output = f"tests/expected_out/portprotcount_{base_name}.csv"
            
            # run parser.py
            subprocess.run(["python", "parser.py", lookup_file, log_file], check=True)

            # check if files are created
            self.assertTrue(os.path.exists(tag_output), f"Missing output file: {tag_output}")
            self.assertTrue(os.path.exists(portprot_output), f"Missing output file: {portprot_output}")

            # compare output files to expected results (ignoring trailing newlines)
            self.assertTrue(self.files_match(tag_output, expected_tag_output), f"Mismatch in {tag_output}")
            self.assertTrue(self.files_match(portprot_output, expected_portprot_output), f"Mismatch in {portprot_output}")

if __name__ == "__main__":
    unittest.main()
