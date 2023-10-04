import frappe


Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False

## CRUD product category in system ##

@frappe.whitelist(allow_guest=True)
def allcategorys():

    # Check for maintenance mode
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:

        query = """
                    SELECT category_id, category_name FROM `tabcategorys` WHERE is_delete = '0'
                """
        category_list = frappe.db.sql(query, as_dict=1) # Get all product category in system condition is not deleted

        if len(category_list) == 0:
            return {"stausCode": "404", "message": "Not Found"}
        else:
            return {"stausCode": "200", "message": "OK", "Data": category_list}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {
            "statusCode": 500,
            "message": frappe.log_error(f"An error occurred: {str(e)}"),
        }


@frappe.whitelist(allow_guest=True)
def addcategory(category_name):

    parameterList = [category_name]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}

    # Check for maintenance mode
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:

        # Insert new category in system
        doc = frappe.get_doc(
            {
                "doctype": "categorys",
                "category_id": "",
                "category_name": category_name,
            }
        )
        doc.insert(ignore_permissions=True)

        # Update the category_id column with the value of the name
        doc.category_id = doc.name
        doc.save(ignore_permissions=True)

        return { "stausCode": "200", "message": "Insert Success" }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {
            "statusCode": 500,
            "message": frappe.log_error(f"An error occurred: {str(e)}"),
        }


@frappe.whitelist(allow_guest=True)
def editcategory(category_id, category_name):
    
    parameterList = [category_id, category_name]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}
    
    # Check for maintenance mode
        if Api_Maintenance or Server_Maintenance:
            return { "statusCode": "503", "message": "This API is currently under maintenance." }
    
    try:

        # Get the category document with category_id
        doc = frappe.get_doc("categorys", category_id)

        # Update the category_name and save the document
        doc.category_name = category_name
        doc.save(ignore_permissions=True)

        # Return a success response
        return {"statusCode": "200", "message": "Update Success"}

    except Exception as e:
        # Log the error for debugging purposes
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return { "statusCode": "500", "message": "An error occurred. Please contact support for assistance." }


@frappe.whitelist(allow_guest=True)
def deletecategory(category_id):
    
    parameterList = [category_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}
    
    # Check for maintenance mode
        if Api_Maintenance or Server_Maintenance:
            return { "statusCode": "503", "message": "This API is currently under maintenance." }
    
    try:

        # Get Doctype at category_id
        account = frappe.get_doc("categorys", category_id)

        # Update status is_delete = 1
        account.is_delete = 1
        account.save(ignore_permissions=True)

        # Return a success response
        return {"statusCode": "200", "message": "Deleted Success"}

    except Exception as e:
        # Log the error for debugging purposes
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return { "statusCode": "500", "message": "An error occurred. Please contact support for assistance." }
