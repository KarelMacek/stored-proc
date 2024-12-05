from util import get_db_connection, run_and_print_provisions

def main():
    connection = None
    try:
        connection = get_db_connection()
        print("Connected to the database.")
        
        print("\nCalculating provisions for Agent 1 (Alice)...")
        run_and_print_provisions(connection, 1)
        
        print("\nCalculating provisions for Agent 2 (Bob)...")
        run_and_print_provisions(connection, 2)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection:
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    print("Starting provision calculations...")
    main()
    print("Calculations completed.")
