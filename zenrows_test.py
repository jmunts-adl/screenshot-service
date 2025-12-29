from api.services.zenrows_service import capture_and_upload_with_zenrows

url = 'http://www.glassdoor.com/Reviews/Employee-Review-The-Forum-Group-RVW5662855.htm'
wait_for = '#__next > div.infosite-layout_infositeContainer__NqDCH.Layout_infositeContainer__B5217 > div > main > div.infosite-layout_moduleBorder__0yC6_ > div.module-container_moduleContainer__tpBfv.module-container_redesignContainer__rLCJ4 > div:nth-child(2) > h1'

# Capture screenshot and upload to Cloudinary using ZenRows service
print(f"Capturing screenshot for URL: {url}")
print(f"Waiting for selector: {wait_for}")

uploaded_url = capture_and_upload_with_zenrows(
    url=url,
    wait_for=wait_for,
    folder="Media Removal"  # Uses CLOUDINARY_FOLDER from env if not specified
)

print(f"\n✅ Success!")
print(f"Cloudinary URL: {uploaded_url}")

