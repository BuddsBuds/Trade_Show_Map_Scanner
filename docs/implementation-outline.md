# TradeShow Scout - Pseudo Code  
**Version**: 1.0  

---

## **File Processing Service**  
```python
class FileProcessor:
    def process_upload(files):
        if multiple_files:
            stitch_images(files)
        else:
            convert_to_image(file)

    def stitch_images(images):
        use OpenCV to align and merge overlapping images
```

## **OCR Service**  
```python
class OCRExtractor:
    def extract_data(image):
        preprocess(image)
        text = tesseract.extract_text(image)
        companies = regex_search(text)
        booth_sizes = regex_search(text) or default_10x10
        return JSON(companies, booth_sizes)
```

## **Contact Scraper**  
```python
class ContactScraper:
    def scrape(company_name):
        emails = hunter_api(company_name)
        linkedin_profiles = linkedin_api(company_name, filter="Marketing")
        return merged_contacts(emails, profiles)
```

## **Frontend (React)**  
```javascript
function FileUploader() {
  return (
    <Dropzone onDrop={files => uploadToBackend(files)}>
      {progress && <ProgressBar value={progress} />}
    </Dropzone>
  );
}