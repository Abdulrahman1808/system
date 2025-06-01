from data_handler import load_data

class AIModel:
    def __init__(self):
        # Initialize any model parameters or state here
        pass

    def respond_to_query(self, query):
        """
        Process the user query, fetch data from the database, and return a response string.
        Enhanced to support searching products by name or kind.
        """
        query_lower = query.lower()

        products = load_data("products")
        suppliers = load_data("suppliers")
        employees = load_data("employees")
        sales = load_data("sales")

        # Search products by name or kind
        if any(keyword in query_lower for keyword in ["product", "products", "hookah", "flavor", "type", "kind"]):
            if not products:
                return "No products found in the database."
            matched_products = []
            for p in products:
                name = p.get("name", "").lower()
                kind = p.get("kind", "").lower()
                if any(word in query_lower for word in name.split()) or any(word in query_lower for word in kind.split()):
                    matched_products.append(p.get("name", "Unnamed"))
            if matched_products:
                return "Matching products: " + ", ".join(matched_products)
            else:
                return "No matching products found."

        # Search suppliers by name
        elif any(keyword in query_lower for keyword in ["supplier", "suppliers"]):
            if not suppliers:
                return "No suppliers found in the database."
            matched_suppliers = []
            for s in suppliers:
                name = s.get("name", "").lower()
                if any(word in query_lower for word in name.split()):
                    matched_suppliers.append(s.get("name", "Unnamed"))
            if matched_suppliers:
                return "Matching suppliers: " + ", ".join(matched_suppliers)
            else:
                return "No matching suppliers found."

        # Search employees by name or position
        elif any(keyword in query_lower for keyword in ["employee", "employees", "worker", "position"]):
            if not employees:
                return "No employees found in the database."
            matched_employees = []
            for e in employees:
                name = e.get("name", "").lower()
                position = e.get("position", "").lower()
                if any(word in query_lower for word in name.split()) or any(word in query_lower for word in position.split()):
                    matched_employees.append(e.get("name", "Unnamed"))
            if matched_employees:
                return "Matching employees: " + ", ".join(matched_employees)
            else:
                return "No matching employees found."

        # Sales info
        elif "sales" in query_lower:
            if not sales:
                return "No sales records found in the database."
            return f"There are {len(sales)} sales records in the database."

        else:
            return "Sorry, I did not understand your query. Please ask about products, suppliers, employees, or sales."
