import random
from embed import read_png_signature, extract_png_info, decompress_idat_data

# Message extraction function compatible with distributed embedding
def extract_message_pixels(pixels, message_length):
    random.seed(100)  # Use the same seed as in the embedding function

    total_pixels = len(pixels)
    # Recompute the indices used for embedding
    indices = random.sample(range(total_pixels), message_length * 8) 

    message_bits = ''
    
    for pixel_index in indices:
        message_bits += str(pixels[pixel_index] & 1)  # Extract the least significant bit
    
    # Split the bits into bytes and convert to characters
    message = ''
    for i in range(0, len(message_bits), 8):
        byte = message_bits[i:i+8]
        if len(byte) < 8:
            break  # In case of an incomplete byte
        char = chr(int(byte, 2))
        if char == '\0':  # Null terminator found
            break
        message += char
    
    return message

# Main function to extract the embedded message from a PNG image
def main():
    input_filename = 'modified_image.png'
    estimated_message_length = 1000 # Adjust based on how many characters you expect to embed

    try:
        read_png_signature(input_filename)

        width, height, idat_chunks = extract_png_info(input_filename)

        decompressed_pixels = decompress_idat_data(idat_chunks)

        # Extract the embedded message
        embedded_message = extract_message_pixels(decompressed_pixels, estimated_message_length)
        print(f"Extracted message: {embedded_message}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
