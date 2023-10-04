import frappe

###########################################################################################################################
################################################### Departments ############################################################
###########################################################################################################################

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False

# GET http://111.223.38.19/api/method/frappe.API.MasterData.department.getAllDepartments
@frappe.whitelist(allow_guest=True)
def getAllDepartments():
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    try:
        
        query = """ 
                    SELECT * FROM `tabdepartments` AS `dpm` 
                    INNER JOIN `tabfaculty_institutes` AS `fi` 
                    ON fi.name = dpm.faculty_institutes_fi_id 
                    WHERE dpm.is_deleted = 0
                    ORDER BY dpm.creation DESC
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
    
# POST http://111.223.38.19/api/method/frappe.API.MasterData.department.insertDepartment
@frappe.whitelist(allow_guest=True)
def insertDepartment(dpm_name_th, dpm_name_en, faculty_institutes_fi_id):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [dpm_name_th, dpm_name_en, faculty_institutes_fi_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        
        # Insert the record with the generated primary key
        doc = frappe.get_doc({
            "doctype": "departments",
            "dpm_id": "DPM-",  
            "dpm_name_th": dpm_name_th,
            "dpm_name_en": dpm_name_en,
            "faculty_institutes_fi_id": faculty_institutes_fi_id,       
        })
        doc.insert(ignore_permissions=True)
        
        # Update the is_id column with the value of the name
        doc.dpm_id = doc.name
        doc.save(ignore_permissions=True)
           
        return { "statusCode": 202, "message": "Insert Success", "Primarykey":str( doc.dpm_id) }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}

# PUT http://111.223.38.19/api/method/frappe.API.MasterData.department.editDepartment
@frappe.whitelist(allow_guest=True)
def editDepartment(dpm_id, dpm_name_th, dpm_name_en, faculty_institutes_fi_id):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [dpm_id, dpm_name_th, dpm_name_en, faculty_institutes_fi_id]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        query = """ 
                    UPDATE `tabdepartments`
                    SET dpm_name_th = "%s", dpm_name_en = "%s", faculty_institutes_fi_id = "%s", modified = NOW()
                    WHERE dpm_id = "%s" 
                """ % (dpm_name_th, dpm_name_en, faculty_institutes_fi_id, dpm_id)
        
        frappe.db.sql(query, as_dict=1)
        
        return {"statusCode": 20, "message": "Update Success"}
    
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}