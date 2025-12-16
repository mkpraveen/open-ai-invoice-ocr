import os

from inv_graph import inv_graph

read_path = os.path.abspath("data/images")
write_path = os.path.abspath("data/json")
enhanced_json_path = os.path.abspath("data/enhanced_json")

class DirectoryProcessor:
    def process_directory(self, read_path, write_path, enhanced_json_path):
        # Ensure output directories exist
        os.makedirs(write_path, exist_ok=True)
        os.makedirs(enhanced_json_path, exist_ok=True)

        for filename in os.listdir(read_path):
            print(f"Processing file: {filename}")
            file_path = os.path.join(read_path, filename)
            if os.path.isfile(file_path):
                inv_graph.invoke({
                    "image_file_path": file_path,
                    "raw_json_path": write_path,
                    "enhanced_json_path": enhanced_json_path
                })


if __name__ == "__main__":
    processor = DirectoryProcessor()
    processor.process_directory(read_path, write_path, enhanced_json_path)

