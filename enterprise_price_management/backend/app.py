import os
import json
from flask import Flask, request, jsonify
from db_connector import get_db_config, update_db_config, get_db_connection
from excel_parser import parse_excel_data
import mysql.connector # Added for database operations

app = Flask(__name__)

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

def allowed_file(filename):
    """Checks if the filename has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/config/db', methods=['GET', 'POST'])
def manage_db_config():
    if request.method == 'GET':
        try:
            config = get_db_config()
            # Exclude password for security
            config_to_return = {k: v for k, v in config.items() if k != "DB_PASSWORD"}
            return jsonify(config_to_return), 200
        except Exception as e:
            # Log the exception e if a logger is configured
            print(f"Error getting DB config: {e}") # Basic logging
            return jsonify({"message": "获取数据库配置失败。"}), 500
            
    elif request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({"message": "请求数据为空。"}), 400
            
            success = update_db_config(data)
            if success:
                return jsonify({"message": "数据库配置已更新。"}), 200
            else:
                return jsonify({"message": "更新数据库配置失败。"}), 500
        except Exception as e:
            # Log the exception e
            print(f"Error updating DB config: {e}") # Basic logging
            return jsonify({"message": "更新数据库配置时发生内部错误。"}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handles file upload, parses Excel data, and inserts it into the database.
    """
    if 'file' not in request.files:
        return jsonify({"message": "没有文件被上传。"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"message": "没有选择文件。"}), 400 # Although 'file' key exists, no file was selected

    if file and allowed_file(file.filename):
        try:
            # Pass the file stream to the parser
            parsed_data = parse_excel_data(file.stream)
            if not parsed_data:
                return jsonify({"message": "Excel文件中没有找到有效数据或数据格式不正确。"}), 400
        except ValueError as e:
            # Handle errors from parse_excel_data (e.g., missing headers, wrong format)
            return jsonify({"message": f"解析Excel文件失败: {e}"}), 400
        except Exception as e:
            # Catch any other unexpected errors during parsing
            print(f"Unexpected error parsing Excel file: {e}") # Basic logging
            return jsonify({"message": f"处理文件时发生未知错误: {e}"}), 500

        conn = None # Initialize conn to None
        try:
            conn = get_db_connection()
            if conn is None:
                return jsonify({"message": "数据库连接失败。"}), 500

            cursor = conn.cursor()
            
            # SQL statement for inserting data
            insert_query = """
            INSERT INTO price (shebei_mingcheng, shebei_canshu, shebei_danjia)
            VALUES (%s, %s, %s)
            """
            
            # Use a transaction
            conn.start_transaction()
            
            inserted_count = 0
            for item in parsed_data:
                try:
                    cursor.execute(insert_query, (
                        item["设备名称"],
                        item["设备参数"],
                        item["设备单价"]
                    ))
                    inserted_count += 1
                except mysql.connector.Error as db_err:
                    # Log the database error
                    print(f"Database insert error: {db_err}") # Basic logging
                    # Rollback transaction on error
                    conn.rollback()
                    # Close cursor and connection
                    cursor.close()
                    conn.close()
                    return jsonify({"message": f"数据导入数据库时发生错误: {db_err}"}), 500
                except KeyError as ke:
                    # This might happen if parsed_data items don't have expected keys
                    conn.rollback()
                    cursor.close()
                    conn.close()
                    print(f"Missing key in parsed data: {ke}") # Basic logging
                    return jsonify({"message": f"解析数据中缺少键: {ke}，请检查Excel列标题是否正确。"}), 400


            # Commit the transaction if all inserts were successful
            conn.commit()
            
            return jsonify({"message": f"文件上传成功，导入了 {inserted_count} 条数据。"}), 201

        except mysql.connector.Error as err:
            # Log the database connection or operational error
            print(f"Database error: {err}") # Basic logging
            if conn and conn.is_connected(): # Check if conn is not None and connected
                 conn.rollback() # Rollback if transaction was started
            return jsonify({"message": f"数据库操作失败: {err}"}), 500
        except Exception as e:
            # Catch any other unexpected errors during database operations
            print(f"Unexpected error during database operation: {e}") # Basic logging
            if conn and conn.is_connected(): # Check if conn is not None and connected
                 conn.rollback()
            return jsonify({"message": "处理数据时发生未知内部错误。"}), 500
        finally:
            if conn and conn.is_connected():
                if 'cursor' in locals() and cursor: # Check if cursor was defined
                    cursor.close()
                conn.close()
                
    elif file and not allowed_file(file.filename):
        return jsonify({"message": "文件类型不支持，请上传Excel文件 (.xls, .xlsx)。"}), 400
    
    # Fallback for any other unhandled case, though should be covered by checks above
    return jsonify({"message": "文件上传失败，未知错误。"}), 500

@app.route('/search', methods=['GET'])
def search_devices():
    """
    Searches for devices in the database based on the deviceName query parameter.
    """
    query_param_name = 'deviceName' # Or 'shebei_mingcheng' if preferred for consistency
    search_term = request.args.get(query_param_name)

    if not search_term or search_term.strip() == "":
        return jsonify({"message": "请输入设备名称进行查询。"}), 400

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"message": "数据库连接失败。"}), 500

        cursor = conn.cursor(dictionary=True) # Use dictionary=True for easy dict conversion

        # Prepare SQL query using LIKE for partial matching
        # Ensure to sanitize search_term if it's directly used, though parameterization handles this
        query = "SELECT id, shebei_mingcheng, shebei_canshu, shebei_danjia, DATE_FORMAT(luru_shijian, '%Y-%m-%d %H:%i:%s') AS luru_shijian FROM price WHERE shebei_mingcheng LIKE %s"
        
        # Add '%' for wildcard search
        search_pattern = f"%{search_term}%"
        
        cursor.execute(query, (search_pattern,))
        
        results = cursor.fetchall()

        # Format 'shebei_danjia' as string to maintain precision
        for row in results:
            if row['shebei_danjia'] is not None:
                row['shebei_danjia'] = str(row['shebei_danjia'])
            # luru_shijian is already formatted by DATE_FORMAT in SQL

        if not results:
            # For consistency with frontend expectations (which now also look for direct array or specific message)
            # it might be better to return an empty list directly if that's the preferred "no results" signal,
            # or ensure the message structure is distinct.
            # However, the task focuses on *successful search with results*.
            # The previous frontend change (turn 32) handles `!results || results.length === 0`
            # and uses a default '未找到相关设备信息。' message.
            # So, returning an empty list for "no results" is fine.
            return jsonify([]), 200 # Return empty list for no results
        
        # Results found, return the list of results directly
        return jsonify(results), 200

    except mysql.connector.Error as err:
        print(f"Database search error: {err}") # Basic logging
        return jsonify({"message": f"数据库查询失败: {err}"}), 500
    except Exception as e:
        print(f"Unexpected error during search: {e}") # Basic logging
        return jsonify({"message": "查询过程中发生未知错误。"}), 500
    finally:
        if conn and conn.is_connected():
            if 'cursor' in locals() and cursor:
                cursor.close()
            conn.close()

if __name__ == '__main__':
    # Make sure the script is run from the backend directory for correct module imports
    # For production, use a proper WSGI server like Gunicorn or uWSGI
    app.run(debug=True, host='0.0.0.0', port=5000)
