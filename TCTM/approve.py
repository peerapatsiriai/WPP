import frappe
from .write_log import write_log

from .notifications import post_noti_member
from .notifications import post_noti_market

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False


# Code status mean
# 0 is baned or reject
# 1 is wait for approve
# 2 is status narmal
# 3 is Recommend

####################################### Handle User function ###########################################
# User queue wait for approve by TCTM
@frappe.whitelist(allow_guest=True)
def userqueue():

    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:
        # Get all user queue wait for approve
        query = """
                    SELECT ac.account_id, mem.member_id, mem.user_first_name, mem.user_last_name, mem.user_company, mem.user_email, mem.user_tel  FROM `tabaccounts` AS `ac`
                    INNER JOIN `tabmembers` AS `mem`
                    ON ac.account_id = mem.account_id
                    WHERE ac.account_status = 1 AND ac.is_delete = 0
                    ORDER BY ac.creation DESC
                """
        queue = frappe.db.sql(query, as_dict=1)

        if len(queue) == 0:
            # write_log("TCTM call api user approve but not found any data.")
            return {"stausCode": "404", "message": "Not Found"}
        else:
            return {"stausCode": "200", "message": "OK", "Data": queue}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("TCTM call api user approve but error {}".format(str(e)))
        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}


# User Approve 
@frappe.whitelist(allow_guest=True)
def userapprove(account_id):
    parameterList = [account_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:

        # Get Doctype at account_id
        account = frappe.get_doc("accounts", account_id)

        # Update account_status
        account.account_status = 2 # status 2 is approve this account. can use system
        account.save(ignore_permissions=True)

        write_log("TCTM approve account id: " + account_id)
        return {"StatusCode": "200", "Message": "OK", "Data": "Account Approved"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("TCTM call api user approve but error {}".format(str(e)))
        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}


# User reject
@frappe.whitelist(allow_guest=True)
def userreject(account_id):
    parameterList = [account_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:

        # Get Doctype at user_id
        account = frappe.get_doc("accounts", account_id)

        # Update user's account status from 1 to 2
        account.account_status = 0 # status 0 is reject this use for system
        account.save(ignore_permissions=True)

        write_log("TCTM reject account id: " + account_id)
        
        return {"StatusCode": "200", "Message": "OK", "Data": "Account Rejected"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("TCTM call api user reject but error {}".format(str(e)))
        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}


####################################### Handle supplier function ###########################################


# Market queue
@frappe.whitelist(allow_guest=True)
def supplierqueue():

    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:
        # Get all Market queue wait for approve
        query = """
                    SELECT sup.sub_id, sub_name, sub_address, sub_tel, user_first_name, user_last_name, user_company FROM `tabsuppliers` AS `sup`
                    INNER JOIN `tabmembers` AS `use`
                    ON sup.sub_id = use.sub_id
                    WHERE sup.sub_status = 1 AND sup.is_delete = 0
                    ORDER BY sup.creation DESC
                """
        queue = frappe.db.sql(query, as_dict=1)

        if len(queue) == 0:
            # write_log("TCTM call api supplier approve but not found any data.")
            return {"stausCode": "404", "message": "Not Found"}
        else:
            return {"stausCode": "200", "message": "OK", "Data": queue}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }


# Market Approve
@frappe.whitelist(allow_guest=True)
def supplierapprove(sub_id):
    parameterList = [sub_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:

        # Get Doctype at sub_id
        supplier = frappe.get_doc("suppliers", sub_id)

        # Update Market status
        supplier.sub_status = 2 # status 2 is market approved
        supplier.save(ignore_permissions=True)
        
        post_noti_market(supplier.sub_id, "You market {} have been approved by TCTM".format(sub_id), "/market")

        write_log("TCTM approve supplier id: " + sub_id)
        return {"StatusCode": "200","Message": "OK","Data": "Market Approved"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("TCTM call api supplier approve but error {}".format(str(e)))
        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}


# Market reject
@frappe.whitelist(allow_guest=True)
def supplierreject(sub_id):
    parameterList = [sub_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:

        # Get Doctype at sub_id
        supplier = frappe.get_doc("suppliers", sub_id)

        # Update sub_status
        supplier.sub_status = 0 # status 0 is market reject
        supplier.save(ignore_permissions=True)

        # Update status of user is link with sub_id
        member_doc = frappe.get_all("members", filters={"sub_id": sub_id}, limit=1)

        if member_doc:
            member_doc = frappe.get_doc(
                "members", member_doc[0].name
            )  # Fetch the existing member document

            # Update user's account status from 1 to 2
            member_doc.sub_id = ""  # Update the sub_id field
            member_doc.user_status = 1  # Update the user_status field
            member_doc.save(ignore_permissions=True)  # Save the changes to the existing document
        
        post_noti_member(member_doc.member_id, "You market {} have been rejected by TCTM".format(sub_id), "/")
        
        write_log("TCTM reject supplier id: " + sub_id)
        
        return {"StatusCode": "200", "Message": "OK", "Data": "Market Reject"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("TCTM call api user reject but error {}".format(str(e)))
        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}


####################################### Handle Products function ###########################################

# Products queue
@frappe.whitelist(allow_guest=True)
def productsqueue():

    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:

        query = """
                    SELECT pro.product_id, product_name, product_price, product_description, sub_name FROM `tabproducts` AS `pro`
                    INNER JOIN `tabsuppliers` AS `sub`
                    ON pro.sub_id = sub.sub_id
                    WHERE pro.product_status = 1 AND pro.is_delete = 0
                    ORDER BY pro.creation DESC
                """
        queue = frappe.db.sql(query, as_dict=1)

        if len(queue) == 0:
            # write_log("TCTM call api products approve but not found any data.")
            return {"stausCode": "404", "message": "Not Found"}
        else:
            return {"stausCode": "200", "message": "OK", "Data": queue}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("TCTM call api supplier approve but error {}".format(str(e)))
        # Return an appropriate error message
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }


# Product Approve
@frappe.whitelist(allow_guest=True)
def productapprove(product_id):
    parameterList = [product_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:

        # Get Doctype at product_id
        product_doc = frappe.get_doc("products", product_id)

        # Update product_status
        product_doc.product_status = 2
        product_doc.save(ignore_permissions=True)
        
        post_noti_market(product_doc.sub_id, "You product {} have been approved by TCTM ".format(product_id), "/market")

        write_log("TCTM approve product id: " + product_id)
        
        return {"StatusCode": "200", "Message": "OK", "Data": "Product Approved"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("TCTM call api supplier approve but error {}".format(str(e)))
        
        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}


# Product reject
@frappe.whitelist(allow_guest=True)
def productreject(product_id):
    
    parameterList = [product_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:

        # Get Doctype at product_id
        product_doc = frappe.get_doc("products", product_id)

        # Update product status
        product_doc.product_status = 0
        product_doc.save(ignore_permissions=True)

        post_noti_market(product_doc.sub_id, "You product {} have been rejected by TCTM ".format(product_id), "/market")

        write_log("TCTM reject product id: " + product_id)
        return {"StatusCode": "200", "Message": "OK", "Data": "Product rejected"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("TCTM call api product reject but error {}".format(str(e)))
        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}


######################################## Handle Requirement function ###########################################

# Requirement queue
@frappe.whitelist(allow_guest=True)
def requirementqueue():

    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:

        query = """
                    SELECT * FROM `tabrequirements` AS `req`
                    INNER JOIN `tabmembers` AS `mem`
                    ON mem.member_id = req.member_id
                    WHERE req.req_status = 1 AND req.is_delete = 0
                    ORDER BY req.creation DESC
                """
        queue = frappe.db.sql(query, as_dict=1)

        if len(queue) == 0:
            # write_log("TCTM call api requirement approve but not found any data.")
            return {"stausCode": "404", "message": "Not Found"}
        else:
            return {"stausCode": "200", "message": "OK", "Data": queue}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")
        
        write_log("TCTM call api requirement approve but error {}".format(str(e)))
        # Return an appropriate error message
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }


@frappe.whitelist(allow_guest=True)
def allsuppliername():

    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:
        ## Get all suppliers name for dropdown in approve requirement page
        query = """
                    SELECT sub_id, sub_name FROM `tabsuppliers` 
                    WHERE sub_status > 1 AND is_delete = 0
                """
        sup_list = frappe.db.sql(query, as_dict=1)

        if len(sup_list) == 0:
            # write_log("TCTM call api all supplier name but not found any data.")
            return {"stausCode": "404", "message": "Not Found"}
        else:
            return {"stausCode": "200", "message": "OK", "Data": sup_list}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("TCTM call api all supplier name but error {}".format(str(e)))
        # Return an appropriate error message
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }


# Requirement Approve
@frappe.whitelist(allow_guest=True)
def requirementapprove(req_id, sub_id):
    parameterList = [req_id, sub_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:

        # Get Doctype at requirement_id
        req_doc = frappe.get_doc("requirements", req_id)

        # Update requirement status and link with supplier
        req_doc.req_status = 2
        req_doc.sub_id = sub_id
        req_doc.save(ignore_permissions=True)

        member_url = "/member/port-detail-member/?req_id={}&sub_id={}".format(req_id, sub_id)
        post_noti_member( req_doc.member_id , "TCTM approved your requirement {} ".format(req_id), member_url)
        
        market_url = "/market/port-detail-marker/?req_id={}&sub_id={}&member_id2={}".format(req_id, sub_id, req_doc.member_id)
        post_noti_market( sub_id, "TCTM send new requirement {} for you".format(req_id), market_url )
        
        write_log("TCTM approve requirement id: " + req_id + " with supplier: " + sub_id)
        return {"StatusCode": "200", "Message": "OK", "Data": "Requirement Approved"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("TCTM call api requirement approve but error {}".format(str(e)))
        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}


# Requirement Reject
@frappe.whitelist(allow_guest=True)
def requirementreject(req_id):
    parameterList = [req_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:

        # Get Doctype at user_id
        req_doc = frappe.get_doc("requirements", req_id)

        # Update user's account status from 1 to 2
        req_doc.req_status = 1
        req_doc.sub_id = ""
        req_doc.save(ignore_permissions=True)
        
        post_noti_member( req_doc.member_id ,"Your requirement {} have been rejected by market ".format(req_id),"/member/ports/")

        write_log("TCTM reject requirement id: " + req_id)
        return {"StatusCode": "200", "Message": "OK", "Data": "Requirement Rejected"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("TCTM call api requirement reject but error {}".format(str(e)))
        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}
