import frappe
import requests
from frappe import get_all
from .write_log import write_log
from .notifications import post_noti_market
from .notifications import post_noti_member

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False

def product_invoice(invoice_filename, product_id, member_id, sub_id, amount, total):
    option_results = []
    try:

        # Insert new invoice
        invoice_doc = frappe.get_doc(
            {
                "doctype": "invoices",
                "invoice_file_name": invoice_filename,
                "product_id": product_id,
                "invoice_status": 1, # status 1 is normal
                "invoice_type":"product",
                "member_id":member_id, 
                "sub_id":sub_id,
                "amount":amount,
                "price_total":total
            }
        )
        invoice_doc.insert(ignore_permissions=True)

        # Update the invoice_id column with the value of the name
        invoice_doc.invoice_id = invoice_doc.name
        invoice_doc.save(ignore_permissions=True)
        
        url = "/member/order/ordersdetail/?invoice_id={}&usertype=2".format(invoice_doc.name)
        response = post_noti_market(sub_id, "You have new a order", url)
        
        write_log("System create product invoice success for member id " + member_id + " with invoice id " + invoice_doc.invoice_id)
        return invoice_doc.name

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("System create product invoice failed for member id " + member_id + " with error " + str(e))
        # Return an appropriate error message
        return {"statusCode": 500,"message": frappe.log_error(f"An error occurred: {str(e)}")}

def requirement_invoice(po_id, invoice_filename, descritp_tion, member_id, sub_id):
    option_results = []
    try:

        # Insert new invoice
        invoice_doc = frappe.get_doc(
            {
                "doctype": "invoices",
                "po_id":po_id,
                "invoice_file_name": invoice_filename,
                "invoice_status": 1, # status 1 is normal
                "invoice_type":"requirement",
                "descritp_tion":descritp_tion,
                "member_id":member_id, 
                "sub_id":sub_id
            }
        )
        invoice_doc.insert(ignore_permissions=True)

        # Update the invoice_id column with the value of the name
        invoice_doc.invoice_id = invoice_doc.name
        invoice_doc.save(ignore_permissions=True)
        
        url = "/market/"
        response = post_noti_market(sub_id, "You have new a Requirement order", url)
        
        write_log("System create requirement invoice success for member id " + member_id + " with invoice id " + invoice_doc.invoice_id)
        return invoice_doc.name

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {
            "statusCode": 500,
            "message": frappe.log_error(f"An error occurred: {str(e)}"),
        }

################################################################### INVOICE DETAIL ####################################################
# Pont new invoice in system 
@frappe.whitelist(allow_guest=True)
def gen_invoice(po_id, invoice_filename, descritp_tion, product_id, type, option, member_id, sub_id, amount, total):
    
    parameterList = [po_id, invoice_filename, descritp_tion, product_id, type, member_id, sub_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:
        
        if type == "product":
            product_pk = product_invoice(invoice_filename, product_id, member_id, sub_id, amount, total)
            for item in option:
                
                invoice_op_doc = frappe.get_doc(
                    {
                        "doctype": "invoice_options",
                        "in_option_id":"",
                        "value_id": item['value_id'],
                        "invoice_id": product_pk,
                    }
                )
                invoice_op_doc.insert(ignore_permissions=True)

                # Update the invoice_id column with the value of the name
                invoice_op_doc.in_option_id = invoice_op_doc.name
                invoice_op_doc.save(ignore_permissions=True)
            status = "Gen Success"

        elif type == "requirement":
            status = requirement_invoice(po_id,invoice_filename, descritp_tion, member_id, sub_id)
            # Get Doctype at requirement by req_id
            po_doc = frappe.get_doc("purchaseorder", po_id)
            
            req_doc = frappe.get_doc("requirements", po_doc.po_requirement)
            req_doc.req_status = 4 # status 4 is this requirement coustomer shipping
            req_doc.save(ignore_permissions=True)
            
            
        else:
            return {"StatusCode": "500", "Message": "Some thing wrong"}

        return {"StatusCode": "200", "Message": status}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}

# invoice Product detail
@frappe.whitelist(allow_guest=True)
def invoice_detail(invoice_id):
    
    parameterList = [invoice_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:

        # get all invoice detail data in system condition is pk = invoice_id
        data_query = """ 
                    SELECT * 
                    FROM `tabinvoices` AS `in`
                    INNER JOIN `tabproducts` AS `pro`  
                    ON in.product_id = pro.product_id
                    INNER JOIN `tabmembers` AS `mem`
                    ON in.member_id = mem.member_id
                    WHERE in.invoice_id = %s
                """
        # get all option in invoice
        option_query = """
                            SELECT op.value_id,option_name,value_name 
                            FROM `tabinvoices` AS `in`
                            INNER JOIN `tabinvoice_options` AS `inop`
                            ON `in`.`invoice_id` = `inop`.`invoice_id`
                            INNER JOIN `tabproduct_option_values` AS `op`
                            ON `op`.`value_id` = `inop`.`value_id`
                            INNER JOIN `tabproduct_options` AS `opn`
                            ON `opn`.`option_id` = `op`.`option_id` 
                            WHERE `in`.`invoice_id` = %s
                        """

        invoice_data = frappe.db.sql(data_query,[invoice_id] ,as_dict=1)
        option_list = frappe.db.sql(option_query,[invoice_id] ,as_dict=1)
        
        if invoice_data[0].invoice_status == "4" or invoice_data[0].invoice_status == "5":
            data_query = """ 
                    SELECT * 
                    FROM `tabinvoices` AS `in`
                    INNER JOIN `tabproducts` AS `pro`  
                    ON in.product_id = pro.product_id
                    INNER JOIN `tabmembers` AS `mem`
                    ON in.member_id = mem.member_id
                    INNER JOIN `tabreceipt` AS `re`
                    ON re.invoice_id = in.invoice_id
                    WHERE in.invoice_id = %s
                """
            invoice_data = frappe.db.sql(data_query,[invoice_id] ,as_dict=1)

        if len(invoice_data) == 0:
            write_log("System call api invoice detail but not found at invoice id: " + invoice_id)
            return {"stausCode": "404", "message": "Not Found"}
        else:
            write_log("System call api invoice detail at invoice id " + invoice_id)
            return {"stausCode": "200", "message": "OK", "Data": invoice_data, "Option_List":option_list}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("System call api invoice detail but error " + str(e))
        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}
    
# invoice Requirement detail
@frappe.whitelist(allow_guest=True)
def invoice_req_detail(invoice_id):
    
    parameterList = [invoice_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:

        # get all invoice detail data in system condition is pk = invoice_id
        data_query = """ 
                    SELECT * 
                    FROM `tabinvoices` AS `in`
                    INNER JOIN `tabmembers` AS `mem`
                    ON in.member_id = mem.member_id
                    WHERE in.invoice_id = %s
                """
 

        invoice_data = frappe.db.sql(data_query,[invoice_id] ,as_dict=1)
        
        if invoice_data[0].invoice_status == "4" or invoice_data[0].invoice_status == "5":
            data_query = """ 
                    SELECT * 
                    FROM `tabinvoices` AS `in`
                    INNER JOIN `tabmembers` AS `mem`
                    ON in.member_id = mem.member_id
                    INNER JOIN `tabreceipt` AS `re`
                    ON re.invoice_id = in.invoice_id
                    WHERE in.invoice_id = %s
                """
            invoice_data = frappe.db.sql(data_query,[invoice_id] ,as_dict=1)


        if len(invoice_data) == 0:
            write_log("System call api requirement invoice detail but not found at invoice id: " + invoice_id)
            return {"stausCode": "404", "message": "Not Found"}
        else:
            write_log("System call api requirement invoice detail at invoice id " + invoice_id)
            return {"stausCode": "200", "message": "OK", "Data": invoice_data}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("System call api invoice detail but error " + str(e))
        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}


##################################################################### ORDER LISTS ###################################################

# My prducts order Member
@frappe.whitelist(allow_guest=True)
def member_order(member_id):
    
    parameterList = [member_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:

        # get all invoice list in system condition is pk = member_id
        data_query = """ 
                    SELECT * 
                    FROM `tabinvoices` AS `in`
                    INNER JOIN `tabproduct_image` AS `img`
                    ON img.product_id = in.product_id
                    INNER JOIN `tabproducts` AS `pro`
                    ON in.product_id = pro.product_id
                    INNER JOIN `tabsuppliers` AS `sup`
                    ON sup.sub_id = pro.sub_id
                    WHERE in.member_id = %s
                    GROUP BY img.product_id
                    ORDER BY in.creation DESC
                """
        option_query = """
                            SELECT op.value_id,option_name,value_name 
                            FROM `tabinvoices` AS `in`
                            INNER JOIN `tabinvoice_options` AS `inop`
                            ON `in`.`invoice_id` = `inop`.`invoice_id`
                            INNER JOIN `tabproduct_option_values` AS `op`
                            ON `op`.`value_id` = `inop`.`value_id`
                            INNER JOIN `tabproduct_options` AS `opn`
                            ON `opn`.`option_id` = `op`.`option_id` 
                            WHERE `in`.`invoice_id` = %s
                        """
        
        queue_order = frappe.db.sql(data_query,[member_id] ,as_dict=1)

        if len(queue_order) == 0:
            # write_log("Member call my order but not found at member id: " + member_id)
            return {"stausCode": "404", "message": "Not Found"}
        else:
            write_log("Member call my order at member id " + member_id)
            return {"stausCode": "200", "message": "OK", "Data": queue_order}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}

# My requirement member order
@frappe.whitelist(allow_guest=True)
def member_req_order(member_id):
    
    parameterList = [member_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:

        # get all invoice list in system condition is pk = member_id
        data_query = """ 
                    SELECT * 
                    FROM `tabinvoices` AS `in`
                    INNER JOIN `tabpurchaseorder` AS `po`
                    ON po.po_id = in.po_id
                    INNER JOIN `tabrequirements` AS `req`
                    ON req.req_id = po.po_requirement
                    WHERE in.member_id = %s AND in.invoice_type = "requirement" AND in.is_delete = 0
                    ORDER BY in.creation DESC
                """
        
        queue_order = frappe.db.sql(data_query,[member_id] ,as_dict=1)

        if len(queue_order) == 0:
            # write_log("Member call my order but not found at member id: " + member_id)
            return {"stausCode": "404", "message": "Not Found"}
        else:
            write_log("Member call requirement my order at member id " + member_id)
            return {"stausCode": "200", "message": "OK", "Data": queue_order}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}

# My order Market 
@frappe.whitelist(allow_guest=True)
def market_order(sub_id):
    
    parameterList = [sub_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:

        # get all invoice list in system condition is pk = sub_id
        data_query = """ 
                    SELECT in.creation, invoice_id, in.member_id, invoice_status, product_name, amount, price_total
                    FROM `tabinvoices` AS `in`
                    INNER JOIN `tabproducts` AS `pro` 
                    ON in.product_id = pro.product_id
                    WHERE in.sub_id = %s
                    ORDER BY in.creation DESC
                """

        queue_order = frappe.db.sql(data_query,[sub_id] ,as_dict=1)

        if len(queue_order) == 0:
            # write_log("Market call my order but not found at supplier id: " + sub_id)
            return {"stausCode": "404", "message": "Not Found"}
        else:
            write_log("Market call my order at supplier id " + sub_id)
            return {"stausCode": "200", "message": "OK", "Data": queue_order}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("Market call my order but error " + str(e))
        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}

# My requirement market order
@frappe.whitelist(allow_guest=True)
def market_req_order(sub_id):
    
    parameterList = [sub_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:

        # get all invoice list in system condition is pk = member_id
        data_query = """ 
                    SELECT * 
                    FROM `tabinvoices`
                    WHERE sub_id = %s AND invoice_type = "requirement" AND is_delete = 0
                    ORDER BY creation DESC
                """
        
        queue_order = frappe.db.sql(data_query,[sub_id] ,as_dict=1)

        if len(queue_order) == 0:
            # write_log("Market call my order but not found at market id: " + sub_id)
            return {"stausCode": "404", "message": "Not Found"}
        else:
            write_log("Market call requirement my order at market id " + sub_id)
            return {"stausCode": "200", "message": "OK", "Data": queue_order}
    
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}
  

##################################################################### MARKET ACTION INVOICE ###################################################
# Market confirm order
@frappe.whitelist(allow_guest=True)
def confirm(invoice_id, member_id):    
    
    parameterList = [invoice_id,  member_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:

        # get all invoice detail data in system condition is pk = invoice_id
        invoice_doc = frappe.get_doc("invoices", invoice_id)

        # Update Invoice status
        invoice_doc.invoice_status = 2 # status 2 is market approved
        invoice_doc.save(ignore_permissions=True)
        
        if invoice_doc.invoice_type == "requirement":
            url = "/member/order/orderReq/?sub_id={}&invoice_id={}".format(invoice_doc.sub_id, invoice_id)
            res = post_noti_member(member_id, "You order {} has been confirmed".format(invoice_id) , url)
        else:  
            url = "/member/order/?sub_id={}&invoice_id={}".format(invoice_doc.sub_id, invoice_id)
            res = post_noti_member(member_id, "You order {} has been confirmed".format(invoice_id) , url)
        
        write_log("Market confirm order invoice id: " + invoice_id + " at member id: " + member_id)
        return {"statusCode": 200, "message": "Confirm Success","res":res}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")
        
        write_log("System call api confirm order but error " + str(e))
        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}

# Reject roder
@frappe.whitelist(allow_guest=True)
def reject(invoice_id, member_id):
    
    parameterList = [invoice_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:

        # get all invoice detail data in system condition is pk = invoice_id
        invoice_doc = frappe.get_doc("invoices", invoice_id)

        # Update Invoice status
        invoice_doc.invoice_status = 0 # status 2 is market approved
        invoice_doc.save(ignore_permissions=True)
        
        url = "/member/order/myoder"
        res = post_noti_member(member_id, "You order {} has been reject".format(invoice_id), url)

        write_log("Market reject order invoice id: " + invoice_id + " at member id: " + member_id)
        return {"stausCode": "200", "message": "Reject Success"}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("System call api reject order but error " + str(e))
        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}

# Market confirm payment
@frappe.whitelist(allow_guest=True)
def confirm_payment(invoice_id):
    
    parameterList = [invoice_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:
        
        # updata status invoice
        query_updata = """ 
                    UPDATE `tabinvoices`
                    SET invoice_status = 4
                    WHERE invoice_id = %s;
                """

        frappe.db.sql(query_updata,[invoice_id] ,as_dict=1)
        
        # Get member_id for send notification
        query_member_id = """ 
                    SELECT member_id,invoice_id FROM `tabinvoices` WHERE invoice_id = %s
                """

        result_query = frappe.db.sql(query_member_id,[invoice_id] ,as_dict=1)
        member_id = result_query[0].member_id
   
        # Create receipts ใบเสร็จ
        receipt_doc = frappe.get_doc(
                    {
                        "module":"TCTM Markectplace",
                        "doctype": "receipt",
                        "receipt_id":"",
                        "invoice_id": invoice_id,
                        "receipt_file_name": "-",
                        "receipt_status":"1",
                        "tracking_mumber":"-"
                    }
                )
        receipt_doc.insert(ignore_permissions=True)

        # Update the invoice_id column with the value of the name
        receipt_doc.receipt_id = receipt_doc.name
        receipt_doc.save(ignore_permissions=True)
        
        # url = "/member/order/ordersdetail/?invoice_id={}&usertype=1".format(invoice_id)
        post_noti_member(member_id, "You order {} have proofed".format(invoice_id), "/member/order/myoder")

        write_log("Market confirm payment invoice id " + invoice_id)
        return {"stausCode": "200", "message": "Updata Success" }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}

# Send Tracking
@frappe.whitelist(allow_guest=True)
def send_tracking(invoice_id, tracking_number, receipt_file_name, invoice_owner_member_id):
    parameterList = [invoice_id, tracking_number, receipt_file_name, invoice_owner_member_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:
        
        # updata status receipt
        query_updata = """ 
                    UPDATE `tabreceipt`
                    SET receipt_file_name = %s, tracking_number = %s, receipt_status = 2
                    WHERE invoice_id = %s;
                """
        query_updata_invoice = """
                                UPDATE `tabinvoices`
                                SET invoice_status = 4
                                WHERE invoice_id = %s;
                            """
        frappe.db.sql(query_updata,[receipt_file_name, tracking_number, invoice_id] ,as_dict=1)
        frappe.db.sql(query_updata_invoice,[invoice_id] ,as_dict=1)
        
        # Get data of invoice
        invoice_doc = frappe.get_doc("invoices", invoice_id)
        
        # Send notification to member
        if invoice_doc.invoice_type == "requirement":
            url = "/member/order/ordersdetailReq/?invoice_id={}&usertype=1".format(invoice_id)
            post_noti_member(invoice_owner_member_id, "Market send tracking number " + tracking_number + " for your order " + invoice_id, url)
        else:
            url = "/member/order/ordersdetail/?invoice_id={}&usertype=1".format(invoice_id)
            post_noti_member(invoice_owner_member_id, "Market send tracking number " + tracking_number + " for your order " + invoice_id, url)

        write_log("Market send tracking number " + tracking_number + " for invoice " + invoice_id)
        return {"stausCode": "200", "message": "Send Tracking success" }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("Market call api send tracking number but error {}".format(str(e)))
        # Return an appropriate error message res.status(400)


#################################################################### MEMBER ACION INVOICE ##################################################

# Member send proof paymant 
@frappe.whitelist(allow_guest=True)
def send_proof(invoice_id, invoice_file_name, sub_id):
    
    parameterList = [invoice_id, invoice_file_name, sub_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:
        
        # Check invoice status 
        in_doc = frappe.get_doc("invoices", invoice_id)
        if in_doc.invoice_status == "3" or in_doc.invoice_status == "4" or in_doc.invoice_status == "5":
            return {"statusCode": 400, "message": "Invoice status not allow to send proof", "RedirectStatus":True}
        
        # updata status invoice
        query_updata = """ 
                    UPDATE `tabinvoices`
                    SET invoice_file_name = %s, invoice_status = 3
                    WHERE invoice_id = %s;
                """

        frappe.db.sql(query_updata,[invoice_file_name, invoice_id] ,as_dict=1)
        
        # Get SUP-ID for send notification
        query_sup_id = """ 
                    SELECT sub_id FROM `tabinvoices` WHERE invoice_id = %s
                """

        result_query = frappe.db.sql(query_sup_id,[invoice_id] ,as_dict=1)
        sup_id = result_query[0].sub_id
        
        # Get data of invoice
        invoice_doc = frappe.get_doc("invoices", invoice_id)
        
        if invoice_doc.invoice_type == "requirement":
            url = "/member/order/ordersdetailReq/?invoice_id={}&usertype=2".format(invoice_id)
            post_noti_market(sup_id, "You custommers send proof payment for invoice " + invoice_id, url)
        else:
            url = "/member/order/ordersdetail/?invoice_id={}&usertype=2".format(invoice_id)
            post_noti_market(sup_id, "You custommers send proof payment for invoice " + invoice_id, url)

        write_log("Member send proof payment invoice id " + invoice_id + " to supplier " + sup_id)
        return {"stausCode": "200", "message": "Updata Success","RedirectStatus":False}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}


# Member confirm prodect
@frappe.whitelist(allow_guest=True)
def member_confirm_product(invoice_id):
    parameterList = [invoice_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message": "Invalid parameters"}

    if Api_Maintenance or Server_Maintenance:
        return { "StatusCode": "503", "Message": "This API is currently under maintenance." }

    try:
        
        # updata status receipt
        query_updata_invoice = """
                                UPDATE `tabinvoices`
                                SET invoice_status = 5
                                WHERE invoice_id = %s;
                            """
        frappe.db.sql(query_updata_invoice,[invoice_id] ,as_dict=1)
        
        
        # Get Doctype at ivoice id
        invoice_doc = frappe.get_doc("invoices", invoice_id)

        invoice_doc.sub_id

        # Send notification to market
        url = "/market/"
        post_noti_market(invoice_doc.sub_id, "Member Confirm your product {}".format(invoice_id), url)

        write_log("Member Confirm Product for invoice " + invoice_id)
        return {"stausCode": "200", "message": "Confirm Product success" }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        write_log("Member confirm product but error {}".format(str(e)))
        # Return an appropriate error message res.status(400)
        return {"StatusCode": 500, "Message": f"An error occurred: {str(e)}"}
    
    