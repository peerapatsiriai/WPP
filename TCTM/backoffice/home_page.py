import frappe
from ..write_log import write_log

###########################################################################################################################
################################################## Home Page ##########################################################
###########################################################################################################################

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False


# All Billboard
@frappe.whitelist(allow_guest=True)
def all_billboard():

    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    try:
        # Get all billboard
        query = """
                    SELECT * FROM `tabbillboards`
                """
        data = frappe.db.sql(query, as_dict=1)
        
        if(len(data) == 0):
            write_log("Admin call api get all bill board but not found any data.")
            return { "stausCode":"404", "message":"Not Found" }
        else:
            
            write_log("Admin call api get all bill board")
            
            return { "stausCode":"200", "message":"OK", "Data": data }
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")
        
        write_log("Admin call api all_billboard but errer {}".format(str(e)))
        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}
       
# Billboard active
@frappe.whitelist(allow_guest=True)
def active_bill_board(bill_id):
    
    parameterList = [bill_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    if Api_Maintenance or Server_Maintenance:
        return {"StatusCode": "503", "Message": "This API is currently under maintenance."}
    
    try:
        
        # Get Doctype at bill_id
        bill_doc = frappe.get_doc("billboards", bill_id)

        # Update billboard status
        bill_doc.bill_status = 1 # status 1 is show is billboard
        bill_doc.save(ignore_permissions=True)
     
        write_log("Admin active billboard id {}".format(bill_id))
        return {"StatusCode": "200", "Message": "OK", "Data": "Active Success"}
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("Admin call api active_bill_board but errer {}".format(str(e)))
        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}

# Billboard unactive
@frappe.whitelist(allow_guest=True)
def unactive_bill_board(bill_id):
    
    parameterList = [bill_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    if Api_Maintenance or Server_Maintenance:
        return {"StatusCode": "503", "Message": "This API is currently under maintenance."}
    
    try:
        
        # Get Doctype at bill_id
        bill_doc = frappe.get_doc("billboards", bill_id)

        # Update billboard status 
        bill_doc.bill_status = 0 # status 0 is not show this billboard
        bill_doc.save(ignore_permissions=True)

        write_log("Admin unactive billboard id {}".format(bill_id))
        
        return {"StatusCode": "200", "Message": "OK", "Data": "Unactive success"}
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("Admin call api unactive_bill_board but errer {}".format(str(e)))
        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}

############################################################################################################################
       
# Market active
@frappe.whitelist(allow_guest=True)
def market_active(sub_id):
    
    parameterList = [sub_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    if Api_Maintenance or Server_Maintenance:
        return {"StatusCode": "503", "Message": "This API is currently under maintenance."}
    
    try:
        
        # Get Doctype at sub_id
        sub_doc = frappe.get_doc("suppliers", sub_id)

        # Update Market status 
        sub_doc.sub_status = 3 # status 3 is market recommend
        sub_doc.save(ignore_permissions=True)

        write_log("Admin active market id {}".format(sub_id))
        
        return {"StatusCode": "200", "Message": "OK", "Data": "Active Success"}
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("Admin call api market_active but errer {}".format(str(e)))
        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}

# Market unactive
@frappe.whitelist(allow_guest=True)
def market_unactive(sub_id):
    
    parameterList = [sub_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    if Api_Maintenance or Server_Maintenance:
        return {"StatusCode": "503", "Message": "This API is currently under maintenance."}
    
    try:
        
        # Get Doctype at sub_id
        sub_doc = frappe.get_doc("suppliers", sub_id)

        # Update market status from 1 to 2
        sub_doc.sub_status = 2 # status 2 is normal market
        sub_doc.save(ignore_permissions=True)

        write_log("Admin unactive market id {}".format(sub_id))
        
        return {"StatusCode": "200", "Message": "OK", "Data": "UnActive Success"}
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("Admin call api market_unactive but errer {}".format(str(e)))
        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}

############################################################################################################################

# Product active
@frappe.whitelist(allow_guest=True)
def product_active(product_id):
    
    parameterList = [product_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    if Api_Maintenance or Server_Maintenance:
        return {"StatusCode": "503", "Message": "This API is currently under maintenance."}
    
    try:
        
        # Get Doctype at product_id
        product_doc = frappe.get_doc("products", product_id)

        # Update product status
        product_doc.product_status = 3 # status 3 is product recommend
        product_doc.save(ignore_permissions=True)

        write_log("Admin active product id {}".format(product_id))
        
        return {"StatusCode": "200", "Message": "OK", "Data": "Active Success"}
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("Admin call api product_active but errer {}".format(str(e)))
        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}

# Product unactive
@frappe.whitelist(allow_guest=True)
def product_unactive(product_id):
    
    parameterList = [product_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    if Api_Maintenance or Server_Maintenance:
        return {"StatusCode": "503", "Message": "This API is currently under maintenance."}
    
    try:
        
        # Get Doctype at product_id
        product_doc = frappe.get_doc("products", product_id)

        # Update product status from 
        product_doc.product_status = 2 # status 2 is normal product
        product_doc.save(ignore_permissions=True)

        write_log("Admin unactive product id {}".format(product_id))
        
        return {"StatusCode": "200", "Message": "OK", "Data": "UnActive Success"}
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("Admin call api product_unactive but errer {}".format(str(e)))
        
        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}
