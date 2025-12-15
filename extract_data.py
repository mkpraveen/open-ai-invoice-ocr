import time

from invoice_extractor import InvoiceExtractor
from transform_data import InvoiceTransformer


read_path= "./data/images"
write_path= "./data/json"
enhanced_json = "./data/enhanced_json"


if __name__ == "__main__":
    
    extractor = InvoiceExtractor()
    extractor.process_directory(read_path, write_path)

    # Sleep for 20 seconds
    time.sleep(20)
    
    transformer = InvoiceTransformer()
    transformer.process_directory(write_path, enhanced_json)
