import frappe

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False


@frappe.whitelist(allow_guest=True)
def allbillboards():
    
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:
        # get all billboard in system condition is status not 0
        query = """ 
                    SELECT * 
                    FROM `tabbillboards` 
                    WHERE bill_status = "1"
                """

        bill_board_list = frappe.db.sql(query, as_dict=1)

        if len(bill_board_list) == 0:
            return {"stausCode": "404", "message": "Not Found"}
        else:
            return {"stausCode": "200", "message": "OK", "Data": bill_board_list}
    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message res.status(400)
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }
        
@frappe.whitelist(allow_guest=True)
def allsupbillboards():
    
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:
        # get all billboard in system condition is status not 0
        query = """ 
                    SELECT * 
                    FROM `tabbillboards` 
                    WHERE bill_status = "2"
                """

        bill_board_list = frappe.db.sql(query, as_dict=1)

        if len(bill_board_list) == 0:
            return {"stausCode": "404", "message": "Not Found"}
        else:
            return {"stausCode": "200", "message": "OK", "Data": bill_board_list}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message res.status(400)
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }


@frappe.whitelist(allow_guest=True)
def market_recommend():
    
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:
        # Get all market recommend in system
        # status 3 is recommend
        query = """ 
                    SELECT * 
                    FROM `tabsuppliers` 
                    WHERE sub_status = "3"
                    LIMIT 7 
                """

        market_list = frappe.db.sql(query, as_dict=1)

        if len(market_list) == 0:
            return {"stausCode": "404", "message": "Not Found"}
        else:
            return {"stausCode": "200", "message": "OK", "Data": market_list}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message res.status(400)
        return {
            "statusCode": 500,
            "message": frappe.log_error(f"An error occurred: {str(e)}"),
        }


@frappe.whitelist(allow_guest=True)
def product_recommend():
    
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:
        # Get all product recommend in system
        query = """ 
                    SELECT
                        cat.category_name,
                        pro.product_id, 
                        product_name, 
                        img.image_file_name,
                        product_description, 
                        product_status, 
                        category_name, 
                        sup.sub_name,
                        MIN(CAST(opv.value_name AS DECIMAL(10))) AS min_price,
                        MAX(CAST(opv.value_name AS DECIMAL(10))) AS max_price
                    FROM
                        `tabproducts` AS pro
                    INNER JOIN
                        `tabcategorys` AS cat ON pro.product_category = cat.category_id
                    INNER JOIN
                        `tabsuppliers` AS sup ON pro.sub_id = sup.sub_id
                    INNER JOIN
                        `tabproduct_image` AS `img` ON pro.product_id = img.product_id
                    INNER JOIN
                        `tabproduct_options` AS `opn` ON opn.product_id = pro.product_id
                    INNER JOIN
                        `tabproduct_option_values` AS `opv` ON opv.option_id = opn.option_id
                    WHERE
                        pro.is_deleted = 0
                        AND product_status > 1
                        AND sup.sub_status != 0
                        AND opn.option_name = "Price"
                        AND pro.product_status = 3
                        AND pro.product_status != 4
                    GROUP BY
                        pro.product_id, opn.option_name
                """

        product_list = frappe.db.sql(query, as_dict=1)

        if len(product_list) == 0:
            return {"stausCode": "404", "message": "Not Found"}
        else:
            return {"stausCode": "200", "message": "OK", "Data": product_list}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message res.status(400)
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }
    
    
@frappe.whitelist(allow_guest=True)
def best_selling():
    
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:
        # Get all product recommend in system
        # query = """ 
        #             SELECT *
        #             FROM tabproducts
        #             ORDER BY RAND()
        #             LIMIT 10;
        #         """
        query = """
                    SELECT
                        cat.category_name,
                        pro.product_id, 
                        product_name, 
                        img.image_file_name,
                        product_description, 
                        product_status, 
                        category_name, 
                        sup.sub_name,
                        MIN(CAST(opv.value_name AS DECIMAL(10))) AS min_price,
                        MAX(CAST(opv.value_name AS DECIMAL(10))) AS max_price
                    FROM
                        `tabproducts` AS pro
                    INNER JOIN
                        `tabcategorys` AS cat ON pro.product_category = cat.category_id
                    INNER JOIN
                        `tabsuppliers` AS sup ON pro.sub_id = sup.sub_id
                    INNER JOIN
                        `tabproduct_image` AS `img` ON pro.product_id = img.product_id
                    INNER JOIN
                        `tabproduct_options` AS `opn` ON opn.product_id = pro.product_id
                    INNER JOIN
                        `tabproduct_option_values` AS `opv` ON opv.option_id = opn.option_id
                    WHERE
                        pro.is_deleted = 0
                        AND product_status > 1
                        AND sup.sub_status != 0
                        AND opn.option_name = "Price"
                        AND pro.product_status != 4
                    GROUP BY
                        pro.product_id, opn.option_name
                    ORDER BY RAND()
                    LIMIT 10;
        """

        product_list = frappe.db.sql(query, as_dict=1)

        if len(product_list) == 0:
            return {"stausCode": "404", "message": "Not Found"}
        else:
            return {"stausCode": "200", "message": "OK", "Data": product_list}

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message res.status(400)
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }
