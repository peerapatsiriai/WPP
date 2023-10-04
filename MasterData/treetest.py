import frappe

# GET http://111.223.38.19/api/method/frappe.API.MasterData.treetest.gettree
@frappe.whitelist(allow_guest=True)
def gettree():    
    try:
        query = """ 
            SELECT sj_id, sj_name_th, sj_parents 
            FROM `tabsubjects` AS `sub` 
            WHERE sub.is_deleted = 1 AND sub.sj_code = "Test"
                """
        subjectList = frappe.db.sql(query, as_dict=1)

        if len(subjectList) == 0:
            return {"statusCode": "404", "message": "Not Found"}
        else:
            tree = build_tree(subjectList)
            if tree == "Error":
                return {"statusCode": 500, "message": "ทำไมมันช่างเปราะบางเหลือเกิน"}
            else:
                return {"statusCode": "200", "message": "OK", "TreeData":tree}
        
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return {"statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}")}



def build_tree(subjects):
    tree_map = {}
    tree = []
    try:
        
        for subject in subjects:
            subject_id = subject["sj_id"]
            subject_name = subject["sj_name_th"]
            # ตัวชี้ว่าพ่อตัวไหน
            parent_id = subject["sj_parents"]
            tree_map[subject_id] = {"sj_id": subject_id, "sj_name_th": subject_name, "children": []}

            # หา Root เพื่อเอาไปเป็นตัวเริ่มต้น
            if parent_id == "-":
                tree.append(tree_map[subject_id])
            else:
                # เพิ่มข้อมูลเข้าไปที่ Children ของพ่อ
                tree_map[parent_id]["children"].append(tree_map[subject_id])

        return tree
    except Exception as e:
        return "Error"
