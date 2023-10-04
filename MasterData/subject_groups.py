import frappe

###########################################################################################################################
###############################################  Subject Group  ###########################################################
###########################################################################################################################

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False


# GET http://111.223.38.19/api/method/frappe.API.MasterData.subject_groups.getAllsubject_groups
@frappe.whitelist(allow_guest=True)
def getAllsubject_groups():
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    try:
        
        query = """ 
                    SELECT * FROM `tabsubject_groups` AS `subg` 
                    INNER JOIN `tabsubject_types` AS `subt` 
                    ON subg.subject_type_id  = subt.subject_type_id
                    INNER JOIN `tabsubject_category` AS `subc`
                    ON subt.subject_category_id = subc.subject_category_id
                    WHERE subg.is_deleted = 0
                    ORDER BY subg.creation DESC
                """
        subjectgroupList = frappe.db.sql(query, as_dict=1)
        
        if(len(subjectgroupList) == 0):
            return { "stausCode":"404", "message":"Not Found" }
        else:
            return { "stausCode":"200", "message":"OK", "Data": subjectgroupList }
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}
    
# POST http://111.223.38.19/api/method/frappe.API.MasterData.subject_groups.insertsubject_groups
@frappe.whitelist(allow_guest=True)
def insertsubject_groups(subject_type_id, sjg_name):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [subject_type_id, sjg_name]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        
        # Insert the record with the generated primary key
        doc = frappe.get_doc({
            "doctype": "subject_groups",
            "sjg_id": "SJG-",  
            "subject_type_id":subject_type_id,  
            "sjg_name": sjg_name,  
        })
        doc.insert(ignore_permissions=True)
        
        # Update the is_id column with the value of the name
        doc.sjg_id = doc.name
        doc.save(ignore_permissions=True)
        
        return { "statusCode": 202, "message": "Insert Success", "Primarykey":str(doc.name) }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}

# PUT http://111.223.38.19/api/method/frappe.API.MasterData.subject_groups.editsubject_groups
@frappe.whitelist(allow_guest=True)
def editsubject_groups(sjg_id, subject_type_id, sjg_name):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [sjg_id, subject_type_id, sjg_name]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        query = """ 
                    UPDATE `tabsubject_groups`
                    SET subject_type_id = "%s", sjg_name = "%s", modified = NOW()
                    WHERE sjg_id = "%s" 
                """ % (subject_type_id, sjg_name, sjg_id)
        
        frappe.db.sql(query, as_dict=1)
        
        return {"statusCode": 20, "message": "Update Success"}
    
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}