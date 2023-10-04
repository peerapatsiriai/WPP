import frappe

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False


@frappe.whitelist(allow_guest=True)
def display_profile(member_id):
    
    parameterList = [member_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}
    
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:
        # get all data of one member
        query_have_market = """ 
                    SELECT *
                    FROM `tabmembers` AS `mem`
                    INNER JOIN `tabsuppliers` AS `sub`
                    ON mem.sub_id = sub.sub_id 
                    WHERE member_id = %s
                """
        query_not_market = """ 
                    SELECT *
                    FROM `tabmembers`
                    WHERE member_id = %s
                """
                
        member_data_detail = frappe.db.sql(query_not_market, [member_id],as_dict=1)
        
        if member_data_detail[0].user_status == "2":
            member_data_detail = frappe.db.sql(query_have_market, [member_id],as_dict=1)

        if len(member_data_detail) == 0:
            return {"stausCode": "404", "message": "Not Found"}
        else:
            return {"stausCode": "200", "message": "OK", "Data": member_data_detail}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message res.status(400)
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }
    
@frappe.whitelist(allow_guest=True)
def update_profile(username, lastname, member_id, email, address, phone, company):
    
    parameterList = [member_id, email, address, phone]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}
    
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:
        
        # Get Doctype at member_id
        mem_doc = frappe.get_doc("members", member_id)

        # Update data of thses member
        mem_doc.username = username
        mem_doc.lastname = lastname
        mem_doc.user_address = address
        mem_doc.user_tel = phone 
        mem_doc.user_email = email 
        mem_doc.user_company = company 
        mem_doc.save(ignore_permissions=True)

        return {"stausCode": "200", "message": "Update Success" }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message res.status(400)
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }
    
