import os
from pyhwp import HwpFile

def extract_text_from_hwp(hwp_path):
    """
    Extract text content from a HWP file.
    
    Args:
        hwp_path (str): Path to the HWP file
        
    Returns:
        str: Extracted text content
    """
    try:
        hwp = HwpFile(hwp_path)
        text = hwp.text
        hwp.close()
        return text
    except Exception as e:
        print(f"Error processing HWP file {hwp_path}: {str(e)}")
        return None

def process_hwp_file(hwp_path, output_path=None):
    """
    Process a HWP file and optionally save the extracted text to a file.
    
    Args:
        hwp_path (str): Path to the HWP file
        output_path (str, optional): Path to save the extracted text
        
    Returns:
        str: Extracted text content
    """
    text = extract_text_from_hwp(hwp_path)
    
    if text and output_path:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
        except Exception as e:
            print(f"Error saving text to {output_path}: {str(e)}")
    
    return text 