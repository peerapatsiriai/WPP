import frappe

###########################################################################################################################
###################################################   company  ############################################################
###########################################################################################################################

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False


# GET http://111.223.38.19/api/method/frappe.API.MasterData.company.getAllcompany
@frappe.whitelist(allow_guest=True)
def getAllcompany():
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    try:
        
        query = """ 
                    SELECT * FROM `tabcompanys` 
                    WHERE is_deleted = 0
                    ORDER BY creation DESC
                """
        companyList = frappe.db.sql(query, as_dict=1)
        
        if(len(companyList) == 0):
            return { "stausCode":"404", "message":"Not Found" }
        else:
            return { "stausCode":"200", "message":"OK", "Data": companyList }
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}
    
# POST http://111.223.38.19/api/method/frappe.API.MasterData.company.insertcompany
@frappe.whitelist(allow_guest=True)
def insertcompany(com_name, com_address, com_tel, com_detail, com_status):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [com_name, com_address, com_tel, com_detail, com_status]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        
        # Insert the record with the generated primary key
        doc = frappe.get_doc({
            "doctype": "companys",
            "com_id": "COM-",  
            "com_name":com_name,  
            "com_address": com_address,  
            "com_tel":com_tel,  
            "com_detail": com_detail,  
            "com_status": com_status
        })
        doc.insert(ignore_permissions=True)
        
        # Update the is_id column with the value of the name
        doc.com_id = doc.name
        doc.save(ignore_permissions=True)
        
        return { "statusCode": 202, "message": "Insert Success", "Primarykey":str(doc.name) }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}

# PUT http://111.223.38.19/api/method/frappe.API.MasterData.subject.editsubject
@frappe.whitelist(allow_guest=True)
def editsubject(com_id ,com_name, com_address, com_tel, com_detail, com_status):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [com_name, com_address, com_tel, com_detail, com_status, com_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        query = """ 
                    UPDATE `tabcompanys`
                    SET com_name = "%s", com_address = "%s", com_tel = "%s", com_detail = "%s", com_status = "%s",modified = NOW()
                    WHERE com_id = "%s" 
                """ % (com_name, com_address, com_tel, com_detail, com_status, com_id)
        
        frappe.db.sql(query, as_dict=1)
        
        return {"statusCode": 20, "message": "Update Success"}
    
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}