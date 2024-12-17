# Script to format stock data

def format_stock_numbers(input_file, output_file):
    stock_numbers = []
    
    # Read stock data line by line
    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:  # Skip empty lines
                try:
                    # Extract stock code
                    stock_code = line.split('\t')[0]
                    stock_numbers.append(stock_code)
                except ValueError:
                    print(f"Error processing line: {line}")

    # Write stock numbers to output file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("\n".join(stock_numbers))
        
    print(f"Stock numbers saved to: {output_file}")


# Example usage
input_file = 'raw_stock_data.txt'  # Input file containing your stock data
output_file = 'stock_numbers.txt'  # Output file
format_stock_numbers(input_file, output_file)
