import frappe
from .write_log import write_log

from .notifications import post_noti_member
from .notifications import post_noti_market
from .notifications import post_new_chat

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False


############################################## Member Requirement ##############################################

# Get All requirement of one user list
@frappe.whitelist(allow_guest=True)
def allrequirement(user_id):
    
    parameterList = [user_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}
    
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:

        query = """ 
                    SELECT * 
                    FROM `tabrequirements` 
                    WHERE is_delete = "0" AND member_id = %s  AND req_status > 0
                """

        requirement_list = frappe.db.sql(query, (user_id),as_dict=1)

        if len(requirement_list) == 0:
            return {"stausCode": "404", "message": "Not Found"}
        else:
            return {"stausCode": "200", "message": "OK", "Data": requirement_list}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message res.status(400)
        return { "statusCode": 500,"message": frappe.log_error(f"An error occurred: {str(e)}") }
    
# Get All requirement of one Market list
@frappe.whitelist(allow_guest=True)
def allrequirement_inone_market(sub_id):
    
    parameterList = [sub_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}
    
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:

        query = """ 
                    SELECT * 
                    FROM `tabrequirements`   
                    WHERE is_delete = "0" AND sub_id = %s  AND req_status > 1
                """

        requirement_list = frappe.db.sql(query, (sub_id),as_dict=1)

        if len(requirement_list) == 0:
            return {"stausCode": "404", "message": "Not Found"}
        else:
            return {"stausCode": "200", "message": "OK", "Data": requirement_list}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message res.status(400)
        return { "statusCode": 500,"message": frappe.log_error(f"An error occurred: {str(e)}") }

# Delete Requirement
@frappe.whitelist(allow_guest=True)
def deleterequirement(req_id):
    
    parameterList = [req_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}
    
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:

        query = """                
                    UPDATE tabrequirements
                    SET is_delete = 1
                    WHERE req_id = %s
                """ 

        frappe.db.sql(query, (req_id),as_dict=1)

        write_log("Your Requirement {} have been reject by TCTM ".format(req_id))
        return {"stausCode": "200", "message": "Deleted"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message res.status(400)
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }
    
# Post new Requirement
@frappe.whitelist(allow_guest=True)
def postrequirement(req_header, req_description, user_id):

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    parameterList = [req_header, req_description]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}

    try:

        # Insert new req and get pk insert in tb requirements
        req_doc = frappe.get_doc(
            {
                "doctype": "requirements",
                "req_header": req_header,
                "req_description": req_description,
                "member_id": user_id,
                "req_status": 1, # status 1 is wait for approve
            }
        )
        req_doc.insert(ignore_permissions=True)

        # Update the req_id column with the value of the name
        req_doc.req_id = req_doc.name
        req_doc.save(ignore_permissions=True)

        write_log("User {} post new requirement successfully".format(user_id))
        return {"StatusCode": 201, "Message": "Posted Success"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("User {} post new requirement failed".format(user_id))
        # Return an appropriate error message
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}

# Edit Requirement
@frappe.whitelist(allow_guest=True)
def editrequirement(req_id, req_header,req_description):

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    parameterList = [req_id, req_header, req_description]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}

    try:

        # Get Doctype at req_id
        req_doc = frappe.get_doc("requirements", req_id)

        # Update requirement
        req_doc.req_header = req_header
        req_doc.req_description = req_description
        req_doc.save(ignore_permissions=True)

        write_log("Requirement {} updated successfully".format(req_id))
        return {"StatusCode": 201, "Message": "Edit Success"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("User {} failed to edit requirement {}".format(user_id, req_id))
        # Return an appropriate error message
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}

############ Requirement Detail ##################

# Requirement Detail
@frappe.whitelist(allow_guest=True)
def requirement_detail(req_id):
    
    parameterList = [req_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}
    
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:

        data_requirement_query = """ SELECT * FROM `tabrequirements` AS req 
                                    INNER JOIN `tabmembers` AS mem 
                                    ON req.member_id = mem.member_id 
                                    INNER JOIN `tabsuppliers` AS `sup`
                                    ON sup.sub_id = req.sub_id
                                    WHERE req_id = %s 
                                 """ 
        
        po_query = """ SELECT po_id, po_file_name, po_status FROM `tabpurchaseorder` WHERE po_requirement = %s AND is_delete != 1 ORDER BY po_id ASC """
        
        question_query = """ 
                            SELECT q.query_id, q.sender, q.recipient, m.user_first_name, m.user_last_name, s.sub_name, q.query_description,
                            q.query_status, q.query_status_readed, q.query_status_respond, q.creation
                            FROM tabquery AS q
                            INNER JOIN tabmembers AS m ON q.sender = m.member_id OR q.recipient = m.member_id
                            INNER JOIN tabsuppliers AS s ON q.sender = s.sub_id OR q.recipient = s.sub_id
                            WHERE q.req_id = %s AND q.is_delete = 0
                            ORDER BY q.creation ASC;
                         """
        
        
        data_requirement = frappe.db.sql(data_requirement_query, (req_id),as_dict=1)
        data_po = frappe.db.sql(po_query, (req_id),as_dict=1)
        data_question = frappe.db.sql(question_query, (req_id),as_dict=1)
        
        if len(data_requirement) == 0:
            return {"stausCode": "404", "message": "Not Found"}
        else:
            return {
                "stausCode": "200", 
                "message": "Query Success", 
                "Requirement_Data": data_requirement,
                "Po_List": data_po,
                "Question_List": data_question
                }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message res.status(400)
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }

# Post new chat
@frappe.whitelist(allow_guest=True)
def postchat(req_id, sender, recipient, query_description):

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    parameterList = [req_id, sender, recipient, query_description]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}

    try:
        # Get Data requiremnet use in send notificotion 
        req_doc = frappe.get_doc("requirements", req_id)
        
        # Insert new chat in this query
        qus_doc = frappe.get_doc(
            {
                "doctype": "query",
                "req_id": req_id,
                "sender": sender,
                "recipient": recipient,
                "query_description": query_description, 
                "query_status":1 # status 1 is normal
            }
        )
        qus_doc.insert(ignore_permissions=True)

        # Update the req_id column with the value of the name
        qus_doc.query_id = qus_doc.name
        
        
        # Get Data requiremnet use in send notificotion 
        req_doc = frappe.get_doc("requirements", req_id)
        
        # sent noti to recipient
        if "SUP" in sender:
            # ถ้าร้านเป็นคนส่ง
            url = "/member/port-detail-member/?req_id={}&sub_id={}".format(req_id, req_doc.sub_id)
            post_noti_member(req_doc.member_id, "You have new message from supplier in order {}".format(req_id), url)
            
            qus_doc.sender = req_doc.sub_id
            qus_doc.recipient = req_doc.member_id
            write_log("New chat posted successfully for requirement {} sended by {} to {}".format(req_id, req_doc.sub_id, req_doc.member_id))
            
        else:
            # ถ้าลูกค้าเป็นคนส่ง
            url = "/market/port-detail-marker/?req_id={}&sub_id={}&member_id2={}".format(req_id, req_doc.sub_id, req_doc.member_id)
            post_noti_market(req_doc.sub_id, "You have new message customer in order {}".format(req_id), url)
            
            qus_doc.sender = req_doc.member_id
            qus_doc.recipient = req_doc.sub_id
            write_log("New chat posted successfully for requirement {} sended by {} to {}".format(req_id, req_doc.member_id, req_doc.sub_id))
            
        qus_doc.save(ignore_permissions=True)
        
        
        return {"StatusCode": 201, "Message": "Posted Success"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("User {} failed to post chat for requirement {} sended by {} to {}".format(req_id, sender, recipient))
        # Return an appropriate error message
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}

# Delete chat
@frappe.whitelist(allow_guest=True)
def deletechat(query_id):
    
    parameterList = [query_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}
    
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:

        query = """                
                    UPDATE tabquery
                    SET is_delete = 1
                    WHERE query_id = %s
                """ 

        frappe.db.sql(query, (query_id),as_dict=1)

        write_log("Chat with ID {} deleted successfully".format(query_id))
        return {"stausCode": "200", "message": "Deleted"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("User failed to delete chat with ID {}".format(query_id))
        # Return an appropriate error message res.status(400)
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }
    
#################### PO ########################

# Sup Add new PO
@frappe.whitelist(allow_guest=True)
def addnew_po(member_id, sub_id, po_requirement, po_file_name):

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    parameterList = [member_id, sub_id, po_requirement, po_file_name]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}

    try:

        # Insert new PO
        po_doc = frappe.get_doc(
            {
                "doctype": "purchaseorder",
                "member_id": member_id,
                "sub_id": sub_id,
                "po_requirement": po_requirement,
                "po_file_name": po_file_name,
                "po_status":1
            }
        )
        po_doc.insert(ignore_permissions=True)

        # Update the po_id column with the value of the name
        po_doc.po_id = po_doc.name
        po_doc.save(ignore_permissions=True)
        
        # GEt member fo custommer from
        req_doc = frappe.get_doc("requirements", po_requirement)
        
        url = "/member/port-detail-member/?req_id={}&sub_id={}".format(po_requirement, sub_id)
        post_noti_member(req_doc.member_id, "Market send offer PO in your requirement {}".format(po_requirement), url)

        write_log("New PO added successfully in {} for member {} sub {}".format(po_requirement, member_id, sub_id))
        return {"StatusCode": 201, "Message": "Posted Success"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")
        
        write_log("User failed to delete chat with ID {}".format(query_id))
        # Return an appropriate error message
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}

# Sup Delete PO
@frappe.whitelist(allow_guest=True)
def delete_po(po_id):
    
    parameterList = [po_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}
    
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:

        query = """                
                    UPDATE tabpurchaseorder
                    SET is_delete = 1
                    WHERE po_id = %s
                """ 

        frappe.db.sql(query, (po_id),as_dict=1)

        write_log("PO with ID {} deleted successfully".format(po_id))
        return {"stausCode": "200", "message": "Deleted"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("User failed to delete PO with ID {}".format(po_id))
        # Return an appropriate error message res.status(400)
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }

# Mem Approve PO
@frappe.whitelist(allow_guest=True)
def approve_po(po_id, req_id):
    
    parameterList = [po_id, req_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}
    
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:
        # Status 2 is approved
        query1 = """                
                    UPDATE tabpurchaseorder
                    SET po_status = 2
                    WHERE po_id = %s
                """ 
        # Update status of requirement
        # Status 3 is Requirement Completed
        query2 = """                
                    UPDATE tabrequirements
                    SET req_status = 3
                    WHERE req_id = %s
                """ 

        frappe.db.sql(query1, (po_id),as_dict=1)
        frappe.db.sql(query2, (req_id),as_dict=1)

        # Get data of po
        po_doc = frappe.get_doc("purchaseorder", po_id)
        
        url = "/market/port-detail-marker/?req_id={}&sub_id={}&member_id2={}".format(po_doc.po_requirement, po_doc.sub_id, po_doc.member_id)
        post_noti_market(po_doc.sub_id, "Youl PO have been Approve from requiremnet {}".format(po_doc.po_requirement), url)

        write_log("PO with ID {} approved successfully".format(po_id))
        return {"stausCode": "200", "message": "Approved"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("Failed to approve PO with ID {}".format(po_id))
        # Return an appropriate error message res.status(400)
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }

# Mem Reject PO
@frappe.whitelist(allow_guest=True)
def reject_po(po_id):
    
    parameterList = [po_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"StatusCode": 400, "Message": "Invalid parameters"}
    
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:
        # status 0 is Reject
        query = """                
                    UPDATE tabpurchaseorder
                    SET po_status = 0
                    WHERE po_id = %s
                """ 

        frappe.db.sql(query, (po_id),as_dict=1)

        # Get data of po
        po_doc = frappe.get_doc("purchaseorder", po_id)
        
        url = "/market/port-detail-marker/?req_id={}&sub_id={}&member_id2={}".format(po_doc.po_requirement, po_doc.sub_id, po_doc.member_id)
        post_noti_market(po_doc.sub_id, "Youl PO have been reject from requiremnet {}".format(po_doc.po_requirement), url)
        
        write_log("PO with ID {} rejected successfully".format(po_id))
        return {"stausCode": "200", "message": "Rejected"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("PO with ID {} rejected but error".format(po_id))
        # Return an appropriate error message res.status(400)
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }



    