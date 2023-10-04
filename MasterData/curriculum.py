import frappe

###########################################################################################################################
################################################### Curriculum ############################################################
###########################################################################################################################
    
Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False


# GET http://111.223.38.19/api/method/frappe.API.MasterData.curriculum.getAllcurriculums
@frappe.whitelist(allow_guest=True)
def getAllcurriculums():
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    try:
        
        query = """ 
                    SELECT * FROM `tabcurriculums` AS `cu` 
                    INNER JOIN `tabfaculty_institutes` AS `fi` 
                    ON fi.name = cu.faculty_institutes_fi_id 
                    INNER JOIN `tabdepartments` AS `dp`
                    ON cu.dpm_id = dp.dpm_id
                    WHERE cu.is_deleted = 0
                    ORDER BY cu.creation DESC
                """
        curriculumList = frappe.db.sql(query, as_dict=1)
        
        if(len(curriculumList) == 0):
            return { "stausCode":"404", "message":"Not Found" }
        else:
            return { "stausCode":"200", "message":"OK", "Data": curriculumList }
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}
    
# POST http://111.223.38.19/api/method/frappe.API.MasterData.curriculum.insertcurriculum
@frappe.whitelist(allow_guest=True)
def insertcurriculum(cur_name_th, cur_name_en, cur_shot_name_th, cur_shot_name_en, dpm_id, faculty_institutes_fi_id, release_year):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [cur_name_th, cur_name_en, cur_shot_name_th, cur_shot_name_en, dpm_id, faculty_institutes_fi_id, release_year]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        
        # Insert the record with the generated primary key
        doc = frappe.get_doc({
            "doctype": "curriculums",
            "cur_id": "CUR-",  
            "cur_name_th": cur_name_th,
            "cur_name_en": cur_name_en,
            "cur_shot_name_th": cur_shot_name_th,
            "cur_shot_name_en": cur_shot_name_en,
            "dpm_id": dpm_id,
            "faculty_institutes_fi_id": faculty_institutes_fi_id,
            "release_year": release_year,
        })
        doc.insert(ignore_permissions=True)
        
        # Update the is_id column with the value of the name
        doc.cur_id = doc.name
        doc.save(ignore_permissions=True)
           
        return { "statusCode": 202, "message": "Insert Success", "Primarykey":str(doc.name) }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}

# PUT http://111.223.38.19/api/method/frappe.API.MasterData.curriculum.editcurriculum
@frappe.whitelist(allow_guest=True)
def editcurriculum(cur_id, cur_name_th, cur_name_en, cur_shot_name_th, cur_shot_name_en, dpm_id, faculty_institutes_fi_id, release_year):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [cur_id, cur_name_th, cur_name_en, cur_shot_name_th, cur_shot_name_en, dpm_id, faculty_institutes_fi_id, release_year]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        query = """ 
                    UPDATE `tabcurriculums`
                    SET cur_name_th = "%s", cur_name_en = "%s", cur_shot_name_th = "%s", cur_shot_name_en = "%s", dpm_id = "%s", faculty_institutes_fi_id = "%s",
                    release_year = "%s", modified = NOW()
                    WHERE cur_id = "%s" 
                """ % (cur_name_th, cur_name_en, cur_shot_name_th, cur_shot_name_en, dpm_id, faculty_institutes_fi_id, release_year, cur_id)
        
        frappe.db.sql(query, as_dict=1)
        
        return {"statusCode": 20, "message": "Update Success"}
    
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}
