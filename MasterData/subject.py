import frappe

###########################################################################################################################
###################################################   Subject  ############################################################
###########################################################################################################################

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False


# GET http://111.223.38.19/api/method/frappe.API.MasterData.subject.getAllsubjects
@frappe.whitelist(allow_guest=True)
def getAllsubjects():
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    try:
        
        query = """ 
                    SELECT * FROM `tabsubjects` AS `sub` 
                    INNER JOIN `tabcurriculums` AS `cur` 
                    ON cur.cur_id = sub.curriculums_cur_id
                    INNER JOIN `tabsubject_groups` AS `subg`
                    ON sub.subject_group_sjg_id = subg.sjg_id
                    WHERE sub.is_deleted = 0
                    ORDER BY sub.creation DESC
                """
        subjectList = frappe.db.sql(query, as_dict=1)
        
        if(len(subjectList) == 0):
            return { "stausCode":"404", "message":"Not Found" }
        else:
            return { "stausCode":"200", "message":"OK", "Data": subjectList }
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}
    
# POST http://111.223.38.19/api/method/frappe.API.MasterData.subject.insertsubject
@frappe.whitelist(allow_guest=True)
def insertsubject(subject_group_sjg_id, curriculums_cur_id, sj_code, sj_name_th, sj_name_en, sj_credit, sj_theory_credit, sj_action_credit, sj_ot_credit, sj_chiles, sj_parents, sj_description):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [subject_group_sjg_id, curriculums_cur_id, sj_code, sj_name_th, sj_name_en, sj_credit, sj_theory_credit, sj_action_credit, sj_ot_credit, sj_chiles, sj_parents, sj_description]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        
        # Insert the record with the generated primary key
        doc = frappe.get_doc({
            "doctype": "subjects",
            "sj_id": "SJ-",  
            "subject_group_sjg_id":subject_group_sjg_id,  
            "curriculums_cur_id": curriculums_cur_id,  
            "sj_code":sj_code,  
            "sj_name_th": sj_name_th,  
            "sj_name_en": sj_name_en,  
            "sj_credit": sj_credit,  
            "sj_theory_credit": sj_theory_credit,  
            "sj_action_credit": sj_action_credit,  
            "sj_ot_credit": sj_ot_credit,  
            "sj_chiles": sj_chiles,  
            "sj_parents": sj_parents,  
            "sj_description": sj_description,  
            
        })
        doc.insert(ignore_permissions=True)
        
        # Update the is_id column with the value of the name
        doc.sj_id = doc.name
        doc.save(ignore_permissions=True)
        
        return { "statusCode": 202, "message": "Insert Success", "Primarykey":str(doc.name) }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}

# PUT http://111.223.38.19/api/method/frappe.API.MasterData.subject.editsubject
@frappe.whitelist(allow_guest=True)
def editsubject(sj_id ,subject_group_sjg_id, curriculums_cur_id, sj_code, sj_name_th, sj_name_en, sj_credit, sj_theory_credit, sj_action_credit, sj_ot_credit, sj_chiles, sj_parents, sj_description):
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"503","Message":"This API is currently under maintenance."}
    
    parameterList = [sj_id ,subject_group_sjg_id, curriculums_cur_id, sj_code, sj_name_th, sj_name_en, sj_credit, sj_theory_credit, sj_action_credit, sj_ot_credit, sj_chiles, sj_parents, sj_description]
    # Check if any parameter is null or empty
    if not all(parameterList) or any(param.strip() == "" for param in parameterList):
        return {"statusCode": 400, "message":"Invalid parameters"}
    
    try:
        query = """ 
                    UPDATE `tabsubjects`
                    SET subject_group_sjg_id = "%s", curriculums_cur_id = "%s", sj_code = "%s", sj_name_th = "%s", sj_name_en = "%s", sj_credit = "%s",
                    sj_theory_credit = "%s",  sj_action_credit = "%s", sj_ot_credit = "%s", sj_chiles = "%s", sj_parents = "%s", sj_description = "%s",modified = NOW()
                    WHERE sj_id = "%s" 
                """ % (subject_group_sjg_id, curriculums_cur_id, sj_code, sj_name_th, sj_name_en, sj_credit, sj_theory_credit, sj_action_credit, sj_ot_credit, sj_chiles, sj_parents, sj_description, sj_id)
        
        frappe.db.sql(query, as_dict=1)
        
        return {"statusCode": 20, "message": "Update Success"}
    
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}