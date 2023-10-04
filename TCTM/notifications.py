import frappe
from .write_log import write_log

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False


@frappe.whitelist(allow_guest=True)
def all_notifications(member_id):
    
    parameterList = [member_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}
    
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    limit = 20
    
    try:
        
        noti_query = """
                    SELECT noti_id,title,read_status,link_url,creation FROM `tabnotifications`
                    WHERE send_to = %s AND is_delete = 0
                    ORDER BY read_status ASC, creation DESC
                    LIMIT %s;
                """
        alert_query = """
                    SELECT COUNT(read_status) AS count_state
                    FROM tabnotifications
                    WHERE read_status = 0 AND send_to = %s
                """
                
        
        result_list = frappe.db.sql(noti_query, (member_id, limit),as_dict=1)
        alert_status = frappe.db.sql(alert_query, (member_id),as_dict=1) # Status 0 is not read
        
        if alert_status[0].count_state > 0: 
            alert_status_display = True # Set a variable to display red
            if alert_status[0].count_state > limit:
                alert_status[0].count_state = limit
        else: alert_status_display = False
        
        if len(result_list) == 0:
            return {"stausCode": "404", "message": "Not Found"}
        else:
            return {
                "stausCode": "200", 
                "message": "OK", 
                "Alert":alert_status_display,
                "Noread":alert_status[0].count_state,
                "Data": result_list
                }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }
    
@frappe.whitelist(allow_guest=True)
def read_noti(noti_id):

    parameterList = [noti_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}
    
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:
        
        # Get Doctype at noti_id
        noti = frappe.get_doc("notifications", noti_id)

        # Update readed_status
        noti.read_status = 1 # status 1 is readed
        noti.save(ignore_permissions=True)

        return {"StatusCode": "200", "Message": "OK", "Data": "Notification marked as read"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }
    
@frappe.whitelist(allow_guest=True)
def read_all_noti(member_id):

    parameterList = [member_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}
    
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:
        
        update_status = """
                    UPDATE `tabnotifications`
                    SET read_status = 1
                    WHERE send_to = %s;
                """
        frappe.db.sql(update_status, (member_id),as_dict=1)

        return {"StatusCode": "200", "Message": "Update All Notification Status to Read Successfully"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }

####### POST #########s

# Noti Chat 

def post_new_chat(recipient, req_id, sub_id):
    member_id = recipient
    parameterList = [member_id, req_id, sub_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}
    
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:
        
        if "SUP" in member_id:
            
            fild_member_id = """
                    SELECT mem.name FROM `tabsuppliers` AS `sup`
                    INNER JOIN `tabmembers` AS `mem` 
                    ON sup.name = mem.sub_id
                    WHERE sup.name = %s
                """
            result_member_id = frappe.db.sql(fild_member_id, (member_id),as_dict=1)
            
            if len(result_member_id) > 0:
                member_id = result_member_id[0].name
                url = "/market/port-detail-marker/?req_id={}&sub_id={}&member_id2={}".format(req_id, sub_id, member_id)
                
            # /member/port-detail-member/?req_id=REQ-100&sub_id=SUP-11
        else: 
            url = "/member/port-detail-member/?req_id={}&sub_id={}".format(req_id, sub_id)
            
        # Insert new noti 
        noti_doc = frappe.get_doc(
                {
                    "doctype": "notifications",
                    "noti_id": "",
                    "send_to": member_id,
                    "title": "You have new a massages in {}".format(req_id), 
                    "link_url": url
                }
            )
        noti_doc.insert(ignore_permissions=True)

        # Update the noti_id column with the value of the name
        noti_doc.noti_id = noti_doc.name
        noti_doc.save(ignore_permissions=True)
        
        write_log("In requiremenet {}, new chat between {} and {} created".format(req_id, member_id))
        return {"StatusCode": "200", "Message": "Posted"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("Error occured while posting new chat: {}".format(str(e)))
        # Return an appropriate error message
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }


# Nodi new order market
def post_noti_market(sup_id, text_description, url):

    if Api_Maintenance or Server_Maintenance:
        return False

    try:
       
        fild_member_id = """
                    SELECT member_id FROM `tabmembers`
                    WHERE sub_id = %s
                """
        result_member_id = frappe.db.sql(fild_member_id, (sup_id),as_dict=1)
       
        member_id = result_member_id[0].member_id
        
            # Insert new noti 
        noti_doc = frappe.get_doc(
                {
                    "doctype": "notifications",
                    "noti_id": "",
                    "send_to": member_id,
                    "title": text_description, 
                    "link_url": url
                }
            )
        noti_doc.insert(ignore_permissions=True)

            # Update the noti_id column with the value of the name
        noti_doc.noti_id = noti_doc.name
        noti_doc.save(ignore_permissions=True)
                
        return True

    except Exception as e:
        # Log the error for debugging purposes if needed
        return False
    
# Updata status invoice
def post_noti_member(member_id, text_description, url):

    if Api_Maintenance or Server_Maintenance:
        return False

    try:

            # Insert new noti 
        noti_doc = frappe.get_doc(
                {
                    "doctype": "notifications",
                    "noti_id": "",
                    "send_to": member_id,
                    "title": text_description, 
                    "link_url": url
                }
            )
        noti_doc.insert(ignore_permissions=True)

            # Update the noti_id column with the value of the name
        noti_doc.noti_id = noti_doc.name
        noti_doc.save(ignore_permissions=True)
                
        return True

    except Exception as e:
        # Log the error for debugging purposes if needed
        return e