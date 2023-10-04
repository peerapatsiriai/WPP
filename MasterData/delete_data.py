import frappe

###########################################################################################################################
################################################### DELETE  ###############################################################
###########################################################################################################################

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False

# DELETE http://111.223.38.19/api/method/frappe.API.MasterData.delete.delete
@frappe.whitelist(allow_guest=True)
def delete(table, primary):

    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}

    parameterList = [table, primary]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        
        query =""" UPDATE `%s` SET is_deleted = 1 WHERE name = "%s"  """ %(table, primary)
                
        frappe.db.sql(query, as_dict=1)
        
        return {"statusCode": 200, "message": "Delete Success"}


    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}
    
    
    
# DELETE http://111.223.38.19/api/method/frappe.API.MasterData.delete.delete
@frappe.whitelist(allow_guest=True)
def trulydelete(table, primary):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [table, primary]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        
        query = """ DELETE FROM `%s` WHERE name = "%s" """ % (table, primary) 
                
        frappe.db.sql(query, as_dict=1)
        
        return {"statusCode": 200, "message": "Delete Success"}


    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}