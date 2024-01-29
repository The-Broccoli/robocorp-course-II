from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.FileSystem import FileSystem
from RPA.Archive import Archive
import os

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
    )
    download_CSV_file()
    open_robot_order_website()
    or_orders()
    archive_receipts()
    
def open_robot_order_website():
    """Open RobotSpareBin Industries Inc. order website."""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def download_CSV_file():
    """Download RobotSpareBin Industries Inc. orders CSV file."""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    
def or_orders():
    """Order robots from RobotSpareBin Industries Inc."""
    orders = get_orders()
    for order in orders:
        fill_the_form(order)
        embed_screenshot_to_receipt(f"order-{order['Order number']}-screenshot.png",
                                    f"order-{order['Order number']}.pdf")

def get_orders():
    """"""
    csv = Tables()
    orders = csv.read_table_from_csv("orders.csv")
    return orders

def fill_the_form(order):
    """Fill and order a robot."""
    page = browser.page()
    # close_annoying_modal(page)
    page.click("button:text('I guess so...')")
    page.select_option('#head', str(order["Head"]))
    page.check(f"#id-body-{str(order['Body'])}")
    page.fill('.form-control', str(order["Legs"]))
    page.fill('#address', str(order["Address"]))
    page.click("button:text('Order')")
    submit_form(str(order["Order number"]))

def submit_form(order_number):
    """Submit the form with error check"""
    page = browser.page()
    visible = page.locator("#receipt").is_visible()    
    if visible :
        save_order_html(order_number)
    else:
        page.click("button:text('Order')")
        submit_form(order_number)
    
def save_order_html(order_nr):
    """save the order HTML in PDF file"""
    page = browser.page()
    order_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(order_html, f"output/receipt/order-{order_nr}.pdf")
    screenshot_robot(order_nr)
    page.click("button:text('Order another robot')")
    
def close_annoying_modal(page):
    page.click("button:text('I guess so...')")

def screenshot_robot(order_nr):
    page = browser.page()   
    loc = page.locator("#robot-preview-image")
    loc.screenshot(path=f"output/order-{order_nr}-screenshot.png")
      
def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    list = [
        f"output/{screenshot}:align=center",
    ]
    pdf.add_files_to_pdf(files=list, target_document=f"output/receipt/{pdf_file}", append=True)

def archive_receipts():
    """Create ZIP archive for all orders-X.pdf files"""
    archive = Archive()
    archive.archive_folder_with_zip(folder="output/receipt", archive_name="output/receipt.zip")