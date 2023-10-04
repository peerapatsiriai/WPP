import frappe

###########################################################################################################################
###################################################   Company Depart Ment  ############################################################
###########################################################################################################################

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False


# GET http://111.223.38.19/api/method/frappe.API.MasterData.company_department.getAllcompanydepartment
@frappe.whitelist(allow_guest=True)
def getAllcompanydepartment():
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    try:
        
        query = """ 
                    SELECT * FROM `tabcompany_departments` AS `cdp`
                    INNER JOIN `tabcompanys` AS `com`
                    ON cdp.com_id = com.name
                    WHERE cdp.is_deleted = 0
                    ORDER BY cdp.creation DESC
                """
        departmentList = frappe.db.sql(query, as_dict=1)
        
        if(len(departmentList) == 0):
            return { "stausCode":"404", "message":"Not Found" }
        else:
            return { "stausCode":"200", "message":"OK", "Data": departmentList }
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}
    
# POST http://111.223.38.19/api/method/frappe.API.MasterData.company.insertcompanydepartment
@frappe.whitelist(allow_guest=True)
def insertcompanydepartment(com_id, dp_name, dp_status):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [com_id, dp_name, dp_status]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        
        # Insert the record with the generated primary key
        doc = frappe.get_doc({
            "doctype": "company_departments",
            "dp_id": "DP-",  
            "com_id":com_id,  
            "dp_name": dp_name,  
            "dp_status":dp_status,  
        })
        doc.insert(ignore_permissions=True)
        
        # Update the is_id column with the value of the name
        doc.dp_id = doc.name
        doc.save(ignore_permissions=True)
        
        return { "statusCode": 202, "message": "Insert Success", "Primarykey":str(doc.name) }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}

# PUT http://111.223.38.19/api/method/frappe.API.MasterData.subject.editcompanydepartment
@frappe.whitelist(allow_guest=True)
def editcompanydepartment(com_id, dp_name, dp_status, dp_id):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [com_id, dp_name, dp_status, dp_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        query = """ 
                    UPDATE `tabcompany_departments`
                    SET com_id = "%s", dp_name = "%s", dp_status = "%s",modified = NOW()
                    WHERE dp_id = "%s" 
                """ % (com_id, dp_name, dp_status, dp_id)
        
        frappe.db.sql(query, as_dict=1)
        
        return {"statusCode": 20, "message": "Update Success"}
    
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}