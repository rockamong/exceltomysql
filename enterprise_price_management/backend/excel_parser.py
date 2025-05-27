import openpyxl

def parse_excel_data(file_stream):
    """
    Parses an Excel file stream to extract equipment data.

    Args:
        file_stream: A file-like object representing the Excel file.

    Returns:
        A list of dictionaries, where each dictionary contains data for one piece of equipment
        with keys "设备名称", "设备参数", "设备单价".

    Raises:
        ValueError: If the Excel file is missing required column headers 
                    or if the file cannot be processed.
    """
    try:
        # Load the workbook from the file stream
        workbook = openpyxl.load_workbook(file_stream)
        # Select the active worksheet
        sheet = workbook.active
    except Exception as e:
        raise ValueError(f"无法加载或处理Excel文件: {e}")

    # Get the header row
    header_row = [cell.value for cell in sheet[1]]

    # Define expected column headers
    expected_headers = ["设备名称", "设备参数", "设备单价"]
    column_indices = {}

    # Find column indices for the expected headers
    for header in expected_headers:
        try:
            column_indices[header] = header_row.index(header)
        except ValueError:
            # If a header is not found, raise an error
            missing_headers = ", ".join(h for h in expected_headers if h not in header_row)
            raise ValueError(f"Excel文件中缺少必要的列标题：{missing_headers}")

    # List to store extracted data
    extracted_data = []

    # Iterate through rows, starting from the second row (index 1, as sheet rows are 1-indexed)
    for row_idx in range(2, sheet.max_row + 1):
        row_data = {}
        # Get the current row
        current_row = sheet[row_idx]
        
        # Extract data for each expected header
        # Ensure cell values are read, handling potential None values
        shebei_mingcheng_val = current_row[column_indices["设备名称"]].value
        shebei_canshu_val = current_row[column_indices["设备参数"]].value
        shebei_danjia_val = current_row[column_indices["设备单价"]].value

        # Basic validation: ensure "设备名称" and "设备单价" are not empty
        # More complex validation can be added here if needed
        if shebei_mingcheng_val is None or str(shebei_mingcheng_val).strip() == "":
            # Potentially skip row or log a warning, for now, we skip if name is missing
            # print(f"Warning: Row {row_idx} is missing '设备名称'. Skipping.")
            continue
        if shebei_danjia_val is None:
            # Potentially skip row or log a warning, for now, we skip if price is missing
            # print(f"Warning: Row {row_idx} is missing '设备单价'. Skipping.")
            continue
            
        row_data["设备名称"] = str(shebei_mingcheng_val)
        # "设备参数" can be None or empty, so handle it gracefully
        row_data["设备参数"] = str(shebei_canshu_val) if shebei_canshu_val is not None else ""
        
        # Convert "设备单价" to float, handling potential errors
        try:
            row_data["设备单价"] = float(shebei_danjia_val)
        except (ValueError, TypeError):
            # print(f"Warning: Row {row_idx} has invalid '设备单价': {shebei_danjia_val}. Skipping.")
            # Depending on requirements, could raise error, skip, or use a default
            continue 

        extracted_data.append(row_data)

    return extracted_data

if __name__ == '__main__':
    # This part is for example usage and basic testing.
    # It requires an Excel file named 'test_data.xlsx' in the same directory.
    from io import BytesIO

    # Create a dummy Excel file in memory for testing
    try:
        from openpyxl import Workbook
        # Create a new workbook and select the active sheet
        wb_test = Workbook()
        ws_test = wb_test.active
        ws_test.title = "TestDataSheet"

        # Add headers
        ws_test.append(["设备名称", "设备参数", "设备单价", "其他列"])
        # Add data rows
        ws_test.append(["设备A", "参数A1, 参数A2", 100.50, "备注A"])
        ws_test.append(["设备B", "参数B1", 200.75, "备注B"])
        ws_test.append(["设备C", None, 300.00, "备注C"]) # Test with None parameter
        ws_test.append(["", "参数D1", 400.00, "备注D"]) # Test with empty name (should be skipped)
        ws_test.append(["设备E", "参数E1", None, "备注E"]) # Test with None price (should be skipped)
        ws_test.append(["设备F", "参数F1", "无效价格", "备注F"]) # Test with invalid price (should be skipped)
        ws_test.append(["设备G", "参数G1", 500, "备注G"])


        # Save to a BytesIO stream
        file_stream_test = BytesIO()
        wb_test.save(file_stream_test)
        file_stream_test.seek(0) # Reset stream position to the beginning

        print("Testing with in-memory Excel data...")
        parsed_data = parse_excel_data(file_stream_test)
        if parsed_data:
            print("Parsed data:")
            for item in parsed_data:
                print(item)
        else:
            print("No data was parsed.")

    except ImportError:
        print("openpyxl is not installed. Skipping in-memory test.")
    except ValueError as ve:
        print(f"ValueError during test: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred during test: {e}")

    print("\nTesting with missing headers (expecting ValueError):")
    try:
        from openpyxl import Workbook
        wb_missing = Workbook()
        ws_missing = wb_missing.active
        ws_missing.append(["设备名称", "参数", "单价"]) # Intentionally use wrong headers
        
        file_stream_missing = BytesIO()
        wb_missing.save(file_stream_missing)
        file_stream_missing.seek(0)
        
        parse_excel_data(file_stream_missing)
    except ValueError as e:
        print(f"Caught expected error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during missing header test: {e}")

    print("\nTesting with non-Excel file (expecting ValueError):")
    try:
        file_stream_invalid = BytesIO(b"This is not an excel file")
        parse_excel_data(file_stream_invalid)
    except ValueError as e:
        print(f"Caught expected error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during invalid file test: {e}")
