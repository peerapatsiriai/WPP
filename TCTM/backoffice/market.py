import frappe
from ..write_log import write_log

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False

@frappe.whitelist(allow_guest=True)
def allmarket():

    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    try:
        # Find All market in system no condition
        query = """
                    SELECT sup.sub_id, sub_name, sub_status, mem.member_id,user_first_name, user_last_name, user_company, sup.is_delete FROM `tabsuppliers` AS `sup`
                    INNER JOIN `tabmembers` AS `mem`
                    ON sup.sub_id = mem.sub_id
                    ORDER BY sup.creation DESC
                """
        queue = frappe.db.sql(query, as_dict=1)
        
        if(len(queue) == 0):
            write_log("Admin call api all market but not found any data.")
            return { "stausCode":"404", "message":"Not Found" }
        else:
            write_log("Admin call api all market")
            return { "stausCode":"200", "message":"OK", "Data": queue }
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("Admin call api all market but errer {}".format(str(e)))
        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}
    

### Ban
@frappe.whitelist(allow_guest=True)
def banmarket(sub_id):

    parameterList = [sub_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    try:
        # update status market = 0. status 0 is this market is baned
        query = """  UPDATE `tabsuppliers` SET sub_status = 0 WHERE name = "%s" """%(sub_id)
        frappe.db.sql(query, as_dict=1)
        
         # Find relation of market with member and update user status
        member_doc = frappe.get_all("members", filters={"sub_id": sub_id}, limit=1)

        if member_doc:
            member_doc = frappe.get_doc("members", member_doc[0].name)  # Fetch the existing member document

            # Update user status 
            member_doc.user_status = 1  # status 1 is this uesr is don't have market
            member_doc.save(ignore_permissions=True)  # Save the changes to the existing document

        write_log("Admin ban market {} ".format(sub_id))
        return { "stausCode":"200", "message":"Baned" }
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("Admin ban market but errer {}".format(str(e)))
        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}

### Un Ban
@frappe.whitelist(allow_guest=True)
def unbanmarket(sub_id):

    parameterList = [sub_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}

    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    try:
        # Find market at sub_id and update market status = 1. status 1 is wait for approve
        query = """  UPDATE `tabsuppliers` SET sub_status = 1 WHERE name = "%s" """%(sub_id)
        frappe.db.sql(query, as_dict=1)

        # Find Doctype at sub_id and update user status
        member_doc = frappe.get_all("members", filters={"sub_id": sub_id}, limit=1)

        if member_doc:
            member_doc = frappe.get_doc("members", member_doc[0].name)  # Fetch the existing member document

            # Update user status
            member_doc.user_status = 2  # status 2 is this user have market
            member_doc.save(ignore_permissions=True)  # Save the changes to the existing document
            
        write_log("Admin unban market {} ".format(sub_id))
        
        return { "stausCode":"200", "message":"Un Baned" }
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("Admin unban market but errer {}".format(str(e)))
        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}