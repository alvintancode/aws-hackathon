from apify_client import ApifyClient
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

# === CONFIGURATION ===
API_TOKEN = "apify_api_m6MiYDsbMaf4FaVyhMH4wcgpFtE1mt1uy6Jg"  # Replace with your own token
PORT = 8000
QUERY = "sausage organic, tofu, and broccoli"  # Search query for ASDA items
LIMIT = 5

# === SCRAPER FUNCTION ===
def fetch_asda_items():
    client = ApifyClient(API_TOKEN)

    run_input = {
        "query": QUERY,
        "limit": LIMIT,
    }

    print("🔄 Running ASDA scraper...")
    run = client.actor("jupri/asda-scraper").call(run_input=run_input)

    dataset_id = run["defaultDatasetId"]
    print(f"✅ Run complete. Dataset: {dataset_id}")

    items = list(client.dataset(dataset_id).iterate_items())
    return items, dataset_id

# === HTTP SERVER ===
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            items, dataset_id = fetch_asda_items()

            html = f"""
            <html>
            <head><title>ASDA Scraped Items</title></head>
            <body>
                <h1>ASDA Results for "{QUERY}"</h1>
                <p><a href="https://console.apify.com/storage/datasets/{dataset_id}" target="_blank">🔗 View dataset in Apify Console</a></p>
                <table border="1" cellpadding="8">
                    <tr><th>Name</th><th>Price</th></tr>
            """

            for item in items:
                name = item.get("name", "N/A")
                price = item.get("price", "N/A")
                html += f"<tr><td>{name}</td><td>{price}</td></tr>"

            html += """
                </table>
            </body>
            </html>
            """

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"<h1>Error</h1><p>{str(e)}</p>".encode("utf-8"))

# === SERVER LAUNCH ===
def run_server():
    print(f"🌐 Serving on http://localhost:{PORT}")
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, RequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
