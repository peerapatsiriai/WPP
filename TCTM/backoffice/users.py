import frappe
from ..write_log import write_log

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False


# User queue
@frappe.whitelist(allow_guest=True)
def alluser():

    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    try:
        # Get all user in system not condition
        query = """
                    SELECT ac.account_id, account_status, mem.member_id, mem.sub_id,  user_first_name, user_last_name, user_company, user_status,user_role, mem.is_delete FROM `tabmembers` AS `mem`
                    INNER JOIN `tabaccounts` AS `ac`
                    ON ac.account_id = mem.account_id
                    WHERE user_role != 'ADMIN'
                    ORDER BY ac.creation DESC
                """
        queue = frappe.db.sql(query, as_dict=1)
        
        if(len(queue) == 0):
            write_log("Admin API called api get all data but not found any data.")
            return { "stausCode":"404", "message":"Not Found" }
        else:
            write_log("Admin API called api get all user data")
            return { "stausCode":"200", "message":"OK", "Data": queue }
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}
    
### Ban User
@frappe.whitelist(allow_guest=True)
def banuser(user_id,account_id):
    
    parameterList = [user_id, account_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}

    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    try:
        # Update account status. status 0 is baned
        query = """  UPDATE `tabaccounts` SET account_status = 0 WHERE name = "%s" """%(account_id)
        frappe.db.sql(query, as_dict=1)
        
        write_log("Admin ban user {} account {}".format(user_id, account_id))
        return { "stausCode":"200", "message":"Baned" }
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}

### Un Ban user
@frappe.whitelist(allow_guest=True)
def unbanuser(user_id,account_id):

    parameterList = [user_id, account_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}

    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    try:
        
        # Update account status at account_id. status 1 is wait for approve
        query = """  UPDATE `tabaccounts` SET account_status = 1 WHERE name = "%s" """%(account_id)
        frappe.db.sql(query, as_dict=1)

        write_log("Admin Unban user {} account {}".format(user_id, account_id))
        return { "stausCode":"200", "message":"UN Baned" }
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}

