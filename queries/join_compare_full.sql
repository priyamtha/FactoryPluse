SELECT c.customer_id, o.order_id, o.order_amount
FROM customers c
FULL OUTER JOIN orders o ON c.customer_id = o.customer_id;
