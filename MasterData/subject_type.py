import frappe

###########################################################################################################################
###############################################  Subject Type   ###########################################################
###########################################################################################################################

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False


# GET http://111.223.38.19/api/method/frappe.API.MasterData.subject_type.getAllsubject_type
@frappe.whitelist(allow_guest=True)
def getAllsubject_type():
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    try:
        
        query = """ 
                    SELECT * FROM `tabsubject_types` AS `subt` 
                    INNER JOIN `tabsubject_category` AS `subc` 
                    ON subt.subject_category_id  = subc.subject_category_id
                    WHERE subt.is_deleted = 0
                    ORDER BY subt.creation DESC
                """
        subjectTypeList = frappe.db.sql(query, as_dict=1)
        
        if(len(subjectTypeList) == 0):
            return { "stausCode":"404", "message":"Not Found" }
        else:
            return { "stausCode":"200", "message":"OK", "Data": subjectTypeList }
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}
    
# POST http://111.223.38.19/api/method/frappe.API.MasterData.subject_type.insertsubject_type
@frappe.whitelist(allow_guest=True)
def insertsubject_type(subject_category_id, subject_type_name):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [subject_category_id, subject_type_name]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        
        # Insert the record with the generated primary key
        doc = frappe.get_doc({
            "doctype": "subject_types",
            "subject_type_id": "SJT-",  
            "subject_category_id":subject_category_id,  
            "subject_type_name": subject_type_name  
        })
        doc.insert(ignore_permissions=True)
        
        # Update the is_id column with the value of the name
        doc.subject_type_id = doc.name
        doc.save(ignore_permissions=True)
        
        return { "statusCode": 202, "message": "Insert Success", "Primarykey":str(doc.name) }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}

# PUT http://111.223.38.19/api/method/frappe.API.MasterData.subject_type.editsubject_type
@frappe.whitelist(allow_guest=True)
def editsubject_type(subject_type_id ,subject_category_id, subject_type_name):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [subject_type_id ,subject_category_id, subject_type_name]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        query = """ 
                    UPDATE `tabsubject_types`
                    SET subject_category_id = "%s", subject_type_name = "%s", modified = NOW()
                    WHERE subject_type_id = "%s" 
                """ % (subject_category_id, subject_type_name, subject_type_id)
        
        frappe.db.sql(query, as_dict=1)
        
        return {"statusCode": 20, "message": "Update Success"}
    
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}