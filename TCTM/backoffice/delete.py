import frappe
from ..write_log import write_log

###########################################################################################################################
################################################### DELETE  ###############################################################
###########################################################################################################################

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False

@frappe.whitelist(allow_guest=True)
def ban(table, primary):

    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}

    parameterList = [table, primary]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        
        query =""" UPDATE `%s` SET is_deleted = 1 WHERE name = "%s"  """ %(table, primary)
                
        frappe.db.sql(query, as_dict=1)
        
        write_log("Admin call api delete data in table {} with primary {}".format(table, primary))
        
        return {"statusCode": 200, "message": "Delete Success"}


    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("Admin call api delete data in table {} with primary {} but error {}".format(table, primary, str(e)))
        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}
    
@frappe.whitelist(allow_guest=True)
def unban(table, primary):

    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}

    parameterList = [table, primary]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        
        query =""" UPDATE `%s` SET is_deleted = 0 WHERE name = "%s"  """ %(table, primary)
                
        frappe.db.sql(query, as_dict=1)

        write_log("Admin call api unban data in table {} with primary {}".format(table, primary))
        
        return {"statusCode": 200, "message": "Delete Success"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("Admin call api unban data in table {} with primary {} but error {}".format(table, primary, str(e)))
        
        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}
    
    
    
