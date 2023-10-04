import frappe
from .write_log import write_log

Server_Maintenance = my_variable = frappe.conf.Maintenance
Api_Maintenance = False


@frappe.whitelist(allow_guest=True)
def get_data_in_dashboard():
    
    if Api_Maintenance or Server_Maintenance:
        return { "Statuscode": "503", "Message": "This API is currently under maintenance." }

    try:
        
        Top_selling_query = """
                    SELECT pro.product_name, COUNT(*) as product_count, sup.sub_name
                    FROM tabinvoices AS `in`
                    INNER JOIN tabproducts AS `pro`
                    ON pro.product_id = in.product_id
                    INNER JOIN `tabsuppliers` AS `sup`
                    ON sup.sub_id = pro.sub_id
                    WHERE in.product_id IS NOT NULL AND in.invoice_status = 5
                    GROUP BY in.product_id
                    LIMIT 10;
                """
        count_all_product_query = """
                    SELECT COUNT(pro.product_id) AS count FROM `tabproducts` AS `pro` WHERE product_status > 1 AND is_deleted = 0;
                """
        count_all_selling_query = """
                    SELECT
                    COUNT(DISTINCT in.invoice_id) AS count_invoices,
                    SUM(price_total) AS total_price
                    FROM `tabinvoices` AS `in`
                    WHERE in.invoice_status = 5;
                """
        count_all_requirement_query = """
                    SELECT
                        CASE WHEN req_status BETWEEN 0 AND 5 THEN req_status ELSE 'All Requirements in system' END AS req_status,
                        COUNT(req_id) AS req_id_count
                    FROM
                        `tabrequirements`
                    GROUP BY
                        req_status
                    WITH ROLLUP;
                """
        count_all_member_query = """
                    SELECT
                        CASE WHEN user_status BETWEEN 0 AND 2 THEN user_status ELSE 'All User in system' END AS user_status,
                        COUNT(member_id) AS member_id_id_count
                    FROM
                        `tabmembers`
                    WHERE user_role != 'ADMIN' AND user_role != 'TCTM'
                    GROUP BY
                        user_status
                    WITH ROLLUP;
                """
        count_all_market_query = """
                    SELECT COUNT(DISTINCT sub_id) AS market_count
                    FROM `tabsuppliers`;
                """
        best_selling_market_query = """
                    SELECT sup.sub_name, COUNT(invoice_id) AS invoice_count
                    FROM `tabinvoices` AS `in`
                    INNER JOIN `tabsuppliers` AS `sup`
                    ON in.sub_id = sup.sub_id
                    WHERE invoice_status != 0 AND invoice_status = 5
                    GROUP BY in.sub_id
                    ORDER BY invoice_count DESC
                """
        all_selling_in_month_query = """
                    SELECT
                        DATE_FORMAT(in.creation, '%Y-%m') AS month,
                        SUM(in.price_total) AS total_price
                    FROM
                        `tabinvoices` AS `in`
                    WHERE
                        in.invoice_status = 5
                        AND DATE_FORMAT(in.creation, '%Y') = '2023'
                    GROUP BY
                        DATE_FORMAT(in.creation, '%Y-%m')
                    ORDER BY
                        total_price DESC
        """
        
        # Get all topselling in system
        top_selling_data = frappe.db.sql(Top_selling_query,as_dict=1)
        
        # count all product in system
        count_all_product = frappe.db.sql(count_all_product_query,as_dict=1)
        
        # Count selling and price in system
        count_all_selling = frappe.db.sql(count_all_selling_query,as_dict=1)
        
        # Count requirement of each status
        count_all_requirement = frappe.db.sql(count_all_requirement_query,as_dict=1)
        
        # Count User of each status 
        count_all_user = frappe.db.sql(count_all_member_query,as_dict=1)
        
        # Count market in system
        count_all_market = frappe.db.sql(count_all_market_query,as_dict=1)
        
        # Best Market selling
        count_best_market_selling = frappe.db.sql(best_selling_market_query,as_dict=1)
        
        # all_selling_in_month
        all_selling_in_month = frappe.db.sql(all_selling_in_month_query,as_dict=1)
        

        return {
            "stausCode": "200",
            "message": "OK",
            "top_product_selling": top_selling_data,
            "all_product_active_in_system": count_all_product[0].count,
            "all_selling_in_system": count_all_selling,
            "all_requirement_in_system": count_all_requirement,
            "all_member_in_system": count_all_user,
            "all_market_in_system": count_all_market,
            "best_market_selling": count_best_market_selling,
            "all_selling_in_month": all_selling_in_month
        }

    except Exception as e:
        # Log the error for debugging purposes if needed
        frappe.log_error(f"An error occurred: {str(e)}")

        # Return an appropriate error message
        return { "statusCode": 500, "message": frappe.log_error(f"An error occurred: {str(e)}") }
