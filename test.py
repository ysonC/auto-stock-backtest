from halo import Halo
import time

# Example 1: Basic Spinner with Success
def basic_spinner_demo():
    spinner = Halo(text='Loading...', spinner='dots')
    spinner.start()
    time.sleep(2)  # Simulate work
    spinner.succeed('Loaded successfully!')

# Example 2: Custom Spinner with Warning
def custom_spinner_demo():
    custom_spinner = {
        'interval': 100,  # Animation speed in milliseconds
        'frames': ['-', '\\', '|', '/']  # Custom frames
    }
    spinner = Halo(text='Working with custom spinner...', spinner=custom_spinner, color='yellow')
    spinner.start()
    time.sleep(2)  # Simulate work
    spinner.warn('Check your input!')

# Example 3: Info Message and Failure
def info_and_failure_demo():
    spinner = Halo(text='Connecting...', spinner='dots', color='blue')
    spinner.start()
    time.sleep(2)  # Simulate connection
    spinner.info('Connection established.')
    spinner.text = 'Downloading files...'
    spinner.start()
    time.sleep(2)  # Simulate download
    spinner.fail('Download failed!')

# Example 4: Persistent Custom Symbol
def stop_and_persist_demo():
    spinner = Halo(text='Processing...', spinner='dots', color='green')
    spinner.start()
    time.sleep(2)  # Simulate work
    spinner.stop_and_persist(symbol='✔', text='Processing completed!')

# Example 5: Multiple Spinners with Different Styles
def multiple_spinners_demo():
    spinners = [
        Halo(text='Task 1: Loading...', spinner='dots', color='cyan'),
        Halo(text='Task 2: Fetching data...', spinner='line', color='magenta'),
        Halo(text='Task 3: Processing...', spinner='bouncingBar', color='green'),
    ]
    for spinner in spinners:
        spinner.start()
        time.sleep(1)  # Simulate work
        spinner.succeed(f"{spinner.text.split(':')[0]} completed!")

# Main Function to Compare All Examples
def main():
    print("\n--- Basic Spinner Demo ---")
    basic_spinner_demo()

    print("\n--- Custom Spinner Demo ---")
    custom_spinner_demo()

    print("\n--- Info and Failure Demo ---")
    info_and_failure_demo()

    print("\n--- Stop and Persist Demo ---")
    stop_and_persist_demo()

    print("\n--- Multiple Spinners Demo ---")
    multiple_spinners_demo()

if __name__ == "__main__":
    main()