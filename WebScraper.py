from apify_client import ApifyClient
from http.server import BaseHTTPRequestHandler, HTTPServer

# === CONFIGURATION ===
API_TOKEN = "apify_api_m6MiYDsbMaf4FaVyhMH4wcgpFtE1mt1uy6Jg"  # Replace with your token
PORT = 8000
QUERY = "tofu, brocolli, sausage"
LIMIT = 1
TIMEOUT = 10  # seconds
recipe1 = ["tofu", "rice", "black bean sauce", "minced beef"]
recipe2 = ["tomato", "dough", "pepperoni", "cheese"]
recipe3 = ["buns", "beef patty", "cheese", "lettuce"]
recipes = [recipe1, recipe2, recipe3]

# === SCRAPER FUNCTION ===
def fetch_asda_items():
    all_items = []
    for recipe in recipes:
        for item in recipe:
            client = ApifyClient(API_TOKEN)

            run_input = {
                "query": item,
                "limit": LIMIT,
            }

            try:
                print("🔄 Running ASDA scraper...")
                run = client.actor("jupri/asda-scraper").call(
                    run_input=run_input,
                    wait_secs=TIMEOUT,
                )
            except Exception:
                raise TimeoutError("❌ Scraper run did not complete within 10 seconds.")

            dataset_id = run.get("defaultDatasetId")
            if not dataset_id:
                raise RuntimeError("❌ No dataset returned from the run.")

            items = list(client.dataset(dataset_id).iterate_items())
            all_items.extend(items)

    return all_items

# === HTTP SERVER ===
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            items = fetch_asda_items()

            html = f"""
            <html>
            <head><title>ASDA Scraped Items</title></head>
            <body>
                <h1>ASDA Results for Mapo Tofu, Pizza, and Hamburger</h1>
                <table border="1" cellpadding="8">
                    <tr><th>Name</th><th>Price</th></tr>
            """

            def render_table(title, items):
                table_html = f"<h2>{title}</h2><table border='1' cellpadding='8'><tr><th>Name</th><th>Price</th></tr>"
                for item in items:
                    name = item.get("name", "N/A")
                    price = item.get("price", "N/A")
                    table_html += f"<tr><td>{name}</td><td>{price}</td></tr>"
                table_html += "</table><br>"
                return table_html

            # Segment items into hardcoded groups
            mapo_items = items[0:4]
            pizza_items = items[4:8]
            hamburger_items = items[8:]

            # Render sections
            html += render_table("🧄 Mapo Tofu Recipe", mapo_items)
            html += render_table("🍕 Pizza Recipe", pizza_items)
            html += render_table("🍔 Hamburger Recipe", hamburger_items)

            html += "</body></html>"

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))

        except TimeoutError as e:
            self.send_response(504)
            self.end_headers()
            self.wfile.write(f"<h1>504 Gateway Timeout</h1><p>{str(e)}</p>".encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"<h1>500 Internal Server Error</h1><p>{str(e)}</p>".encode("utf-8"))

# === SERVER LAUNCH ===
def run_server():
    print(f"🌐 Serving on http://localhost:{PORT}")
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, RequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
