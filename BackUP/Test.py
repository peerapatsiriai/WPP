import frappe
import os

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False

@frappe.whitelist(allow_guest=True)
def getAllAcademics():
    
    if(Api_Maintenance or Server_Maintenance): return {"Statuscode":"504","Message":"This API is currently under maintenance."}
    query = """ SELECT * FROM tabacademic_types """
    academicsList = frappe.db.sql(query, as_dict=1)
    return academicsList

@frappe.whitelist(allow_guest=True)
def insertacademic(ac_type_name_th, ac_type_name_en , ac_area):
    
    try:
        # Insert the record with the generated primary key
        doc = frappe.get_doc({
            "doctype": "academic_types",
            "ac_type_id": "",  
            "ac_type_name_th": ac_type_name_th,
            "ac_type_name_en": ac_type_name_en,
            "ac_area": ac_area,
        })
        doc.insert(ignore_permissions=True)
        
        # # Update the is_id column with the value of the name
        doc.ac_type_id = doc.name
        doc.save(ignore_permissions=True)
        
        return { "statusCode": 201, "message": "Insert Success", "Primarykey":str(doc.name) }


    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}

@frappe.whitelist(allow_guest=True)
def testschedule():
	dummy = {
        "id": 1,
        "std_id": 1,
        "Term_id": 1,
        "Day1": [0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Day2": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Day3": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Day4": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Day5": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Day6": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        "Day7": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        }

    def checksame(day,min,max):
        long = max - min
        for i in range(long + 1):
            if(dummy[day][min] != 0):
            return "ลงไม่ไดเวลานี้"
            min = min + 1
        return "ลงได้เวลานี้"

    return print(checksame("Day1",4,14))









query = """
                    SELECT pro.product_id, pro.sub_id, pro.product_name,pro.product_price,pro.product_status,pro.product_category,sup.sub_name, cat.category_name
                    FROM 
                        tabproducts AS pro
                    INNER JOIN 
                        tabsuppliers AS sup
                    ON 
                        pro.sub_id = sup.sub_id
                    INNER JOIN 
                        tabcategorys AS cat
                    ON 
                        pro.product_category = cat.category_id
                    ORDER BY 
                        pro.creation DESC;
                """